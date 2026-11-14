"""test_modular_app.py - End-to-End Verification of Modular Enterprise App

Verifies:
1. GET / (Dashboard) returns 200 with AppShell, KPI cards, and controls
2. GET /data (Data Hub) returns 200 with DataTable and filters
3. GET /copilot (AI Copilot) returns 200 with Chat interface
4. GET /settings (Settings) returns 200 with Form
5. POST event triggering scale_up_workers mutates state
6. POST event submitting settings form with name="alert_email" updates state
"""

import sys
import re
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from starlette.testclient import TestClient
from examples.modular_enterprise_app.app import app
from examples.modular_enterprise_app.state import dashboard_state, settings_state


def run_tests():
    client = TestClient(app.asgi_app)

    print(">>> 1. Testing GET / (Dashboard)...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "Real-Time Analytics Dashboard" in res.text
    assert "Active Workers" in res.text
    assert "Ingestion Rate" in res.text
    print("✓ GET / (Dashboard) passed.")

    print(">>> 2. Testing GET /data (Data Hub)...")
    res = client.get("/data")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "Cluster Node Data Hub" in res.text
    assert "Active Node Inventory" in res.text
    assert "SRV-01" in res.text
    print("✓ GET /data (Data Hub) passed.")

    print(">>> 3. Testing GET /copilot (AI Copilot)...")
    res = client.get("/copilot")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "AI Architecture Copilot" in res.text
    assert "PyDataUI Copilot" in res.text
    print("✓ GET /copilot (AI Copilot) passed.")

    print(">>> 4. Testing GET /settings (Settings)...")
    res = client.get("/settings")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "System Preferences" in res.text
    assert 'name="alert_email"' in res.text
    assert 'name="api_rate_limit"' in res.text
    print("✓ GET /settings (Settings) passed.")

    print(">>> 5. Testing Interactive Event (Scale Up Workers)...")
    # Fetch initial page to capture CSRF token
    page_res = client.get("/")
    match = re.search(r'<meta name="pdu-csrf-token" content="([^"]+)"', page_res.text)
    assert match, "CSRF token meta tag not found"
    csrf_token = match.group(1)

    headers = {
        "X-CSRF-Token": csrf_token,
        "HX-Request": "true"
    }

    initial_workers = int(dashboard_state.active_workers)
    expected_workers = initial_workers + 4
    post_res = client.post(
        f"/_pdu/event/{dashboard_state._name}/scale_up_workers",
        headers=headers
    )
    assert post_res.status_code == 200, f"Event post failed: {post_res.status_code}"
    # Assert that the updated worker count is reflected in the server's re-rendered HTMX response
    assert str(expected_workers) in post_res.text, f"Expected {expected_workers} in response HTML"
    print(f"✓ State mutated and re-rendered: active_workers {initial_workers} -> {expected_workers}")

    print(">>> 6. Testing Form Submission (Save Settings with explicit field names)...")
    settings_page_res = client.get("/settings")
    match = re.search(r'<meta name="pdu-csrf-token" content="([^"]+)"', settings_page_res.text)
    csrf_token = match.group(1)
    headers["X-CSRF-Token"] = csrf_token

    post_res = client.post(
        f"/_pdu/event/{settings_state._name}/save_settings",
        data={"alert_email": "ops-lead@enterprise.org", "api_rate_limit": "5000"},
        headers=headers
    )
    assert post_res.status_code == 200, f"Form post failed: {post_res.status_code}"
    assert "ops-lead@enterprise.org" in post_res.text, "Submitted email not found in re-rendered HTML"
    assert "Settings saved successfully" in post_res.text, "Saved feedback banner not found in response"
    print("✓ Form state updated and re-rendered: alert_email='ops-lead@enterprise.org' & saved feedback banner visible")

    print("\n🎉 ALL MODULAR ENTERPRISE APP INTEGRATION TESTS PASSED!")


if __name__ == "__main__":
    run_tests()
