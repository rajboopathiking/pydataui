"""state.py - Centralized State Management

All reactive state models and variables are defined here.
Keeping state decoupled from layout and business logic allows easy testing,
sharing across multiple pages, and clean React-like separation of concerns.
"""

import pydataui as pdu

# 1. Analytics & Telemetry State
dashboard_state = pdu.state(
    active_workers=24,
    throughput_k=148.5,
    error_rate=0.04,
    system_status="HEALTHY",
    chart_metric="Traffic"
)

# 2. Data Hub State (Tabular records & filtering)
INITIAL_RECORDS = [
    {"id": "SRV-01", "region": "US-East", "cpu_pct": 42.1, "mem_pct": 68.4, "status": "ONLINE"},
    {"id": "SRV-02", "region": "EU-Central", "cpu_pct": 78.9, "mem_pct": 84.1, "status": "WARNING"},
    {"id": "SRV-03", "region": "AP-South", "cpu_pct": 29.5, "mem_pct": 45.2, "status": "ONLINE"},
    {"id": "SRV-04", "region": "US-West", "cpu_pct": 91.2, "mem_pct": 94.0, "status": "CRITICAL"},
    {"id": "SRV-05", "region": "US-East", "cpu_pct": 34.8, "mem_pct": 52.0, "status": "ONLINE"},
    {"id": "SRV-06", "region": "EU-Central", "cpu_pct": 55.4, "mem_pct": 61.2, "status": "ONLINE"},
    {"id": "SRV-07", "region": "AP-South", "cpu_pct": 82.0, "mem_pct": 88.5, "status": "WARNING"},
]

data_hub_state = pdu.state(
    search_query="",
    selected_region="ALL",
    records=INITIAL_RECORDS,
    total_nodes=len(INITIAL_RECORDS)
)

# 3. AI Copilot State
copilot_state = pdu.state(
    messages=[
        {"role": "assistant", "content": "Hello! I am your PyDataUI Architecture Copilot. Ask me about cluster nodes, SQL queries, or scaling data pipelines."}
    ],
    is_loading=False,
    active_model="qwen2.5:7b-instruct",
    total_tokens=350
)

# 4. Settings & Configuration State
settings_state = pdu.state(
    app_theme="slate",
    enable_notifications=True,
    refresh_rate=5,
    api_rate_limit=2500,
    alert_email="ops-monitor@enterprise.internal",
    saved_feedback=""
)
