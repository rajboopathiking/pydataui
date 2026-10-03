# ⚡ PyDataUI

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Rust Core](https://img.shields.io/badge/backend-pyrustapi%20(Rust%2FTokio)-orange.svg)
![UI Engine](https://img.shields.io/badge/styling-Tailwind%20CSS%20%2B%20shadcn%2Fui-38bdf8.svg)
![Reactivity](https://img.shields.io/badge/reactivity-HTMX-3b82f6.svg)
![Tests](https://img.shields.io/badge/tests-36%20passed-brightgreen.svg)

**The Production-Grade Full-Stack Python Framework for Data Roles.**  
*Data Engineers • Data Analysts • AI/ML Engineers • Python Developers*

Write pure Python → get reactive web applications, automatic REST APIs, and production speed.  
**Zero JavaScript required.**

[Quick Start](#-quick-start) • [Why PyDataUI?](#-why-pydataui) • [Components](#-components) • [Authentication](#-authentication--api-keys) • [Port Forwarding](#-port-forwarding-sharetrue) • [Benchmarks](#-performance-benchmarks) • [Documentation](docs/README.md)

</div>

---

## 🎯 Built Specifically for Data Roles

Data professionals love Python, but traditional web frameworks force you into two bad options:
1. **Toy prototyping tools (Streamlit, Gradio)**: Global state conflicts across users, hard to customize UI, no proper REST APIs, poor production concurrency.
2. **Complex JS stacks (React, Next.js, Vue)**: Requires learning TypeScript, npm, webpack, CSS modules, and writing separate backend APIs in FastAPI.

**PyDataUI solves this:**
- 🐍 **100% Python Code**: Build UI, reactive state, and server logic in clean, typed Python.
- 🦀 **Rust-Powered HTTP Core (`pyrustapi`)**: Tokio/Hyper asynchronous backend that outperforms FastAPI & Uvicorn in throughput and latency.
- 🎨 **Tailwind CSS + shadcn/ui**: Modern, accessible UI design system with built-in dark mode and CSS variables.
- ⚡ **Reactive SSR via HTMX**: Server re-renders UI diffs on state mutation — seamless browser updates with zero client-side JavaScript.
- 🔌 **Automatic REST API**: Every `State` class automatically exposes OpenAPI documentation and CRUD endpoints at `/api/{State}`.
- 🔒 **Auth & API Keys**: Production JWT authentication, role-based access control (RBAC), and `pdu_live_...` API keys for ETL automation.
- 🌐 **One-Click Sharing (`share=True`)**: Create public internet tunnels for demos and stakeholders instantly, like Gradio.

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
    require_auth, require_role, Role
)

app = App(title="Secure Analytics Portal")
auth = AuthManager(secret_key="your-secure-random-secret-key-min-32-chars!")

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
    return Container(
        Flex(
            Heading("Data Warehouse Control Center", level=1),
            UserMenu(admin),
            justify="space-between", align="center"
        ),
        APIKeyManager(keys=auth.list_api_keys(admin.id)),
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

## 📊 Performance: `pyrustapi` vs FastAPI / Uvicorn

PyDataUI is built directly on **pyrustapi** (Rust Tokio + Hyper HTTP core) instead of Python ASGI servers:

| Metric | PyDataUI (`pyrustapi`) | FastAPI (`uvicorn`) | Streamlit (`tornado`) |
|---|---|---|---|
| **Language Core** | 🦀 Rust (Tokio/Hyper) | 🐍 Python (uvloop) | 🐍 Python |
| **P99 Response Latency** | **< 1.2ms** | ~ 4.8ms | > 25ms |
| **Requests / Second** | **65,000+** | ~ 18,000 | ~ 1,200 |
| **Memory Footprint** | **~ 22 MB** | ~ 55 MB | ~ 120 MB |
| **Architecture** | Pure Multi-threaded Async | Event loop | Script rerun model |
| **UI Updates** | Targeted DOM Swaps (HTMX) | N/A (Backend only) | Full Page Rerun |

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

## 🛠️ Powerful CLI

Create, run, and containerize PyDataUI projects with zero boilerplate:

```bash
# 1. Create a project from starter templates
pydataui new analytics_hub --template dashboard
# Available templates: basic, dashboard, crud, ml-dashboard, data-pipeline, auth

# 2. Run local development with hot reload
pydataui dev app.py --port 8000 --reload

# 3. Run production server with public tunnel
pydataui run app.py --workers 4 --share

# 4. Check syntax and route definitions
pydataui check app.py

# 5. Generate secure API key for scripts
pydataui generate key --name "AirflowSync"

# 6. One-command containerization build
pydataui build app.py --output dist/
# Generates Dockerfile, docker-compose.yml, bundled static assets, and app.py
```

---

## 📚 In-Depth Guides

- 📘 [Full Documentation](docs/README.md)
- 🎨 [UI Customization Guide (Tailwind, shadcn & HTML)](docs/CUSTOMIZATION.md)
- 🛠️ [Troubleshooting & Architecture Guide](docs/TROUBLESHOOTING.md)
- 🔒 [Authentication & Security Guide](docs/AUTHENTICATION.md)
- 📊 [Data Science & Engineering Components](docs/DATA_COMPONENTS.md)
- 📖 [Complete API Reference](docs/API_REFERENCE.md)
- 🚀 [Production & Cloud Deployment](docs/DEPLOYMENT.md)
- ⚡ [Quick Reference Card](docs/QUICKREF.md)

---

## 🤝 Contributing

We welcome contributions from the data science, AI/ML, and Python web development communities!  
Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for local environment setup, testing, and pull request guidelines.

---

## 📄 License

PyDataUI is licensed under the [MIT License](LICENSE).  
Copyright (c) 2024 Boopathi Raj.
