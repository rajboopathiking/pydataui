"""
Unit and Integration Test Suite for Streamlit-Grade Developer Experience (DX) in PyDataUI.
Verifies all high-level procedural abstractions, context managers, polymorphic write,
session state, charts, input widgets, and full SSR dispatch rendering.
"""
import pytest
import asyncio
import pydataui as pdu
from pydataui.dx import (
    title, header, subheader, caption, text, markdown, code, write,
    sidebar, columns, expander, tabs, container, metric, session_state,
    dataframe, table, json, line_chart, bar_chart, area_chart, scatter_chart,
    button, input, text_input, textarea, text_area, number_input, slider,
    selectbox, multiselect, checkbox, radio, switch, toggle, file_uploader,
    chat_message, chat_input, chat, card, row, column, divider, code_editor,
    success, info, warning, error, toast, spinner, progress,
    set_page_config, theme_toggle, get_app
)


@pytest.mark.anyio
async def test_streamlit_dx_complete_workflow():
    # 1. Page Configuration
    set_page_config(title="Test Executive Dashboard", layout="wide", theme="zinc", dark_mode=True)

    # 2. Sidebar with Controls
    with sidebar():
        title("System Configuration")
        model = selectbox("Select Model", ["Llama-3.3", "DeepSeek-R1", "GPT-4o"], index=1)
        temp = slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)
        theme_toggle()

    # 3. Main Header & Typography
    title("AI Operations Center")
    caption("Real-time GPU cluster telemetry and AI agent workflows.")
    
    # 4. Status Banners
    success("Cluster healthy. 8/8 H100 SXM5 nodes online.")
    info("Scheduled batch maintenance at 02:00 UTC.")
    warning("High memory pressure on Worker-04 (88% allocated).")
    error("Node 7 reported a transient PCIe bus error.")
    toast("Telemetry streams connected successfully.")

    # 5. Multi-Column KPIs
    col1, col2, col3 = columns([1, 1, 1])
    with col1:
        metric("Processed Inferences", "1.24M", delta="+14.2%")
    with col2:
        metric("Average Latency", "12.4ms", delta="-2.1ms")
    with col3:
        metric("Throughput", "3,400 req/s", delta="+8.5%")

    # 6. Polymorphic write() with various data types
    write("# Interactive Section")
    write("This is a simple body text rendered via polymorphic write.")
    write({"status": "active", "nodes": 8, "gpu_temp_avg": 42.5})
    write(["Worker-1", "Worker-2", "Worker-3"])

    # 7. Built-in Charts
    line_chart([45, 52, 58, 65, 72, 80], height="250px")
    bar_chart({"Series A": [10, 20, 30], "Series B": [15, 25, 35]}, height="250px")
    area_chart([100, 120, 140, 180, 210], height="250px")
    scatter_chart([1, 4, 9, 16, 25], height="250px")

    # 8. Interactive Tabs
    tab_data, tab_chat, tab_settings = tabs(["Data Explorer", "Agent Chat", "Configuration"])
    
    with tab_data:
        table([
            {"Node": "node-01", "IP": "10.0.0.1", "Status": "Online"},
            {"Node": "node-02", "IP": "10.0.0.2", "Status": "Online"},
        ])

    with tab_chat:
        with chat_message("user"):
            write("Summarize cluster utilization for today.")
        with chat_message("assistant"):
            write("GPU utilization averaged 82% over the last 24 hours.")
        chat_input("Ask a follow-up question...")

    with tab_settings:
        with expander("Advanced Hyperparameters", expanded=False):
            text_input("API Key", placeholder="sk-...", type="password")
            number_input("Top P", min_value=0.0, max_value=1.0, value=0.9, step=0.05)
            checkbox("Enable FP8 quantization", value=True)
            switch("Log full prompts to disk", value=False)
            file_uploader("Upload Fine-tuning Dataset", accept=[".jsonl", ".parquet"])

    # 9. Session State Access
    session_state.test_flag = "dx_verified"
    session_state["node_count"] = 8
    assert session_state.test_flag == "dx_verified"
    assert session_state["node_count"] == 8
    assert "node_count" in session_state
    assert session_state.get("non_existent", "fallback") == "fallback"

    # 10. Verify Full SSR Dispatch Rendering
    app = get_app()
    status, body, headers = await app._engine.dispatch_request('GET', '/', '', {}, '')
    
    assert status == 200
    assert "AI Operations Center" in body
    assert "System Configuration" in body
    assert "Cluster healthy" in body
    assert "1.24M" in body
    assert "12.4ms" in body
    assert "Data Explorer" in body
    assert "Agent Chat" in body
    assert "GPU utilization averaged" in body
    assert "Advanced Hyperparameters" in body
    assert "pdu-expander" in body
    assert "pdu-tab-btn" in body
    assert "pdu-toast" in body


def test_session_state_dict_and_attribute_operations():
    session_state.username = "alice"
    session_state["role"] = "admin"
    session_state.setdefault("counter", 100)
    session_state.setdefault("counter", 999)  # Should remain 100

    assert session_state.username == "alice"
    assert session_state["role"] == "admin"
    assert session_state.counter == 100
    assert "username" in session_state
    assert "role" in session_state
    assert session_state.get("role") == "admin"
    assert session_state.get("missing", 42) == 42


def test_polymorphic_write_dispatch():
    from pydataui.components.typography import Text
    # Direct component
    comp = Text("Custom component")
    write(comp)
    
    # Primitives
    write(12345)
    write(3.14159)
    write(True)
    write("Simple string")
    write("### Markdown heading\n- item 1\n- item 2")


def test_chart_data_normalization():
    from pydataui.dx import _normalize_chart_data
    
    # 1. List
    res_list = _normalize_chart_data([10, 20, 30], "line")
    assert len(res_list["labels"]) == 3
    assert res_list["datasets"][0]["data"] == [10, 20, 30]

    # 2. Dict
    res_dict = _normalize_chart_data({"Alpha": [1, 2], "Beta": [3, 4]}, "bar")
    assert len(res_dict["labels"]) == 2
    assert len(res_dict["datasets"]) == 2
    assert res_dict["datasets"][0]["label"] == "Alpha"
    assert res_dict["datasets"][1]["label"] == "Beta"


def test_theme_system_presets_and_custom_palettes():
    from pydataui.dx import _resolve_theme_css, THEME_PRESETS
    
    # 1. Check all 20 presets are registered
    expected_presets = [
        "zinc", "slate", "stone", "neutral", "gray", "emerald", "green", "teal",
        "cyan", "blue", "indigo", "violet", "purple", "fuchsia", "pink", "rose",
        "red", "orange", "amber", "yellow"
    ]
    for p in expected_presets:
        assert p in THEME_PRESETS
        css = _resolve_theme_css(p)
        assert "--primary:" in css
        assert THEME_PRESETS[p]["primary"] in css

    # 2. Custom Hex Theme
    hex_css = _resolve_theme_css("#4f46e5")
    assert "--primary: #4f46e5" in hex_css

    # 3. Custom Dictionary Palette
    custom_dict = {"primary": "#6366f1", "bg": "#0f172a", "accent": "#a855f7"}
    dict_css = _resolve_theme_css(custom_dict)
    assert "--primary: #6366f1" in dict_css
    assert "--bg: #0f172a" in dict_css
    assert "--accent: #a855f7" in dict_css

