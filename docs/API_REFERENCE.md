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
