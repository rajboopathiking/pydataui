# PyDataUI Documentation

> **The Production-Grade Full-Stack Python Framework for Web, Mobile & Desktop.**  
> Powered by standard FastAPI ASGI (default) with optional PyRustAPI (compiled Rust Tokio/Hyper Core), HTMX, Tailwind CSS, and shadcn/ui.

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
14. [UI Customization Guide (Tailwind, shadcn & HTML)](CUSTOMIZATION.md)
15. [Production Readiness & Architecture Assessment](PRODUCTION_READINESS.md)
16. [Performance & Real Benchmarks Guide (PyDataUI vs FastAPI)](BENCHMARKS.md)

---

## 1. Overview

**PyDataUI** is a modern full-stack web, mobile, and desktop framework designed for Data Engineers, Data Analysts, AI/ML Engineers, and Python developers. It bridges the gap between toy prototype libraries (Streamlit, Gradio) and complex multi-language web stacks (React + TypeScript + FastAPI).

With PyDataUI:
- 🐍 **100% Python Code**: Build responsive web, mobile (Android/iOS), and desktop apps without writing JavaScript, Swift, or Kotlin.
- ⚡ **FastAPI Default Engine**: Native ASGI foundation running on standard FastAPI and Uvicorn with zero C/Rust compilation requirements.
- 🦀 **Optional PyRustAPI Core**: Seamlessly switch to an ultra-high-throughput compiled Rust HTTP engine (Tokio & Hyper) delivering up to 34,000+ req/sec for hyper-scale workloads.
- 🔌 **Native FastAPI Mounting**: Mount PyDataUI dashboards, admin consoles, and AI tools directly inside existing FastAPI backends via `mount(api, app, path="/dashboard")`.
- 🪄 **Dual Developer Experience**: Use the rapid procedural API (`import pydataui as ui; ui.title(...); ui.run()`) for instant scripts, or the declarative Component & State system for large-scale enterprise applications.
- 📱 **Cross-Platform Mobile & Desktop**: Built-in Progressive Web App (PWA), Capacitor mobile shell (Android `.apk` and iOS `.ipa`), and standalone desktop apps (`--desktop` or Tauri 2.0).
- 🎨 **Tailwind CSS + shadcn/ui**: Modern design system with dark mode, CSS variables, and accessible components.
- ⚡ **Reactive SSR via HTMX**: State changes trigger hypermedia fragment responses that update the DOM dynamically without client-side virtual DOM overhead.
- 🤖 **AI & Agent Ready**: Built-in `Chat`, `Markdown`, and `CodeEditor` components compatible with LangGraph, UnifiedNexus, and LLMs.
- 🔒 **Auth & API Keys**: Built-in JWT authentication, RBAC (`@require_auth(roles=[...])`), and secure API keys (`pdu_live_...`).
- 📊 **Enterprise Page Templates**: Pre-packaged analyst, data quality, pipeline, and ML model registry templates via `pydataui.templates`.
- 🌐 **One-Click Sharing (`share=True`)**: Create public internet tunnels instantly via Cloudflare or ngrok for remote client demos.
- 📖 **Automatic REST APIs**: Every reactive State class automatically creates OpenAPI-documented REST endpoints for external data integration.

---

## 2. Why PyDataUI?

### Comparison with Existing Frameworks

| Capability | PyDataUI (v1.0.0 Stable) | Streamlit | Gradio | FastAPI + React |
|---|---|---|---|---|
| **Programming Language** | **100% Python** | 100% Python | 100% Python | Python + TypeScript |
| **Default HTTP Engine** | ⚡ **FastAPI ASGI** | 🐍 Tornado | 🐍 Uvicorn | 🐍 Uvicorn + Node |
| **High-Throughput Option** | 🦀 **Rust (PyRustAPI Tokio/Hyper)** | ❌ None | ❌ None | ❌ None |
| **Mount in FastAPI App** | ✅ **Native (`mount()`)** | ❌ Separate process | ⚠️ Mount as WSGI/ASGI | ✅ Native |
| **Streamlit-like DX (`ui.*`)** | ✅ **Yes (`import pydataui as ui`)** | ✅ Yes | ⚠️ Blocks | ❌ No |
| **Mobile Apps (APK & IPA)** | ✅ **Native (Capacitor 8.x) + PWA** | ❌ None | ❌ None | ⚠️ React Native rewrite |
| **Desktop Executables** | ✅ **Tauri 2.0 & Native Window** | ❌ None | ❌ None | ⚠️ Electron rewrite |
| **P99 Latency** | **< 1.2ms** (Rust) / ~2.5ms (FastAPI) | > 25ms | > 15ms | ~ 5ms |
| **Multi-User Session Isolation** | ✅ **Per-user session state** | ❌ Script reruns | ❌ Global state issues | ✅ Full JWT / sessions |
| **Auto-Generated REST APIs** | ✅ **Full OpenAPI CRUD per State** | ❌ None | ❌ Limited | ⚠️ Manual routes |
| **UI Design System** | ✅ **Tailwind + shadcn/ui** | ⚠️ Custom opinionated | ⚠️ Block-based | ⚠️ Manual CSS |
| **Port Forwarding (`share=True`)** | ✅ **Built-in tunnel** | ❌ None | ✅ ngrok tunnel | ❌ Manual setup |
| **Data & AI Components** | ✅ **Chat, Code, DF, Metrics, Charts** | ⚠️ Basic | ⚠️ Basic | ❌ Build from scratch |
| **Built-in RBAC & API Keys** | ✅ **Yes** | ❌ None | ❌ None | ⚠️ Manual |

---

## 3. Architecture & Request Flow

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    CLIENT: BROWSER / MOBILE / DESKTOP                     │
│  - Web Browser / PWA (Standalone Display)                                 │
│  - Native Mobile Webview (Capacitor 8.x: Android APK / iOS IPA)           │
│  - Native Desktop Window (Tauri 2.0 or OS Webview)                        │
│  - Executes HTMX engine (bundled locally via /_pdu/static/htmx.min.js)     │
└─────────────────────┬───────────────────────────────▲─────────────────────┘
                      │                               │
       Initial Page   │ GET / or GET /dashboard       │ HTML Document (SSR)
       or User Event  │ POST /_pdu/event/State/method │ HTML Partial (Fragment)
                      ▼                               │
┌─────────────────────────────────────────────────────┴─────────────────────┐
│                          PYDATAUI SERVER                                  │
│                                                                           │
│   ┌───────────────────────────────────────────────────────────────────┐   │
│   │   FastAPI ASGI Engine (Default) or PyRustAPI Engine (Rust/Tokio)  │   │
│   │   Supports standalone App() or mounted inside existing FastAPI    │   │
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
    version="0.3.1",               # Semantic version
    debug=True,                    # Verbose logs
    host="127.0.0.1",              # Host interface
    port=8000,                     # Port
    session_max_age=86400,         # Session timeout in seconds (24h)
    max_request_size=10*1024*1024, # Reject larger bodies with HTTP 413
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

### Native FastAPI Mounting & Conflict Handling

You can mount any PyDataUI application directly into an existing FastAPI application with a single line of code:

```python
from fastapi import FastAPI
from pydataui import App, mount

api = FastAPI(title="Production API")
dashboard = App(title="Internal Dashboard")

@dashboard.page("/")
def home():
    return "Operations Control Center"

mount(api, dashboard, path="/dashboard")
# or: dashboard.mount_to(api, path="/dashboard")
```

#### How PyDataUI Resolves & Prevents Conflicts:
- **Route Collisions**: Parent FastAPI routes (e.g. `/users`) and PyDataUI routes (e.g. `/dashboard/users`) live in isolated routing subtrees with zero collisions.
- **OpenAPI / Swagger Separation**: Parent API keeps its root `/docs`; PyDataUI automatically serves its dedicated interactive docs at `/dashboard/docs`.
- **Static Asset Sandboxing**: PyDataUI isolates internal Tailwind CSS & HTMX under `/_pdu/static/*`, never clashing with parent `/static/*`.
- **Session & Cookie Isolation**: PyDataUI uses a distinct signed cookie (`pdu-session`). Parent JWT or session cookies are never touched.
- **Multiple Sub-Apps**: You can mount multiple distinct PyDataUI apps (`/admin`, `/portal`, `/analytics`) on one FastAPI app with zero state leakage.

> 📖 **Full Architectural Guide**: See [FastAPI Mounting & Conflicts](FASTAPI_MOUNTING_AND_CONFLICTS.md).

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
