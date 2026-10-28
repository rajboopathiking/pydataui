"""
PyDataUI Cross-Platform Desktop & Mobile Shell Integration.
Supports Tauri 2.0 (macOS, Windows, Linux, iOS, Android),
Capacitor (iOS, Android), and standalone desktop window mode.
"""
from .tauri import init_tauri, run_tauri_dev, build_tauri
from .capacitor import init_capacitor, run_capacitor_dev, build_mobile, install_mobile
from .window import open_desktop_window
from .preview import get_preview_html, get_local_ip
from .bridge import JNIBridge, dispatch_in_process

__all__ = [
    "init_tauri",
    "run_tauri_dev",
    "build_tauri",
    "init_capacitor",
    "run_capacitor_dev",
    "build_mobile",
    "install_mobile",
    "open_desktop_window",
    "get_preview_html",
    "get_local_ip",
    "JNIBridge",
    "dispatch_in_process",
]
