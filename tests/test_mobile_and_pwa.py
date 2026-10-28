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

    # Verify capacitor.config.json
    with open(config_file, "r", encoding="utf-8") as f:
        config = json.load(f)
    assert config["appId"] == "io.pydataui.analytics"
    assert config["appName"] == "Analytics Mobile"
    assert "8050" in config["server"]["url"]

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

