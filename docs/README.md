# PyDataUI Documentation

> **The Production-Grade Full-Stack Python Framework for Data Roles.**  
> Powered by `pyrustapi` (Rust Tokio/Hyper Core), HTMX, Tailwind CSS, and shadcn/ui.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Why PyDataUI?](#2-why-pydataui)
3. [Architecture & Request Flow](#3-architecture--request-flow)
4. [Installation & Requirements](#4-installation--requirements)
5. [Quick Start](#5-quick-start)
6. [Core Concepts](#6-core-concepts)
   - [App Configuration](#app-configuration)
   - [Reactive State & StateVar](#reactive-state--statevar)
   - [Page Routing](#page-routing)
   - [Event Handlers & SSR](#event-handlers--ssr)
   - [Automatic REST APIs](#automatic-rest-apis)
7. [Tailwind CSS & shadcn/ui Integration](#7-tailwind-css--shadcnui-integration)
8. [Components Overview](#8-components-overview)
9. [Authentication, RBAC & API Keys](#9-authentication-rbac--api-keys)
10. [Port Forwarding (share=True)](#10-port-forwarding-sharetrue)
11. [CLI Tooling](#11-cli-tooling)
12. [Production Deployment](#12-production-deployment)
13. [Troubleshooting & Architecture Guide](TROUBLESHOOTING.md)

---

## 1. Overview

**PyDataUI** is a modern full-stack web framework designed for Data Engineers, Data Analysts, AI/ML Engineers, and Python developers. It bridges the gap between simple toy prototype libraries (Gradio, Streamlit) and complex multi-language web stacks (React + TypeScript + FastAPI).

With PyDataUI:
- You write **100% Python**.
- The backend runs on **pyrustapi**, an asynchronous HTTP core written in Rust (Tokio & Hyper) delivering lower latency and higher throughput than standard Python servers like Uvicorn.
- The UI is styled with **Tailwind CSS** and **shadcn/ui** design patterns, including full dark mode support.
- Reactivity is powered by **HTMX** server-side rendering (SSR): when state changes, minimal HTML fragments are sent to the browser and swapped into place with zero client JavaScript.
- Every state class automatically creates an OpenAPI-documented REST API for data integration.

---

## 2. Why PyDataUI?

### Comparison with Existing Frameworks

| Capability | PyDataUI | Streamlit | Gradio | FastAPI + React |
|---|---|---|---|---|
| **Programming Language** | 100% Python | 100% Python | 100% Python | Python + TypeScript |
| **HTTP Engine** | 🦀 **Rust (pyrustapi)** | 🐍 Tornado | 🐍 Uvicorn | 🐍 Uvicorn + Node |
| **P99 Latency** | **< 1.2ms** | > 25ms | > 15ms | ~ 5ms |
| **Multi-User Session Isolation** | ✅ Per-user session cookies | ❌ Script reruns | ❌ Global state issues | ✅ Full JWT / sessions |
| **Auto-Generated REST APIs** | ✅ Full CRUD per State | ❌ None | ❌ Limited | ⚠️ Manual routes |
| **UI Design System** | ✅ Tailwind + shadcn/ui | ⚠️ Custom opinionated | ⚠️ Block-based | ⚠️ Manual CSS |
| **Port Forwarding (`share=True`)** | ✅ Built-in tunnel | ❌ None | ✅ ngrok tunnel | ❌ Manual setup |
| **Data Components** | ✅ DF, Metrics, ML, SQL | ⚠️ Basic | ⚠️ Basic | ❌ Build from scratch |
| **Built-in RBAC & API Keys** | ✅ Yes | ❌ None | ❌ None | ⚠️ Manual |

---

## 3. Architecture & Request Flow

```
┌───────────────────────────────────────────────────────────────────────────┐
│                                BROWSER                                    │
│  - Loads Tailwind CSS Play CDN + shadcn variables                         │
│  - Executes HTMX engine (bundled locally via /_pdu/static/htmx.min.js)     │
└─────────────────────┬───────────────────────────────▲─────────────────────┘
                      │                               │
       Initial Page   │ GET /                         │ HTML Document (SSR)
       or User Event  │ POST /_pdu/event/State/method │ HTML Partial (Fragment)
                      ▼                               │
┌─────────────────────────────────────────────────────┴─────────────────────┐
│                          PYDATAUI SERVER                                  │
│                                                                           │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │                 pyrustapi HTTP Engine (Rust/Tokio)                │   │
│   └─────────────────┬───────────────────────────────▲─────────────────┘   │
│                     │                               │                     │
│                     ▼                               │                     │
│          Session Manager & Cookies             HTML Response              │
│                     │                               │                     │
│                     ▼                               │                     │
│            State Mutation Handler              Renderer Engine            │
│          (Executes Python methods)       (Component.render() to HTML)     │
│                     │                               ▲                     │
│                     └───────────────────────────────┘                     │
│                                                                           │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │            Auto-Generated REST API (/api/{StateName})             │   │
│   │    GET, PUT, DELETE state & POST methods as JSON endpoints        │   │
│   └───────────────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Installation & Requirements

PyDataUI requires **Python 3.9+**.

```bash
# Core framework
pip install pydataui

# With data science & ML dependencies (pandas, plotly, pyarrow)
pip install "pydataui[data]"

# Full installation (data + tunnel + dev)
pip install "pydataui[all]"
```

---

## 5. Quick Start

Create an app file `app.py`:

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

Run with the CLI:
```bash
pydataui dev app.py --reload
```

---

## 6. Core Concepts

### App Configuration

```python
from pydataui import App

app = App(
    title="Data Hub",              # Browser & Swagger UI title
    description="Corporate Portal",# OpenAPI description
    version="0.2.0",               # Semantic version
    debug=True,                    # Verbose logs
    host="127.0.0.1",              # Host interface
    port=8000,                     # Port
    session_max_age=86400,         # Session timeout in seconds (24h)
)
```

### Reactive State & StateVar

State in PyDataUI is defined by subclassing `State`. Typed class variables become reactive state descriptors:

```python
from pydataui import State

class PipelineState(State):
    batch_size: int = 5000
    is_running: bool = False
    status_log: list = []

    def start_pipeline(self):
        self.is_running = True
        self.status_log.append("Started batch run")

    def stop_pipeline(self):
        self.is_running = False
        self.status_log.append("Halted by operator")
```

- When referenced at the **class level** (e.g. `PipelineState.batch_size`), it returns a `StateVarRef` which binds to the current user's session snapshot during rendering.
- When accessed inside a method (`self.batch_size`), it operates as a standard Python attribute.

### Page Routing

Register pages using `@app.page(path)`:

```python
@app.page("/")
def home():
    return Container(...)

@app.page("/models")
def models_view():
    return Container(...)

@app.page("/pipeline/{pipeline_id}")
def pipeline_details(pipeline_id: str):
    return Container(...)
```

### Event Handlers & SSR

Buttons, forms, and inputs connect to State methods using props:

```python
# Direct method reference
Button("Start", on_click=PipelineState.start_pipeline)

# Lambda with argument capture
Button("Delete", on_click=lambda id=item.id: TableState.delete_item(id))

# Two-way input binding
Input("Batch Size", bind=PipelineState.batch_size, type="number")
```

### Automatic REST APIs

For every registered `State`, PyDataUI creates endpoints automatically:

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/{State}` | Full state dictionary serialized to JSON |
| `GET` | `/api/{State}/{field}` | Single field value |
| `PUT` | `/api/{State}` | Update state variables from JSON body |
| `DELETE` | `/api/{State}` | Reset state instance to class defaults |
| `POST` | `/api/{State}/{method}` | Execute a method (accepts optional JSON payload) |

Catalog all states and endpoints:
```bash
curl http://localhost:8000/api
```

Interactive Swagger UI:
- `http://localhost:8000/docs`
- `http://localhost:8000/api/docs`

---

## 7. Tailwind CSS & shadcn/ui Integration

PyDataUI includes the **Tailwind CSS Play CDN** and pre-configured **shadcn/ui CSS custom variables** (`--primary`, `--secondary`, `--destructive`, `--background`, `--card`, etc.) in the HTML shell.

### Using shadcn Components

```python
from pydataui.components.shadcn import (
    ShadCard, ShadCardHeader, ShadCardTitle, ShadCardContent,
    ShadButton, ShadBadge, ShadInput, ShadSwitch
)

ShadCard(
    ShadCardHeader(
        ShadCardTitle("Model Deployment"),
        ShadBadge("Active", variant="default")
    ),
    ShadCardContent(
        ShadButton("Deploy Model", variant="default", size="lg")
    )
)
```

All standard HTML elements also support arbitrary Tailwind utility classes through the `class_name` or `className` prop:
```python
Box(
    Heading("Custom Styled"),
    class_name="bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-2xl shadow-xl"
)
```

---

## 8. Components Overview

PyDataUI comes with **80+ components**:

- **Layout:** `Container`, `Flex`, `Grid`, `Stack`, `HStack`, `VStack`, `Box`, `Center`, `Spacer`, `Divider`, `Wrap`
- **Typography:** `Heading`, `Text`, `Paragraph`, `Label`, `Link`, `Code`, `Blockquote`
- **Forms:** `Button`, `Input`, `TextArea`, `Select`, `Checkbox`, `Radio`, `RadioGroup`, `Switch`, `Slider`, `FileUpload`, `Form`
- **Data Display:** `Table`, `DataTable`, `Stat`, `Badge`, `Tag`, `Avatar`, `KeyValue`, `DescriptionList`, `List`, `ListItem`
- **Feedback:** `Alert`, `Spinner`, `Toast`, `Progress`, `Skeleton`, `Empty`
- **Navigation:** `Navbar`, `Sidebar`, `Tabs`, `Tab`, `Breadcrumb`, `Menu`, `NavLink`, `Dropdown`, `Pagination`
- **Overlay:** `Modal`, `Drawer`, `Tooltip`, `Popover`
- **Charts:** `BarChart`, `LineChart`, `PieChart`, `DoughnutChart`, `Sparkline`
- **Data Science:** `DataFrameTable`, `PlotlyChart`, `MetricCard`, `ModelMetrics`, `ConfusionMatrix`, `FeatureImportance`, `PipelineStatus`, `DataTimeline`, `SchemaViewer`, `SQLEditor`, `JSONViewer`, `FileDownload`, `DataUpload`
- **shadcn/ui:** `ShadButton`, `ShadCard`, `ShadInput`, `ShadBadge`, `ShadAlert`, `ShadSeparator`, `ShadProgress`, `ShadSkeleton`, `ShadSwitch`, `ShadTable`, `ShadSelect`, `ShadTextarea`, `ShadLabel`, `ShadDialog`, `ShadScrollArea`, `ShadTabs`, `ShadToast`, `ShadAvatar`, `ShadHoverCard`, `ShadAccordion`, `ShadSheet`

---

## 9. Authentication, RBAC & API Keys

See the full [Authentication Guide](AUTHENTICATION.md).

```python
from pydataui.auth import AuthManager, Role, LoginPage, UserMenu, require_auth

auth = AuthManager(secret_key="a-secure-secret-key-at-least-32-characters!")
admin = auth.add_user("lead_eng", "secret123", roles=[Role.ADMIN, Role.DATA_ENGINEER])
app.setup_auth(auth)
```

Generate programmatic keys:
```python
key = auth.create_api_key(name="AirflowSync", user_id=admin.id, scopes=["read", "write"])
print(key.key) # pdu_live_...
```

---

## 10. Port Forwarding (`share=True`)

Share your application with remote stakeholders, clients, or team members with a single flag:

```python
app.run(share=True)
```
Or via CLI:
```bash
pydataui run app.py --share
```

Tunnels use `pyngrok` if installed, or fallback to encrypted SSH port-forwarding via `serveo.net`.

---

## 11. CLI Tooling

```bash
# Create a project from starter templates
pydataui new analytics_hub --template ml-dashboard

# Start development server
pydataui dev app.py --port 8000 --reload

# Start production server with public tunnel
pydataui run app.py --workers 4 --share

# Validate app syntax and routes
pydataui check app.py

# Generate API key
pydataui generate key --name "ProductionETL"

# Containerize build
pydataui build app.py --output dist/
```

---

## 12. Production Deployment

See the full [Deployment Guide](DEPLOYMENT.md) for Docker, Kubernetes, and Systemd configurations.
