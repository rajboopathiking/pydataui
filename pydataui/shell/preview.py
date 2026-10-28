"""
In-Browser Mobile Device Simulator & Previewer for PyDataUI.
Provides an interactive mobile device chassis (iPhone 15 Pro, Pixel 8, iPad Mini),
portrait/landscape rotation, live reload, and QR Code generation for real-device testing
without requiring Xcode or Android Studio.
"""
from __future__ import annotations

import socket
from typing import Optional


def get_local_ip() -> str:
    """Detect LAN IP address for QR code mobile testing over local WiFi."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def get_preview_html(
    target_url: str = "/",
    app_title: str = "PyDataUI Mobile App",
    port: int = 8000,
    public_url: Optional[str] = None
) -> str:
    """
    Generate the complete HTML shell for the in-browser mobile device previewer.
    """
    local_ip = get_local_ip()
    mobile_lan_url = public_url or f"http://{local_ip}:{port}/"
    
    html = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 Mobile Preview - {app_title}</title>
    <style>
        :root {{
            --bg-page: #09090b;
            --bg-card: #18181b;
            --border: #27272a;
            --text-main: #f4f4f5;
            --text-muted: #a1a1aa;
            --primary: #3b82f6;
            --primary-hover: #2563eb;
            --bezel: #121215;
            --bezel-border: #27272a;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }}
        body {{
            background-color: var(--bg-page);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }}
        /* Top Navigation Toolbar */
        .toolbar {{
            background-color: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 12px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 50;
        }}
        .toolbar-left, .toolbar-center, .toolbar-right {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brand {{
            font-weight: 700;
            font-size: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .brand span {{
            color: var(--primary);
        }}
        .select-input, .btn {{
            background: #27272a;
            color: var(--text-main);
            border: 1px solid #3f3f46;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .select-input:hover, .btn:hover {{
            background: #3f3f46;
        }}
        .btn-primary {{
            background: var(--primary);
            border-color: var(--primary);
            color: #ffffff;
            font-weight: 600;
        }}
        .btn-primary:hover {{
            background: var(--primary-hover);
        }}
        /* Main Preview Canvas */
        .canvas {{
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 30px;
            background: radial-gradient(circle at 50% 50%, #18181b 0%, #09090b 100%);
        }}
        /* Device Chassis */
        .device-wrapper {{
            position: relative;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.8), 0 0 0 12px var(--bezel), 0 0 0 13px var(--bezel-border);
            border-radius: 50px;
            background: #000;
            overflow: hidden;
        }}
        /* Dynamic Island / Camera Notch */
        .notch {{
            position: absolute;
            top: 12px;
            left: 50%;
            transform: translateX(-50%);
            width: 110px;
            height: 28px;
            background: #000;
            border-radius: 20px;
            z-index: 40;
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
            transition: all 0.2s ease;
        }}
        .notch-camera {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #111;
            margin-right: 8px;
            border: 1px solid #222;
        }}
        .notch-speaker {{
            width: 35px;
            height: 4px;
            border-radius: 2px;
            background: #1c1c1e;
        }}
        /* Home Indicator Bar */
        .home-indicator {{
            position: absolute;
            bottom: 8px;
            left: 50%;
            transform: translateX(-50%);
            width: 130px;
            height: 5px;
            background: rgba(255, 255, 255, 0.4);
            border-radius: 3px;
            z-index: 40;
            pointer-events: none;
        }}
        /* Iframe */
        iframe {{
            border: none;
            width: 100%;
            height: 100%;
            display: block;
            background: #09090b;
        }}
        /* QR Code Modal */
        .modal-overlay {{
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 100;
        }}
        .modal {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            max-width: 420px;
            width: 90%;
            text-align: center;
        }}
        .modal h3 {{
            margin-bottom: 8px;
        }}
        .modal p {{
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 20px;
        }}
        .qr-box {{
            background: #fff;
            padding: 16px;
            border-radius: 8px;
            display: inline-block;
            margin-bottom: 16px;
        }}
        .url-display {{
            background: #27272a;
            padding: 8px 12px;
            border-radius: 6px;
            font-family: monospace;
            font-size: 13px;
            color: #38bdf8;
            word-break: break-all;
            margin-bottom: 16px;
        }}
    </style>
</head>
<body>
    <!-- Top Toolbar -->
    <header class="toolbar">
        <div class="toolbar-left">
            <div class="brand">
                📱 PyDataUI <span>Mobile Preview</span>
            </div>
            <select id="device-select" class="select-input" onchange="changeDevice()">
                <option value="iphone15">iPhone 15 Pro (393 × 852)</option>
                <option value="pixel8">Google Pixel 8 (412 × 915)</option>
                <option value="iphonese">iPhone SE (375 × 667)</option>
                <option value="ipadmini">iPad Mini (768 × 1024)</option>
            </select>
        </div>

        <div class="toolbar-center">
            <button class="btn" onclick="toggleOrientation()" title="Rotate Device">
                🔄 Rotate
            </button>
            <button class="btn" onclick="reloadFrame()" title="Reload Mobile App">
                ⚡ Fast Reload
            </button>
            <select id="scale-select" class="select-input" onchange="changeScale()">
                <option value="1">100%</option>
                <option value="0.85" selected>85%</option>
                <option value="0.75">75%</option>
            </select>
        </div>

        <div class="toolbar-right">
            <button class="btn btn-primary" onclick="openQrModal()">
                📲 Test on Real Phone
            </button>
            <a href="{target_url}" target="_blank" class="btn" style="text-decoration: none;">
                ↗ Open Fullscreen
            </a>
        </div>
    </header>

    <!-- Canvas & Chassis -->
    <main class="canvas">
        <div id="device-wrapper" class="device-wrapper" style="width: 393px; height: 852px; transform: scale(0.85); transform-origin: center center;">
            <div id="notch" class="notch">
                <div class="notch-camera"></div>
                <div class="notch-speaker"></div>
            </div>
            <iframe id="mobile-frame" src="{target_url}" title="App Mobile Frame"></iframe>
            <div class="home-indicator"></div>
        </div>
    </main>

    <!-- QR Code Modal for Physical Phone Testing -->
    <div id="qr-modal" class="modal-overlay" onclick="closeQrModal(event)">
        <div class="modal" onclick="event.stopPropagation()">
            <h3>📱 Test on Physical Phone</h3>
            <p>Scan with your iPhone or Android camera to run directly on your phone over local Wi-Fi or tunnel with <strong>zero Xcode / Android Studio</strong>.</p>
            <div class="qr-box">
                <img id="qr-img" src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={mobile_lan_url}" width="200" height="200" alt="Mobile QR Code" />
            </div>
            <div class="url-display">{mobile_lan_url}</div>
            <button class="btn btn-primary" onclick="closeQrModal()" style="width: 100%;">Done</button>
        </div>
    </div>

    <script>
        const devices = {{
            iphone15: {{ width: 393, height: 852, radius: 50, notch: true }},
            pixel8: {{ width: 412, height: 915, radius: 46, notch: true }},
            iphonese: {{ width: 375, height: 667, radius: 36, notch: false }},
            ipadmini: {{ width: 768, height: 1024, radius: 32, notch: false }}
        }};

        let currentDevice = "iphone15";
        let isLandscape = false;
        let currentScale = 0.85;

        function updateDeviceDisplay() {{
            const wrapper = document.getElementById("device-wrapper");
            const notch = document.getElementById("notch");
            const d = devices[currentDevice];

            let w = isLandscape ? d.height : d.width;
            let h = isLandscape ? d.width : d.height;

            wrapper.style.width = w + "px";
            wrapper.style.height = h + "px";
            wrapper.style.borderRadius = d.radius + "px";
            wrapper.style.transform = `scale(${{currentScale}})`;

            if (notch) {{
                notch.style.display = (!isLandscape && d.notch) ? "flex" : "none";
            }}
        }}

        function changeDevice() {{
            currentDevice = document.getElementById("device-select").value;
            updateDeviceDisplay();
        }}

        function toggleOrientation() {{
            isLandscape = !isLandscape;
            updateDeviceDisplay();
        }}

        function changeScale() {{
            currentScale = parseFloat(document.getElementById("scale-select").value);
            updateDeviceDisplay();
        }}

        function reloadFrame() {{
            const frame = document.getElementById("mobile-frame");
            frame.src = frame.src;
        }}

        function openQrModal() {{
            document.getElementById("qr-modal").style.display = "flex";
        }}

        function closeQrModal(event) {{
            document.getElementById("qr-modal").style.display = "none";
        }}

        // Initialize view
        updateDeviceDisplay();
    </script>
</body>
</html>
"""
    return html
