"""
Tauri 2.0 Native Desktop & Mobile Integration for PyDataUI.
Provides scaffolding, development live-sync, and production bundling
for macOS (.app, .dmg), Windows (.exe, .msi), Linux (.deb, AppImage),
Android (.apk, .aab), and iOS (.ipa).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import urlopen, Request


def get_tauri_cli_cmd() -> List[str]:
    """Return the command to invoke Tauri CLI (local cargo-tauri or npx)."""
    if shutil.which("cargo-tauri"):
        return ["cargo-tauri"]
    if shutil.which("tauri"):
        return ["tauri"]
    return ["npx", "--yes", "@tauri-apps/cli@latest"]


def init_tauri(
    project_dir: str = ".",
    app_name: str = "PyDataUI App",
    identifier: str = "com.pydataui.app",
    port: int = 8000,
    overwrite: bool = False,
) -> str:
    """
    Scaffold a complete, production-ready Tauri 2.0 shell for desktop and mobile.
    """
    root = Path(project_dir).resolve()
    tauri_dir = root / "src-tauri"
    src_dir = tauri_dir / "src"
    caps_dir = tauri_dir / "capabilities"
    dist_dir = root / "dist"

    if tauri_dir.exists() and not overwrite:
        return str(tauri_dir)

    src_dir.mkdir(parents=True, exist_ok=True)
    caps_dir.mkdir(parents=True, exist_ok=True)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 1. Dist placeholder index.html (fallback when dev server is offline)
    index_html = dist_dir / "index.html"
    if not index_html.exists():
        index_html.write_text(
            f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{app_name}</title>
    <style>
        body {{
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #09090b;
            color: #f4f4f5;
        }}
        .spinner {{
            width: 40px;
            height: 40px;
            border: 3px solid rgba(255,255,255,0.1);
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
            margin: 0 auto 16px;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div style="text-align: center;">
        <div class="spinner"></div>
        <h2>Starting {app_name}...</h2>
        <p style="color: #71717a; font-size: 14px;">Connecting to PyDataUI core backend</p>
    </div>
    <script>
        // Auto-redirect to local server once available
        function checkServer() {{
            fetch("http://127.0.0.1:{port}/_pdu/health")
                .then(r => {{ if (r.ok) window.location.href = "http://127.0.0.1:{port}"; }})
                .catch(() => setTimeout(checkServer, 400));
        }}
        checkServer();
    </script>
</body>
</html>
""",
            encoding="utf-8",
        )

    # 2. Cargo.toml
    cargo_toml = f"""[package]
name = "{identifier.split('.')[-1].lower()}-shell"
version = "1.1.1"
description = "{app_name} Native Desktop & Mobile Application Shell"
authors = ["Boopathi Raj <rajboopathiking@gmail.com>"]
edition = "2021"

[lib]
name = "pydataui_app_lib"
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = {{ version = "2", features = [] }}

[dependencies]
tauri = {{ version = "2", features = [] }}
serde = {{ version = "1", features = ["derive"] }}
serde_json = "1"
"""
    (tauri_dir / "Cargo.toml").write_text(cargo_toml, encoding="utf-8")

    # 3. build.rs
    build_rs = """fn main() {
    tauri_build::build()
}
"""
    (tauri_dir / "build.rs").write_text(build_rs, encoding="utf-8")

    # 4. src/lib.rs (Tauri 2 cross-platform library entrypoint)
    lib_rs = """#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .setup(|_app| {
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running PyDataUI native application");
}
"""
    (src_dir / "lib.rs").write_text(lib_rs, encoding="utf-8")

    # 5. src/main.rs (Desktop binary entrypoint)
    main_rs = """#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    pydataui_app_lib::run();
}
"""
    (src_dir / "main.rs").write_text(main_rs, encoding="utf-8")

    # 6. capabilities/default.json (Tauri 2 Security & Windows)
    cap_json = {
        "$schema": "../gen/schemas/desktop-schema.json",
        "identifier": "default",
        "description": f"Default capabilities for {app_name}",
        "windows": ["main*"],
        "permissions": [
            "core:default",
            "core:window:allow-start-dragging",
            "core:window:allow-close",
            "core:window:allow-set-title",
            "core:window:allow-maximize",
            "core:window:allow-minimize",
            "core:window:allow-unmaximize",
            "core:window:allow-unminimize",
            "core:window:allow-show",
            "core:window:allow-hide",
        ],
    }
    (caps_dir / "default.json").write_text(json.dumps(cap_json, indent=2), encoding="utf-8")

    # 7. tauri.conf.json (Core configuration for Desktop + iOS + Android)
    tauri_conf = {
        "$schema": "https://schema.tauri.app/config/2",
        "productName": app_name,
        "version": "1.1.1",
        "identifier": identifier,
        "build": {
            "beforeDevCommand": "",
            "devUrl": f"http://127.0.0.1:{port}",
            "beforeBuildCommand": "",
            "frontendDist": "../dist",
        },
        "app": {
            "windows": [
                {
                    "label": "main",
                    "title": app_name,
                    "width": 1200,
                    "height": 800,
                    "minWidth": 640,
                    "minHeight": 480,
                    "resizable": True,
                    "fullscreen": False,
                    "center": True,
                }
            ],
            "security": {
                "csp": None,
            },
        },
        "bundle": {
            "active": True,
            "targets": "all",
            "category": "DeveloperTool",
            "shortDescription": app_name,
            "longDescription": f"{app_name} built with PyDataUI and Tauri 2.0",
        },
    }
    (tauri_dir / "tauri.conf.json").write_text(json.dumps(tauri_conf, indent=2), encoding="utf-8")

    # 8. .gitignore for src-tauri
    (tauri_dir / ".gitignore").write_text("target/\ngen/\n", encoding="utf-8")

    return str(tauri_dir)


def wait_for_server(url: str, timeout: float = 15.0) -> bool:
    """Poll URL until server is responsive or timeout expires."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            req = Request(url, headers={"User-Agent": "PyDataUI-Shell"})
            with urlopen(req, timeout=1.0) as resp:
                if resp.status in (200, 301, 302):
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def run_tauri_dev(
    project_dir: str = ".",
    app_file: str = "app.py",
    host: str = "127.0.0.1",
    port: int = 8000,
    target: Optional[str] = None,
) -> int:
    """
    Launch PyDataUI server and open the native Tauri desktop/mobile development window.
    """
    root = Path(project_dir).resolve()
    init_tauri(str(root), port=port)

    # 1. Start Python server
    print(f"\n🚀 [Desktop/Mobile] Starting PyDataUI backend on http://{host}:{port}...")
    server_env = dict(os.environ, PYDATAUI_HOST=host, PYDATAUI_PORT=str(port))
    cmd = [sys.executable, str(root / app_file)]
    server_proc = subprocess.Popen(cmd, cwd=str(root), env=server_env)

    try:
        # Wait for server health endpoint
        health_url = f"http://{host}:{port}/_pdu/health"
        print(f"⏳ Waiting for PyDataUI core backend to become ready...")
        if not wait_for_server(health_url, timeout=20.0):
            print(f"⚠️ Server took longer than expected; proceeding to open window...")

        # 2. Run Tauri CLI
        tauri_cmd = get_tauri_cli_cmd()
        if target in ("android", "ios"):
            tauri_args = tauri_cmd + [target, "dev"]
            print(f"📱 Launching Tauri 2.0 Mobile Simulator ({target})...")
        else:
            tauri_args = tauri_cmd + ["dev"]
            print(f"🖥️  Launching Tauri 2.0 Native Desktop Window...")

        ret = subprocess.call(tauri_args, cwd=str(root))
        return ret
    finally:
        print("\n🛑 Shutting down PyDataUI backend server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_proc.kill()


def build_tauri(
    project_dir: str = ".",
    target: Optional[str] = None,
) -> int:
    """
    Compile and bundle the native installer or APK/IPA for production.
    """
    root = Path(project_dir).resolve()
    init_tauri(str(root))

    tauri_cmd = get_tauri_cli_cmd()
    if target in ("android", "ios"):
        build_args = tauri_cmd + [target, "build"]
        print(f"📦 Compiling and bundling Tauri 2.0 Mobile ({target})...")
    else:
        build_args = tauri_cmd + ["build"]
        print(f"📦 Compiling and bundling Tauri 2.0 Desktop app...")

    return subprocess.call(build_args, cwd=str(root))
