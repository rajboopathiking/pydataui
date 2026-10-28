"""
Backend abstraction layer for PyDataUI.
Provides FastAPI as the default backend with optional PyRustAPI support.
"""
from __future__ import annotations
import inspect
import functools
import json
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response
import httpx


DEFAULT_MAX_REQUEST_SIZE = 10 * 1024 * 1024


def _body_limit_response() -> bytes:
    return b"Request body too large"


async def _send_body_limit_exceeded(send: Callable) -> None:
    body = _body_limit_response()
    await send({
        "type": "http.response.start",
        "status": 413,
        "headers": [
            (b"content-type", b"text/plain; charset=utf-8"),
            (b"content-length", str(len(body)).encode("ascii")),
            (b"connection", b"close"),
        ],
    })
    await send({
        "type": "http.response.body",
        "body": body,
        "more_body": False,
    })


def _scope_content_length(scope: Dict[str, Any]) -> Optional[int]:
    for key, value in scope.get("headers") or []:
        if isinstance(key, bytes):
            is_match = key.lower() == b"content-length"
        else:
            is_match = str(key).lower() == "content-length"
        if not is_match:
            continue
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    return None


class BodyBufferASGIMiddleware:
    """Buffers the HTTP request body with a hard size limit."""
    def __init__(self, app: Any, max_request_size: int = DEFAULT_MAX_REQUEST_SIZE):
        self.app = app
        self.max_request_size = int(max_request_size)

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        content_length = _scope_content_length(scope)
        if content_length is not None and content_length > self.max_request_size:
            await _send_body_limit_exceeded(send)
            return

        if scope.get("method") in ("GET", "HEAD"):
            scope["_cached_body"] = b""
            scope["_cached_json"] = {}
            await self.app(scope, receive, send)
            return

        buffer = bytearray()
        more_body = True
        while more_body:
            message = await receive()
            if message.get("type") == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(buffer) + len(chunk) > self.max_request_size:
                await _send_body_limit_exceeded(send)
                return
            buffer.extend(chunk)
            more_body = message.get("more_body", False)

        body = bytes(buffer)
        scope["_cached_body"] = body
        if body:
            try:
                scope["_cached_json"] = json.loads(body.decode("utf-8"))
            except Exception:
                scope["_cached_json"] = None
        else:
            scope["_cached_json"] = {}

        sent_body = False
        async def cached_receive() -> Dict[str, Any]:
            nonlocal sent_body
            if not sent_body:
                sent_body = True
                return {"type": "http.request", "body": body, "more_body": False}
            return await receive()

        await self.app(scope, cached_receive, send)


def _normalize_endpoint(func: Callable) -> Callable:
    """
    Ensure parameters named 'request' are annotated with Request
    so FastAPI does not treat them as required query parameters.
    Preserves exact callable signature, wrapper name, and docstring.
    """
    sig = getattr(func, "__signature__", None) or inspect.signature(func)
    params = list(sig.parameters.values())
    modified = False
    new_params = []
    for p in params:
        if p.name == "request" and p.annotation is inspect.Parameter.empty:
            new_params.append(p.replace(annotation=Request))
            modified = True
        else:
            new_params.append(p)

    if not modified and not inspect.iscoroutinefunction(func):
        return func

    new_sig = sig.replace(parameters=new_params)
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

    wrapper.__signature__ = new_sig
    return wrapper


class FastAPIEngine:
    """FastAPI-based ASGI engine for PyDataUI."""

    def __init__(
        self,
        title: str = "PyDataUI App",
        description: str = "",
        version: str = "0.3.4",
        docs_url: Optional[str] = None,
        openapi_url: Optional[str] = None,
        max_request_size: int = DEFAULT_MAX_REQUEST_SIZE,
        **kwargs
    ):
        from fastapi import FastAPI
        self.title = title
        self.description = description
        self.version = version
        self.docs_url = docs_url
        self.openapi_url = openapi_url
        self.max_request_size = int(max_request_size)
        self.auth = None

        self.app = FastAPI(
            title=title,
            description=description,
            version=version,
            docs_url=None,
            redoc_url=None,
            openapi_url=None,
        )
        self.app.add_middleware(
            BodyBufferASGIMiddleware,
            max_request_size=self.max_request_size,
        )

    def get(self, path: str, **kwargs):
        def decorator(func: Callable):
            norm_func = _normalize_endpoint(func)
            self.app.add_api_route(path, norm_func, methods=["GET"], **kwargs)
            return func
        return decorator

    def post(self, path: str, **kwargs):
        def decorator(func: Callable):
            norm_func = _normalize_endpoint(func)
            self.app.add_api_route(path, norm_func, methods=["POST"], **kwargs)
            return func
        return decorator

    def put(self, path: str, **kwargs):
        def decorator(func: Callable):
            norm_func = _normalize_endpoint(func)
            self.app.add_api_route(path, norm_func, methods=["PUT"], **kwargs)
            return func
        return decorator

    def delete(self, path: str, **kwargs):
        def decorator(func: Callable):
            norm_func = _normalize_endpoint(func)
            self.app.add_api_route(path, norm_func, methods=["DELETE"], **kwargs)
            return func
        return decorator

    def patch(self, path: str, **kwargs):
        def decorator(func: Callable):
            norm_func = _normalize_endpoint(func)
            self.app.add_api_route(path, norm_func, methods=["PATCH"], **kwargs)
            return func
        return decorator

    def options(self, path: str, **kwargs):
        def decorator(func: Callable):
            norm_func = _normalize_endpoint(func)
            self.app.add_api_route(path, norm_func, methods=["OPTIONS"], **kwargs)
            return func
        return decorator

    def head(self, path: str, **kwargs):
        def decorator(func: Callable):
            norm_func = _normalize_endpoint(func)
            self.app.add_api_route(path, norm_func, methods=["HEAD"], **kwargs)
            return func
        return decorator

    def _get_swagger_ui_html(self) -> str:
        from fastapi.openapi.docs import get_swagger_ui_html
        api_openapi_url = self.openapi_url or "/openapi.json"
        response = get_swagger_ui_html(openapi_url=api_openapi_url, title=f"{self.title} - Swagger UI")
        return response.body.decode("utf-8")

    def openapi(self) -> Dict[str, Any]:
        from fastapi.openapi.utils import get_openapi
        if getattr(self.app, "openapi_schema", None):
            return self.app.openapi_schema
        schema = get_openapi(
            title=self.title,
            version=self.version,
            description=self.description,
            routes=self.app.routes,
        )
        self.app.openapi_schema = schema
        return schema

    async def dispatch_request(
        self,
        method: str,
        path: str,
        query_string: str = "",
        headers: Optional[Dict[str, str]] = None,
        body: Union[str, bytes] = "",
    ) -> Tuple[int, str, Dict[str, str]]:
        url = f"http://testserver{path}"
        if query_string:
            url += f"?{query_string}"

        content = body.encode("utf-8") if isinstance(body, str) else body
        transport = httpx.ASGITransport(app=self.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            resp = await client.request(
                method=method,
                url=url,
                headers=headers or {},
                content=content,
            )
            resp_headers = {k.lower(): v for k, v in resp.headers.items()}
            if "set-cookie" in resp_headers:
                resp_headers["Set-Cookie"] = resp_headers["set-cookie"]

            try:
                text_body = resp.text
            except Exception:
                text_body = resp.content.decode("utf-8", errors="replace")
            return resp.status_code, text_body, resp_headers

    def run(self, host: str = "127.0.0.1", port: int = 8000, reload: bool = False, workers: int = 1):
        import uvicorn
        if workers > 1 or reload:
            import sys
            main_mod = sys.modules.get("__main__")
            app_attr = None
            if main_mod:
                for k, v in main_mod.__dict__.items():
                    if (hasattr(v, "_engine") and getattr(v, "_engine", None) is self) or v is self.app:
                        app_attr = k
                        break
            if app_attr and hasattr(main_mod, "__file__") and main_mod.__file__:
                import os
                mod_name = os.path.splitext(os.path.basename(main_mod.__file__))[0]
                target = f"{mod_name}:{app_attr}.asgi_app" if hasattr(getattr(main_mod, app_attr), "asgi_app") else f"{mod_name}:{app_attr}"
                uvicorn.run(target, host=host, port=port, reload=reload, workers=workers)
                return
        uvicorn.run(self.app, host=host, port=port)

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        await self.app(scope, receive, send)


class RustAPIEngine:
    """Optional PyRustAPI engine for PyDataUI."""

    def __init__(self, *args, **kwargs):
        try:
            from rustapi import FastAPI as RustAPIApp
        except ImportError as e:
            raise ImportError(
                "PyRustAPI backend requested, but 'pyrustapi' / 'rustapi' is not installed. "
                "Install it with: pip install 'pydataui[pyrustapi]'"
            ) from e
        self._engine = RustAPIApp(*args, **kwargs)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._engine, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_engine":
            super().__setattr__(name, value)
        else:
            setattr(self._engine, name, value)

    async def __call__(self, scope: Dict[str, Any], receive: Callable, send: Callable) -> None:
        if hasattr(self._engine, "__call__"):
            await self._engine(scope, receive, send)
        else:
            raise NotImplementedError("PyRustAPI engine does not implement ASGI __call__ directly.")


def create_engine(backend: str = "fastapi", **kwargs) -> Any:
    """Factory creating either FastAPIEngine (default) or RustAPIEngine."""
    backend_norm = (backend or "fastapi").strip().lower()
    if backend_norm == "fastapi":
        return FastAPIEngine(**kwargs)
    elif backend_norm in ("pyrustapi", "rustapi"):
        kwargs.pop("max_request_size", None)
        return RustAPIEngine(**kwargs)
    else:
        raise ValueError(
            f"Unknown PyDataUI backend: '{backend}'. Available backends: 'fastapi' (default), 'pyrustapi'."
        )
