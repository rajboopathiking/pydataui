# PyDataUI Optional Extensions & Native Packaging

This folder contains examples for **optional deployment targets and extensions**. 

> **Important**: If you are building Web Applications, Data Science Dashboards, AI Agents, or Internal Tooling, **you do NOT need these extensions**. PyDataUI runs natively as a high-performance web application on standard browsers.

---

## 1. Native Desktop Packaging (Tauri / pywebview)
* File: `examples/desktop_app.py`
* Compiles your PyDataUI web application into a native desktop `.app` or `.exe` with zero changes to your Python code.
* Uses lightweight WebKit / Edge WebView2 instead of heavy Electron (~15 MB memory footprint vs 400 MB).

## 2. Native Mobile & PWA Packaging (Capacitor / Android / iOS)
* File: `examples/mobile_pwa_app.py`
* Packages your PyDataUI application for iOS and Android app stores using Capacitor.
* Supports offline caching, camera/GPS bridge, and haptic feedback.

## 3. Headless Terminal UI (TUI) & Cluster Telemetry
* Run with: `pdu dev --tui` or `pydataui.tui`
* Useful for SSH sessions and remote GPU clusters where no browser window is available.
