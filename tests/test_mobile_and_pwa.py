"""
Tests for Mobile (PWA & Capacitor) and Desktop Shell in PyDataUI.
Verifies:
- Built-in Mobile PWA Manifest & Service Worker
- HTML mobile viewport and standalone webview meta tags
- Mount root path preservation for PWA assets
- Capacitor mobile shell scaffolding
- Tauri 2.0 desktop/mobile shell scaffolding
- CLI command parser for desktop & mobile
"""
import json
import pytest
import httpx
from fastapi import FastAPI
from pathlib import Path

import pydataui as ui
from pydataui import App, mount
from pydataui.components import Text, Heading, Container
from pydataui.shell import init_tauri, init_capacitor, open_desktop_window
from pydataui.cli.main import main


@pytest.mark.anyio
async def test_pwa_manifest_and_service_worker():
    app = App(title="Mobile Test App")

    @app.page("/")
    def home():
        return Heading("Mobile Home")

    transport = httpx.ASGITransport(app=app.asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. Test HTML includes mobile PWA tags and viewport-fit=cover
        res_page = await client.get("/")
        assert res_page.status_code == 200
        html = res_page.text
        assert 'name="apple-mobile-web-app-capable" content="yes"' in html
        assert 'name="mobile-web-app-capable" content="yes"' in html
        assert 'viewport-fit=cover' in html
        assert '/_pdu/manifest.json' in html
        assert '/_pdu/sw.js' in html

        # 2. Test manifest.json returns valid PWA standalone configuration
        res_manifest = await client.get("/_pdu/manifest.json")
        assert res_manifest.status_code == 200
        assert "application/manifest+json" in res_manifest.headers.get("content-type", "")
        manifest = res_manifest.json()
        assert manifest["name"] == "Mobile Test App"
        assert manifest["display"] == "standalone"
        assert manifest["start_url"] == "/"
        assert len(manifest["icons"]) >= 2

        # 3. Test sw.js returns service worker JavaScript
        res_sw = await client.get("/_pdu/sw.js")
        assert res_sw.status_code == 200
        assert "application/javascript" in res_sw.headers.get("content-type", "")
        assert "pydataui-cache-v1" in res_sw.text


@pytest.mark.anyio
async def test_pwa_in_mounted_fastapi():
    parent = FastAPI()
    sub_app = App(title="Sub Mobile App")

    @sub_app.page("/")
    def sub_home():
        return Text("Sub App")

    mount(parent, sub_app, path="/portal")

    transport = httpx.ASGITransport(app=parent)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Check rendered HTML uses mounted root path for manifest & sw
        res = await client.get("/portal/")
        assert res.status_code == 200
        assert "/portal/_pdu/manifest.json" in res.text
        assert "/portal/_pdu/sw.js" in res.text

        # Fetch manifest under mounted prefix
        res_manifest = await client.get("/portal/_pdu/manifest.json")
        assert res_manifest.status_code == 200
        manifest = res_manifest.json()
        assert manifest["start_url"] == "/portal/"
        assert manifest["scope"] == "/portal/"


def test_capacitor_scaffolding(tmp_path):
    config_file = init_capacitor(
        project_dir=str(tmp_path),
        app_name="Analytics Mobile",
        app_id="io.pydataui.analytics",
        port=8050
    )
    assert Path(config_file).exists()

    # Verify standalone capacitor.config.json has NO server.url (React Native / Offline Parity)
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    assert config["appId"] == "io.pydataui.analytics"
    assert config["appName"] == "Analytics Mobile"
    assert config["webDir"] == "www"
    assert "server" not in config

    # Verify live-sync / remote server configuration attaches server.url
    config_live = init_capacitor(
        project_dir=str(tmp_path),
        app_name="Analytics Mobile",
        app_id="io.pydataui.analytics",
        server_url="http://192.168.1.100:8050",
        overwrite=True
    )
    with open(config_live, "r", encoding="utf-8") as f:
        config_l = json.load(f)
    assert config_l["server"]["url"] == "http://192.168.1.100:8050"

    # Verify package.json
    pkg_file = tmp_path / "package.json"
    assert pkg_file.exists()
    with open(pkg_file, "r", encoding="utf-8") as f:
        pkg = json.load(f)
    assert "@capacitor/core" in pkg["devDependencies"]


def test_tauri_scaffolding(tmp_path):
    tauri_dir = init_tauri(
        project_dir=str(tmp_path),
        app_name="Enterprise Ops",
        identifier="com.ops.enterprise",
        port=9000
    )
    tauri_path = Path(tauri_dir)
    assert tauri_path.exists()
    assert (tauri_path / "Cargo.toml").exists()
    assert (tauri_path / "build.rs").exists()
    assert (tauri_path / "src" / "lib.rs").exists()
    assert (tauri_path / "src" / "main.rs").exists()
    assert (tauri_path / "capabilities" / "default.json").exists()

    # Check tauri.conf.json contents
    conf_file = tauri_path / "tauri.conf.json"
    with open(conf_file, "r", encoding="utf-8") as f:
        conf = json.load(f)
    assert conf["productName"] == "Enterprise Ops"
    assert conf["identifier"] == "com.ops.enterprise"
    assert conf["build"]["devUrl"] == "http://127.0.0.1:9000"


def test_cli_subparsers_exist():
    import argparse
    from pydataui.cli.main import main
    import sys

    # Test running with --help triggers SystemExit(0) cleanly
    old_argv = sys.argv
    try:
        sys.argv = ["pydataui", "desktop", "--help"]
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

        sys.argv = ["pydataui", "mobile", "--help"]
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

        sys.argv = ["pydataui", "mobile", "preview", "--help"]
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0

        sys.argv = ["pydataui", "mobile", "install", "--help"]
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
    finally:
        sys.argv = old_argv


@pytest.mark.anyio
async def test_mobile_preview_endpoint():
    from pydataui.shell.preview import get_preview_html, get_local_ip

    app = App(title="Simulator Test App")

    @app.page("/")
    def home():
        return Heading("Mobile View")

    transport = httpx.ASGITransport(app=app.asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        res = await client.get("/_pdu/preview")
        assert res.status_code == 200
        assert "text/html" in res.headers["content-type"]
        assert "Mobile Preview" in res.text
        assert "device-select" in res.text
        assert "iPhone 15 Pro" in res.text
        assert "Google Pixel 8" in res.text
        assert "Test on Real Phone" in res.text
        assert "create-qr-code" in res.text

    # Also test get_preview_html standalone
    html_raw = get_preview_html(target_url="/", app_title="Standalone Preview", port=8000)
    assert "<iframe" in html_raw
    assert "Standalone Preview" in html_raw
    assert get_local_ip() != ""


def test_headless_build_and_install_mobile(tmp_path):
    from pydataui.shell.capacitor import build_mobile, install_mobile

    # Test build_mobile without Android Studio/Xcode
    code_build = build_mobile(project_dir=str(tmp_path), platform="android")
    assert code_build == 0

    # Test install_mobile without adb/devices
    code_install = install_mobile(project_dir=str(tmp_path), platform="android")
    assert code_install == 0


@pytest.mark.anyio
async def test_live_auto_reload_and_factory(tmp_path):
    import os
    from pydataui.cli.main import _app_factory

    app_file = tmp_path / "sample_app.py"
    app_file.write_text("""from pydataui import App
from pydataui.components import Heading

app = App(title="Live Reload App", reload=True)

@app.page("/")
def home():
    return Heading("Live Reload Works!")
""")

    os.environ["PYDATAUI_APP_FILE"] = str(app_file)
    os.environ["PYDATAUI_MOBILE_PREVIEW"] = "1"
    os.environ["PYDATAUI_RELOAD"] = "1"

    asgi_app = _app_factory()
    assert asgi_app is not None

    transport = httpx.ASGITransport(app=asgi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # Check health returns boot_id
        res_health = await client.get("/_pdu/health")
        assert res_health.status_code == 200
        data = res_health.json()
        assert data["status"] == "ok"
        assert "boot_id" in data
        assert len(data["boot_id"]) > 0

        # Check preview page has auto-reload toolbar and polling script
        res_preview = await client.get("/_pdu/preview")
        assert res_preview.status_code == 200
        preview_html = res_preview.text
        assert "Auto-Reload: ON" in preview_html
        assert "reload-badge" in preview_html
        assert "checkServerHealth" in preview_html
        assert "reload-toast" in preview_html

        # Check main page has dev auto-reload script
        res_page = await client.get("/")
        assert res_page.status_code == 200
        page_html = res_page.text
        assert "PyDataUI Dev Auto-Reload Watcher" in page_html
        assert "/_pdu/health" in page_html

