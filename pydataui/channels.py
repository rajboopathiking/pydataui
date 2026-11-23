"""
Native Bi-Directional WebSockets and Real-Time Channel Streaming Engine for PyDataUI.

Enables high-throughput, sub-millisecond real-time DOM updates, live telemetry streams,
financial tickers, and AI agent operation streams without HTTP polling overhead.
"""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
from collections import defaultdict
from typing import Any, AsyncGenerator, Callable, Dict, Generator, List, Optional, Set, Union

logger = logging.getLogger("pydataui.channels")


class ChannelHub:
    """
    Central WebSocket broker managing client subscriptions, streaming generators,
    and bi-directional message dispatches for PyDataUI channels.
    """

    def __init__(self) -> None:
        self._subscribers: Dict[str, Set[Any]] = defaultdict(set)
        self._handlers: Dict[str, Callable] = {}
        self._message_handlers: Dict[str, Callable] = {}

    def register(self, channel_name: str, handler: Optional[Callable] = None) -> Callable:
        """
        Register a stream generator, async generator, or socket handler for a channel.
        Can be used as a decorator or method.

        Example:
            @hub.register("telemetry")
            async def stream_telemetry():
                while True:
                    yield pdu.metric("Throughput", "1.2k req/s")
                    await asyncio.sleep(1)
        """
        def decorator(func: Callable) -> Callable:
            self._handlers[channel_name] = func
            return func

        if handler is not None:
            return decorator(handler)
        return decorator

    def on_message(self, channel_name: str, handler: Callable) -> Callable:
        """Register a handler for incoming client messages on a channel."""
        self._message_handlers[channel_name] = handler
        return handler

    def add_subscriber(self, channel_name: str, ws: Any) -> None:
        """Add an active WebSocket connection to a channel."""
        self._subscribers[channel_name].add(ws)

    def remove_subscriber(self, channel_name: str, ws: Any) -> None:
        """Remove a WebSocket connection from a channel."""
        self._subscribers[channel_name].discard(ws)
        if not self._subscribers[channel_name]:
            self._subscribers.pop(channel_name, None)

    def subscriber_count(self, channel_name: str) -> int:
        """Return the number of active subscribers on a channel."""
        return len(self._subscribers.get(channel_name, ()))

    async def broadcast(self, channel_name: str, message: Any) -> int:
        """
        Broadcast a message to all active WebSocket clients subscribed to channel_name.
        Automatically renders Component objects to HTML strings.
        Returns the number of clients successfully reached.
        """
        subs = list(self._subscribers.get(channel_name, ()))
        if not subs:
            return 0

        # Serialize component / dict / string
        if hasattr(message, "render"):
            text = message.render()
        elif isinstance(message, dict):
            text = json.dumps(message)
        else:
            text = str(message)

        dead: List[Any] = []
        sent_count = 0

        for ws in subs:
            try:
                await ws.send_text(text)
                sent_count += 1
            except Exception:
                dead.append(ws)

        for d in dead:
            self.remove_subscriber(channel_name, d)

        return sent_count

    def broadcast_sync(self, channel_name: str, message: Any) -> int:
        """
        Thread-safe synchronous wrapper for broadcast.
        Safe to call from background threads, Celery tasks, or procedural DX functions.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            try:
                # If currently inside a running task in this event loop:
                asyncio.current_task()
                asyncio.create_task(self.broadcast(channel_name, message))
                return len(self._subscribers.get(channel_name, ()))
            except RuntimeError:
                task = asyncio.run_coroutine_threadsafe(self.broadcast(channel_name, message), loop)
                return task.result(timeout=5.0)
        else:
            return asyncio.run(self.broadcast(channel_name, message))

    async def handle_connection(self, channel_name: str, websocket: Any) -> None:
        """
        Handle a WebSocket client connection lifecycle:
        accepts connection, executes channel generator/handler if registered,
        and listens for client messages until disconnect.
        """
        await websocket.accept()
        self.add_subscriber(channel_name, websocket)

        handler = self._handlers.get(channel_name)
        msg_handler = self._message_handlers.get(channel_name)

        try:
            if handler is not None:
                if inspect.isasyncgenfunction(handler):
                    async for item in handler():
                        text = item.render() if hasattr(item, "render") else (json.dumps(item) if isinstance(item, dict) else str(item))
                        await websocket.send_text(text)
                elif inspect.isgeneratorfunction(handler):
                    for item in handler():
                        text = item.render() if hasattr(item, "render") else (json.dumps(item) if isinstance(item, dict) else str(item))
                        await websocket.send_text(text)
                elif inspect.iscoroutinefunction(handler):
                    sig = inspect.signature(handler)
                    if len(sig.parameters) >= 1:
                        await handler(websocket)
                    else:
                        await handler()
                else:
                    sig = inspect.signature(handler)
                    if len(sig.parameters) >= 1:
                        handler(websocket)
                    else:
                        handler()

            # Passive receiver loop for messages / keeping connection alive
            while True:
                data = await websocket.receive_text()
                if msg_handler is not None:
                    if inspect.iscoroutinefunction(msg_handler):
                        await msg_handler(data, websocket)
                    else:
                        msg_handler(data, websocket)
        except Exception:
            # Client disconnected or connection closed
            pass
        finally:
            self.remove_subscriber(channel_name, websocket)


# Default global channel hub for procedural DX and application channels
default_hub = ChannelHub()


def channel(channel_name: str) -> Callable:
    """
    Decorator to register a server-side WebSocket streaming generator or handler.

    Example:
        @pdu.channel("market_ticker")
        async def stream_ticker():
            while True:
                yield pdu.metric("NVDA", "$148.20", delta="+3.4%")
                await asyncio.sleep(0.5)
    """
    return default_hub.register(channel_name)


def broadcast(channel_name: str, message: Any) -> int:
    """
    Broadcast a component, HTML string, or data payload to all clients
    connected to channel_name.

    Example:
        pdu.broadcast("agent_logs", pdu.card("Agent #4 initialized subtask..."))
    """
    return default_hub.broadcast_sync(channel_name, message)
