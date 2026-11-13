"""
Tests for PyDataUI v1.2.0 DX enhancements and TUI runner:
1. Zero-Class Procedural State Hook (state / reactive_state / @s.action)
2. Universal Tabular Data Sniffing (Pandas, Polars, DuckDB, Arrow, Pydantic, Dataclasses)
3. Pythonic Layout Shorthands (Row, Col, Grid, Spacer)
4. Pydantic Auto-Form Generator (ShadForm.from_pydantic)
5. Multi-Page Directory Auto-Discovery (pages/ auto-routing & Sidebar.from_app)
6. TUI Runner & Rich / ASCII Rendering
"""
import datetime
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Optional
import pytest
from pydantic import BaseModel, Field

import pydataui as ui
from pydataui import (
    App,
    state,
    reactive_state,
    ProceduralState,
    Row,
    Col,
    Grid,
    Spacer,
    DataTable,
    Table,
    sniff_tabular_data,
    ShadForm,
    Form,
    Button,
    Text,
    Heading,
    Card,
    Badge,
)
from pydataui.components.shadcn import DashboardLayout, Sidebar, NavGroup, NavItem
from pydataui.tui import render_to_rich, render_to_ascii, run_tui


# ---------------------------------------------------------------------------
# 1. Zero-Class Procedural State Hook
# ---------------------------------------------------------------------------

def test_procedural_state_initialization_and_refs():
    s = state(count=0, name="Alice", tags=["ml", "ai"])
    assert isinstance(s, ProceduralState)
    assert s.state_name.startswith("ProceduralState_")
    
    # State variable references
    count_ref = s.count
    assert hasattr(count_ref, "state_cls_name")
    assert count_ref.field_name == "count"
    assert count_ref._get_val() == 0

    name_ref = s.name
    assert hasattr(name_ref, "state_cls_name")
    assert name_ref.field_name == "name"
    assert name_ref._get_val() == "Alice"


    # Dictionary access
    assert s["count"]._get_val() == 0
    assert s.to_dict()["count"] == 0


def test_procedural_state_action_decorator_and_mutation():
    s = state(counter=10, status="idle")

    @s.action
    def increment():
        s.counter += 1

    @s.action
    def set_status(val: str):
        s.status = val

    # Verify action registered on dynamic class
    handler = s.increment
    assert hasattr(handler, "get_endpoint")
    assert handler.method_name == "increment"
    assert s._cls.__name__ in handler.get_endpoint()

    # Direct function invocation updates class store outside request session
    s.counter = 25
    assert s.counter._get_val() == 25
    s.set(counter=30, status="active")
    assert s.counter._get_val() == 30
    assert s.status._get_val() == "active"


def test_procedural_state_setter():
    s = state(threshold=0.5)
    setter_handler = s.setter("threshold", 0.95)
    assert hasattr(setter_handler, "get_endpoint")
    assert "set_threshold" in setter_handler.method_name


# ---------------------------------------------------------------------------
# 2. Universal Data Sniffing for DataTable & Table
# ---------------------------------------------------------------------------

class UserSchema(BaseModel):
    id: int
    username: str
    role: str = "analyst"


@dataclass
class ModelMetric:
    model_name: str
    f1_score: float
    latency_ms: int


def test_sniff_tabular_data_dict_list():
    raw = [
        {"model": "Llama-3", "params": "8B", "accuracy": 0.88},
        {"model": "Mistral", "params": "7B", "accuracy": 0.86},
    ]
    records, cols, headers = sniff_tabular_data(raw)
    assert len(records) == 2
    assert cols == ["model", "params", "accuracy"]
    assert headers == ["Model", "Params", "Accuracy"]


def test_sniff_tabular_data_columnar_dict():
    raw = {
        "epoch": [1, 2, 3],
        "train_loss": [0.45, 0.32, 0.21],
        "val_loss": [0.49, 0.35, 0.24],
    }
    records, cols, headers = sniff_tabular_data(raw)
    assert len(records) == 3
    assert cols == ["epoch", "train_loss", "val_loss"]
    assert records[0]["epoch"] == 1
    assert records[2]["val_loss"] == 0.24


def test_sniff_tabular_data_pydantic():
    users = [
        UserSchema(id=1, username="alex", role="admin"),
        UserSchema(id=2, username="sam", role="viewer"),
    ]
    records, cols, headers = sniff_tabular_data(users)
    assert len(records) == 2
    assert cols == ["id", "username", "role"]
    assert records[0]["username"] == "alex"
    assert headers == ["Id", "Username", "Role"]


def test_sniff_tabular_data_dataclass():
    metrics = [
        ModelMetric(model_name="ResNet50", f1_score=0.912, latency_ms=14),
        ModelMetric(model_name="ViT-Base", f1_score=0.935, latency_ms=28),
    ]
    records, cols, headers = sniff_tabular_data(metrics)
    assert len(records) == 2
    assert cols == ["model_name", "f1_score", "latency_ms"]
    assert records[1]["f1_score"] == 0.935


def test_sniff_tabular_data_pandas():
    try:
        import pandas as pd
    except ImportError:
        pytest.skip("Pandas not installed")
    df = pd.DataFrame({
        "city": ["San Francisco", "Tokyo", "London"],
        "population": [870000, 14000000, 9000000],
    })
    records, cols, headers = sniff_tabular_data(df)
    assert len(records) == 3
    assert cols == ["city", "population"]
    assert records[0]["city"] == "San Francisco"


def test_datatable_render():
    raw = [
        {"job_id": "job_01", "status": "COMPLETED", "gpu": "H100"},
        {"job_id": "job_02", "status": "RUNNING", "gpu": "A100"},
    ]
    table = DataTable(data=raw, sortable=True, searchable=True, paginated=True, page_size=5)
    html = table.render({})
    assert "pdu-datatable-wrapper" in html
    assert "data-sortable='true'" in html
    assert "Search records..." in html
    assert "job_01" in html
    assert "COMPLETED" in html
    assert "pdu-page-prev" in html


# ---------------------------------------------------------------------------
# 3. Pythonic Layout Shorthands (Row, Col, Grid, Spacer)
# ---------------------------------------------------------------------------

def test_row_col_grid_layout():
    r = Row(
        Col(Text("Left"), span=4),
        Col(Text("Middle"), width="1/2"),
        Col(Text("Right"), width="full"),
        gap="6",
        align="center"
    )
    html = r.render({})
    assert "pdu-row" in html
    assert "pdu-col" in html
    assert "pdu-col-span-4" in html
    assert "max-width: 33.3333%" in html  # span 4/12
    assert "max-width: 50.0%" in html      # 1/2
    assert "gap: 1.5rem" in html           # 6 * 0.25rem = 1.5rem


def test_spacer():
    s_flex = Spacer()
    html_flex = s_flex.render({})
    assert "flex: 1 1 auto" in html_flex

    s_fixed = Spacer(size=24)
    html_fixed = s_fixed.render({})
    assert "width: 24px" in html_fixed
    assert "height: 24px" in html_fixed


def test_grid():
    g = Grid(Text("Item 1"), Text("Item 2"), Text("Item 3"), columns=3, gap="4")
    html = g.render({})
    assert "pdu-grid" in html
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in html
    assert "gap: 1.0rem" in html


# ---------------------------------------------------------------------------
# 4. Pydantic Auto-Form Generator
# ---------------------------------------------------------------------------

class ModelTier(str, Enum):
    STANDARD = "standard"
    ENTERPRISE = "enterprise"


class AIJobConfig(BaseModel):
    experiment_name: str = Field(..., description="Unique experiment title")
    learning_rate: float = Field(0.001, description="Initial learning rate")
    batch_size: int = Field(32, description="Batch size for training")
    use_fp16: bool = Field(True, description="Enable mixed precision")
    tier: ModelTier = Field(ModelTier.STANDARD, description="Compute tier")
    sampling_strategy: Literal["greedy", "beam", "top_k"] = "beam"


def test_shadform_from_pydantic():
    s = state(job_submitted=False)

    @s.action
    def submit_job():
        s.job_submitted = True

    form_card = ShadForm.from_pydantic(
        AIJobConfig,
        on_submit=s.submit_job,
        submit_text="Deploy Experiment",
        field_configs={
            "learning_rate": {"component": "slider", "min": 0.0001, "max": 0.01, "step": 0.0001}
        }
    )
    html = form_card.render({})
    assert "AIJobConfig" in html or "Ai Job Config" in html
    assert "name=\"experiment_name\"" in html
    assert "name=\"learning_rate\"" in html
    assert "data-pdu-slider=\"true\"" in html or "type=\"range\"" in html or "slider" in html
    assert "name=\"use_fp16\"" in html
    assert "name=\"tier\"" in html
    assert "Deploy Experiment" in html
    assert "hx-post=\"" in html
    assert "submit_job" in html


def test_form_alias_from_pydantic():
    f = Form.from_pydantic(UserSchema, card_wrapper=False)
    html = f.render({})
    assert "name=\"username\"" in html
    assert "name=\"role\"" in html
    assert "<form" in html


# ---------------------------------------------------------------------------
# 5. Multi-Page Directory Auto-Discovery
# ---------------------------------------------------------------------------

def test_multi_page_discovery(tmp_path):
    pages_dir = tmp_path / "pages"
    pages_dir.mkdir()

    # Page 1: 01_dashboard.py
    p1 = pages_dir / "01_dashboard.py"
    p1.write_text("""
TITLE = "Executive Dashboard"
ICON = "layout-dashboard"

def page():
    from pydataui import Heading, Text
    return Heading("Executive Overview")
""")

    # Page 2: 02_model_registry.py
    p2 = pages_dir / "02_model_registry.py"
    p2.write_text("""
TITLE = "Model Registry"
ICON = "cpu"

def render():
    from pydataui import Text
    return Text("All registered models")
""")

    app = App(title="Test Discovery App", auto_discover=False)
    discovered = app.discover_pages(pages_dir=str(pages_dir))

    assert len(discovered) == 2
    assert discovered[0]["path"] == "/dashboard"
    assert discovered[0]["title"] == "Executive Dashboard"
    assert discovered[0]["icon"] == "layout-dashboard"
    assert discovered[1]["path"] == "/model-registry"
    assert discovered[1]["title"] == "Model Registry"

    # Verify routes registered on app
    assert "/dashboard" in app.routes
    assert "/model-registry" in app.routes

    # Verify auto-generated Sidebar from app
    sidebar = Sidebar.from_app(app, active_path="/dashboard")
    sb_html = sidebar.render({})
    assert "Executive Dashboard" in sb_html
    assert "Model Registry" in sb_html
    assert "href=\"/dashboard\"" in sb_html
    assert "href=\"/model-registry\"" in sb_html


# ---------------------------------------------------------------------------
# 6. Terminal User Interface (TUI) Rendering
# ---------------------------------------------------------------------------

def test_tui_render():
    app = App(title="TUI Test App", auto_discover=False)

    @app.page("/")
    def home():
        from pydataui.components.data_science import MetricCard
        return Card(
            Heading("System Metrics", level=2),
            Row(
                MetricCard("GPU Utilization", "94%", "+8%"),
                MetricCard("Memory Used", "68.4 GB", "-2.1 GB"),
            ),
            DataTable([
                {"node": "gpu-worker-01", "temp": "62C", "power": "340W"},
                {"node": "gpu-worker-02", "temp": "59C", "power": "315W"},
            ])
        )

    root = app.routes["/"]()

    # Test Rich render
    rich_view = render_to_rich(root)
    assert rich_view is not None

    # Test ASCII fallback render
    ascii_txt = render_to_ascii(root)
    assert "System Metrics" in ascii_txt
    assert "GPU Utilization: 94%" in ascii_txt
    assert "gpu-worker-01" in ascii_txt
    assert "gpu-worker-02" in ascii_txt

    # Test run_tui once=True (does not hang)
    run_tui(app, once=True)


def test_tui_chat_and_inputs_render():
    from pydataui.components.advanced import Chat
    from pydataui import Input, TextArea

    chat = Chat(
        messages=[
            {"role": "user", "content": "What is PyDataUI?"},
            {"role": "assistant", "content": "It is a full-stack Python framework."},
        ],
        title="Agent Bot",
    )
    rich_chat = render_to_rich(chat)
    assert rich_chat is not None
    ascii_chat = render_to_ascii(chat)
    assert "Agent Bot" in ascii_chat
    assert "What is PyDataUI?" in ascii_chat

    inp = Input(label="Search", value="polars", placeholder="Search records...")
    rich_inp = render_to_rich(inp)
    assert rich_inp is not None
    ascii_inp = render_to_ascii(inp)
    assert "polars" in ascii_inp


def test_tui_interactive_io_dispatch():
    import io
    import sys

    app = App(title="Interactive TUI App", auto_discover=False)
    s = state(count=5, response="")

    @s.action
    def submit_prompt(user_input: str = "", **kwargs):
        s.response = f"Echo: {user_input}"
        s.count += 1

    @app.page("/")
    def home():
        return Col(
            Heading("Interactive Dashboard", level=1),
            Text(s.response),
        )

    # Simulate keyboard inputs: 'input test message', then 'q' to exit
    old_stdin, old_stdout = sys.stdin, sys.stdout
    captured = io.StringIO()
    try:
        sys.stdin = io.StringIO("input test message\nq\n")
        sys.stdout = captured
        run_tui(app, interactive=True)
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout

    assert s.response == "Echo: test message"
    assert s.count == 6
    assert any(k in captured.getvalue() for k in ("Interactive TUI Command Dock", "Commands:"))


def test_chat_loading_indicator_and_htmx_attrs():
    """Verify that Chat component includes HTMX loading indicators, spinner, and disabled attributes."""
    from pydataui.components.advanced import Chat
    s = state(messages=[{"role": "assistant", "content": "Welcome!"}], is_waiting=False)

    @s.action
    def send_msg(message: str = ""):
        pass

    chat = Chat(messages=s.messages, on_send=send_msg, title="Support Bot", loading=s.is_waiting)
    html = chat.render()

    assert "Support Bot is thinking..." in html
    assert "htmx-indicator" in html
    assert "animate-spin" in html
    assert "hx-indicator" in html
    assert "hx-disabled-elt" in html


def test_tui_chat_mode_and_async_dispatch():
    """Verify that Chat components automatically trigger streamlined conversational TUI with async dispatch."""
    import io
    import sys
    from pydataui import Container
    from pydataui.components.advanced import Chat

    app = App(title="AI Chat App", auto_discover=False)
    chat_state = state(messages=[{"role": "assistant", "content": "Hello human!"}], session_id="test_sess")

    @chat_state.action
    async def handle_message(message: str = "", **kwargs):
        user_msg = message or kwargs.get("message", "").strip()
        chat_state.messages.append({"role": "user", "content": user_msg})
        chat_state.messages.append({"role": "assistant", "content": f"AI Reply: {user_msg}"})

    @app.page("/")
    def home():
        return Container(
            Chat(
                messages=chat_state.messages,
                title="Customer Support AI",
                on_send=handle_message,
            )
        )

    old_stdin, old_stdout = sys.stdin, sys.stdout
    captured = io.StringIO()
    try:
        # Simulate typing 'hello world', then 'q' to exit
        sys.stdin = io.StringIO("hello world\nq\n")
        sys.stdout = captured
        run_tui(app, interactive=True)
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout

    # Verify messages in state were updated by the async action
    assert len(chat_state.messages) == 3
    assert chat_state.messages[1] == {"role": "user", "content": "hello world"}
    assert chat_state.messages[2] == {"role": "assistant", "content": "AI Reply: hello world"}
    output = captured.getvalue()
    assert "Customer Support AI" in output
    assert "Exited PyDataUI chat session." in output


def test_chat_commercial_features():
    """Verify modern commercial features: suggestions chips, multiline IME-safe textarea, auto-scroll, and copy."""
    from pydataui.components.advanced import Chat
    s = state(messages=[{"role": "assistant", "content": "Welcome!", "timestamp": "12:00 PM"}])

    @s.action
    def send_msg(message: str = ""): pass

    @s.action
    def clear_chat(): pass

    chat = Chat(
        messages=s.messages,
        title="Copilot AI",
        subtitle="SLM 8B Model",
        suggestions=["Explain LoRA", "Cluster Health"],
        on_send=send_msg,
        on_clear=clear_chat,
        height="700px"
    )
    html = chat.render()

    assert "Copilot AI" in html
    assert "SLM 8B Model" in html
    assert "Explain LoRA" in html
    assert "Cluster Health" in html
    assert "textarea" in html
    assert "event.isComposing" in html
    assert "el.scrollTop = el.scrollHeight" in html
    assert "navigator.clipboard.writeText" in html
    assert "12:00 PM" in html
