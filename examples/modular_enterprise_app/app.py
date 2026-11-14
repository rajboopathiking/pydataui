"""app.py - Main Entrypoint & Page Router

This is the central application file. It assembles the entire application:
- Initializes the PyDataUI application
- Registers multi-page routes
- Boots the server or runs in Terminal UI mode
"""

import sys
from pathlib import Path

# Ensure local package path is discoverable when running directly
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pydataui as pdu
try:
    from .pages import DashboardPage, DataHubPage, CopilotPage, SettingsPage
except ImportError:
    from pages import DashboardPage, DataHubPage, CopilotPage, SettingsPage

# 1. Initialize PyDataUI Application
app = pdu.App(
    title="Enterprise Operations Hub",
    theme="slate",
    debug=True
)

# 2. Register Multi-Page Routes
@app.page("/", title="Dashboard")
def route_dashboard():
    return DashboardPage()

@app.page("/data", title="Data Hub")
def route_data_hub():
    return DataHubPage()

@app.page("/copilot", title="AI Copilot")
def route_copilot():
    return CopilotPage()

@app.page("/settings", title="Settings")
def route_settings():
    return SettingsPage()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Enterprise Modular App")
    parser.add_argument("--tui", action="store_true", help="Run in Terminal UI mode instead of Web server")
    parser.add_argument("--port", type=int, default=8000, help="Web server port")
    args = parser.parse_args()

    if args.tui:
        print("Launching Terminal UI mode...")
        pdu.run_tui(app, interactive=True)
    else:
        print(f"Launching Web Server on http://127.0.0.1:{args.port}...")
        app.run(port=args.port, reload=True)
