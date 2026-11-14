# PyDataUI Modular Architecture & Clean Organization Guide

This guide establishes the architectural standards for building clean, maintainable, production-ready enterprise applications with **PyDataUI**. It provides a clear mental model comparing PyDataUI with React, Redux, Streamlit, and standard HTML/CSS, and eliminates common developer confusion around state, forms, and component lifecycle.

---

## 1. The Core Philosophy: Why Organization Matters

PyDataUI combines the expressiveness of Python with the sub-millisecond execution speeds of compiled Rust and the simplicity of modern HTMX. Unlike script-based frameworks that re-execute the entire file from line 1 on every user click, PyDataUI operates on a **persistent, session-isolated reactive state engine**.

To prevent codebases from becoming messy or tightly coupled, PyDataUI enforces a clean separation of concerns modeled after modern enterprise React/Next.js architectures:

```text
my_enterprise_app/
├── app.py                  # Main Entrypoint & Page Router
├── state.py                # Pure Reactive State Schemas (Single Source of Truth)
├── actions.py              # Business Logic, Calculations, & Event Handlers
├── components/             # Reusable UI Presentation Elements
│   ├── __init__.py
│   ├── layout.py           # AppShell, Navbar, Sidebar, NavItem
│   └── cards.py            # Domain-specific UI widgets
└── pages/                  # Page Views (Assembled from Components & Bound to State)
    ├── __init__.py
    ├── dashboard.py
    ├── data_view.py
    └── settings.py
```

---

## 2. Comparative Mental Model

### For React & Redux Developers

| React / Redux Concept | PyDataUI Equivalent | How It Works in PyDataUI |
| :--- | :--- | :--- |
| **Redux Store / Zustand** | `pdu.state(...)` in `state.py` | Holds session-isolated reactive variables with dirty-tracking. |
| **Action Creators & Reducers** | `@state.action` in `actions.py` | Pure Python functions that mutate state variables directly without boilerplate. |
| **Functional Components** | Python Functions returning `Component` | Return declarative tree of UI primitives (`pdu.Card`, `pdu.Grid`). |
| **Virtual DOM Reconciliation** | Server-Side HTMX DOM Diffing | Instead of running a heavy JS runtime in the browser, the server sends precise HTML fragments to swap in the DOM. |
| **Controlled Inputs (`value + onChange`)** | `pdu.Input(name="field", value=s.field)` | Standard HTML input attributes with automatic two-way binding. |
| **Next.js App Router** | `@app.page("/path")` in `app.py` | Native multi-page routing with automatic CSRF protection and SEO metadata. |

### For Streamlit Developers

| Streamlit Pattern | Streamlit Limitation | PyDataUI Solution |
| :--- | :--- | :--- |
| `st.button("Click")` | Re-executes the entire script from line 1. | Executes only the targeted `@state.action`, swapping only the mutated DOM element. |
| `st.session_state` | Hard to decouple; mutable anywhere in script. | Centralized in `state.py` with typed schemas and transaction boundaries. |
| Custom CSS / Layout | Fragile `unsafe_allow_html=True` hacks. | Built-in Tailwind CSS utility classes and Shadcn-inspired modern design system. |
| Terminal UI | Impossible (Browser only). | Native Terminal UI (`pdu.run_tui(app)`) from the exact same codebase! |

### For HTML / CSS Developers

| HTML5 / CSS Construct | PyDataUI Primitive | Rendered Output |
| :--- | :--- | :--- |
| `<h1>`, `<h2>`, `<h3>` | `pdu.Heading("Title", level=1)` | `<h1 class="pdu-heading...">Title</h1>` |
| `<div class="container">` | `pdu.Container(...)` | Responsive auto-centering container |
| `<div class="flex flex-row">` | `pdu.Row(...)` or `pdu.HStack(...)` | Flexbox row layout |
| `<div class="flex flex-col">` | `pdu.Col(...)` or `pdu.VStack(...)` | Flexbox column layout |
| `<div class="grid grid-cols-4">` | `pdu.Grid(..., columns=4)` | Responsive CSS Grid layout |
| `<a href="/path">` | `pdu.Link("Label", href="/path")` | Semantic anchor with HTMX SPA transition capabilities |
| `<button>` | `pdu.Button("Click", on_click=fn)` | Accessible button wired to reactive event endpoints |

---

## 3. The 4 Essential Golden Rules

### Rule 1: The Mandatory `name="..."` Attribute for Form Inputs
In HTML and HTMX, an `<input>` element **must have a `name="..."` attribute** to be serialized in HTTP POST payloads:

```python
# ❌ INCORRECT (Lacks name attribute; browser sends empty body {})
pdu.Input(placeholder="Enter search term")

# ✅ CORRECT (name="query" ensures data is serialized and passed to action)
pdu.Input(placeholder="Enter search term", name="query", value=s.query)
```

When placed inside `pdu.Form(..., on_submit=handle_search)`, PyDataUI matches the `name` attribute directly to the action parameters:

```python
@search_state.action
def handle_search(query: str = "", **kwargs):
    search_state.query = query
    # Execute search logic...
```

### Rule 2: StateVarRef vs Evaluated Primitive Values
When passing state into UI layouts:
```python
pdu.Heading(s.count, level=2)
```
`s.count` is a **`StateVarRef`** — an active reference to the state property. PyDataUI's rendering engine binds this reference to the DOM element with `data-bind="count"`. When an action modifies `s.count`, only this heading updates!

If you need the raw primitive value outside an action (e.g. for Python arithmetic or logging):
```python
current_count = int(s.count)
current_label = str(s.label)
```

### Rule 3: Procedural State (`pdu.state`) vs Class State (`class S(pdu.State)`)
PyDataUI supports two complementary state patterns:

1. **Procedural State (`pdu.state(...)`) — Recommended for most apps**:
   ```python
   # state.py
   auth_state = pdu.state(username="", is_authenticated=False)

   # actions.py
   @auth_state.action
   def login(username: str = ""):
       auth_state.username = username
       auth_state.is_authenticated = True
   ```
2. **Class-based State (`class MyState(pdu.State)`) — For complex OOP designs**:
   ```python
   class AnalyticsState(pdu.State):
       active_nodes: int = 12
       traffic_gb: float = 450.2

       def scale_cluster(self):
           self.active_nodes += 2
   ```

### Rule 4: Clean Layered Imports & Fallbacks
To ensure components can run both as part of an imported package and as standalone scripts, use resilient import blocks:

```python
# pages/dashboard.py
import pydataui as pdu
try:
    from ..state import dashboard_state
    from ..actions import scale_up_workers
    from ..components import AppShell, KpiCard
except ImportError:
    from state import dashboard_state
    from actions import scale_up_workers
    from components import AppShell, KpiCard
```

---

## 4. Complete Architecture Blueprint (File-by-File)

### Step 1: `state.py` (Centralized Data Models)
```python
# state.py
import pydataui as pdu

dashboard_state = pdu.state(
    active_workers=24,
    throughput_k=148.5,
    system_status="HEALTHY"
)
```

### Step 2: `actions.py` (Decoupled Business Logic)
```python
# actions.py
try:
    from .state import dashboard_state
except ImportError:
    from state import dashboard_state

@dashboard_state.action
def scale_up_workers():
    dashboard_state.active_workers += 4
    dashboard_state.throughput_k = round(dashboard_state.throughput_k * 1.15, 1)
```

### Step 3: `components/layout.py` (Reusable Visual Shell)
```python
# components/layout.py
import pydataui as pdu

def AppShell(title: str, content: pdu.Component, current_path: str = "/") -> pdu.Container:
    navbar = pdu.Row(
        pdu.Heading("Enterprise Portal", level=3, class_name="font-bold text-lg"),
        pdu.Row(
            pdu.Link("Dashboard", href="/", class_name="px-3 py-1 hover:underline"),
            pdu.Link("Settings", href="/settings", class_name="px-3 py-1 hover:underline"),
            class_name="space-x-4"
        ),
        class_name="justify-between items-center pb-4 border-b border-border mb-6"
    )
    return pdu.Container(navbar, content, class_name="max-w-6xl py-6")
```

### Step 4: `pages/dashboard.py` (Declarative View)
```python
# pages/dashboard.py
import pydataui as pdu
try:
    from ..state import dashboard_state
    from ..actions import scale_up_workers
    from ..components import AppShell
except ImportError:
    from state import dashboard_state
    from actions import scale_up_workers
    from components import AppShell

def DashboardPage() -> pdu.Container:
    body = pdu.Card(
        pdu.Col(
            pdu.Heading(f"Active Nodes: {dashboard_state.active_workers}", level=2),
            pdu.Button("Add Node", on_click=scale_up_workers, variant="primary")
        ),
        class_name="p-6"
    )
    return AppShell(title="Operations Dashboard", content=body, current_path="/")
```

### Step 5: `app.py` (Routing & Application Bootstrap)
```python
# app.py
import pydataui as pdu
try:
    from .pages import DashboardPage
except ImportError:
    from pages import DashboardPage

app = pdu.App(title="Enterprise Ops Hub", theme="slate")

@app.page("/", title="Dashboard")
def route_dashboard():
    return DashboardPage()

if __name__ == "__main__":
    app.run(reload=True)
```

---

## 5. Comprehensive Component Catalog (v1.2.2)

All canonical components are accessible directly from top-level `import pydataui as pdu`:

### Layout & Containers
- `pdu.Container(*children, class_name=...)`: Centered responsive container.
- `pdu.Row(*children, class_name=...)`: Horizontal flex container (`flex-direction: row`).
- `pdu.Col(*children, class_name=...)`: Vertical flex container (`flex-direction: column`).
- `pdu.Grid(*children, columns=4, class_name=...)`: Responsive CSS grid.
- `pdu.Card(*children, class_name=...)`: Elevated container with border, padding, and subtle shadow.
- `pdu.Divider()`: Subtle horizontal divider rule.

### Forms & Input
- `pdu.Button(text, on_click=None, variant="primary"|"outline"|"secondary", size="sm"|"md"|"lg")`
- `pdu.Input(placeholder="", name="fieldName", value=None, type="text"|"number"|"password")`
- `pdu.TextArea(placeholder="", name="fieldName", rows=4)`
- `pdu.Select(options=[{"label": "A", "value": "a"}], name="fieldName")`
- `pdu.Slider(min=0, max=100, step=1, name="fieldName")`
- `pdu.Checkbox(label="Accept terms", name="fieldName")`
- `pdu.Switch(label="Enable Notifications", name="fieldName")`
- `pdu.Form(*children, on_submit=action_function)`: Wraps controls and serializes all named inputs.

### Data Display
- `pdu.DataTable(data=records, sortable=True, pagination=True, page_size=10)`: High-performance tabular data grid with automatic schema sniffing.
- `pdu.Badge(text, variant="default"|"secondary"|"outline")`: Status and tag indicators.
- `pdu.Stat(label="Revenue", value="$1.2M", change="+12%")`: Metric KPI widget.
- `pdu.Avatar(src=None, fallback="JD")`: User avatar with fallback initials.
- `pdu.Tooltip(text="Help info", content=pdu.Button("Hover me"))`: Hover tooltip.

### Typography
- `pdu.Heading(text, level=1|2|3|4|5|6)`: Semantic heading (`h1` through `h6`).
- `pdu.Text(text, class_name="...")`: Inline text span with typography tokens.
- `pdu.Paragraph(text)`: Body copy paragraph (`<p>`).
- `pdu.Link(label, href="/path", external=False)`: Navigational anchor.
- `pdu.Code(snippet, language="python")`: Syntax-highlighted code block.

### Feedback & Overlays
- `pdu.Alert(title="Notice", message="Backup complete", variant="info"|"warning"|"success"|"danger")`
- `pdu.Progress(value=75, max=100)`: Animated progress bar.
- `pdu.Spinner(size="sm"|"md"|"lg")`: Loading spinner.
- `pdu.Modal(title="Confirm", trigger=pdu.Button("Open"), content=pdu.Text("Are you sure?"))`: Accessible dialog overlay.

### Advanced & AI
- `pdu.Chat(messages=s.messages, on_send=handle_chat, suggestions=[...])`: Turn-key conversational AI chat interface.
- `pdu.Markdown(source=markdown_str)`: Real-time Markdown parser.
- `pdu.CodeEditor(code=s.code, language="sql")`: Live interactive code editor.

---

## 6. Testing & Quality Assurance

To ensure rock-solid stability without needing manual browser clicks, PyDataUI provides native compatibility with Starlette's `TestClient`:

```python
# test_app.py
from starlette.testclient import TestClient
from app import app
from state import dashboard_state

def test_dashboard_flow():
    client = TestClient(app.asgi_app)

    # 1. Verify GET renders 200 OK
    res = client.get("/")
    assert res.status_code == 200
    assert "Active Nodes" in res.text

    # 2. Trigger action event via POST
    post_res = client.post(
        f"/_pdu/event/{dashboard_state._name}/scale_up_workers",
        headers={"HX-Request": "true"}
    )
    assert post_res.status_code == 200
    assert "28" in post_res.text  # Server-rendered HTMX contains updated count!
```
