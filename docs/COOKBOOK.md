# PyDataUI Developer Cookbook (v1.2.1)

> **Production Full-Stack Python Framework for Data & AI Applications**  
> Build reactive web apps and interactive terminal dashboards in pure Python without writing JavaScript or dealing with top-to-bottom script reruns.

---

## Table of Contents
1. [The PyDataUI Mental Model](#1-the-pydataui-mental-model)
2. [Recipe 1: Zero-Class Procedural State](#recipe-1-zero-class-procedural-state)
3. [Recipe 2: Production AI Chatbot with Loading Indicators & Modern UI/UX](#recipe-2-production-ai-chatbot-with-loading-indicators-modern-uiux)
4. [Recipe 3: Universal Tabular Data Sniffing (DuckDB, Polars, Pandas)](#recipe-3-universal-tabular-data-sniffing)
5. [Recipe 4: Pythonic Spatial Layouts (Row, Col, Grid, Spacer)](#recipe-4-pythonic-spatial-layouts)
6. [Recipe 5: Dynamic Forms from Pydantic Models](#recipe-5-dynamic-forms-from-pydantic-models)
7. [Recipe 6: Multi-Page Directory Routing (`pages/`)](#recipe-6-multi-page-directory-routing)
8. [Recipe 7: Dual-Surface Terminal UI (TUI) Mode](#recipe-7-dual-surface-terminal-ui-tui-mode)
9. [Recipe 8: FastAPI Native Mounting & Microservices](#recipe-8-fastapi-native-mounting)
10. [Recipe 9: Production Deployment & Dockerization](#recipe-9-production-deployment-dockerization)
11. [Recipe 10: Advanced Flexbox & Responsive CSS Grid Layouts](#recipe-10-advanced-flexbox-responsive-css-grid-layouts)
12. [Recipe 11: Absolute Floating Badges & Sticky Action Bars](#recipe-11-absolute-floating-badges-sticky-action-bars)
13. [Recipe 12: Headless Multi-Step Interactive Wizard](#recipe-12-headless-multi-step-interactive-wizard)
14. [Recipe 13: Commercial FinTech Executive Dashboard](#recipe-13-commercial-fintech-executive-dashboard)
15. [Recipe 14: FastAPI Production Hardening & Swagger Filtering](#recipe-14-fastapi-production-hardening-swagger-filtering)

---

## 1. The PyDataUI Mental Model

### Why PyDataUI Over Streamlit?
Streamlit re-executes your entire `.py` script from line 1 on every single user click. This creates heavy caching workarounds (`@st.cache_data`) and consumes high RAM per session.

**PyDataUI operates on standard ASGI (Starlette / FastHTML / HTMX):**
1. **Event Delegation**: Clicking a button or sending a message sends a lightweight HTMX POST event (`/_pydataui/event`).
2. **Targeted Mutation**: Only the targeted `@s.action` runs.
3. **DOM Diff Swapping**: Only the affected component subtree is rendered and swapped into the DOM.
4. **Dual Surface**: The exact same code runs in a modern web browser and as an interactive Terminal UI (TUI).

```python
from pydataui import App, state, Button, Text, Row

app = App()
s = state(count=0)

@s.action
def increment():
    s.count += 1

@app.page("/")
def home():
    return Row(
        Button("-", on_click=lambda: s.set(count=s.count - 1)),
        Text(s.count),
        Button("+", on_click=increment)
    )

if __name__ == "__main__":
    app.run()
```

---

## Recipe 1: Zero-Class Procedural State

Eliminate verbose classes for rapid prototypes while retaining full reactivity.

```python
from pydataui import App, state, Input, Button, Text, Card, Col

app = App(title="Procedural State")

# 1. Initialize state with defaults
s = state(
    query="",
    results=[],
    status="Ready"
)

# 2. Define action handlers
@s.action
def search(query: str = ""):
    val = query or s.query
    s.query = val
    s.status = "Searching..."
    # Inside actions, attributes resolve as native Python types:
    s.results = [f"Result for: {val} #{i}" for i in range(1, 4)]
    s.status = f"Found {len(s.results)} items."

@app.page("/")
def home():
    return Col(
        Input(placeholder="Search docs...", on_change=search),
        Text(s.status),
        Card(
            title="Search Results",
            children=[Text(r) for r in s.results]
        )
    )
```

---

## Recipe 2: Production AI Chatbot with Loading Indicators & Modern UI/UX

Renders an interactive commercial-grade chat interface with:
- **IME-Safe Multiline Textarea**: Auto-expanding with `Shift+Enter` for new line and `Enter` to submit.
- **Built-in HTMX Indicators**: 3-dot pulsing typing bubble (`animate-bounce`), button spinner (`animate-spin`), and button/input double-submission locks (`hx-disabled-elt`).
- **Clickable Suggestion Chips**: Auto-fills and triggers quick starter prompts with one click.
- **Auto-Scroll to Bottom**: Smoothly keeps the newest messages in view on render and updates.
- **Markdown & Code Formatting**: Beautiful syntax and styling for assistant responses with copy-to-clipboard button.
- **Clear Chat Support**: Dedicated `on_clear` action handler and trash button in header.

```python
import httpx
from pydataui import App, state, Container
from pydataui.components import Chat

app = App(title="AI Agent Chat")

s = state(
    messages=[
        {"role": "assistant", "content": "Hello! I am your AI Assistant. Ask me anything or select a suggestion below.", "timestamp": "10:00 AM"}
    ],
    session_id="chat_session_01",
    loading=False
)

@s.action
async def handle_message(message: str = "", **kwargs):
    user_msg = message or kwargs.get("message", "").strip()
    if not user_msg:
        return

    # Immediately push user message into history
    s.messages.append({"role": "user", "content": user_msg})
    s.loading = True

    try:
        # Non-blocking async API call to your LLM or LangGraph agent
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                "http://127.0.0.1:8000/chat/invoke",
                json={"id": str(s.session_id), "message": user_msg}
            )
            resp.raise_for_status()
            reply = resp.json().get("response", "No response received.")
    except Exception as e:
        reply = f"Error: {e}"
    finally:
        s.loading = False

    s.messages.append({"role": "assistant", "content": reply})

@s.action
def clear_chat():
    s.messages = [
        {"role": "assistant", "content": "Chat history cleared. How can I assist you today?"}
    ]

@app.page("/")
def home():
    return Container(
        Chat(
            messages=s.messages,
            title="Customer Support AI",
            subtitle="SLM Agent • Model: Llama-3-8B • Context: 8k",
            placeholder="Type a message... (Shift+Enter for new line)",
            on_send=handle_message,
            on_clear=clear_chat,
            suggestions=[
                "How do I reset my password?",
                "What are your business hours?",
                "Show cluster compute telemetry"
            ],
            loading=s.loading,  # Triggers pulsing typing dots + button spinner
            height="650px",
            show_clear=True
        ),
        max_width="lg",
        padding="lg"
    )

if __name__ == "__main__":
    app.run(port=8000)
```

---

## Recipe 3: Universal Tabular Data Sniffing

Pass tabular data directly into `DataTable` without manual conversion.

```python
import polars as pl
import duckdb
import pandas as pd
from pydataui import App, DataTable, Card, Col, Heading

app = App(title="Data Sniffing")

# Polars
pl_df = pl.DataFrame({
    "model": ["Llama-3-8B", "Mistral-7B", "Phi-3-Mini"],
    "params_b": [8.03, 7.24, 3.82],
    "mmlu": [68.4, 62.7, 69.1]
})

# DuckDB Relation
duck_conn = duckdb.connect(":memory:")
duck_rel = duck_conn.sql("SELECT 'Worker-01' as node, 98.4 as load_pct UNION ALL SELECT 'Worker-02', 45.2")

# Pandas
pd_df = pd.DataFrame({
    "optimizer": ["AdamW", "Lion", "Sophia"],
    "lr": [0.0001, 0.00005, 0.0002]
})

@app.page("/")
def home():
    return Col(
        Heading("Universal Data Display", level=1),
        Card("Polars DataFrame", [DataTable(pl_df)]),
        Card("DuckDB PyRelation", [DataTable(duck_rel)]),
        Card("Pandas DataFrame", [DataTable(pd_df)])
    )
```

---

## Recipe 4: Pythonic Spatial Layouts

Use declarative layout shorthands instead of raw Tailwind string hacking.

```python
from pydataui import App, Row, Col, Grid, Spacer, Card, MetricCard, Text, Button

app = App()

@app.page("/")
def home():
    return Col(
        # Top KPI Metrics Row
        Row(
            MetricCard("Active Workers", 16, delta="+4 scaled"),
            MetricCard("Throughput", "2,450 req/s", delta="+14.2%"),
            MetricCard("Error Rate", "0.002%", delta="-0.01%"),
            gap="4"
        ),
        Spacer(size=8),
        # 3-Column Responsive Grid
        Grid(
            Card("Node Alpha", [Text("Status: Healthy")]),
            Card("Node Beta", [Text("Status: Training")]),
            Card("Node Gamma", [Text("Status: Idle")]),
            columns=3,
            gap="6"
        )
    )
```

---

## Recipe 5: Dynamic Forms from Pydantic Models

Generate Shadcn-styled validated forms straight from Pydantic v2 classes.

```python
from enum import Enum
from pydantic import BaseModel, Field
from pydataui import App, state, ShadForm, Container

class ComputeTier(str, Enum):
    STANDARD = "standard"
    ENTERPRISE = "enterprise"

class TrainingJob(BaseModel):
    experiment_name: str = Field(..., description="Unique job title")
    epochs: int = Field(10, description="Training epochs")
    learning_rate: float = Field(0.001, description="Learning rate")
    tier: ComputeTier = Field(ComputeTier.STANDARD, description="Compute tier")

app = App()
s = state(job_submitted=None)

@s.action
def launch_job(**kwargs):
    s.job_submitted = kwargs

@app.page("/")
def home():
    return Container(
        ShadForm.from_pydantic(
            TrainingJob,
            title="Launch SLM Job",
            on_submit=launch_job
        )
    )
```

---

## Recipe 6: Multi-Page Directory Routing

Create a `pages/` directory next to your `app.py`. PyDataUI auto-discovers each page:

```text
my_app/
├── app.py
└── pages/
    ├── 01_dashboard.py
    ├── 02_analytics.py
    └── 03_settings.py
```

Inside `pages/01_dashboard.py`:
```python
from pydataui import Col, Heading, Text

TITLE = "Analytics Dashboard"
ICON = "chart-bar"
ORDER = 1
PUBLIC = True

def render():
    return Col(
        Heading("Analytics", level=1),
        Text("Real-time telemetry overview.")
    )
```

---

## Recipe 7: Dual-Surface Terminal UI (TUI) Mode

Run your app without a browser in remote SSH, tmux, or Kubernetes pods:

```bash
# Launch interactive terminal UI
pydataui run --tui app.py

# Or single-shot ASCII render for cron logs
pydataui tui --once app.py
```

- When `Chat` is present, launches conversational terminal chat:
  - `You > hello`
  - `Customer Support AI is thinking...`
  - `Customer Support AI: Hello! How can I assist you?`
  - Single keypress `q` or `quit` exits immediately.

---

## Recipe 8: FastAPI Native Mounting

Mount PyDataUI directly into existing FastAPI backends:

```python
from fastapi import FastAPI
from pydataui import App, Container, Text, mount

api = FastAPI(title="Backend Microservice")
dashboard = App(title="Admin Panel")

@dashboard.page("/")
def admin_home():
    return Container(Text("Welcome to the Admin Panel"))

# API Route
@api.get("/api/v1/health")
def health():
    return {"status": "ok"}

# Mount PyDataUI at /dashboard
mount(api, dashboard, path="/dashboard")

# Run: uvicorn server:api --port 8000
```

---

## Recipe 9: Production Deployment & Dockerization

### Production Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["pydataui", "run", "app.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Production Checklist
- [x] Configure reverse proxy (`nginx` or AWS ALB) to forward `X-Forwarded-For` and `X-Forwarded-Proto`.
- [x] Enable HTTPS for encrypted cookie transmission.
- [x] Run with multiple Uvicorn workers (`--workers 4`).
- [x] Pre-validate routes with `pydataui check app.py`.


---

## Recipe 10: Advanced Flexbox & Responsive CSS Grid Layouts

Build modern, auto-wrapping dashboard layouts without writing CSS media queries.

```python
import pydataui as pdu

pdu.set_page_config(title="Cluster Telemetry", layout="wide", theme="zinc", dark_mode=True)

# 1. Navigation Header with Flexbox distribution
with pdu.flex(direction="row", justify="between", align="center", gap=4):
    with pdu.row(align="center", gap=3):
        pdu.subheader("Production Cluster Alpha")
        pdu.badge("US-EAST-1", color="zinc", variant="outline")
        pdu.badge("32/32 PODS HEALTHY", color="emerald", variant="subtle")
    
    with pdu.row(align="center", gap=2):
        pdu.button("Drain Nodes", type="destructive")
        pdu.button("+ Deploy Pod", type="primary")

pdu.spacer(height=16)

# 2. Responsive CSS Grid: Cards automatically wrap when screen or card reaches 260px width!
with pdu.grid(min_column_width="260px", gap=4):
    pdu.stat_card("Active Pods", "32 / 32", change="100% OK", sparkline=[10, 10, 10, 10], color="emerald")
    pdu.stat_card("P99 Latency", "8.2 ms", change="-2.1ms", sparkline=[14, 12, 10, 8], color="indigo")
    pdu.stat_card("VRAM Allocated", "1,180 GB", change="+12%", sparkline=[60, 75, 85, 92], color="amber")
    pdu.stat_card("Token Throughput", "18.4k t/s", change="+24.8%", sparkline=[12, 15, 17, 18], color="rose")

if __name__ == "__main__":
    pdu.run(port=8000)
```

---

## Recipe 11: Absolute Floating Badges & Sticky Action Bars

Combine relative parent containers with absolute children and viewport-docked action bars.

```python
import pydataui as pdu

pdu.set_page_config(title="Incident Remediation", theme="slate")

# Relative Card with Absolute Floating Badge
with pdu.card(position="relative"):
    # Pinned to the top-right corner of this card
    pdu.badge("HOTSPOT DETECTED", color="rose", position="absolute", top="14px", right="14px")
    pdu.title("Worker Node 04")
    pdu.caption("High thermal signature detected during distributed LLM checkpointing.")
    pdu.line_chart([65, 72, 80, 85, 94, 98, 82], color="rose")

# Sticky Docked Viewport Action Bar (docked to bottom of browser window)
with pdu.pinned(position="bottom"):
    with pdu.flex(justify="between", align="center", class_name="max-w-4xl mx-auto py-2"):
        pdu.text("⚠️ 3 worker nodes require kernel updates before next training run.")
        with pdu.row(gap=2):
            pdu.button("Ignore for 24h", type="outline")
            pdu.button("Apply Batch Update", type="primary")

if __name__ == "__main__":
    pdu.run(port=8000)
```

---

## Recipe 12: Headless Multi-Step Interactive Wizard

Create checkout flows, multi-stage data pipelines, and AI interview wizards in 1 line by setting `hide_tab_buttons=True`:

```python
import pydataui as pdu

pdu.set_page_config(title="SaaS Onboarding Wizard", theme="violet")

# Initialize current step in session_state
if "step" not in pdu.session_state:
    pdu.session_state["step"] = 0

# Multi-Step Tabs with navigation buttons completely hidden
steps = pdu.tabs(["Account", "Organization", "Billing", "Finish"], hide_tab_buttons=True)

# Step 0: Account Details
with steps[0]:
    with pdu.card(title="Step 1: Account Information", subtitle="Create your admin login"):
        pdu.text_input("Full Name", key="wiz_name")
        pdu.text_input("Work Email", key="wiz_email")
        pdu.button("Next: Organization →", type="primary", on_click=lambda: pdu.session_state.update({"step": 1}))

# Step 1: Organization Details
with steps[1]:
    with pdu.card(title="Step 2: Organization Setup"):
        pdu.text_input("Company Name", key="wiz_company")
        pdu.selectbox("Team Size", ["1-10", "11-50", "51-200", "200+"])
        with pdu.row(justify="between"):
            pdu.button("← Back", on_click=lambda: pdu.session_state.update({"step": 0}))
            pdu.button("Next: Billing →", type="primary", on_click=lambda: pdu.session_state.update({"step": 2}))

# Step 2: Plan Selection
with steps[2]:
    with pdu.card(title="Step 3: Select Plan"):
        with pdu.grid(columns=2, gap=4):
            pdu.pricing_card("Pro", "$49", features=["Up to 10 nodes", "Shared cluster"])
            pdu.pricing_card("Enterprise", "$199", features=["Unlimited nodes", "Dedicated VPC"], highlighted=True)
        with pdu.row(justify="between"):
            pdu.button("← Back", on_click=lambda: pdu.session_state.update({"step": 1}))
            pdu.button("Complete Setup 🚀", type="primary", on_click=lambda: pdu.session_state.update({"step": 3}))

# Step 3: Success Screen
with steps[3]:
    pdu.success("🎉 Welcome aboard! Your cluster workspace is provisioned.")
    pdu.button("Launch Dashboard", type="primary", on_click=lambda: pdu.switch_page("/dashboard"))

if __name__ == "__main__":
    pdu.run(port=8000)
```

---

## Recipe 13: Commercial FinTech Executive Dashboard

Renders ARR/MRR velocity, customer cohorts, and pure inline SVG sparklines in ~0.001ms.

```python
import pydataui as pdu
import pandas as pd

pdu.set_page_config(title="ApexPay FinTech Analytics", layout="wide", theme="emerald")

pdu.title("ApexPay Revenue Operations & Cohorts")
pdu.success("Stripe Webhook Sync: Active • 99.99% Gateway Uptime")

# 1. Executive Stat Cards with inline Sparklines
with pdu.grid(columns=4, gap=4):
    pdu.stat_card("Annual Run Rate (ARR)", "$1,840,500", change="+24.8%", sparkline=[90, 110, 130, 145, 160, 184], icon="💳", color="emerald")
    pdu.stat_card("Monthly Recurring (MRR)", "$154,200", change="+18.2%", sparkline=[92, 104, 118, 132, 145, 154], icon="📈", color="emerald")
    pdu.stat_card("Active Accounts", "2,840", change="+142 mo", sparkline=[2200, 2400, 2600, 2840], icon="👥", color="indigo")
    pdu.stat_card("Net Retention Rate", "118.4%", change="TOP 5%", sparkline=[112, 114, 116, 118], icon="⚡", color="amber")

pdu.spacer(height=20)

# 2. Date Filtering & Revenue Cohorts Table
with pdu.flex(direction="row", justify="between", align="center"):
    pdu.subheader("Revenue Ingestion Ledger")
    with pdu.row(align="center", gap=2):
        pdu.date_input("Audit Window", value="2026-11-18", key="ledger_date")
        pdu.button("Export CSV", type="outline")

df = pd.DataFrame({
    "Transaction ID": [f"tx-894{i}" for i in range(1, 6)],
    "Customer": ["Acme Corp", "BioHealth AI", "FinFlow Inc", "DataMesh Labs", "ScaleOps"],
    "Tier": ["Enterprise", "Pro", "Pro", "Enterprise", "Pro"],
    "Amount": ["$12,400", "$4,900", "$4,900", "$15,200", "$4,900"],
    "Status": ["Settled", "Settled", "Settled", "Processing", "Settled"]
})
pdu.write(df)

if __name__ == "__main__":
    pdu.run(port=8000)
```

---

## Recipe 14: FastAPI Production Hardening & Swagger Filtering

Access the native FastAPI engine directly to integrate background tasks, add CORS middleware, and harden Swagger UI for production.

```python
import pydataui as pdu
from fastapi import APIRouter, BackgroundTasks
from starlette.middleware.cors import CORSMiddleware

# 1. Configure production Swagger UI security
pdu.set_page_config(
    title="Production Hardened App",
    # Enable search filtering in Swagger UI
    swagger_ui_parameters={"filter": True, "syntaxHighlight.theme": "monokai"},
    # Only allow users with the 'admin' role to view /docs
    docs_roles=["admin"]
)

# 2. Access the native FastAPI application
fastapi_app = pdu.get_fastapi()

# 3. Attach standard Starlette / FastAPI middlewares
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://mycompany.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)

# 4. Attach APIRouter with Starlette BackgroundTasks
router = APIRouter(prefix="/v1")

def audit_log_worker(event: str):
    print(f"[AUDIT WORKER] Logging event: {event}")

@router.post("/trigger-audit")
def trigger_audit(bg: BackgroundTasks):
    bg.add_task(audit_log_worker, "User initiated cluster security scan")
    return {"status": "enqueued", "queue": "background"}

fastapi_app.include_router(router)

# 5. Build procedural UI
pdu.title("Hardened Operations Center")
pdu.write("All requests secured with CORS and authenticated Swagger UI.")

if __name__ == "__main__":
    pdu.run(port=8000)
```
