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





