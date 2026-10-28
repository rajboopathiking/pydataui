import json
import pytest
from pydataui import App, State
from pydataui.components import Button, Container, Heading, Card
from pydataui.shell.bridge import JNIBridge, dispatch_in_process


class CounterBridgeState(State):
    count: int = 100

    def increment(self):
        self.count += 10

    def decrement(self):
        self.count -= 10

    def reset(self):
        self.count = 100


def test_jni_bridge_initialization():
    """Verify JNIBridge class and singleton dispatch."""
    bridge = JNIBridge()
    assert bridge is not None


def test_jni_bridge_get_page():
    """Verify in-process GET page dispatch without HTTP sockets."""
    app = App(title="JNI Bridge App")

    @app.page("/")
    def index():
        return Container(
            Heading("JNI In-Process Bridge Active", id="hero-title"),
            Heading(CounterBridgeState.count, id="counter-value"),
            Button("+10", on_click=CounterBridgeState.increment),
        )

    res = dispatch_in_process("GET", "/", app=app)

    assert isinstance(res, dict)
    assert res["status_code"] == 200
    assert res["status"] == 200
    assert isinstance(res["body"], bytes)
    assert isinstance(res["body_text"], str)
    assert "JNI In-Process Bridge Active" in res["body_text"]
    assert "text/html" in res["content_type"]

    headers = json.loads(res["headers_json"])
    assert isinstance(headers, dict)


def test_jni_bridge_post_event_execution():
    """Verify in-process POST event dispatch and state mutation."""
    app = App(title="JNI Event App")

    @app.page("/")
    def index():
        return Container(
            Heading(CounterBridgeState.count, id="val"),
            Button("+10", on_click=CounterBridgeState.increment),
        )

    # 1. Get initial page to establish session cookie & csrf token
    init_res = dispatch_in_process("GET", "/", app=app)
    cookie = init_res["headers"].get("set-cookie") or init_res["headers"].get("Set-Cookie", "")
    cookie_val = cookie.split(";", 1)[0]
    import re
    token = re.search(r'name="pdu-csrf-token" content="([^"]+)"', init_res["body_text"]).group(1)

    req_headers = {
        "cookie": cookie_val,
        "x-csrf-token": token,
        "hx-request": "true",
    }

    # 2. Fire action via in-process JNI dispatch
    event_res = dispatch_in_process(
        "POST",
        "/_pdu/event/CounterBridgeState/increment",
        headers=json.dumps(req_headers),
        body="",
        app=app,
    )

    assert event_res["status_code"] == 200
    assert "110" in event_res["body_text"]


def test_jni_bridge_targeted_partial_re_render():
    """Verify in-process JNI dispatch supports targeted component subtree re-renders."""
    app = App(title="JNI Partial App")

    @app.page("/")
    def index():
        return Container(
            Heading("Main Page Title", id="main-title"),
            Card(
                Heading(CounterBridgeState.count, id="card-val"),
                id="target-card",
            ),
            Button("Inc", on_click=CounterBridgeState.increment.target_to("#target-card")),
        )

    init_res = dispatch_in_process("GET", "/", app=app)
    cookie_val = (init_res["headers"].get("set-cookie") or init_res["headers"].get("Set-Cookie", "")).split(";", 1)[0]
    import re
    token = re.search(r'name="pdu-csrf-token" content="([^"]+)"', init_res["body_text"]).group(1)

    # Fire event with hx-target: #target-card
    req_headers = {
        "cookie": cookie_val,
        "x-csrf-token": token,
        "hx-request": "true",
        "hx-target": "#target-card",
    }

    event_res = dispatch_in_process(
        "POST",
        "/_pdu/event/CounterBridgeState/increment",
        headers=req_headers,
        body="",
        app=app,
    )

    assert event_res["status_code"] == 200
    # Targeted partial re-render should return ONLY #target-card, not #main-title!
    assert 'id="target-card"' in event_res["body_text"]
    assert "Main Page Title" not in event_res["body_text"]
    assert "110" in event_res["body_text"]


def test_jni_bridge_health_endpoint():
    """Verify internal health endpoint dispatch."""
    app = App(title="Health App")
    res = dispatch_in_process("GET", "/_pdu/health", app=app)
    assert res["status_code"] == 200
    data = json.loads(res["body_text"])
    assert data["status"] == "ok"
