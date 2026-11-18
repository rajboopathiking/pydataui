# PyDataUI Core API & Methods Reference

Comprehensive specification of all core classes, methods, signatures, decorators, storage engines, and CLI tools in **PyDataUI**.

---

## Table of Contents

1. [Application Core (`App`)](#1-application-core-app)
2. [State & Reactivity (`state`, `State`, `ProceduralState`)](#2-state-reactivity)
3. [Authentication & Security (`AuthManager`)](#3-authentication-security-authmanager)
4. [Storage Engines & Cluster Persistence (`storage`)](#4-storage-engines-cluster-persistence-storage)
5. [Data Ingestion & Tabular Sniffing (`DataTable`)](#5-data-ingestion-tabular-sniffing-datatable)
6. [Pydantic Form Generator (`ShadForm`)](#6-pydantic-form-generator-shadform)
7. [Terminal User Interface Engine (`tui`, `run_tui`)](#7-terminal-user-interface-engine-tui)
8. [CLI Command Reference](#8-cli-command-reference)
9. [Internal HTTP & Event Wire Protocol](#9-internal-http-event-wire-protocol)
10. [Procedural Streamlit-Style DX Reference (`pydataui as pdu`)](#10-procedural-streamlit-style-dx-reference-import-pydataui-as-pdu)

---

## 1. Application Core (`App`)

### `class App(...)`
Located in `pydataui.app.App`. The central orchestrator integrating routing, state snapshots, REST APIs, middleware, and the HTTP server engine.

```python
from pydataui import App, AppConfig

app = App(
    title="Enterprise AI Operations",
    description="Internal control plane for SLM clusters",
    version="1.2.2",
    debug=False,
    secret_key="your-32-byte-production-secret-key-goes-here",
    session_store=None,     # Defaults to SQLite or Memory
    auth_store=None,        # Defaults to SQLite or Memory
    max_request_size=10 * 1024 * 1024  # 10 MB limit
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | `"PyDataUI App"` | The title shown in HTML document `<title>` and TUI dashboard headers. |
| `description` | `str` | `""` | App description for OpenAPI metadata and page headers. |
| `version` | `str` | `"1.2.2"` | Semantic application version for telemetry and API catalogs. |
| `debug` | `bool` | `False` | Enables verbose stack traces and development logs. |
| `secret_key` | `Optional[str]` | `None` | Cryptographic secret for signing session cookies and JWT tokens. |
| `session_store` | `Optional[BaseSessionStore]`| `None` | Storage backend for user sessions (`Memory`, `SQLite`, `Postgres`). |
| `auth_store` | `Optional[BaseAuthStore]` | `None` | Storage backend for users and API keys (`Memory`, `SQLite`, `Postgres`). |
| `max_request_size` | `int` | `10485760` | Max request body size in bytes (10MB). Rejects oversized requests with HTTP 413. |

---

#### Methods on `App`

##### `app.page(path: str, title: Optional[str] = None, layout: Optional[Callable] = None)`
Decorator that registers a Server-Side Rendered (SSR) page route.

- **Parameters**:
  - `path` (`str`): URL pattern (e.g. `'/'`, `'/dashboard'`, `'/model/{model_id}'`).
  - `title` (`Optional[str]`): Custom `<title>` override for this page.
  - `layout` (`Optional[Callable]`): Wrapper layout function receiving the page content component.
- **Handler Return Value**: Must return a `Component` instance (e.g. `Container`, `DashboardLayout`, `Card`) or valid HTML string.
- **Example**:
  ```python
  @app.page("/clusters")
  def cluster_view():
      return Container(Heading("Cluster Status", level=1))
  ```

##### `app.api(path: str, method: str = 'GET', public: bool = False, roles: tuple = (), **kwargs)`
Decorator that registers a high-speed custom REST API endpoint on the underlying engine.

- **Parameters**:
  - `path` (`str`): REST endpoint path (e.g. `'/api/v1/telemetry'`).
  - `method` (`str`): HTTP verb (`'GET'`, `'POST'`, `'PUT'`, `'DELETE'`).
  - `public` (`bool`): If `True`, bypasses authentication. Default is `False`.
  - `roles` (`tuple[str]`): List of required role names (e.g. `(Role.ADMIN,)`).
- **Example**:
  ```python
  @app.api("/api/v1/health", method="GET", public=True)
  async def health_check():
      return {"status": "healthy", "uptime_s": 84920}
  ```

##### `app.setup_auth(auth_manager: AuthManager, allow_registration: bool = False)`
Mounts standard `/api/auth/*` endpoints (`/login`, `/logout`, `/me`, `/keys`) and binds authentication middleware.

- **Parameters**:
  - `auth_manager` (`AuthManager`): Initialized authentication manager.
  - `allow_registration` (`bool`): If `True`, enables public `/api/auth/register`.

##### `app.mount(path: str, asgi_app: Any)`
Mounts an external ASGI application (such as an existing FastAPI, Starlette, or LangGraph backend) under a sub-path prefix.

- **Parameters**:
  - `path` (`str`): Prefix path (e.g. `'/sub-api'`).
  - `asgi_app` (`Any`): Valid ASGI-compatible app.

##### `app.run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False, workers: int = 1, share: bool = False)`
Starts the production or development HTTP server.

- **Parameters**:
  - `host` (`str`): IP address to bind to (`"127.0.0.1"` for local, `"0.0.0.0"` for all interfaces).
  - `port` (`int`): Port number.
  - `reload` (`bool`): If `True`, enables live auto-reloading on code edits.
  - `workers` (`int`): Number of parallel multi-threaded worker processes.
  - `share` (`bool`): Launches a public internet tunnel and prints the public HTTPS URL.

##### `app.build_openapi() -> Dict[str, Any]`
Generates an OpenAPI 3.0-compliant JSON dictionary documenting all registered REST APIs and state actions.

---

## 2. State & Reactivity

PyDataUI provides two state management models:
1. **Procedural State (`state()`)**: Zero-class procedural hook ideal for scripts, internal dashboards, and prototypes.
2. **Object-Oriented State (`class State`)**: Class-based reactive store for multi-model enterprise applications.

### Procedural State Hook: `state(**defaults) -> ProceduralState`

```python
from pydataui import state

# 1. Initialize state with default values
s = state(
    counter=0,
    active_node="Node-A",
    messages=[{"role": "assistant", "content": "Welcome!"}],
    loading=False
)

# 2. Register reactive action
@s.action
def increment():
    s.counter += 1

@s.action
async def set_node(node_name: str = "", **kwargs):
    s.active_node = node_name or kwargs.get("node", "Node-A")
```

#### Methods & Attributes on `ProceduralState`
- `@s.action`: Decorator registering a function as an interactive server action callable via HTMX or the TUI.
- `s.<variable_name>`:
  - Inside `@s.action` handlers: Resolves to the active session value and permits direct mutation.
  - Inside `@app.page` layout declarations: Evaluates to a `StateVarRef` descriptor that renders reactive bindings.
- `s.to_dict() -> Dict[str, Any]`: Returns a JSON-serializable dictionary of current state variables.
- `s.reset()`: Resets all values back to the original initial values.

---

### Class-Based Reactive State: `class State`

```python
from pydataui import State, StateVar

class ClusterState(State):
    node_count: int = 8
    region: str = "us-east-1"
    is_busy: bool = False

    def scale_up(self):
        self.node_count += 1

    def scale_down(self):
        if self.node_count > 1:
            self.node_count -= 1
```

#### Lifecycle & Session Isolation
- Each browser session / cookie receives an independent instance of `ClusterState`.
- `ClusterState.node_count` accessed on the class returns a `StateVarRef` for declarative component binding.
- `self.node_count` accessed inside methods operates on the session's isolated instance.

---

## 3. Authentication & Security (`AuthManager`)

### `class AuthManager(secret_key, token_expire_hours=24, store=None, enable_throttling=True, ...)`
Located in `pydataui.auth.AuthManager`. Implements production security:
- Password hashing with PBKDF2-HMAC-SHA256 (600,000 rounds) + unique salt.
- Signed JSON Web Tokens (JWT) with HMAC-SHA256.
- Brute-force rate limiting and lockout protection.
- Scoped API keys with prefix `pdu_live_`.

```python
from pydataui import AuthManager, Role
from pydataui.storage import SQLiteAuthStore

auth = AuthManager(
    secret_key="your-32-byte-secret-key-at-least-32-bytes-long",
    token_expire_hours=24,
    store=SQLiteAuthStore("auth.db"),
    enable_throttling=True,
    max_login_attempts=5,
    lockout_duration_seconds=300
)
```

#### Methods on `AuthManager`

| Method Signature | Return Type | Description |
| :--- | :--- | :--- |
| `add_user(username, password, email="", roles=None)` | `User` | Provisions a new user. Hashes password with unique salt. Raises `ValueError` if username exists. |
| `get_or_create_user(username, password, email="", roles=None)` | `User` | Idempotently retrieves existing user or creates a new one. |
| `authenticate(username, password, client_ip=None)` | `Optional[str]` | Validates credentials against password hash. If valid, returns signed JWT token string; if invalid or throttled, returns `None` or raises `AuthenticationThrottledError`. |
| `verify_token(token: str)` | `Optional[User]` | Decodes and verifies a JWT token. Returns `User` object if valid, or `None` if expired/tampered. |
| `create_api_key(name, user_id, scopes=None, expires_days=None)` | `APIKey` | Generates a scoped API key string starting with `pdu_live_` and stores SHA256 key hash. |
| `verify_api_key(raw_key: str)` | `Optional[APIKey]` | Validates an API key, checks expiration, updates `last_used` timestamp, and increments usage counter. |
| `revoke_api_key(key_id: str)` | `bool` | Deactivates an API key. |
| `list_api_keys(user_id: str)` | `List[APIKey]` | Returns all API keys belonging to a user. |
| `set_user_password(user_id: str, new_password: str)` | `bool` | Resets user password to new salted hash. |
| `delete_user(user_id: str)` | `bool` | Permanently deletes user from identity store. |

#### Security Decorators
- `@require_auth`: Protects an endpoint or page; redirects unauthenticated requests to `/login`.
- `@require_role(Role.ADMIN)`: Requires specific role clearance.
- `@require_api_key(scopes=["read:telemetry"])`: Enforces valid API key in `X-API-Key` or `Authorization` header.

---

## 4. Storage Engines & Cluster Persistence (`storage`)

PyDataUI supports swappable session and authentication storage backends:

```python
from pydataui.storage import (
    MemorySessionStore, SQLiteSessionStore, PostgresSessionStore,
    MemoryAuthStore, SQLiteAuthStore, PostgresAuthStore
)
```

### Storage Backends Comparison

| Store | Durability | Multi-Process / Cluster Safe | Best For |
| :--- | :---: | :---: | :--- |
| **Memory** | Ephemeral | No (single process only) | Unit testing, local development |
| **SQLite** | Persistent disk | Yes (WAL mode with SQLite lock management) | Single-node production, embedded appliances |
| **PostgreSQL**| Distributed | Yes (cluster-wide shared identity & sessions)| Multi-node Kubernetes, high-availability deployments |

---

## 5. Data Ingestion & Tabular Sniffing (`DataTable`)

### `sniff_tabular_data(data: Any) -> Tuple[List[Dict[str, Any]], List[str]]`
Automatically sniffs, extracts columns, and normalizes tabular data from:
- `pandas.DataFrame`
- `polars.DataFrame`
- `duckdb.PyRelation`
- `pyarrow.Table`
- `list[pydantic.BaseModel]`
- `list[dict]`

```python
import polars as pl
from pydataui import DataTable

df = pl.DataFrame({
    "cluster": ["us-east", "eu-west", "ap-south"],
    "nodes": [12, 8, 16],
    "status": ["HEALTHY", "HEALTHY", "WARNING"]
})

DataTable(
    data=df,
    searchable=True,
    paginated=True,
    page_size=10,
    bordered=True
)
```

---

## 6. Pydantic Form Generator (`ShadForm`)

### `ShadForm.from_pydantic(model_cls, on_submit, submit_label="Submit", ...)`
Generates validated input fields matching Pydantic type annotations:
- `str` -> Text `<input>`
- `int`, `float` -> Number `<input>`
- `bool` -> `<switch>` or `<checkbox>`
- `datetime.date` -> `<input type="date">`
- `Enum` -> `<select>` dropdown
- `Field(description="...")` -> Helper description text
- `Field(ge=..., le=...)` -> Min / max HTML validation constraints

---

## 7. Terminal User Interface Engine (`tui`)

PyDataUI includes a built-in terminal dashboard engine (`pydataui.tui.run_tui`):

```bash
# Launch interactive TUI
pydataui run --tui app.py
```

### Keyboard Navigation & Commands

| Input Command | Action in TUI Mode |
| :--- | :--- |
| `[1-N]` | Switches directly to page index number `1` through `N`. |
| `<action_name>` | Executes a registered state action method. |
| `input <text>` | Passes input string to active page handler. |
| `set <key>=<value>` | Updates a state variable directly from the terminal prompt. |
| `r` | Refreshes terminal dashboard rendering. |
| `q` or `quit` | Cleanly exits the TUI session without double confirmation. |

### Interactive AI Chat in TUI
When a page contains a `Chat` component, the TUI activates conversational chat mode:
- Number keys (`1`, `2`, `3`) instantly execute numbered suggestion chips.
- `/clear` invokes the `on_clear` handler and resets conversation history.
- `q` cleanly exits back to the terminal prompt.

---

## 8. CLI Command Reference

The `pydataui` CLI provides commands for the full application lifecycle:

```bash
# 1. Create a new application from template
pydataui new my_app --template ml-dashboard

# 2. Start local development server with auto-reload
pydataui dev app.py --port 8000 --reload

# 3. Run production server
pydataui run app.py --host 0.0.0.0 --port 8000 --workers 4

# 4. Run interactive Terminal UI (TUI)
pydataui run --tui app.py

# 5. Share via secure public HTTPS tunnel
pydataui run app.py --share

# 6. Syntax and routing validation check
pydataui check app.py

# 7. Generate production API key
pydataui generate key --name "TelemetryWorker"

# 8. Show installed framework version
pydataui version
```

---

## 9. Internal HTTP & Event Wire Protocol

PyDataUI uses clean REST endpoints and HTMX partial swap protocols:

| Route Pattern | Method | Purpose | Response Format |
| :--- | :--- | :--- | :--- |
| `GET /` | `GET` | SSR HTML Page initial load | `text/html` |
| `POST /_pdu/event/{State}/{action}` | `POST` | Reactive UI event trigger | `text/html` (DOM Partial) |
| `GET /api/{State}` | `GET` | State variable snapshot | `application/json` |
| `POST /api/{State}/{action}` | `POST` | Headless REST action trigger | `application/json` |
| `POST /api/auth/login` | `POST` | User credential authentication | `application/json` (JWT Token) |
| `POST /api/auth/logout` | `POST` | Session termination | `application/json` |
| `GET /api/auth/me` | `GET` | Authenticated user profile | `application/json` |
| `GET /_pdu/health` | `GET` | Infrastructure health check | `application/json` |
| `GET /docs` | `GET` | OpenAPI Swagger documentation | `text/html` |


---

## 10. Procedural Streamlit-Style DX Reference (`import pydataui as pdu`)

PyDataUI v1.5.0 provides a comprehensive procedural API under the `pydataui` module namespace. All methods support top-to-bottom procedural execution, context managers (`with` syntax), and direct component return values.

### 10.1 Global Configuration & Lifecycle

#### `pdu.set_page_config(...)`
Configures application metadata, layout mode, visual theme, and production FastAPI OpenAPI/Swagger settings.

```python
pdu.set_page_config(
    title="Cluster Operations",
    layout="wide",
    theme="zinc",
    dark_mode=True,
    docs_url="/docs",
    openapi_url="/openapi.json",
    swagger_ui_parameters={"filter": True, "syntaxHighlight.theme": "monokai"},
    docs_roles=["admin"]
)
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `title` | `str` | `"PyDataUI App"` | HTML `<title>` tag and browser tab name. |
| `layout` | `str` | `"centered"` | Layout width: `"centered"` (max 1200px) or `"wide"` (100% responsive fluid width). |
| `theme` | `str | dict` | `"indigo"` | Theme name (e.g. `"zinc"`, `"emerald"`, `"violet"`), custom HEX (`"#4f46e5"`), or palette dict. |
| `dark_mode` | `bool` | `False` | Forces dark mode if `True`. |
| `docs_url` | `Optional[str]` | `"/docs"` | Path to Swagger UI docs. Pass `None` to completely disable in production. |
| `openapi_url` | `Optional[str]` | `"/openapi.json"` | Path to OpenAPI JSON schema. Pass `None` to disable in production. |
| `swagger_ui_parameters` | `Optional[dict]` | `None` | Dictionary of Swagger UI config parameters (e.g. `{"filter": True}`). |
| `docs_roles` | `Optional[list[str]]`| `None` | List of user roles allowed to access `/docs` (e.g. `["admin"]`). |

#### `pdu.run(app=None, host="127.0.0.1", port=8000, reload=False, share=False)`
Starts the ASGI web application and optional instant public HTTPS tunnel.

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `app` | `Optional[App]` | `None` | Custom App instance. If `None`, runs the active default procedural app. |
| `host` | `str` | `"127.0.0.1"` | Bind interface IP. Use `"0.0.0.0"` for Docker containers. |
| `port` | `int` | `8000` | Port number to listen on. |
| `reload` | `bool` | `False` | Enables auto-reload on source code modification. |
| `share` | `bool` | `False` | Starts an instant, secure public HTTPS tunnel (ready in ~3.5s). |

#### `pdu.page(path, title=None, roles=None, public=False)`
Decorator for defining multi-page routes in procedural apps.

```python
@pdu.page("/analytics", title="Telemetry", roles=["admin"])
def analytics_view():
    pdu.title("Telemetry Dashboard")
```

#### `pdu.page_link(path, label=None, icon=None)`
Renders an interactive internal page navigation anchor.

#### `pdu.switch_page(path)`
Programmatically redirects the user to a different route.

---

### 10.2 Structural Layout & Containers

#### `pdu.flex(direction="row", justify="start", align="stretch", gap=3, wrap=False, **props)`
Flexbox container context manager. Provides granular control over CSS flexbox layout.

```python
with pdu.flex(direction="row", justify="between", align="center", gap=4):
    pdu.subheader("Cluster Nodes")
    pdu.badge("Active", color="emerald")
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `direction` | `str` | `"row"` | `"row"` or `"column"`. |
| `justify` | `str` | `"start"` | `"start"`, `"center"`, `"end"`, `"between"`, `"around"`, `"evenly"`. |
| `align` | `str` | `"stretch"` | `"stretch"`, `"start"`, `"center"`, `"end"`, `"baseline"`. |
| `gap` | `int | str` | `3` | Space between child items (`1` through `12` or CSS string like `"16px"`). |
| `wrap` | `bool | str` | `False` | Whether children wrap onto multiple lines. |

#### `pdu.row(align="center", justify="start", gap=3, wrap=False, **props)`
Convenience shorthand for `pdu.flex(direction="row", ...)`.

#### `pdu.column(align="stretch", justify="start", gap=3, **props)`
Convenience shorthand for `pdu.flex(direction="column", ...)`.

#### `pdu.grid(columns=None, min_column_width=None, gap=4, row_gap=None, column_gap=None, **props)`
Responsive CSS Grid layout container.

```python
# Auto-responsive card grid: columns automatically wrap when items reach 260px!
with pdu.grid(min_column_width="260px", gap=4):
    pdu.stat_card("Node 1", "98%")
    pdu.stat_card("Node 2", "84%")

# Fixed 3-column grid
with pdu.grid(columns=3, gap=6):
    pdu.metric("CPU", "45%")
    pdu.metric("RAM", "12 GB")
    pdu.metric("Disk", "68%")
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `columns` | `int | list[int] | dict` | `None` | Number of columns (`3`), ratio list (`[1, 2, 1]`), or breakpoint dict (`{"sm": 1, "md": 2, "lg": 4}`). |
| `min_column_width`| `str` | `None` | Activates responsive auto-fit grid (`repeat(auto-fit, minmax(width, 1fr))`). |
| `gap` | `int | str` | `4` | General grid gap. |
| `row_gap` | `int | str` | `None` | Row-specific gap override. |
| `column_gap` | `int | str` | `None` | Column-specific gap override. |

#### `pdu.columns(spec, gap="medium")`
Streamlit-parity multi-column splitter. Accepts integer count (`3`) or relative weights (`[1, 2, 1]`). Returns a list of column context managers.

#### `pdu.tabs(tabs, expand=False, hide_tab_buttons=False, variant="line")`
Tab container supporting full width distribution and headless multi-step wizards.

```python
# 1. Standard navigation tabs
tab1, tab2 = pdu.tabs(["Overview", "Logs"], expand=True)

# 2. Segmented pill tabs
tab_day, tab_mo = pdu.tabs(["Day", "Month"], variant="pill")

# 3. Headless Multi-Step Wizard (tab headers completely hidden)
steps = pdu.tabs(["Account", "Billing", "Review"], hide_tab_buttons=True)
with steps[0]:
    pdu.text_input("Organization")
    pdu.button("Next →")
```

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `tabs` | `list[str]` | Required | Labels for each tab. |
| `expand` | `bool` | `False` | Distributes tabs equally across 100% of available container width. |
| `hide_tab_buttons`| `bool` | `False` | Hides the top navigation tab bar completely. Ideal for multi-step wizards. |
| `variant` | `str` | `"line"` | Tab style: `"line"` (underline indicator) or `"pill"` (segmented pill). |

#### `pdu.pinned(position="bottom", class_name="", **props)`
Docked sticky viewport container (e.g. sticky bottom action bar, pinned top notice).

#### `pdu.overlay(z_index=50, class_name="", **props)`
Full-screen or relative overlay backdrop container.

#### `pdu.card(title=None, subtitle=None, position=None, **props)`
Elevated card container with subtle border and shadow.

#### `pdu.container(border=False, **props)`
Layout wrapper container with optional border.

#### `pdu.expander(label, expanded=False)`
Collapsible disclosure panel.

#### `pdu.dialog(title, trigger_label="Open")`
Modal dialog overlay container.

#### `pdu.status(label, expanded=True, state="running")`
Live operational status block. Yields status controller with `s.update(label=..., state="complete")`.

#### `pdu.spacer(height=16)`
Vertical whitespace divider (`height` in pixels or CSS string).

#### `pdu.divider(label=None)`
Horizontal rule with optional centered text label (e.g. `pdu.divider("OR")`).

---

### 10.3 Component Coordinate Positioning Engine

Every visual component in PyDataUI v1.5.0 accepts coordinate positioning props:

| Prop | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `position` | `str` | `None` | CSS positioning model: `"relative"`, `"absolute"`, `"fixed"`, `"sticky"`. |
| `top` | `str | int` | `None` | Top coordinate offset (e.g. `"14px"`, `"1rem"`, `0`). |
| `bottom` | `str | int` | `None` | Bottom coordinate offset. |
| `left` | `str | int` | `None` | Left coordinate offset. |
| `right` | `str | int` | `None` | Right coordinate offset. |
| `inset` | `str | int` | `None` | Shorthand for all 4 coordinates (e.g. `0` for full fill). |
| `z_index` | `int` | `None` | Z-index stacking context priority (e.g. `50`). |

**Example: Absolute Floating Badge on Relative Card**
```python
with pdu.card(position="relative"):
    pdu.badge("HIGH PRIORITY", color="rose", position="absolute", top="12px", right="12px")
    pdu.subheader("Inference Node 04")
```

---

### 10.4 Commercial Dashboard & Analytics Primitives

#### `pdu.metric(label, value, delta=None, delta_color="normal", icon=None)`
Executive KPI metric block with delta trend indicator.

#### `pdu.stat_card(title, value, change=None, change_type=None, icon=None, sparkline=None, color="indigo")`
Commercial dashboard KPI card with integrated inline SVG sparkline and icon.

```python
pdu.stat_card(
    title="Monthly Recurring Revenue",
    value="$154,200",
    change="+18.2% vs last mo",
    sparkline=[92, 110, 125, 140, 154],
    icon="📈",
    color="emerald"
)
```

#### `pdu.sparkline(data, color="indigo", width=120, height=36, stroke_width=2, fill=True)`
Pure inline SVG sparkline graph. Zero JavaScript, zero external dependencies, renders in 0.001ms.

#### `pdu.badge(label, color="indigo", variant="subtle", icon=None, **props)`
Status tag badge. `variant` accepts `"subtle"`, `"solid"`, or `"outline"`. `color` accepts any theme preset or custom HEX code.

#### `pdu.pricing_card(tier, price, period="/month", features=[], button_text="Get Started", highlighted=False, badge_label=None)`
SaaS subscription pricing tier card with highlighted CTA.

---

### 10.5 Forms, Inputs & Temporal Controls

| Function | Signature Summary | Description |
| :--- | :--- | :--- |
| `pdu.button(label, on_click=None, type="default")` | `type`: `"primary"`, `"secondary"`, `"destructive"`, `"outline"` | Interactive click button. |
| `pdu.download_button(label, data, file_name, mime)` | `data`: `str | bytes`, `file_name`: `str` | Client-side file downloader. |
| `pdu.text_input(label, value="", key=None, ...)` | `type`: `"text"` or `"password"` | Single-line text input field. |
| `pdu.text_area(label, value="", height=None, ...)`| Multiline text input. | Multi-line textarea. |
| `pdu.search_input(placeholder="...", on_search=...)`| Instant reactive search bar with HTMX trigger. | Real-time search query field. |
| `pdu.date_input(label, value=None, min_value=..., key=...)`| Native HTML5 date picker bound to session_state. | Calendar date selector. |
| `pdu.time_input(label, value=None, key=...)` | Native HTML5 time picker bound to session_state. | 24h / 12h time selector. |
| `pdu.number_input(label, min_value=None, max_value=None, step=1)` | Numeric stepper input. | Number input field. |
| `pdu.slider(label, min_value=0, max_value=100, value=None, step=1)` | Visual range slider. | Slider range bar. |
| `pdu.selectbox(label, options, index=0, key=None)` | Dropdown select menu. | Dropdown select picker. |
| `pdu.multiselect(label, options, default=None)` | Multi-tag dropdown picker. | Tag multi-selector. |
| `pdu.checkbox(label, value=False, key=None)` | Boolean checkbox toggle. | Standard checkbox. |
| `pdu.toggle(label, value=False, key=None)` | iOS-style switch toggle. | Switch toggle. |
| `pdu.file_uploader(label, accept=None, multiple=False)` | File upload drag & drop zone. | File upload input. |
| `pdu.color_picker(label, value="#4f46e5")` | Visual color palette picker. | Color selection tool. |

#### Batched Forms (`pdu.form`, `pdu.form_submit_button`)
Prevents instant state updates on individual keystrokes; gathers inputs and submits in a single batch.

```python
with pdu.form("user_settings"):
    name = pdu.text_input("Name")
    email = pdu.text_input("Email")
    pdu.form_submit_button("Save Changes", on_click=save_user)
```

---

### 10.6 Tabular Data & Charts

| Function | Signature Summary | Description |
| :--- | :--- | :--- |
| `pdu.dataframe(data, use_container_width=True)` | Universal dataframe viewer (Pandas, Polars, PyArrow, DuckDB, lists of dicts). | Interactive paginated table. |
| `pdu.table(data)` | Static clean HTML table. | Fast static table. |
| `pdu.line_chart(data, x=None, y=None, color=None)` | Responsive line chart. | Line chart visualization. |
| `pdu.bar_chart(data, x=None, y=None, color=None)` | Bar chart with custom or multi-color support. | Bar chart visualization. |
| `pdu.area_chart(data, x=None, y=None, color=None)`| Area gradient chart. | Area chart visualization. |
| `pdu.scatter_chart(data, x=None, y=None, color=None)`| Point scatter chart. | Scatter plot visualization. |

---

### 10.7 Feedback & Status Notifications

| Function | Signature Summary | Description |
| :--- | :--- | :--- |
| `pdu.success(body, icon=None)` | Green success banner with icon. | Positive confirmation message. |
| `pdu.error(body, icon=None)` | Red error banner with icon. | Error notification. |
| `pdu.warning(body, icon=None)` | Amber warning banner with icon. | Warning caution message. |
| `pdu.info(body, icon=None)` | Blue informative banner with icon. | Informational notice. |
| `pdu.toast(body, icon=None)` | Transient auto-dismissing toast notification. | Floating toast. |
| `pdu.spinner(text="In progress...")`| Loading spinner context manager. | Animated loading indicator. |
| `pdu.progress(value, text=None)`| Progress bar (0 to 100). | Visual progress meter. |

---

### 10.8 State & Production Authentication

```python
# 1. Procedural Session State
pdu.session_state["active_node"] = "node-01"
val = pdu.session_state.get("active_node")

# 2. User Management
pdu.create_user("alice", "SecurePassword123!", email="alice@company.com", roles=["admin"])

# 3. Authentication
is_ok = pdu.login("alice", "SecurePassword123!")
pdu.logout()

# 4. Route Guard
pdu.require_auth(roles=["admin"], redirect_url="/login")
```

---

### 10.9 FastAPI Production Hardening & ASGI Methods

#### `pdu.get_fastapi()` or `app.fastapi`
Returns the underlying native `fastapi.FastAPI` application instance.

```python
import pydataui as pdu
from fastapi import APIRouter, BackgroundTasks

fastapi_app = pdu.get_fastapi()

# Mount custom FastAPI router
router = APIRouter(prefix="/v1")

@router.post("/telemetry")
def log_telemetry(bg: BackgroundTasks):
    bg.add_task(persist_to_clickhouse)
    return {"status": "enqueued"}

fastapi_app.include_router(router)
```

#### Production Security & Documentation Filtering
```python
# 1. Strip docs completely in production:
pdu.set_page_config(docs_url=None, openapi_url=None)

# 2. Filter Swagger UI endpoints:
pdu.set_page_config(swagger_ui_parameters={"filter": True, "persistAuthorization": True})

# 3. Lock docs behind RBAC authentication:
pdu.set_page_config(docs_roles=["admin"])
```

#### Mounting PyDataUI into Existing FastAPI
```python
from fastapi import FastAPI
import pydataui as pdu

parent_api = FastAPI()
# Build your PyDataUI views...
parent_api.mount("/dashboard", pdu.get_fastapi())
```

### 10.10 Final Commercial Extensions (v1.5.0)

#### `pdu.navbar(*children, title=None, logo=None, links=None, search=False, user=None, sticky=True, **kwargs)`
Renders a top commercial application shell with brand logo, title, horizontal nav links, search input, and user profile avatar.

```python
pdu.navbar(
    title="CloudAI Ops",
    logo="⚡",
    links=[{"label": "Overview", "href": "/"}, {"label": "Telemetry", "href": "/telemetry"}],
    search=True,
    user={"name": "Alice", "role": "Admin"}
)
```

#### `pdu.breadcrumb(items, separator="/", **kwargs)`
Renders hierarchical navigation breadcrumbs (`["Home", "Clusters", "Node 04"]`).

#### `pdu.image(src, caption=None, width=None, use_container_width=False, rounded=True)`
Renders images from URLs, local file paths, raw bytes, or PIL Images (Streamlit `st.image` equivalent).

#### `pdu.video(data, format="video/mp4", caption=None, controls=True, **kwargs)`
Renders HTML5 video player from URLs or bytes (Streamlit `st.video` equivalent).

#### `pdu.audio(data, format="audio/mp3", caption=None, controls=True, **kwargs)`
Renders HTML5 audio player from URLs or bytes (Streamlit `st.audio` equivalent).

#### `pdu.popover(label="Options", *children, position="bottom", icon=None)`
Adds a floating popover card container (Streamlit `st.popover` equivalent). Supports `with pdu.popover("Filter"): ...`.

#### `pdu.tooltip(text, *children, position="top")`
Renders an accessible hover tooltip popup over children or standalone info icon.

#### `pdu.write_stream(stream_generator, key=None)`
Streams real-time tokens directly into the UI from OpenAI, Ollama, LangChain, or custom generators (Streamlit `st.write_stream` equivalent).

```python
def stream():
    for token in ["Analyzing ", "cluster ", "telemetry..."]:
        yield token

with pdu.chat_message("assistant"):
    pdu.write_stream(stream)
```

#### `pdu.date_range_picker(label, value=None, min_date=None, max_date=None, key=None, help=None)`
Renders a dual-date range selector (Start Date → End Date) bound to `pdu.session_state`. Returns `(start_date, end_date)`.

#### `pdu.data_editor(data, num_rows="fixed", disabled_columns=None, key=None)`
Renders an interactive in-place editable spreadsheet table (Streamlit `st.data_editor` equivalent). Double-click to edit cell values; syncs back to `pdu.session_state`.
