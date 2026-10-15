"""
Tests for FastAPI Migration & Developer Experience Upgrade in PyDataUI.
Covers:
- FastAPI default backend
- Optional PyRustAPI backend fallback
- Native mounting inside FastAPI
- Simplified DX (ui.title, ui.button, etc.)
- Advanced components (Markdown, CodeEditor, Chat)
- Ecosystem compatibility (FastAPI co-hosting, async streaming/LangGraph simulation)
"""
import pytest
import httpx
from fastapi import FastAPI
from pydantic import BaseModel

import pydataui as ui
from pydataui import App, State, mount
from pydataui.components import Container, Heading, Text, Button, Card, Metric
from pydataui.components.advanced import Markdown, CodeEditor, Chat
from pydataui.backend import FastAPIEngine, RustAPIEngine


class CounterState(State):
    count: int = 0

    def increment(self):
        self.count += 1


class ItemPayload(BaseModel):
    name: str
    price: float


# -----------------------------------------------------------------------------
# 1. FastAPI Default Engine & Async / Pydantic Routing
# -----------------------------------------------------------------------------
@pytest.mark.anyio
async def test_fastapi_is_default_backend():
    app = App(title="FastAPI Default Test")
    assert isinstance(app._engine, FastAPIEngine)
    assert isinstance(app.asgi_app, FastAPI)


@pytest.mark.anyio
async def test_fastapi_endpoints_and_pydantic_support():
    app = App()

    @app.api("/calc", method="POST")
    async def calculate(item: ItemPayload):
        return {"total": item.price * 1.1, "item": item.name}

    @app.api("/greet", method="GET")
    async def greet(name: str = "World"):
        return {"message": f"Hello, {name}!"}

    transport = httpx.ASGITransport(app=app.asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Test GET
        res_get = await client.get("/greet?name=Developer")
        assert res_get.status_code == 200
        assert res_get.json() == {"message": "Hello, Developer!"}

        # Test POST with Pydantic body
        res_post = await client.post("/calc", json={"name": "Book", "price": 100.0})
        assert res_post.status_code == 200
        data = res_post.json()
        assert data["item"] == "Book"
        assert abs(data["total"] - 110.0) < 1e-4


# -----------------------------------------------------------------------------
# 2. Optional PyRustAPI Engine
# -----------------------------------------------------------------------------
def test_backend_selection():
    app_fastapi = App(backend="fastapi")
    assert isinstance(app_fastapi._engine, FastAPIEngine)

    # When backend='pyrustapi', RustAPIEngine should be instantiated or error informatively if not installed
    try:
        app_rust = App(backend="pyrustapi")
        assert isinstance(app_rust._engine, RustAPIEngine)
    except ImportError as e:
        assert "pyrustapi" in str(e).lower()


# -----------------------------------------------------------------------------
# 3. Native Mounting Inside Existing FastAPI App
# -----------------------------------------------------------------------------
@pytest.mark.anyio
async def test_native_mounting_inside_fastapi():
    # Create parent FastAPI enterprise service
    parent_api = FastAPI(title="Unified Service")

    @parent_api.get("/api/v1/health")
    async def service_health():
        return {"status": "ok", "service": "enterprise-nexus"}

    # Create PyDataUI dashboard app
    dashboard = App(title="Admin Dashboard")

    @dashboard.page("/")
    def dashboard_home():
        return Container(
            Heading(CounterState.count),
            Button("Increment", on_click=CounterState.increment)
        )

    # Mount via mount() helper
    mount(parent_api, dashboard, path="/dashboard")

    transport = httpx.ASGITransport(app=parent_api)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Main API route still works
        res_health = await client.get("/api/v1/health")
        assert res_health.status_code == 200
        assert res_health.json()["service"] == "enterprise-nexus"

        # 2. Mounted dashboard root page renders
        res_dash = await client.get("/dashboard/")
        assert res_dash.status_code == 200
        html = res_dash.text
        assert "Admin Dashboard" in html
        # Static asset link must include mount root path
        assert "/dashboard/_pdu/static/" in html

        # 3. Internal static file can be retrieved through the mount path
        res_static = await client.get("/dashboard/_pdu/static/css/pydataui.css")
        assert res_static.status_code == 200

        # 4. Trigger state event through mounted prefix
        cookie = res_dash.headers.get("set-cookie", "").split(";")[0]
        import re
        csrf_match = re.search(r'name="pdu-csrf-token" content="([^"]+)"', html)
        assert csrf_match, "CSRF token should be in rendered HTML"
        csrf = csrf_match.group(1)

        res_event = await client.post(
            "/dashboard/_pdu/event/CounterState/increment",
            headers={"Cookie": cookie, "X-CSRF-Token": csrf}
        )
        assert res_event.status_code == 200


@pytest.mark.anyio
async def test_dashboard_mount_to_method():
    parent_api = FastAPI()
    dashboard = App(title="Sub Dashboard")

    @dashboard.page("/")
    def home():
        return Text("Sub Dashboard Home")

    dashboard.mount_to(parent_api, path="/sub")

    transport = httpx.ASGITransport(app=parent_api)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/sub/")
        assert res.status_code == 200
        assert "Sub Dashboard Home" in res.text


# -----------------------------------------------------------------------------
# 4. Simplified DX (import pydataui as ui)
# -----------------------------------------------------------------------------
@pytest.mark.anyio
async def test_simplified_dx():
    # Reset default app state
    ui._default_app = None
    ui.dx._dx_default_app = None

    clicked = {"count": 0}

    def on_btn_click():
        clicked["count"] += 1

    ui.title("Minimal DX Dashboard")
    ui.text("Welcome to streamlined PyDataUI")
    ui.metric("Users", "1,200", change="+12%")
    ui.button("Click Me", on_click=on_btn_click)

    app = ui.get_default_app()
    assert app is not None

    transport = httpx.ASGITransport(app=app.asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/")
        assert res.status_code == 200
        html = res.text
        assert "Minimal DX Dashboard" in html
        assert "Welcome to streamlined PyDataUI" in html
        assert "1,200" in html

        # Verify button rendered with an event action
        assert "_pdu/event/ActionState/" in html


# -----------------------------------------------------------------------------
# 5. Advanced Python-First Components (Markdown, CodeEditor, Chat)
# -----------------------------------------------------------------------------
def test_advanced_components():
    # Markdown
    md_text = "# Header 1\n**bold text** and `inline_code`\n```python\nprint('hello')\n```"
    md = Markdown(md_text)
    md_html = md.render()
    assert "<h1" in md_html
    assert "<strong>bold text</strong>" in md_html
    assert "<pre><code" in md_html

    # CodeEditor
    code = "def add(a, b):\n    return a + b"
    editor = CodeEditor(value=code, language="python", read_only=True)
    editor_html = editor.render()
    assert "data-language=\"python\"" in editor_html
    assert "copy-code-btn" in editor_html
    assert "def add" in editor_html

    # Chat
    messages = [
        {"role": "user", "content": "Hello AI"},
        {"role": "assistant", "content": "Hello human, how can I help you today?"}
    ]
    chat = Chat(messages=messages, placeholder="Type your query...")
    chat_html = chat.render()
    assert "chat-container" in chat_html
    assert "Hello AI" in chat_html
    assert "Hello human" in chat_html
    assert "chat-input" in chat_html


# -----------------------------------------------------------------------------
# 6. Ecosystem Integration (FastAPI co-hosting & Async Streaming simulation)
# -----------------------------------------------------------------------------
@pytest.mark.anyio
async def test_fastapi_cohosting_and_streaming():
    import asyncio
    from starlette.responses import StreamingResponse

    parent = FastAPI()

    # LangGraph-style or LLM streaming endpoint
    @parent.get("/api/chat/stream")
    async def fake_llm_stream():
        async def token_generator():
            tokens = ["Hello", " ", "from", " ", "LangGraph", " ", "agent!"]
            for token in tokens:
                await asyncio.sleep(0.01)
                yield token
        return StreamingResponse(token_generator(), media_type="text/event-stream")

    # PyDataUI interface
    ui_app = App(title="AI Agent Interface")

    @ui_app.page("/")
    def ai_page():
        return Container(
            Heading("Agent Interface"),
            Chat(messages=[{"role": "assistant", "content": "Ready to process graphs."}])
        )

    parent.mount("/agent", ui_app.asgi_app)

    transport = httpx.ASGITransport(app=parent)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Check UI page
        res_ui = await client.get("/agent/")
        assert res_ui.status_code == 200
        assert "Agent Interface" in res_ui.text

        # Check async streaming endpoint
        res_stream = await client.get("/api/chat/stream")
        assert res_stream.status_code == 200
        stream_content = res_stream.text
        assert "Hello from LangGraph agent!" in stream_content
