"""
Zero-dependency and Tauri-powered desktop window runner for PyDataUI.
Allows running PyDataUI apps in native OS desktop windows on macOS, Windows, and Linux.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
import webbrowser
from pathlib import Path
from typing import List, Optional


def find_desktop_browser() -> Optional[List[str]]:
    """
    Locate an installed browser capable of standalone app mode (--app=...).
    Prefers EgoLite, Chromium, Google Chrome, Microsoft Edge, or Brave.
    """
    candidates = [
        # macOS paths
        "/Applications/ego lite.app/Contents/MacOS/ego lite",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        # Common PATH binaries
        shutil.which("ego-browser"),
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        shutil.which("edge"),
        shutil.which("msedge"),
        shutil.which("brave-browser"),
    ]

    for c in candidates:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return [c]
    return None


def open_desktop_window(
    url: str,
    title: str = "PyDataUI Desktop",
    width: int = 1200,
    height: int = 800,
    project_dir: str = ".",
) -> Optional[subprocess.Popen]:
    """
    Open the application inside a native desktop window.
    - If Tauri (src-tauri) is present, launches Tauri.
    - Otherwise, launches standalone app-mode window using native browser engine.
    - Falls back to system default browser if no app-mode runner is found.
    """
    root = Path(project_dir).resolve()
    tauri_dir = root / "src-tauri"

    # 1. Tauri 2.0 native shell if initialized
    if tauri_dir.exists():
        from .tauri import get_tauri_cli_cmd
        cmd = get_tauri_cli_cmd() + ["dev"]
        print(f"🖥️  Opening Tauri 2.0 Native Desktop Window...")
        proc = subprocess.Popen(cmd, cwd=str(root))
        return proc

    # 2. Standalone Chromium / WebKit App Mode
    browser_bin = find_desktop_browser()
    if browser_bin:
        temp_profile = tempfile.mkdtemp(prefix="pydataui_desktop_")
        flags = [
            f"--app={url}",
            f"--user-data-dir={temp_profile}",
            f"--window-size={width},{height}",
            f"--app-id=pydataui-{title.lower().replace(' ', '-')}",
            "--no-first-run",
            "--no-default-browser-check",
        ]
        print(f"🖥️  Opening standalone desktop window using {os.path.basename(browser_bin[0])}...")
        proc = subprocess.Popen(browser_bin + flags)
        return proc

    # 3. Fallback to system browser
    print(f"🌐 Opening in default system browser: {url}")
    webbrowser.open(url)
    return None
