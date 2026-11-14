"""actions.py - Business Logic & State Mutations

All user actions, calculations, external API calls, and reactive state updates
live in this file. Pages and components simply import and attach these functions
to `on_click`, `on_submit`, or `on_change` triggers.
"""

try:
    from .state import dashboard_state, data_hub_state, copilot_state, settings_state, INITIAL_RECORDS
except ImportError:
    from state import dashboard_state, data_hub_state, copilot_state, settings_state, INITIAL_RECORDS


# ==============================================================================
# 1. Dashboard Actions
# ==============================================================================

@dashboard_state.action
def scale_up_workers():
    dashboard_state.active_workers += 4
    dashboard_state.throughput_k = round(dashboard_state.throughput_k * 1.15, 1)


@dashboard_state.action
def scale_down_workers():
    if dashboard_state.active_workers > 4:
        dashboard_state.active_workers -= 4
        dashboard_state.throughput_k = round(max(20.0, dashboard_state.throughput_k * 0.88), 1)


@dashboard_state.action
def toggle_system_stress():
    if dashboard_state.system_status == "HEALTHY":
        dashboard_state.system_status = "STRESSED"
        dashboard_state.error_rate = 0.12
    else:
        dashboard_state.system_status = "HEALTHY"
        dashboard_state.error_rate = 0.04


# ==============================================================================
# 2. Data Hub Actions
# ==============================================================================

def _apply_data_filters():
    region = data_hub_state.selected_region
    query = data_hub_state.search_query.strip().lower()
    
    filtered = INITIAL_RECORDS
    if region != "ALL":
        filtered = [r for r in filtered if r["region"] == region]
    if query:
        filtered = [r for r in filtered if query in r["id"].lower() or query in r["status"].lower()]
        
    data_hub_state.records = filtered
    data_hub_state.total_nodes = len(filtered)


@data_hub_state.action
def filter_region(region: str = "ALL"):
    data_hub_state.selected_region = region
    _apply_data_filters()


@data_hub_state.action
def search_nodes(query: str = ""):
    data_hub_state.search_query = query
    _apply_data_filters()


@data_hub_state.action
def add_random_node():
    new_id = f"SRV-{len(INITIAL_RECORDS) + 1:02d}"
    new_record = {
        "id": new_id,
        "region": "US-East",
        "cpu_pct": 38.2,
        "mem_pct": 49.0,
        "status": "ONLINE"
    }
    INITIAL_RECORDS.append(new_record)
    _apply_data_filters()


# ==============================================================================
# 3. AI Copilot Actions
# ==============================================================================

@copilot_state.action
def handle_copilot_message(message: str = "", **kwargs):
    if not message.strip():
        return

    # 1. Immediately append user prompt
    copilot_state.messages.append({"role": "user", "content": message.strip()})
    copilot_state.is_loading = True

    # 2. Generate contextual response
    user_q = message.lower()
    if "node" in user_q or "cluster" in user_q:
        reply = f"Currently managing **{data_hub_state.total_nodes} nodes**. Active workers: `{dashboard_state.active_workers}`. Status: `{dashboard_state.system_status}`."
    elif "throughput" in user_q or "traffic" in user_q:
        reply = f"Current ingestion rate is `{dashboard_state.throughput_k}k events/sec` with error rate `{dashboard_state.error_rate * 100:.1f}%`."
    elif "sql" in user_q or "duckdb" in user_q:
        reply = "```sql\nSELECT region, AVG(cpu_pct) AS avg_cpu \nFROM cluster_telemetry \nGROUP BY region;\n```"
    else:
        reply = f"Telemetry verified for: '{message}'. All orchestrator pipelines are operating within SLAs."

    copilot_state.messages.append({"role": "assistant", "content": reply})
    copilot_state.total_tokens += len(message.split()) * 2 + 35
    copilot_state.is_loading = False


@copilot_state.action
def clear_copilot_chat():
    copilot_state.messages = [
        {"role": "assistant", "content": "Chat history cleared. What would you like to inspect next?"}
    ]


# ==============================================================================
# 4. Settings Actions
# ==============================================================================

@settings_state.action
def save_settings(alert_email: str = "", api_rate_limit: int = 2500, **kwargs):
    if alert_email:
        settings_state.alert_email = alert_email
    settings_state.api_rate_limit = int(api_rate_limit)
    settings_state.saved_feedback = "Settings saved successfully to persistence store!"
