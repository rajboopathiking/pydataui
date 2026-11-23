import asyncio
import pytest
from starlette.testclient import TestClient

import pydataui as pdu
from pydataui.channels import ChannelHub, default_hub


def test_from_jsx_basic():
    """Verify pdu.from_jsx transpiles JSX into a native callable Component factory."""
    Card = pdu.from_jsx('''
    <div className="rounded-xl border bg-card p-4 text-card-foreground shadow-sm">
        <h3 className="font-semibold text-lg">{title}</h3>
        <p className="text-sm text-muted-foreground">{description}</p>
        <div className="mt-2">{children}</div>
    </div>
    ''')

    instance = Card(
        title="Agent Worker #1",
        description="Autonomous LLM Task Runner",
        children=[pdu.Text("Status: Healthy")]
    )

    rendered = instance.render({})
    assert 'class="rounded-xl border bg-card p-4 text-card-foreground shadow-sm"' in rendered
    assert "Agent Worker #1" in rendered
    assert "Autonomous LLM Task Runner" in rendered
    assert "Status: Healthy" in rendered
    assert "className=" not in rendered


def test_from_html_basic():
    """Verify pdu.from_html creates component factories with token slot interpolation."""
    Badge = pdu.from_html('''<span class="badge-custom">{label}</span>''')
    instance = Badge(label="ACTIVE")
    rendered = instance.render({})
    assert '<span class="badge-custom">ACTIVE</span>' == rendered


def test_channel_hub_subscribers_and_broadcast():
    """Verify ChannelHub subscription lifecycle and component broadcast."""
    hub = ChannelHub()
    assert hub.subscriber_count("telemetry") == 0

    class MockWebSocket:
        def __init__(self):
            self.sent = []
            self.closed = False

        async def send_text(self, text: str):
            if self.closed:
                raise RuntimeError("Closed")
            self.sent.append(text)

    ws1 = MockWebSocket()
    ws2 = MockWebSocket()

    hub.add_subscriber("telemetry", ws1)
    hub.add_subscriber("telemetry", ws2)
    assert hub.subscriber_count("telemetry") == 2

    # Broadcast string
    reached = asyncio.run(hub.broadcast("telemetry", "<div id='metric'>42</div>"))
    assert reached == 2
    assert ws1.sent[-1] == "<div id='metric'>42</div>"
    assert ws2.sent[-1] == "<div id='metric'>42</div>"

    # Broadcast Component
    reached = asyncio.run(hub.broadcast("telemetry", pdu.Heading("Live Node", level=2)))
    assert reached == 2
    assert "Live Node" in ws1.sent[-1]

    # Test disconnect cleanup
    ws1.closed = True
    reached = asyncio.run(hub.broadcast("telemetry", "Update"))
    assert reached == 1
    assert hub.subscriber_count("telemetry") == 1
    assert ws1 not in hub._subscribers["telemetry"]


def test_live_channel_procedural_context():
    """Verify pdu.live_channel renders an HTMX WebSocket container."""
    pdu.reset()

    with pdu.live_channel("ops_stream", key="ops-container", class_name="p-4 border rounded"):
        pdu.write("Ops telemetry stream active")

    app = pdu.get_app()
    html = app._renderer.render_page(lambda: pdu.dx._ProceduralPageLayout([], pdu.dx._default_page_components, False, ""), {})
    assert 'hx-ext="ws"' in html or "hx-ext='ws'" in html
    assert 'ws-connect="/_pdu/ws/ops_stream"' in html or "ws-connect='/_pdu/ws/ops_stream'" in html
    assert 'id="ops-container"' in html or "id='ops-container'" in html
    assert "Ops telemetry stream active" in html


def test_websocket_fastapi_asgi_streaming():
    """Integration test: connect to PyDataUI WebSocket endpoint and stream live updates."""
    app = pdu.App(title="WS Test App")

    @app.channel("heartbeat")
    async def stream_heartbeats():
        for i in range(3):
            yield f"<div id='beat'>{i}</div>"

    client = TestClient(app.asgi_app)

    with client.websocket_connect("/_pdu/ws/heartbeat") as ws:
        msg1 = ws.receive_text()
        assert msg1 == "<div id='beat'>0</div>"
        msg2 = ws.receive_text()
        assert msg2 == "<div id='beat'>1</div>"
        msg3 = ws.receive_text()
        assert msg3 == "<div id='beat'>2</div>"


def test_websocket_bidirectional_broadcast():
    """Integration test: connect to passive channel and receive broadcast pushes."""
    app = pdu.App(title="Broadcast App")

    client = TestClient(app.asgi_app)

    with client.websocket_connect("/_pdu/ws/market") as ws:
        # Push message from app.broadcast
        app.broadcast("market", "<div id='ticker'>NVDA: $148.50</div>")
        msg = ws.receive_text()
        assert msg == "<div id='ticker'>NVDA: $148.50</div>"


def test_procedural_channel_decorator_and_broadcast():
    """Integration test: connect to procedural channel registered via @pdu.channel."""
    pdu.reset()
    app = pdu.get_app()

    @pdu.channel("agent_stream")
    async def stream_agent():
        yield "<div id='status'>RUNNING</div>"

    client = TestClient(app.asgi_app)

    with client.websocket_connect("/_pdu/ws/agent_stream") as ws:
        msg = ws.receive_text()
        assert msg == "<div id='status'>RUNNING</div>"
        
        # Test procedural pdu.broadcast
        pdu.broadcast("agent_stream", "<div id='status'>COMPLETED</div>")
        msg2 = ws.receive_text()
        assert msg2 == "<div id='status'>COMPLETED</div>"

