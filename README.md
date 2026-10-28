# ⚡ PyDataUI

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Backend](https://img.shields.io/badge/backend-FastAPI%20(Default)%20%7C%20PyRustAPI%20(Optional)-emerald.svg)
![UI Engine](https://img.shields.io/badge/styling-Tailwind%20CSS%20%2B%20shadcn%2Fui-38bdf8.svg)
![Reactivity](https://img.shields.io/badge/reactivity-HTMX-3b82f6.svg)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-2ea44f.svg)](https://rajboopathiking.github.io/pydataui/)


**A Python-First Full-Stack Framework for Reactive Apps, APIs, and AI Workloads.**
*Data Engineers • Data Analysts • AI/ML Engineers • Python Developers*

Write pure Python → get reactive web applications, automatic REST APIs, native FastAPI mounting, and optional Rust performance.
**Zero JavaScript required.**

[🌐 Docs Website](https://rajboopathiking.github.io/pydataui/) • [Quick Start](#-quick-start) • [Streamlined DX](#-streamlined-developer-experience-streamlit-like) • [FastAPI Mounting](#-native-mounting-inside-fastapi) • [Components](#-components) • [Authentication](#-authentication--api-keys)

</div>

---

## 🎯 Modern Python-First Web Framework

Build dashboards, dataset explorers, AI agent interfaces, and microservice workflows using pure Python UI components and server-side logic.

**v0.3.0 Upgrade Guide:** see [the v0.3.0 Migration Guide](docs/MIGRATION_0_3_0.md) for FastAPI default backend, mounting inside FastAPI, and simplified DX.

**PyDataUI Core Advantages:**
- 🐍 **100% Python Code**: Build UI, reactive state, and server logic in clean, typed Python.
- 📱 **Cross-Platform Mobile & Desktop**: Built-in Progressive Web App (PWA), Capacitor mobile shell (iOS/Android), and standalone desktop window (`--desktop` or Tauri 2.0).
- ⚡ **FastAPI Default Engine**: Native ASGI foundation running on standard FastAPI and Uvicorn.
- 🦀 **Optional PyRustAPI Support**: Plug in Rust-powered `pyrustapi` for high-throughput I/O.
- 🔌 **Native FastAPI Mounting**: Mount PyDataUI dashboards inside any existing FastAPI app via `mount(api, dashboard, path="/dashboard")`.
- 🪄 **Streamlit-Like Simplicity**: Create immediate UIs with `import pydataui as ui; ui.title(...); ui.run()`.
- 🎨 **Tailwind CSS + shadcn/ui**: Modern design system with dark mode and CSS variables.
- ⚡ **Reactive SSR via HTMX**: Server re-renders page fragments on state mutation without client-side JavaScript.
- 🤖 **AI & Agent Ready**: Built-in `Chat`, `Markdown`, and `CodeEditor` components compatible with LangGraph, UnifiedNexus, and LLMs.
- 🔒 **Auth & API Keys**: JWT authentication, RBAC, and `pdu_live_...` API keys for ETL automation.
- **Data Team Templates**: Ready-made analyst, data-quality, pipeline, and ML registry pages via `pydataui.templates`.
- 🌐 **One-Click Sharing (`share=True`)**: Create public internet tunnels instantly for demos.

---

## ⚡ Quick Start

### Installation

```bash
pip install pydataui
```

Optional dependencies for data science and port forwarding:
```bash
pip install "pydataui[all]"   # includes pandas, plotly, pyngrok, pyarrow
```

### 1. Minimal Reactive Counter (30 seconds)

```python
from pydataui import App, State
from pydataui.components import Container, Card, Flex, Button, Heading, Divider

class CounterState(State):
    count: int = 0
    def increment(self): self.count += 1
    def decrement(self): self.count -= 1
    def reset(self): self.count = 0

app = App(title="PyDataUI Counter")

@app.page("/")
def home():
    return Container(
        Card(
            title="Reactive Counter",
            children=[
                Flex(
                    Button("-", on_click=CounterState.decrement, variant="danger"),
                    Heading(CounterState.count, level=2),
                    Button("+", on_click=CounterState.increment, variant="success"),
                    align="center", justify="center", gap="lg",
                ),
                Divider(),
                Button("Reset", on_click=CounterState.reset, variant="outline", full_width=True),
            ]
        ),
        max_width="md",
        padding="lg",
    )

if __name__ == "__main__":
    app.run()
```

Run it:
```bash
python app.py
```
- 🌐 **Web UI:** `http://127.0.0.1:8000`
- 📖 **Swagger UI:** `http://127.0.0.1:8000/docs`
- 📡 **REST API Catalog:** `http://127.0.0.1:8000/api`

---

## 🪄 Streamlined Developer Experience (Streamlit-Like)

Write simple, procedural scripts with automatic state and event handling — no boilerplate required:

```python
import pydataui as ui

ui.title("Sales & Customer Metrics")
ui.metric("Active Subscriptions", "4,820", change="+8.4%")
ui.metric("Monthly Recurring Revenue", "$124,500", change="+12.1%")

def on_export():
    print("Exporting data report...")

ui.button("Export CSV Report", on_click=on_export)

if __name__ == "__main__":
    ui.run()
```

---

## 🔌 Native Mounting Inside FastAPI

Already have an existing FastAPI backend or microservice? Mount a PyDataUI dashboard directly into your FastAPI application with preserved sub-paths:

```python
from fastapi import FastAPI
from pydataui import App, mount
from pydataui.components import Container, Heading, Text

# Your existing FastAPI app
api = FastAPI(title="Unified Core Service")

@api.get("/api/v1/health")
def health():
    return {"status": "ok"}

# Create PyDataUI dashboard
dashboard = App(title="Ops Portal")

@dashboard.page("/")
def ops_home():
    return Container(
        Heading("Operations Portal"),
        Text("Real-time system telemetry and controls")
    )

# Mount dashboard at /ops
mount(api, dashboard, path="/ops")

# Run with standard uvicorn: uvicorn main:api --reload
```

---

## 🤖 Machine Learning Dashboard Example

PyDataUI includes native components for model evaluation:

```python
from pydataui import App
from pydataui.components import Container, Heading, Grid
from pydataui.components.data_science import ModelMetrics, ConfusionMatrix, FeatureImportance

app = App(title="Fraud Detection Model v3")

@app.page("/")
def dashboard():
    return Container(
        Heading("Production XGBoost Model Evaluation", level=1, margin_bottom="lg"),
        ModelMetrics(
            metrics={
                "Accuracy": 0.9642,
                "Precision": 0.9410,
                "Recall": 0.9780,
                "ROC-AUC": 0.9891
            }
        ),
        Grid(
            ConfusionMatrix(
                matrix=[[1450, 42], [28, 1380]],
                labels=["Legitimate", "Fraud"]
            ),
            FeatureImportance(
                features={
                    "velocity_1h": 0.34,
                    "avg_amount_ratio": 0.28,
                    "device_fingerprint_entropy": 0.18,
                    "geo_distance_anomaly": 0.12,
                    "is_international": 0.08
                },
                title="Top Predictive Features"
            ),
            columns=2, gap="lg", margin_top="lg"
        ),
        padding="lg"
    )

if __name__ == "__main__":
    app.run()
```

---

## 🔒 Authentication, Roles & API Keys

Secure your application for enterprise data workflows:

```python
from pydataui import App
from pydataui.components import Container, Heading, Flex
from pydataui.auth import (
    AuthManager, LoginPage, UserMenu, APIKeyManager,
    require_auth, require_role, Role, current_user
)

app = App(title="Secure Analytics Portal")
auth = AuthManager()  # Configure PYDATAUI_AUTH_SECRET for deployment

# Register users with roles
admin = auth.add_user("lead_eng", "password123", roles=[Role.ADMIN, Role.DATA_ENGINEER])
analyst = auth.add_user("analyst_jane", "password456", roles=[Role.DATA_ANALYST])

# Wire up auth routes (/api/auth/login, /api/auth/me, /api/auth/keys)
app.setup_auth(auth)

@app.page("/login")
def login_route():
    return LoginPage(title="Analytics Portal", subtitle="Sign in with your corporate credentials")

@app.page("/")
def dashboard():
    user = current_user.get()
    return Container(
        Flex(
            Heading("Data Warehouse Control Center", level=1),
            UserMenu(user),
            justify="space-between", align="center"
        ),
        APIKeyManager(keys=auth.list_api_keys(user.id) if user else []),
        padding="lg"
    )

# Protected API endpoint with API key requirement
@app.api("/data/export", method="GET")
def export_data(request):
    user = auth.require_auth_middleware(request)
    if not user:
        return {"error": "Unauthorized"}
    return {"status": "ok", "records": 100000}

if __name__ == "__main__":
    app.run()
```

### Automated API Key Authentication (ETL & Airflow)
Automate ingestion pipelines by passing the generated key:
```bash
curl -H "Authorization: Bearer pdu_live_819dd41a93870327fdc57311d0080755" \
     http://localhost:8000/data/export
```

---

## 🌐 Port Forwarding (`share=True`)

Share your application with remote stakeholders, clients, or team members with a single flag:

```python
# In your Python code:
app.run(share=True)
```
Or via CLI:
```bash
pydataui run app.py --share
```
Output:
```
  PyDataUI v0.2.0
  Running on http://127.0.0.1:8000
  Public URL: https://abc123.ngrok.app
  API docs at http://127.0.0.1:8000/docs
  REST API root at http://127.0.0.1:8000/api
```

---

## 📊 Performance

The backend uses pyrustapi. This repository does not yet contain a reproducible
benchmark suite establishing throughput, P99 latency, or memory superiority over
other frameworks. Evaluate equivalent real applications on the same hardware;
HTTP hello-world throughput does not establish data-application performance.

---

## 🧩 Comprehensive Component Library (80+ Components)

PyDataUI includes modern Tailwind and shadcn/ui components:

### 🔬 Data & Machine Learning
- `DataFrameTable`: Interactive table with automatic pandas integration
- `PlotlyChart`: Native Plotly figure embedding
- `MetricCard`: KPI card with delta percentage and trend indicators
- `ModelMetrics`: Evaluation grid (Accuracy, Precision, Recall, AUC, F1)
- `ConfusionMatrix`: Heat-mapped confusion matrix
- `FeatureImportance`: Horizontal bar chart for predictive features
- `PipelineStatus`: Step-by-step DAG execution tracker
- `DataTimeline`: Run history and audit event timeline
- `SchemaViewer`: Inspect table schemas, dtypes, nulls, and uniques
- `SQLEditor`: SQL query editor with inline Run button
- `JSONViewer`: Pretty-printed, collapsible JSON display
- `FileDownload`: In-browser data export to CSV/JSON

### 🎨 shadcn/ui Styled Components
- `ShadButton`, `ShadCard`, `ShadBadge`, `ShadAlert`, `ShadSeparator`
- `ShadProgress`, `ShadSkeleton`, `ShadSwitch`, `ShadTable`, `ShadSelect`
- `ShadTextarea`, `ShadLabel`, `ShadDialog` (Modal), `ShadScrollArea`
- `ShadTabs`, `ShadToast`, `ShadAvatar`, `ShadHoverCard`, `ShadAccordion`, `ShadSheet` (Drawer)

### 📐 Classic Layout & Forms
- `Container`, `Flex`, `Grid`, `Stack`, `HStack`, `VStack`, `Box`, `Center`, `Divider`
- `Heading`, `Text`, `Paragraph`, `Link`, `Code`, `Blockquote`
- `Button`, `Input`, `TextArea`, `Select`, `Checkbox`, `Radio`, `Switch`, `Slider`, `FileUpload`
- `Table`, `DataTable`, `Badge`, `Stat`, `Progress`, `Spinner`, `Modal`, `Drawer`
- `BarChart`, `LineChart`, `PieChart`, `DoughnutChart`, `Sparkline`

---

### 💼 Commercial SaaS Application Example

Experience an enterprise-grade AI gateway and subscription billing platform built entirely with PyDataUI:

```bash
python examples/commercial_saas_app.py
```

* **Executive Observability**: Live KPI cards (MRR, Token Volume, P99 Latency), time-window filters (`24h`, `7d`, `30d`), and pipeline step tracking.
* **Model Observatory**: Multi-model routing matrix (Claude 3.5 Sonnet, GPT-4o, Gemini 1.5 Pro, Llama 3 70B) with pricing and quality benchmarks.
* **Tiered Subscription Billing**: Interactive plan cards (Starter, Growth, Enterprise Scale) with usage quota progress and automated invoice history.
* **API Key Gateway**: Provision scoped production tokens (`pdu_live_...`) for automated pipelines.
* **Production Persistence**: Backed by SQLite WAL cross-process storage supporting multi-worker execution out of the box.

## 🛠️ Powerful CLI

Create, run, and containerize PyDataUI projects with zero boilerplate:

```bash
# 1. Create a project from starter templates
pydataui new analytics_hub --template dashboard
# Available templates: basic, dashboard, crud, ml-dashboard, data-pipeline, auth

# 2. Run local development with hot reload
pydataui dev app.py --port 8000 --reload

# 3. Run production server with public tunnel
pydataui run app.py --workers 1 --share

# 4. Check syntax and route definitions
pydataui check app.py

# 5. Generate secure API key for scripts
pydataui generate key --name "AirflowSync"

# 6. One-command containerization build
pydataui build app.py --output dist/
# Generates Dockerfile, docker-compose.yml, bundled static assets, and app.py
```

---

## 🚀 Performance & Benchmarks

PyDataUI is powered by the compiled Rust **`pyrustapi`** engine (built on Tokio and Hyper). Below are real benchmark measurements comparing PyDataUI against **FastAPI (Uvicorn + uvloop)** under identical hardware, models, and load conditions (ApacheBench, 2,000 requests, 50 concurrency):

### 1. High-Concurrency Stress Test (c=100, 5,000 requests)

Under heavy concurrent load (`c=100`), PyDataUI sustains high throughput and tight sub-100ms latency, while FastAPI/Uvicorn suffers severe queuing contention on asynchronous POST:

| Workload | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Speedup Advantage | PyDataUI Latency | FastAPI Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Real POST (Async Pydantic)**| **1,172.9 req/s** | 220.3 req/s | **⚡ 5.32x Faster** | **85.26 ms** | 453.85 ms (p99: 17.6s) |
| **Real GET (Sync)** | **4,066.8 req/s** | 1,679.0 req/s | **⚡ 2.42x Faster** | **24.59 ms** | 59.56 ms |
| **Real POST (Sync Pydantic)** | **1,845.0 req/s** | 935.3 req/s | **⚡ 1.97x Faster** | **54.20 ms** | 106.92 ms |
| **Real GET (Async I/O)** | **2,444.8 req/s** | 1,557.6 req/s | **⚡ 1.57x Faster** | **40.90 ms** | 64.20 ms |

### 2. Standard Load (c=50, 2,000 requests)

| Workload | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn + uvloop`) | Speedup Advantage | PyDataUI Latency | FastAPI Latency |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Real GET (Sync)** | **4,028.9 req/s** | 1,705.1 req/s | **⚡ 2.36x Faster** | **12.41 ms** | 29.32 ms |
| **Real POST (Sync Pydantic)** | **3,736.5 req/s** | 1,302.3 req/s | **⚡ 2.87x Faster** | **13.38 ms** | 38.39 ms |
| **Real POST (Async Pydantic)**| **2,311.5 req/s** | 1,388.6 req/s | **⚡ 1.66x Faster** | **21.63 ms** | 36.01 ms |
| **Real GET (Async I/O)** | **2,772.4 req/s** | 1,966.6 req/s | **⚡ 1.41x Faster** | **18.04 ms** | 25.42 ms |

- **Tested on Local Device**: Measured over loopback TCP using ApacheBench on macOS Darwin (Python 3.13).
- **Rust Tokio/Hyper Core**: Zero-copy network buffering prevents Python event-loop exhaustion under high concurrency.
- **Detailed Report**: See [docs/BENCHMARKS.md](docs/BENCHMARKS.md) for complete latency distributions (p50, p90, p95, p99) and reproduction instructions.

```bash
# Run standard benchmark:
python benchmarks/run_benchmark.py --requests 2000 --concurrency 50

# Run high-concurrency stress test:
python benchmarks/run_benchmark.py --requests 5000 --concurrency 100
```

---

## 📚 In-Depth Guides

- ⚡ [Performance & Benchmarks Guide](docs/BENCHMARKS.md)
- 📘 [Full Documentation](docs/README.md)
- 🎨 [UI Customization Guide (Tailwind, shadcn & HTML)](docs/CUSTOMIZATION.md)
- [HTML Reference for Developers](docs/HTML_REFERENCE.md)
- [CSS Reference for Developers](docs/CSS_REFERENCE.md)
- 🛠️ [Troubleshooting & Architecture Guide](docs/TROUBLESHOOTING.md)
- 🔒 [Authentication & Security Guide](docs/AUTHENTICATION.md)
- 📊 [Data Science & Engineering Components](docs/DATA_COMPONENTS.md)
- [Data Team Page Templates](docs/DATA_TEMPLATES.md)
- [Data Team Template Gallery (HTML)](https://rajboopathiking.github.io/pydataui/TEMPLATE_GALLERY/)
- 📖 [Complete API Reference](docs/API_REFERENCE.md)
- 🚀 [Production & Cloud Deployment](docs/DEPLOYMENT.md)
- 🛡️ [Production Readiness Assessment](docs/PRODUCTION_READINESS.md)
- ⚡ [Quick Reference Card](docs/QUICKREF.md)

---

## 🤝 Contributing

We welcome contributions from the data science, AI/ML, and Python web development communities!
Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for local environment setup, testing, and pull request guidelines.

---

## 📄 License

PyDataUI is licensed under the [MIT License](LICENSE).
Copyright (c) 2024 Boopathi Raj.

## Async custom API endpoints

Custom `@app.api` routes support both synchronous and asynchronous functions:

```python
import asyncio
from pydataui import App

app = App()

@app.api('/async-example', public=True)
async def async_example(request):
    await asyncio.sleep(0.01)  # Replace with an async API/database client.
    return {'message': 'Async endpoint completed'}

if __name__ == '__main__':
    app.run()
```

Authentication, roles, API-key scopes and CSRF checks still apply. Request and
current-user context remain active until the coroutine finishes, including
exception and cancellation cleanup. Existing synchronous routes keep their
session-locked behavior.

Async handlers do not hold the session's threading lock while awaiting I/O.
Consequently, custom async handlers must manage synchronization for shared
mutable data themselves; do not assume a whole handler is an atomic session
transaction. Use database transactions for concurrent writes. CPU-heavy ML
training and blocking libraries belong in worker jobs or a suitable executor.
This support is for custom API routes, not async pages or automatic State actions.
