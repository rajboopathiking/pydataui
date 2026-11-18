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
    assert "<aside" in body
    assert "<main" in body
    assert "pdu-dx-shell" in body
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
    assert "--primary:" in hex_css
    assert "--pdu-color-primary: #4f46e5" in hex_css

    # 3. Custom Dictionary Palette
    custom_dict = {"primary": "#6366f1", "bg": "#0f172a", "accent": "#a855f7"}
    dict_css = _resolve_theme_css(custom_dict)
    assert "--primary: #6366f1" in dict_css
    assert "--bg: #0f172a" in dict_css
    assert "--accent: #a855f7" in dict_css

    # 4. Custom Dictionary Palette with light background
    light_dict = {"primary": "#6366f1", "primary_hover": "#4f46e5", "bg": "#eceef3", "accent": "#eceef3"}
    light_css = _resolve_theme_css(light_dict)
    assert "--primary:" in light_css
    assert "--background:" in light_css
    assert "--card: 0 0% 100%" in light_css
    assert "--foreground: 222.2 47.4% 11.2%" in light_css
    assert "background-color: #eceef3 !important" in light_css


@pytest.mark.anyio
async def test_chartjs_inclusion_and_custom_theme_render():
    pdu.reset()
    pdu.set_page_config(title="FinTech Test", theme={"primary": "#6366f1", "bg": "#eceef3"}, layout="wide")
    pdu.area_chart([10, 20, 30])
    app = pdu.get_app()
    status, body, headers = await app._engine.dispatch_request('GET', '/', '', {}, '')
    assert status == 200
    assert "chart.umd.min.js" in body
    assert "#6366f1" in body
    assert "#eceef3" in body


@pytest.mark.anyio
async def test_sidebar_and_fastapi_mount_workflow():
    pdu.reset()
    pdu.set_page_config(title="FastAPI Mounted AI App", layout="wide", theme="zinc", dark_mode=True)
    
    with pdu.sidebar():
        pdu.title("Controls")
        pdu.theme_toggle()
        pdu.selectbox("Select Model", ["Llama-3.3", "DeepSeek-R1", "GPT-4o"])
        pdu.slider("Temperature", 0.0, 1.0, 0.7)
        pdu.file_uploader("Upload Evaluation CSV", accept=[".csv"])
    
    pdu.title("GPU Cluster Telemetry & Agent Dispatch")
    pdu.success("All 16 H100 SXM5 nodes online.")
    
    # Verify app is ASGI-compliant and mountable
    app = pdu.get_app()
    assert hasattr(app._engine, "app")
    
    # Render page directly
    status, body, headers = await app._engine.dispatch_request('GET', '/', '', {}, '')
    assert status == 200
    assert "<aside" in body
    assert "Controls" in body
    assert "Select Model" in body
    assert "Temperature" in body
    assert 'accept=".csv"' in body
    assert "<main" in body
    assert "GPU Cluster Telemetry & Agent Dispatch" in body
    assert "All 16 H100 SXM5 nodes online" in body


def test_float_slider_and_auto_step_inference():
    pdu.reset()
    # 1. Float range [0.0, 1.0] with default step inference -> 0.01
    s_temp = pdu.slider("Temperature", 0.0, 1.0, 0.7)
    assert s_temp.min == 0.0
    assert s_temp.max == 1.0
    assert s_temp.value == 0.7
    assert s_temp.step == 0.01
    html = s_temp.render({})
    assert "step='0.01'" in html
    assert "value='0.7'" in html
    assert "data-pdu-slider='true'" in html
    assert "oninput=" in html

    # 2. Medium float range [0.0, 10.0] -> 0.1
    s_scale = pdu.slider("Scale", 0.0, 10.0, 5.5)
    assert s_scale.step == 0.1

    # 3. Standard Integer range -> 1
    s_int = pdu.slider("Count", 0, 100, 25)
    assert s_int.step == 1
    assert "step='1'" in s_int.render({})

    # 4. Explicit step is preserved
    s_exp = pdu.slider("Threshold", 0.0, 1.0, 0.5, step=0.05)
    assert s_exp.step == 0.05
    assert "step='0.05'" in s_exp.render({})


def test_uploaded_file_and_read_csv_pandas_integration():
    import pandas as pd
    from pydataui.request import UploadedFile

    csv_bytes = b"node,gpu_util,vram\nnode-01,88%,72 GB\nnode-02,92%,76 GB\nnode-03,78%,64 GB\n"
    uploaded = UploadedFile("telemetry.csv", csv_bytes, "text/csv")

    # 1. Direct pd.read_csv(uploaded) using file-like protocol
    df1 = pd.read_csv(uploaded)
    assert isinstance(df1, pd.DataFrame)
    assert len(df1) == 3
    assert list(df1.columns) == ["node", "gpu_util", "vram"]
    assert df1.iloc[0]["node"] == "node-01"

    # 2. pdu.read_csv(uploaded) convenience helper
    df2 = pdu.read_csv(uploaded)
    assert isinstance(df2, pd.DataFrame)
    assert len(df2) == 3

    # 3. uploaded.to_pandas() / to_dataframe() method
    df3 = uploaded.to_pandas()
    assert isinstance(df3, pd.DataFrame)
    assert len(df3) == 3
    assert uploaded.to_dataframe() is not None

    # 4. Stream inspection methods
    assert uploaded.tell() == len(csv_bytes)
    assert uploaded.seekable() is True
    assert uploaded.readable() is True
    assert uploaded.getvalue() == csv_bytes


def test_file_uploader_multipart_encoding():
    pdu.reset()
    uploader = pdu.file_uploader("Upload Evaluation CSV", accept=[".csv"])
    html = uploader.render({})
    assert 'type="file"' in html
    assert 'accept=".csv"' in html
    assert 'hx-encoding="multipart/form-data"' in html


def test_chat_input_form_and_session_state_integration():
    pdu.reset()
    received_message = None

    def my_agent_callback(query):
        nonlocal received_message
        received_message = query
        pdu.session_state["agent_reply"] = f"Processed: {query}"

    chat_box = pdu.chat_input("Ask a question...", key="user_prompt", on_submit=my_agent_callback)
    html = chat_box.render({})
    assert "<form" in html
    assert "type='submit'" in html or 'type="submit"' in html
    assert "hx-on::after-request=\"this.reset()\"" in html
    assert "name='user_prompt'" in html or 'name="user_prompt"' in html

    # Verify callback invocation via ActionState
    from pydataui.dx import ActionState
    # Find registered action
    for attr in dir(ActionState):
        if attr.startswith("act_"):
            getattr(ActionState, attr)(None, user_prompt="Explain RAG cluster")
            break

    assert received_message == "Explain RAG cluster"
    assert pdu.session_state["user_prompt"] == "Explain RAG cluster"
    assert pdu.session_state["agent_reply"] == "Processed: Explain RAG cluster"


def test_page_link_rendering():
    pdu.reset()
    link = pdu.page_link("/chat", label="Operations Copilot", icon="💬")
    html = link.render({})
    assert "href='/chat'" in html or 'href="/chat"' in html
    assert 'Operations Copilot' in html
    assert '💬' in html


def test_dynamic_table_rendering_callable_and_session_state():
    import pandas as pd
    pdu.reset()

    # 1. Test None state -> Empty placeholder
    df_comp = pdu.dataframe(lambda: pdu.session_state.get("dyn_df"))
    html_empty = df_comp.render({})
    assert "No data loaded yet" in html_empty

    # 2. Populate session_state -> Table renders dynamically
    test_df = pd.DataFrame({"Node": ["node-01", "node-02"], "Load": [75, 82]})
    pdu.session_state["dyn_df"] = test_df
    html_filled = df_comp.render({})
    assert "node-01" in html_filled
    assert "node-02" in html_filled
    assert "75" in html_filled
    assert "2 rows × 2 columns" in html_filled

    # 3. Test string key resolution
    df_key_comp = pdu.dataframe("dyn_df")
    html_key = df_key_comp.render({})
    assert "node-01" in html_key

    # 4. Test pdu.write with dynamic callable
    pdu.reset()
    pdu.session_state["telemetry"] = pd.DataFrame({"GPU": ["H100-0", "H100-1"]})
    pdu.write(lambda: pdu.session_state.get("telemetry"))
    app = pdu.get_app()
    from pydataui.dx import _default_page_components
    assert len(_default_page_components) > 0
    table_html = _default_page_components[0].render({})
    assert "H100-0" in table_html
    assert "H100-1" in table_html


def test_table_with_file_uploader_widget_binding():
    import pandas as pd
    from pydataui.request import UploadedFile
    pdu.reset()

    # Create uploader widget
    uploader = pdu.file_uploader("Upload CSV", key="user_csv")
    
    # Pass uploader widget directly to pdu.table
    tbl = pdu.table(uploader)
    
    # 1. Before upload: Empty
    html_before = tbl.render({})
    assert "No data" in html_before

    # 2. Simulate upload by placing UploadedFile into session_state[uploader.key]
    csv_payload = b"id,val\n1,100\n2,200\n"
    pdu.session_state["user_csv"] = UploadedFile("test.csv", csv_payload, "text/csv")

    # 3. After upload: Table automatically renders parsed CSV rows
    html_after = tbl.render({})
    assert "100" in html_after
    assert "200" in html_after


def test_bar_chart_categorical_dict_normalization():
    pdu.reset()
    pdu.set_page_config(title="Cluster Telemetry", theme="zinc", dark_mode=False)

    chart = pdu.bar_chart({"lat1": 140, "lat2": 110, "lat3": 125, "lat4": 75, "lat5": 60, "lat6": 45})
    html = chart.render({})

    assert "lat1" in html
    assert "lat2" in html
    assert "140" in html
    assert "beginAtZero" in html
    assert "type: 'bar'" in html


def test_chat_bottom_positioning_and_lambda_callbacks():
    pdu.reset()
    pdu.set_page_config(title="DeepAgent Copilot", theme="violet", dark_mode=True)

    # 1. Test docked bottom positioning (default)
    bottom_input = pdu.chat_input("Ask Copilot...", position="bottom")
    b_html = bottom_input.render({})
    assert "fixed bottom-0" in b_html
    assert "backdrop-blur" in b_html
    assert "hx-target=\"#pdu-root\"" in b_html
    assert "max-w-3xl" in b_html

    # 2. Test inline positioning
    inline_input = pdu.chat_input("Ask Copilot inline...", position="inline")
    i_html = inline_input.render({})
    assert "fixed bottom-0" not in i_html

    # 3. Test lambda callback in Button (verifies base.py fallback to ActionState)
    lambda_btn = pdu.button("Clear", on_click=lambda: pdu.session_state.clear())
    btn_html = lambda_btn.render({})
    assert "hx-post=\"/_pdu/event/ActionState/" in btn_html


@pytest.mark.anyio
async def test_procedural_multipage_and_switch_page():
    pdu.reset()

    # 1. Register procedural pages
    @pdu.page("/login", public=True)
    def login_page():
        pdu.title("Sign In to DeepAgent")
        pdu.text_input("Work Email", key="login_email")
        def do_login():
            pdu.session_state["authenticated"] = True
            pdu.switch_page("/dashboard")
        pdu.button("Sign In", on_click=do_login)

    @pdu.page("/signup", public=True)
    def signup_page():
        pdu.title("Create Enterprise Account")
        pdu.text_input("Full Name", key="signup_name")

    @pdu.page("/dashboard", public=True)
    def dashboard_page():
        pdu.title("Production Operations Dashboard")
        pdu.metric("Active Clusters", "16 / 16")

    app = pdu.get_app()

    # 2. Verify GET /login renders isolated procedural components
    s1, b1, h1 = await app._engine.dispatch_request('GET', '/login', '', {}, '')
    assert s1 == 200
    assert "Sign In to DeepAgent" in b1
    assert "Work Email" in b1

    # 3. Verify GET /signup renders signup components
    s_up, b_up, _ = await app._engine.dispatch_request('GET', '/signup', '', {}, '')
    assert s_up == 200
    assert "Create Enterprise Account" in b_up
    assert "Full Name" in b_up

    # 4. Verify switch_page redirect in event callback
    cookie = h1.get('set-cookie', '')
    import re
    csrf = re.search(r'name=\"csrf_token\" value=\"([^\"]+)\"', b1) or re.search(r'meta name=\"pdu-csrf-token\" content=\"([^\"]+)\"', b1)
    csrf_val = csrf.group(1) if csrf else ''

    from pydataui.dx import ActionState
    action_name = [a for a in dir(ActionState) if a.endswith('_do_login')][0]
    headers = {'cookie': cookie, 'x-csrf-token': csrf_val, 'hx-request': 'true'}
    s2, b2, h2 = await app._engine.dispatch_request('POST', f'/_pdu/event/ActionState/{action_name}', '', headers, '')
    assert s2 == 200
    assert h2.get('hx-redirect') == '/dashboard' or h2.get('HX-Redirect') == '/dashboard'

    # 5. Verify GET /dashboard renders dashboard with authenticated state
    s3, b3, _ = await app._engine.dispatch_request('GET', '/dashboard', '', {'cookie': cookie}, '')
    assert s3 == 200
    assert "Production Operations Dashboard" in b3
    assert "Active Clusters" in b3


@pytest.mark.anyio
async def test_form_batching_and_session_state_sync():
    pdu.reset()
    
    @pdu.page("/test_form", public=True)
    def form_page():
        pdu.title("Form Test")
        with pdu.form("user_form"):
            pdu.text_input("Username", key="form_user")
            pdu.text_input("Email", key="form_email")
            btn = pdu.form_submit_button("Submit")
            if btn:
                pdu.success(f"Saved: {pdu.session_state.get('form_user')}")

    app = pdu.get_app()
    s1, b1, h1 = await app._engine.dispatch_request('GET', '/test_form', '', {}, '')
    assert s1 == 200
    assert "form_user_form" in b1
    assert "form_user" in b1
    assert "form_email" in b1

    # Find the submit action
    import re
    action_match = re.search(r'hx-post=\"/_pdu/event/ActionState/([^\"]+)\"', b1)
    action_name = action_match.group(1) if action_match else ''
    cookie = h1.get('set-cookie', '')
    csrf = re.search(r'name=\"csrf_token\" value=\"([^\"]+)\"', b1) or re.search(r'meta name=\"pdu-csrf-token\" content=\"([^\"]+)\"', b1)
    csrf_val = csrf.group(1) if csrf else ''

    # Post form data
    body = "form_user=Alice&form_email=alice%40example.com"
    headers = {
        'cookie': cookie,
        'x-csrf-token': csrf_val,
        'hx-request': 'true',
        'content-type': 'application/x-www-form-urlencoded'
    }
    s2, b2, _ = await app._engine.dispatch_request('POST', f'/_pdu/event/ActionState/{action_name}', '', headers, body)
    assert s2 == 200
    assert "Saved: Alice" in b2
    assert 'value="Alice"' in b2
    assert 'value="alice@example.com"' in b2


@pytest.mark.anyio
async def test_production_auth_login_and_role_protection():
    pdu.reset()

    # 1. Create user with roles
    pdu.create_user("ops_admin", "SuperSecret123!", email="ops@example.com", roles=["admin"])

    @pdu.page("/login", public=True)
    def login_page():
        pdu.title("Sign In")
        with pdu.form("login_form"):
            pdu.text_input("Username", key="u_name")
            pdu.text_input("Password", type="password", key="p_word")
            def do_login():
                u = pdu.session_state.get("u_name")
                p = pdu.session_state.get("p_word")
                if pdu.login(u, p):
                    pdu.switch_page("/telemetry")
                else:
                    pdu.error("Invalid credentials")
            pdu.form_submit_button("Sign In", on_click=do_login)

    @pdu.page("/telemetry", roles=["admin"])
    def telemetry_page():
        pdu.title("Protected Telemetry Dashboard")
        pdu.metric("Health", "100%")

    app = pdu.get_app()

    # 2. Accessing /telemetry unauthenticated should be denied (401 or redirect)
    s_denied, _, _ = await app._engine.dispatch_request('GET', '/telemetry', '', {}, '')
    assert s_denied in (401, 303, 307)

    # 3. GET /login
    s_login, b_login, h_login = await app._engine.dispatch_request('GET', '/login', '', {}, '')
    assert s_login == 200
    cookie = h_login.get('set-cookie', '')
    import re
    csrf = re.search(r'name=\"csrf_token\" value=\"([^\"]+)\"', b_login) or re.search(r'meta name=\"pdu-csrf-token\" content=\"([^\"]+)\"', b_login)
    csrf_val = csrf.group(1) if csrf else ''

    # Find action directly from rendered button
    action_match = re.search(r'hx-post=\"/_pdu/event/ActionState/([^\"]+)\"', b_login)
    action_name = action_match.group(1) if action_match else ''

    # 4. Attempt login with bad password
    bad_body = "u_name=ops_admin&p_word=WrongPassword"
    headers = {
        'cookie': cookie,
        'x-csrf-token': csrf_val,
        'hx-request': 'true',
        'content-type': 'application/x-www-form-urlencoded'
    }
    s_bad, b_bad, _ = await app._engine.dispatch_request('POST', f'/_pdu/event/ActionState/{action_name}', '', headers, bad_body)
    assert s_bad == 200
    assert "Invalid credentials" in b_bad

    # 5. Login with correct credentials
    good_body = "u_name=ops_admin&p_word=SuperSecret123!"
    s_good, _, h_good = await app._engine.dispatch_request('POST', f'/_pdu/event/ActionState/{action_name}', '', headers, good_body)
    assert s_good == 200
    assert h_good.get('hx-redirect') == '/telemetry' or h_good.get('HX-Redirect') == '/telemetry'
    if h_good.get('set-cookie'):
        cookie = h_good.get('set-cookie')

    # 6. Access /telemetry with session cookie -> 200 Allowed!
    s_tel, b_tel, _ = await app._engine.dispatch_request('GET', '/telemetry', '', {'cookie': cookie}, '')
    assert s_tel == 200
    assert "Protected Telemetry Dashboard" in b_tel


def test_cache_data_and_cache_resource():
    pdu.reset()
    counter = 0

    @pdu.cache_data(ttl=60)
    def fetch_data(x: int):
        nonlocal counter
        counter += 1
        return {"result": x * 2, "counter": counter}

    # Call twice with same arg -> returns cached result, counter stays 1
    r1 = fetch_data(10)
    r2 = fetch_data(10)
    assert r1["counter"] == 1
    assert r2["counter"] == 1
    assert counter == 1

    # Call with different arg -> computes fresh
    r3 = fetch_data(20)
    assert r3["counter"] == 2
    assert counter == 2

    # Clear cache -> recomputes
    fetch_data.clear()
    r4 = fetch_data(10)
    assert r4["counter"] == 3
    assert counter == 3

    # Test cache_resource
    res_counter = 0

    @pdu.cache_resource
    def get_model():
        nonlocal res_counter
        res_counter += 1
        return f"ModelInstance_{res_counter}"

    m1 = get_model()
    m2 = get_model()
    assert m1 == "ModelInstance_1"
    assert m2 == "ModelInstance_1"
    assert res_counter == 1


def test_dialog_status_empty_navigation_rerun():
    pdu.reset()

    # 1. Dialog (both context manager and decorator)
    with pdu.dialog("User Delete Confirmation"):
        pdu.write("Are you sure you want to delete this?")
    
    @pdu.dialog("Edit Profile Dialog")
    def edit_dialog(name):
        pdu.write(f"Editing {name}")
    edit_dialog("Charlie")

    # 2. Status container
    with pdu.status("Loading cluster telemetry...", expanded=True) as s:
        pdu.write("Connecting to nodes...")
        s.update(label="Cluster ready", state="complete", expanded=False)

    # 3. Empty container
    ph = pdu.empty()
    ph.text("First text")
    ph.text("Replaced text")

    # 4. Navigation
    pdu.navigation({"Dashboards": ["/"], "Settings": ["/config"]})

    # 5. Rerun
    res = pdu.rerun(scope="app")
    assert res.headers.get("HX-Refresh") == "true"


def test_card_context_manager_and_direct_syntax():
    pdu.reset()

    # 1. Test `with pdu.card():` (fixes user reported error: 'Card' object does not support the context manager protocol)
    with pdu.card():
        pdu.title("User Profile")
        pdu.write("Card content inside context manager")

    # 2. Test `with pdu.card(title=..., subtitle=...):`
    with pdu.card(title="Security", subtitle="Two-factor authentication"):
        pdu.checkbox("Enable 2FA")

    # 3. Test direct arguments
    c_direct = pdu.card(pdu.text("Direct child"), title="Direct Card")

    # 4. Test method proxy on card component: `card.write(...)`
    c_direct.write("Appended via card method proxy")

    html = pdu.get_app()._page_router.get_page("/").handler().render({})
    assert "pdu-card" in html
    assert "User Profile" in html
    assert "Card content inside context manager" in html
    assert "Security" in html
    assert "Two-factor authentication" in html
    assert "Enable 2FA" in html
    assert "Direct Card" in html
    assert "Direct child" in html
    assert "Appended via card method proxy" in html


def test_row_column_box_container_context_managers():
    pdu.reset()

    # 1. Test with pdu.row()
    with pdu.row():
        pdu.button("Cancel")
        pdu.button("Confirm")

    # 2. Test with pdu.column() and with pdu.col()
    with pdu.column():
        pdu.write("Col 1")
    with pdu.col():
        pdu.write("Col 2")

    # 3. Test with pdu.box()
    with pdu.box(class_name="bg-muted p-4 rounded-xl"):
        pdu.write("Box Content")

    # 4. Test with pdu.container() and with pdu.container(border=True)
    with pdu.container():
        pdu.write("Regular Container")
    with pdu.container(border=True):
        pdu.write("Bordered Card Container")

    html = pdu.get_app()._page_router.get_page("/").handler().render({})
    assert "pdu-row" in html
    assert "Cancel" in html
    assert "Confirm" in html
    assert "Col 1" in html
    assert "Col 2" in html
    assert "Box Content" in html
    assert "Regular Container" in html
    assert "Bordered Card Container" in html
    assert "bg-muted p-4 rounded-xl" in html


def test_nested_context_managers_hierarchy():
    pdu.reset()

    with pdu.card(title="Outer Card"):
        with pdu.row():
            with pdu.column():
                pdu.write("Row 1 - Column 1")
            with pdu.column():
                pdu.write("Row 1 - Column 2")
        with pdu.box(class_name="nested-box"):
            pdu.write("Nested inside box")

    html = pdu.get_app()._page_router.get_page("/").handler().render({})
    assert "Outer Card" in html
    assert "Row 1 - Column 1" in html
    assert "Row 1 - Column 2" in html
    assert "Nested inside box" in html


def test_container_method_call_proxies():
    pdu.reset()

    col1, col2 = pdu.columns(2)
    # Test direct method proxy on ColumnContext without `with`
    col1.metric("Throughput", "14.2k t/s", delta="+18%")
    col2.metric("Latency", "12.8 ms", delta="-2.4ms")
    col1.write("Col1 notes")

    html = pdu.get_app()._page_router.get_page("/").handler().render({})
    assert "Throughput" in html
    assert "14.2k t/s" in html
    assert "Latency" in html
    assert "12.8 ms" in html
    assert "Col1 notes" in html


@pytest.mark.anyio
async def test_signup_screen_multipage_exact_user_scenario():
    """
    Verifies that the exact scenario reported by the user:
    File "cluster.py", line 68, in signup_screen
      with pdu.card():
    runs cleanly without TypeError: 'Card' object does not support the context manager protocol.
    """
    pdu.reset()

    @pdu.page("/signup", public=True)
    def signup_screen():
        with pdu.card():
            pdu.title("Create an Account")
            pdu.text_input("Username", key="su_user")
            pdu.text_input("Password", type="password", key="su_pass")
            pdu.button("Sign Up")

    app = pdu.get_app()
    status_code, body, _ = await app._engine.dispatch_request('GET', '/signup', '', {}, '')
    assert status_code == 200
    assert "Create an Account" in body
    assert "su_user" in body
    assert "su_pass" in body
    assert "Sign Up" in body
    assert "pdu-card" in body


def test_component_level_color_theming():
    pdu.reset()
    pdu.set_page_config(title="Cluster Telemetry", theme="zinc", dark_mode=False)

    # 1. Test metric with component-specific accent colors
    m1 = pdu.metric("P99 Latency", "12.8 ms", delta="-2.4ms", color="rose")
    m2 = pdu.metric("Active Pods", "32 / 32", delta="100% OK", color="emerald")
    m3 = pdu.metric("VRAM Allocated", "1,180 GB", delta="92.1%", color="#6366f1")

    h_m1 = m1.render({})
    h_m2 = m2.render({})
    h_m3 = m3.render({})

    assert "#e11d48" in h_m1  # Rose resolved preset hex
    assert "#059669" in h_m2 or "#10b981" in h_m2  # Emerald resolved hex
    assert "#6366f1" in h_m3  # Custom hex

    # 2. Test bar_chart with single color (e.g. `color="grey"`)
    b_grey = pdu.bar_chart({"lat1": 140, "lat2": 110, "lat3": 125}, color="grey")
    h_bgrey = b_grey.render({})
    assert "#71717a" in h_bgrey  # Grey resolved hex

    # 3. Test bar_chart with multiple-color palette list
    b_pal = pdu.bar_chart({"A": 10, "B": 20, "C": 30}, color=["#ef4444", "#10b981", "#3b82f6"])
    h_bpal = b_pal.render({})
    assert "#ef4444" in h_bpal
    assert "#10b981" in h_bpal
    assert "#3b82f6" in h_bpal

    # 4. Test line_chart and area_chart with custom color
    l_chart = pdu.line_chart([10, 20, 30], color="#8b5cf6")
    a_chart = pdu.area_chart([5, 15, 25], color="cyan")
    h_l = l_chart.render({})
    h_a = a_chart.render({})
    assert "#8b5cf6" in h_l
    assert "#0891b2" in h_a  # Cyan resolved preset hex


@pytest.mark.anyio
async def test_flex_layout_and_alignment():
    """Verify procedural Flexbox container with direction, align, justify, gap, and wrap."""
    pdu.reset()

    # 1. Direct invocation
    fl = pdu.flex(direction="row", align="center", justify="between", gap="4", wrap=True)
    h_fl = fl.render({})
    assert "display: flex" in h_fl
    assert "flex-direction: row" in h_fl
    assert "align-items: center" in h_fl
    assert "justify-content: space-between" in h_fl
    assert "gap: 1.0rem" in h_fl or "gap: var(--pdu-spacing-4" in h_fl
    assert "flex-wrap: wrap" in h_fl

    # 2. Context manager protocol
    with pdu.flex(direction="column", align="stretch", justify="start", gap="8"):
        pdu.write("Item 1")
        pdu.write("Item 2")

    # 3. Enhanced row and col shorthands
    rw = pdu.row(gap="2", align="center", justify="center")
    cl = pdu.column(gap="6", align="stretch")
    h_rw = rw.render({})
    h_cl = cl.render({})
    assert "display: flex" in h_rw
    assert "align-items: center" in h_rw
    assert "justify-content: center" in h_rw
    assert "display: flex" in h_cl
    assert "flex-direction: column" in h_cl


@pytest.mark.anyio
async def test_grid_layout_columns_and_autofit():
    """Verify procedural CSS Grid with fixed columns, auto-fit min-width, and ratios."""
    pdu.reset()

    # 1. Fixed integer columns
    g1 = pdu.grid(columns=3, gap="4")
    h_g1 = g1.render({})
    assert "display: grid" in h_g1
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in h_g1

    # 2. Responsive auto-fit grid
    g2 = pdu.grid(min_column_width="260px", gap="1.5rem")
    h_g2 = g2.render({})
    assert "grid-template-columns: repeat(auto-fit, minmax(260px, 1fr))" in h_g2
    assert "gap: 1.5rem" in h_g2

    # 3. Fractional column ratios
    g3 = pdu.grid(columns=[1, 2, 1], row_gap="2", column_gap="4")
    h_g3 = g3.render({})
    assert "grid-template-columns: 1fr 2fr 1fr" in h_g3
    assert "row-gap: 0.5rem" in h_g3 or "row-gap: var" in h_g3
    assert "column-gap: 1.0rem" in h_g3 or "column-gap: var" in h_g3

    # 4. Context manager usage
    with pdu.grid(columns=2):
        pdu.metric("Metric A", "100")
        pdu.metric("Metric B", "200")


@pytest.mark.anyio
async def test_coordinate_positioning_relative_and_absolute():
    """Verify absolute and relative positioning props, floating badges, pinned toolbars, and overlays."""
    pdu.reset()

    # 1. Component with relative position
    bx = pdu.box(position="relative")
    h_bx = bx.render({})
    assert "position: relative" in h_bx
    assert "pdu-relative" in h_bx

    # 2. Absolute positioned badge
    bg = pdu.badge("LIVE", color="emerald", position="absolute", top=10, right="15px", z_index=50)
    h_bg = bg.render({})
    assert "position: absolute" in h_bg
    assert "top: 10px" in h_bg
    assert "right: 15px" in h_bg
    assert "z-index: 50" in h_bg

    # 3. Card with nested absolute badge
    with pdu.card(position="relative") as c:
        pdu.badge("HOT", color="rose", position="absolute", top="12px", right="12px")
        pdu.header("Cluster GPU 01")
    h_c = c.render({})
    assert "position: relative" in h_c
    assert "position: absolute" in h_c
    assert "top: 12px" in h_c
    assert "right: 12px" in h_c

    # 4. Pinned container
    p_bot = pdu.pinned(position="bottom", z_index=40)
    h_p = p_bot.render({})
    assert "fixed bottom-0" in h_p
    assert "position: fixed" in h_p

    # 5. Overlay container
    ov = pdu.overlay(blur=True)
    h_ov = ov.render({})
    assert "position: absolute" in h_ov
    assert "inset: 0" in h_ov
    assert "backdrop-blur-sm" in h_ov


@pytest.mark.anyio
async def test_tabs_expand_and_headless_wizard():
    """Verify tabs with expand=True, hide_tab_buttons=True (headless wizards), and pill styling."""
    pdu.reset()

    # 1. Expand=True (equal width buttons spanning 100%)
    t_exp = pdu.tabs(["Tab 1", "Tab 2"], expand=True)
    with t_exp[0]:
        pdu.write("Content 1")
    with t_exp[1]:
        pdu.write("Content 2")

    # 2. Headless wizard (hide_tab_buttons=True)
    t_head = pdu.tabs(["Step 1", "Step 2", "Step 3"], hide_tab_buttons=True)
    with t_head[0]:
        pdu.write("Step 1 content")

    # 3. Pill variant
    t_pill = pdu.tabs(["Overview", "Billing"], variant="pill")

    app = pdu.get_app()
    status, body, headers = await app._engine.dispatch_request('GET', '/', '', {}, '')
    assert status == 200
    assert "pdu-tabs-expand" in body
    assert "pdu-tabs-headless" in body
    assert "style='display: none;'" in body
    assert "pdu-tabs-pill" in body


@pytest.mark.anyio
async def test_spacer_and_labeled_divider():
    """Verify fixed-height spacer, flexible push spacer, and labeled divider lines."""
    pdu.reset()

    # 1. Fixed height spacer
    sp_h = pdu.spacer(height=24)
    h_sph = sp_h.render({})
    assert "height: 24px" in h_sph

    # 2. Flexible expanding spacer
    sp_f = pdu.spacer(flex=1)
    h_spf = sp_f.render({})
    assert "flex: 1 1 auto" in h_spf

    # 3. Standard divider vs labeled divider
    d_plain = pdu.divider()
    d_label = pdu.divider(label="OR")
    h_dp = d_plain.render({})
    h_dl = d_label.render({})
    assert "<hr" in h_dp
    assert "pdu-divider-with-label" in h_dl
    assert "pdu-divider-text" in h_dl
    assert "OR" in h_dl


@pytest.mark.anyio
async def test_commercial_dashboard_components():
    """Verify badge variants, SVG sparklines, stat_card, date/time inputs, search, and pricing_card."""
    pdu.reset()

    # 1. Badge variants (subtle, solid, outline)
    b_sub = pdu.badge("Operational", color="emerald", variant="subtle")
    b_sol = pdu.badge("Critical", color="rose", variant="solid")
    b_out = pdu.badge("Draft", color="zinc", variant="outline")
    h_sub = b_sub.render({})
    h_sol = b_sol.render({})
    h_out = b_out.render({})
    assert "Operational" in h_sub
    assert "Critical" in h_sol
    assert "#ffffff" in h_sol
    assert "Draft" in h_out
    assert "border: 1px solid" in h_out

    # 2. Pure SVG inline sparkline
    spk = pdu.sparkline([10, 25, 18, 32, 28, 45], color="indigo", height=32, fill=True)
    h_spk = spk.render({})
    assert "<svg" in h_spk
    assert "<polyline points=" in h_spk
    assert "<polygon points=" in h_spk
    assert "linearGradient" in h_spk

    # 3. Executive StatCard
    sc = pdu.stat_card(
        title="Token Throughput",
        value="18.4k t/s",
        change="+24.8%",
        sparkline=[12, 14, 15, 17, 18],
        icon="⚡",
        color="amber"
    )
    h_sc = sc.render({})
    assert "Token Throughput" in h_sc
    assert "18.4k t/s" in h_sc
    assert "+24.8%" in h_sc
    assert "⚡" in h_sc

    # 4. Date & Time inputs
    d_in = pdu.date_input("Start Date", value="2026-11-18", key="start_date")
    t_in = pdu.time_input("Execution Time", value="14:30", key="exec_time")
    h_din = d_in.render({})
    h_tin = t_in.render({})
    assert 'type="date"' in h_din
    assert 'value="2026-11-18"' in h_din
    assert 'type="time"' in h_tin
    assert 'value="14:30"' in h_tin

    # 5. Search input
    s_in = pdu.search_input("Search telemetry logs...", value="error")
    h_sin = s_in.render({})
    assert "type='search'" in h_sin or 'type="search"' in h_sin
    assert 'Search telemetry logs...' in h_sin
    assert 'value="error"' in h_sin or "value='error'" in h_sin

    # 6. Commercial SaaS Pricing Card
    pc = pdu.pricing_card(
        title="Pro Tier",
        price="$149",
        period="/ month",
        description="For high-growth engineering teams",
        features=["Up to 50 GPU clusters", "90-day telemetry retention", "24/7 SLA Guarantee"],
        highlighted=True,
        badge_label="BEST VALUE"
    )
    h_pc = pc.render({})
    assert "Pro Tier" in h_pc
    assert "$149" in h_pc
    assert "BEST VALUE" in h_pc
    assert "90-day telemetry retention" in h_pc


@pytest.mark.anyio
async def test_full_commercial_saas_screen_ssr():
    """Verify an entire commercial SaaS multi-panel application renders cleanly via SSR."""
    pdu.reset()
    pdu.set_page_config(title="DataScale AI", theme="indigo", dark_mode=True)

    with pdu.flex(justify="between", align="center", class_name="py-4 border-b border-border"):
        pdu.header("DataScale AI Console")
        with pdu.row(gap="2", align="center"):
            pdu.badge("Online", color="emerald")
            pdu.badge("v1.4.4", color="indigo")

    with pdu.grid(min_column_width="240px", gap="4"):
        pdu.stat_card("Active Nodes", "64 / 64", change="100% OK", sparkline=[10, 10, 10], color="emerald")
        pdu.stat_card("P99 Latency", "8.2 ms", change="-2.1ms", sparkline=[14, 12, 10, 8], color="indigo")
        pdu.stat_card("VRAM Pool", "2,480 GB", change="+12%", sparkline=[60, 70, 85, 92], color="amber")

    with pdu.card(position="relative"):
        pdu.badge("HOTSPOT", color="rose", position="absolute", top="12px", right="12px")
        pdu.title("Cluster Temperature Heatmap")
        pdu.line_chart([45, 52, 60, 68, 72, 85], color="rose")

    tab1, tab2 = pdu.tabs(["Filters & Controls", "Pricing Tiers"], expand=True)
    with tab1:
        pdu.search_input("Search nodes by IP or region...")
        pdu.date_input("Audit Window", value="2026-11-18")
    with tab2:
        with pdu.grid(columns=2, gap="4"):
            pdu.pricing_card("Starter", "$29", features=["5 nodes", "Community Slack"])
            pdu.pricing_card("Enterprise", "$299", features=["Unlimited nodes", "Dedicated Support"], highlighted=True)

    app = pdu.get_app()
    status, body, headers = await app._engine.dispatch_request('GET', '/', '', {}, '')
    assert status == 200
    assert "DataScale AI Console" in body
    assert "Token Throughput" not in body or "Active Nodes" in body
    assert "VRAM Pool" in body
    assert "HOTSPOT" in body
    assert "Pricing Tiers" in body
    assert "Starter" in body
    assert "Enterprise" in body








