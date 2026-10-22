"""Real-browser beta readiness tests.

Browser selection is configurable:

* ``PYDATAUI_BROWSER_EXECUTABLE`` - path to a Chromium-compatible executable.
  When unset, common system Chromium/Chrome locations (including EgoLite) are
  probed.
* ``PYDATAUI_BROWSER_CDP_ENDPOINT`` - localhost CDP endpoint for an already
  running browser.
* ``PYDATAUI_REQUIRE_BROWSER=1`` - turn an unavailable browser into a failure
  instead of a skip.

Playwright's managed Chromium is never downloaded by these tests.
"""
from __future__ import annotations

import os
import re
import shutil
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import ProxyHandler, build_opener

import pytest

playwright = pytest.importorskip("playwright.sync_api")

PROJECT = Path(__file__).resolve().parents[1]
EGOLITE_MAC = "/Applications/ego lite.app/Contents/MacOS/ego lite"


APP = r'''
import os
from pydataui import App, State, AuthManager
from pydataui.components import Container, Heading, Button, Text
from pydataui.components.advanced import Chat, Markdown
from pydataui.components.data_science import DataUpload
from pydataui.auth import LoginPage, UserMenu, current_user


class CounterState(State):
    count: int = 0

    def increment(self):
        self.count += 1


class ChatState(State):
    messages: list = []

    def send(self, message: str):
        self.messages = list(self.messages) + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "Echo: " + message},
        ]


class UploadState(State):
    last_name: str = ""
    last_size: int = 0

    def note_upload(self, file=None):
        self.last_name = getattr(file, "filename", "")
        self.last_size = getattr(file, "size", 0)


MARKDOWN_TEXT = """# Safe heading

This is **bold** and *italic* with `inline code`.

```python
print("safe")
```

- first item
- second item

[good link](https://example.com)

[bad link](javascript:window.__pwned=4)

<a href="javascript:window.__pwned=5">raw javascript link</a>

<img src="javascript:window.__pwned=6" onerror="window.__pwned=1">

<script>window.__pwned=2</script>

<button onclick="window.__pwned=3">raw button</button>
"""


def build_app():
    app = App(title="Browser Beta")

    auth = AuthManager()
    auth.add_user("alice", "browser-test-password")
    app.setup_auth(auth)

    @app.api("/upload", method="POST", public=True)
    async def upload(request):
        form = request.form()
        upload_file = form.get("file")
        return {
            "filename": getattr(upload_file, "filename", None),
            "size": upload_file.size if upload_file else 0,
        }

    @app.page("/login")
    def login():
        return LoginPage()

    @app.page("/")
    def home():
        return Container(
            Heading("Home"),
            Heading(CounterState.count, level=2),
            Button("Increment", on_click=CounterState.increment),
            UserMenu(current_user.get()),
        )

    @app.page("/chat")
    def chat():
        return Container(
            Heading("Chat"),
            Chat(messages=ChatState.messages, on_send=ChatState.send),
        )

    @app.page("/upload")
    def upload_page():
        return Container(
            Heading("Upload"),
            DataUpload(accept=".csv,.json", on_upload="/upload"),
        )

    @app.page("/upload-state")
    def upload_state_page():
        return Container(
            Heading("Upload State"),
            Text(UploadState.last_name),
            Text(UploadState.last_size),
            DataUpload(accept=".csv,.json", on_upload=UploadState.note_upload),
        )

    @app.page("/markdown")
    def markdown():
        return Container(Heading("Markdown Safety"), Markdown(MARKDOWN_TEXT))

    @app.page("/public", public=True)
    def public():
        return Container(Heading("Public Page"))

    return app


app = build_app()

if os.environ.get("PYDATAUI_TEST_MOUNT") == "1":
    from fastapi import FastAPI
    from pydataui import mount

    parent = FastAPI(title="Parent")

    @parent.get("/health")
    def health():
        return {"status": "ok"}

    mount(parent, app, path="/ops")
    asgi = parent
else:
    asgi = app.asgi_app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        asgi,
        host="127.0.0.1",
        port=int(os.environ["PYDATAUI_TEST_PORT"]),
        log_level="warning",
    )
'''


@dataclass
class Server:
    base: str
    process: subprocess.Popen
    log_path: Path
    log_handle: object

    def stop(self) -> None:
        self.process.terminate()
        try:
            self.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.log_handle.close()


def _browser_unavailable(reason: str) -> None:
    if os.environ.get("PYDATAUI_REQUIRE_BROWSER") == "1":
        pytest.fail("Browser test required but unavailable: " + reason)
    pytest.skip(reason)


def _browser_executable() -> str | None:
    explicit = os.environ.get("PYDATAUI_BROWSER_EXECUTABLE")
    if explicit:
        path = Path(explicit).expanduser()
        return str(path) if path.is_file() else None
    candidates = [
        EGOLITE_MAC,
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("msedge"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return str(candidate)
    return None


@pytest.fixture(scope="module")
def browser():
    executable = _browser_executable()
    cdp_endpoint = os.environ.get("PYDATAUI_BROWSER_CDP_ENDPOINT")
    if not executable and not cdp_endpoint:
        _browser_unavailable(
            "No Chromium-compatible executable found. Set "
            "PYDATAUI_BROWSER_EXECUTABLE or PYDATAUI_BROWSER_CDP_ENDPOINT."
        )
    if cdp_endpoint:
        endpoint_host = urlsplit(cdp_endpoint).hostname
        if endpoint_host not in {"127.0.0.1", "localhost", "::1"}:
            _browser_unavailable(
                "PYDATAUI_BROWSER_CDP_ENDPOINT must point at localhost."
            )

    try:
        pw = playwright.sync_playwright().start()
    except Exception as exc:
        _browser_unavailable(f"Playwright could not start: {exc}")

    launched = None
    try:
        if cdp_endpoint:
            launched = pw.chromium.connect_over_cdp(cdp_endpoint)
        else:
            launched = pw.chromium.launch(
                executable_path=executable,
                headless=True,
                args=[
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-background-networking",
                ],
            )
        yield launched
    except Exception as exc:
        _browser_unavailable(
            f"Could not launch Chromium-compatible browser at "
            f"{cdp_endpoint or executable}: {exc}"
        )
    finally:
        if launched is not None and not cdp_endpoint:
            try:
                launched.close()
            except Exception:
                pass
        pw.stop()


@contextmanager
def isolated_page(browser, viewport=None):
    context = browser.new_context(viewport=viewport)
    page = context.new_page()
    errors = {"console": [], "page": [], "failed": [], "http": []}

    def route_external(route, request):
        if request.url.startswith("https://cdn.tailwindcss.com"):
            route.fulfill(
                status=200,
                content_type="application/javascript",
                body="window.tailwind={config:{}};",
            )
        else:
            route.abort()

    def on_console(message):
        if message.type == "error":
            errors["console"].append(message.text)

    def on_response(response):
        if response.status >= 400 and not response.url.endswith("/favicon.ico"):
            errors["http"].append((response.status, response.url))

    page.route("https://**", route_external)
    page.on("console", on_console)
    page.on("pageerror", lambda exc: errors["page"].append(str(exc)))
    page.on("requestfailed", lambda req: errors["failed"].append(
        (req.url, str(req.failure))
    ))
    page.on("response", on_response)

    try:
        yield page, errors
    finally:
        context.close()


def assert_clean(errors):
    assert errors["console"] == []
    assert errors["page"] == []
    assert errors["failed"] == []
    assert errors["http"] == []


def login(page, server: Server, next_path: str = "/"):
    target = server.base + next_path
    page.goto(
        server.base + "/login?next=" + quote(next_path, safe="/")
    )
    page.fill("input[name=username]", "alice")
    page.fill("input[name=password]", "browser-test-password")
    with page.expect_response(
        lambda response: (
            response.request.method == "POST"
            and response.url.endswith("/_pdu/event/LoginState/login")
        )
    ) as response_info:
        page.get_by_role("button", name="Sign In", exact=True).click()
    assert response_info.value.status == 200
    page.wait_for_url(re.compile("^" + re.escape(target) + "$"))


def assert_no_horizontal_overflow(page):
    metrics = page.evaluate(
        "() => ({scrollWidth: document.documentElement.scrollWidth, "
        "innerWidth: window.innerWidth})"
    )
    assert metrics["scrollWidth"] <= metrics["innerWidth"] + 1, metrics


def _start_server(tmp_path_factory, mount: bool) -> Server:
    tmp_path = tmp_path_factory.mktemp("browser-server")
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    script = tmp_path / "browser_app.py"
    script.write_text(APP)
    env = dict(
        os.environ,
        PYTHONPATH=str(PROJECT),
        PYDATAUI_TEST_PORT=str(port),
        PYDATAUI_TEST_MOUNT="1" if mount else "0",
    )
    log_path = tmp_path / "server.log"
    log_handle = log_path.open("w")
    process = subprocess.Popen(
        [sys.executable, str(script)],
        env=env,
        stdout=log_handle,
        stderr=log_handle,
    )
    root = "/ops" if mount else ""
    base = f"http://127.0.0.1:{port}{root}"
    opener = build_opener(ProxyHandler({}))
    try:
        for _ in range(100):
            if process.poll() is not None:
                log_handle.close()
                pytest.fail("Browser fixture failed: " + log_path.read_text())
            try:
                opener.open(base + "/_pdu/health", timeout=0.2).close()
                break
            except OSError:
                time.sleep(0.1)
        else:
            process.terminate()
            process.wait(timeout=5)
            log_handle.close()
            pytest.fail("Browser fixture server did not become ready")
    except Exception:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        log_handle.close()
        raise
    return Server(base=base, process=process, log_path=log_path,
                  log_handle=log_handle)


@pytest.fixture(scope="module")
def default_server(tmp_path_factory):
    server = _start_server(tmp_path_factory, mount=False)
    yield server
    server.stop()


@pytest.fixture(scope="module")
def mounted_server(tmp_path_factory):
    server = _start_server(tmp_path_factory, mount=True)
    yield server
    server.stop()


def test_require_browser_flag_turns_missing_browser_into_failure(monkeypatch):
    monkeypatch.setenv("PYDATAUI_REQUIRE_BROWSER", "1")
    with pytest.raises(pytest.fail.Exception):
        _browser_unavailable("no browser available")


def test_browser_login_invalid_credentials_protected_access_and_logout(
    browser, default_server
):
    with isolated_page(browser) as (page, errors):
        page.goto(default_server.base + "/")
        page.wait_for_url(
            re.compile(re.escape(default_server.base + "/login?next=/") + "$")
        )

        page.fill("input[name=username]", "alice")
        page.fill("input[name=password]", "wrong-password")
        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and response.url.endswith("/_pdu/event/LoginState/login")
            )
        ) as response_info:
            page.get_by_role("button", name="Sign In", exact=True).click()
        assert response_info.value.status == 200
        page.get_by_text("Invalid username or password").wait_for()
        assert page.url.endswith("/login?next=/")

        page.fill("input[name=username]", "alice")
        page.fill("input[name=password]", "browser-test-password")
        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and response.url.endswith("/_pdu/event/LoginState/login")
            )
        ) as response_info:
            page.get_by_role("button", name="Sign In", exact=True).click()
        assert response_info.value.status == 200
        page.wait_for_url(
            re.compile("^" + re.escape(default_server.base + "/") + "$")
        )
        page.get_by_role("heading", name="Home", exact=True).wait_for()
        page.get_by_role("heading", name="0", exact=True).wait_for()

        page.goto(default_server.base + "/chat")
        page.get_by_role("heading", name="Chat", exact=True).wait_for()

        page.goto(default_server.base + "/")
        page.get_by_role("heading", name="Home", exact=True).wait_for()
        with page.expect_response(
            lambda response: response.url.endswith(
                "/_pdu/event/LoginState/logout"
            )
        ) as response_info:
            page.get_by_role("button", name="Logout", exact=True).click()
        assert response_info.value.status == 200
        page.wait_for_url(
            re.compile(
                "^" + re.escape(default_server.base + "/login") + "$"
            )
        )

        page.goto(default_server.base + "/")
        page.wait_for_url(
            re.compile(re.escape(default_server.base + "/login?next=/") + "$")
        )
        response = page.context.request.get(
            default_server.base + "/api/CounterState"
        )
        assert response.status == 401
        assert_clean(errors)


def test_browser_counter_updates_persist_and_sessions_are_isolated(
    browser, default_server
):
    with isolated_page(browser) as (first, first_errors):
        with isolated_page(browser) as (second, second_errors):
            login(first, default_server)
            login(second, default_server)
            assert first.context.cookies() != second.context.cookies()

            for value in range(1, 4):
                with first.expect_response(
                    lambda response: response.url.endswith(
                        "/_pdu/event/CounterState/increment"
                    )
                ) as response_info:
                    first.get_by_role(
                        "button", name="Increment", exact=True
                    ).click()
                assert response_info.value.status == 200
                first.get_by_role(
                    "heading", name=str(value), exact=True
                ).wait_for()

            first.reload()
            first.get_by_role("heading", name="3", exact=True).wait_for()

            second.reload()
            second.get_by_role("heading", name="0", exact=True).wait_for()
            with second.expect_response(
                lambda response: response.url.endswith(
                    "/_pdu/event/CounterState/increment"
                )
            ) as response_info:
                second.get_by_role(
                    "button", name="Increment", exact=True
                ).click()
            assert response_info.value.status == 200
            second.get_by_role("heading", name="1", exact=True).wait_for()

            first.reload()
            first.get_by_role("heading", name="3", exact=True).wait_for()

            first_api = first.context.request.get(
                default_server.base + "/api/CounterState"
            )
            second_api = second.context.request.get(
                default_server.base + "/api/CounterState"
            )
            assert first_api.status == 200 and first_api.json()["count"] == 3
            assert second_api.status == 200 and second_api.json()["count"] == 1
            assert_clean(first_errors)
            assert_clean(second_errors)


def test_browser_mounted_dashboard_navigation_assets_events_and_upload(
    browser, mounted_server
):
    with isolated_page(browser) as (page, errors):
        page.goto(mounted_server.base + "/")
        page.wait_for_url(
            re.compile(
                re.escape(mounted_server.base + "/login?next=/") + "$"
            )
        )

        login(page, mounted_server, next_path="/chat")
        page.get_by_role("heading", name="Chat", exact=True).wait_for()

        page.goto(mounted_server.base + "/")
        page.get_by_role("heading", name="Home", exact=True).wait_for()
        assets = page.eval_on_selector_all(
            "link[rel=stylesheet][href], script[src]",
            "els => els.map(el => el.href || el.src)"
            ".filter(src => src && new URL(src).pathname.includes('/_pdu/static/'))"
            ".map(src => new URL(src).pathname)",
        )
        assert assets
        assert all(
            asset.startswith("/ops/_pdu/static/") for asset in assets
        )
        for asset in assets:
            response = page.context.request.get(urljoin(mounted_server.base, asset))
            assert response.status == 200

        with page.expect_response(
            lambda response: response.url.startswith(
                mounted_server.base + "/_pdu/event/CounterState/increment"
            )
        ) as response_info:
            page.get_by_role(
                "button", name="Increment", exact=True
            ).click()
        assert response_info.value.status == 200
        page.get_by_role("heading", name="1", exact=True).wait_for()

        page.goto(mounted_server.base + "/chat")
        page.fill(".chat-input", "mounted hello")
        with page.expect_response(
            lambda response: response.url.startswith(
                mounted_server.base + "/_pdu/event/ChatState/send"
            )
        ) as response_info:
            page.get_by_role("button", name="Send", exact=True).click()
        assert response_info.value.status == 200
        page.get_by_text("Echo: mounted hello", exact=True).wait_for()

        page.goto(mounted_server.base + "/upload")
        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and response.url == mounted_server.base + "/upload"
            )
        ) as response_info:
            page.set_input_files(
                "input[type=file]",
                files=[
                    {
                        "name": "mounted.csv",
                        "mimeType": "text/csv",
                        "buffer": b"a,b\n1,2\n",
                    }
                ],
            )
        assert response_info.value.status == 200
        assert response_info.value.json()["filename"] == "mounted.csv"

        page.goto(mounted_server.base + "/")
        page.get_by_role("heading", name="Home", exact=True).wait_for()
        with page.expect_response(
            lambda response: response.url.startswith(
                mounted_server.base + "/_pdu/event/LoginState/logout"
            )
        ) as response_info:
            page.get_by_role("button", name="Logout", exact=True).click()
        assert response_info.value.status == 200
        page.wait_for_url(
            re.compile(
                "^" + re.escape(mounted_server.base + "/login") + "$"
            )
        )
        assert_clean(errors)


def test_browser_chat_submission_and_documented_upload_callbacks(
    browser, default_server
):
    with isolated_page(browser) as (page, errors):
        login(page, default_server)

        page.goto(default_server.base + "/chat")
        page.fill(".chat-input", "hello beta")
        with page.expect_response(
            lambda response: response.url.endswith("/_pdu/event/ChatState/send")
        ) as response_info:
            page.get_by_role("button", name="Send", exact=True).click()
        assert response_info.value.status == 200
        page.get_by_text("hello beta", exact=True).wait_for()
        page.get_by_text("Echo: hello beta", exact=True).wait_for()

        page.reload()
        page.get_by_text("Echo: hello beta", exact=True).wait_for()

        page.goto(default_server.base + "/upload")
        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and response.url == default_server.base + "/upload"
            )
        ) as response_info:
            page.set_input_files(
                "input[type=file]",
                files=[
                    {
                        "name": "data.csv",
                        "mimeType": "text/csv",
                        "buffer": b"a,b\n1,2\n",
                    }
                ],
            )
        payload = response_info.value.json()
        assert response_info.value.status == 200
        assert payload == {"filename": "data.csv", "size": 8}

        page.goto(default_server.base + "/upload-state")
        with page.expect_response(
            lambda response: response.url.endswith(
                "/_pdu/event/UploadState/note_upload"
            )
        ) as response_info:
            page.set_input_files(
                "input[type=file]",
                files=[
                    {
                        "name": "state.csv",
                        "mimeType": "text/csv",
                        "buffer": b"x,y\n3,4\n",
                    }
                ],
            )
        assert response_info.value.status == 200
        page.get_by_text("state.csv", exact=True).wait_for()
        page.get_by_text("8", exact=True).wait_for()
        assert_clean(errors)


def test_browser_markdown_formatting_and_active_content_rejection(
    browser, default_server
):
    with isolated_page(browser) as (page, errors):
        login(page, default_server)
        page.goto(default_server.base + "/markdown")

        markdown = page.locator(".pdu-markdown")
        assert markdown.locator("h1").inner_text() == "Safe heading"
        assert markdown.locator("strong").inner_text() == "bold"
        assert markdown.locator("em").inner_text() == "italic"
        assert markdown.locator("code").first.inner_text() == "inline code"
        assert markdown.locator("pre code").inner_text().strip() == 'print("safe")'
        assert markdown.locator("li").count() == 2

        assert markdown.locator("script").count() == 0
        assert markdown.locator("[onerror]").count() == 0
        assert markdown.locator("[onclick]").count() == 0
        assert markdown.locator("button").count() == 0

        links = page.eval_on_selector_all(
            ".pdu-markdown a", "els => els.map(el => el.getAttribute('href'))"
        )
        assert "https://example.com" in links
        assert all(
            not (href or "").strip().lower().startswith("javascript:")
            for href in links
        )
        assert page.evaluate("window.__pwned") is None
        assert_clean(errors)


def test_browser_console_network_and_responsive_layout(
    browser, default_server
):
    with isolated_page(
        browser, viewport={"width": 1280, "height": 800}
    ) as (page, errors):
        login(page, default_server)
        page.get_by_role("heading", name="Home", exact=True).wait_for()
        assert_no_horizontal_overflow(page)
        increment = page.get_by_role("button", name="Increment", exact=True)
        assert increment.is_visible()
        box = increment.bounding_box()
        assert box and box["x"] >= 0 and box["x"] + box["width"] <= 1280

        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("window.innerWidth") == 390
        assert_no_horizontal_overflow(page)
        assert increment.is_visible()
        box = increment.bounding_box()
        assert box and box["x"] >= 0 and box["x"] + box["width"] <= 390

        page.goto(default_server.base + "/chat")
        assert_no_horizontal_overflow(page)
        chat_input = page.locator(".chat-input")
        assert chat_input.is_visible()
        input_box = chat_input.bounding_box()
        assert input_box and input_box["x"] >= 0
        assert input_box["x"] + input_box["width"] <= 390
        assert page.get_by_role("button", name="Send", exact=True).is_visible()

        page.goto(default_server.base + "/login")
        assert_no_horizontal_overflow(page)
        assert page.locator("form").is_visible()
        assert_clean(errors)
