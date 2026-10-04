> See [0.2.1 migration](MIGRATION_0_2_1.md) for security defaults and state controls.

# PyDataUI API Reference

Complete reference for classes, functions, decorators, components, and CLI tools.

---

## Table of Contents

1. [App & Configuration](#1-app--configuration)
2. [State & Reactivity](#2-state--reactivity)
3. [Authentication & Security](#3-authentication--security)
4. [Tunnel & Port Forwarding](#4-tunnel--port-forwarding)
5. [Component Index](#5-component-index)
6. [CLI Command Reference](#6-cli-command-reference)
7. [System HTTP Routes](#7-system-http-routes)

---

## 1. App & Configuration

### `class App(title="PyDataUI App", description="", version="0.2.1", debug=False, **kwargs)`
The central application object integrating routing, state snapshots, REST APIs, and the pyrustapi HTTP server.

#### Methods:
- `app.page(path: str, title: Optional[str] = None, layout: Optional[Callable] = None)`
  Decorator registering an SSR page route. The decorated function must return a `Component` or HTML string.
- `app.api(path: str, method: str = 'GET', public=False, roles=(), **kwargs)`
  Decorator registering a custom JSON endpoint on the underlying pyrustapi engine.
- `app.setup_auth(auth_manager: AuthManager, allow_registration=False)`
  Mounts `/api/auth/*` endpoints and registers authentication middleware handlers.
- `app.run(host=None, port=None, reload=False, workers=1, share=False, auth=None)`
  Starts the HTTP server.
  - `share=True`: Launches a public internet tunnel (port forwarding) and prints the public URL.
  - `workers=N`: Number of pyrustapi multi-threaded worker processes.

#### Properties:
- `app.title`: Application title.
- `app.routes`: Mapping of registered page routes to handler functions.
- `app.api_routes`: Mapping of registered custom API routes.

---

## 2. State & Reactivity

### `class State`
Base class for reactive application state stores.
- Annotated class variables become reactive `StateVar` descriptors.
- Methods serve as event handlers and automatic REST actions.

```python
class MyState(State):
    count: int = 0
    def increment(self): self.count += 1
```

- **Class-level access** (`MyState.count`): Returns a `StateVarRef` proxy that evaluates against the active session snapshot during rendering.
- **Instance-level access** (`self.count`): Standard Python value.
- `to_dict() -> Dict[str, Any]`: Serializes the current state instance to a JSON-compatible dictionary.
- `reset()`: Resets all state variables back to class default values.

---

## 3. Authentication & Security

### `class AuthManager(secret_key: str, token_expire_hours: int = 24)`
Handles user authentication, password hashing (`pbkdf2_hmac`), JWT encoding/decoding, and API key management.

#### Methods:
- `add_user(username: str, password: str, email: str = "", roles: List[str] = None) -> User`
  Creates a user with hashed password. Raises `ValueError` if username exists.
- `authenticate(username: str, password: str) -> Optional[str]`
  Verifies credentials and returns a signed JWT token, or `None`.
- `verify_token(token: str) -> Optional[User]`
  Decodes JWT token and returns the `User` object if valid.
- `create_api_key(name: str, user_id: str, scopes: List[str] = None, expires_days: Optional[int] = None) -> APIKey`
  Generates a production API key starting with `pdu_live_`.
- `verify_api_key(key: str) -> Optional[APIKey]`
  Validates API key token, increments `usage_count`, updates `last_used`.
- `revoke_api_key(key_id: str)`
  Deactivates an API key.
- `list_api_keys(user_id: str) -> List[APIKey]`
  Returns all active API keys for a user.
- `require_auth_middleware(request) -> Optional[User]`
  Extracts and verifies user from `Authorization: Bearer <token>` or `pdu-auth` cookie.

### `class Role`
Standard role constants:
- `Role.ADMIN = "admin"`
- `Role.USER = "user"`
- `Role.VIEWER = "viewer"`
- `Role.DATA_ENGINEER = "data_engineer"`
- `Role.DATA_ANALYST = "data_analyst"`
- `Role.ML_ENGINEER = "ml_engineer"`

### Decorators:
- `@require_auth(redirect_to="/login")`: Protects page routes; redirects unauthenticated users.
- `@require_role(*roles)`: Enforces that the authenticated user possesses at least one of the specified roles.
- `@require_api_key(scopes=None)`: Protects `@app.api()` endpoints using `pdu_live_...` API keys.

---

## 4. Tunnel & Port Forwarding

### `class TunnelManager(port: Optional[int] = None)`
Provides one-click public internet forwarding (like Gradio's `share=True`).

#### Methods:
- `start(port: Optional[int] = None) -> Optional[str]`: Creates tunnel and returns public URL.
- `stop()`: Terminates active tunnels and subprocesses.

---

## 5. Component Index

### Data Science & Machine Learning (`pydataui.components.data_science`)
- `DataFrameTable(df, max_rows=100)`: Interactive styled pandas DataFrame table.
- `PlotlyChart(figure, height=400)`: Embedded responsive Plotly figure.
- `MetricCard(title, value, format="", delta="", delta_type="neutral", icon="", description="")`: KPI card.
- `ModelMetrics(metrics: Dict[str, float])`: Grid of model evaluation cards.
- `ConfusionMatrix(matrix: List[List[int]], labels: List[str])`: Coloured confusion matrix.
- `FeatureImportance(features: Dict[str, float], title="Feature Importance")`: Horizontal bar chart.
- `PipelineStatus(steps: List[Dict[str, str]])`: Real-time DAG/pipeline stage monitor.
- `DataTimeline(events: List[Dict[str, str]])`: Audit and event timeline.
- `SchemaViewer(df=None, schema=None)`: Column dtypes, nulls, and uniques inspector.
- `SQLEditor(bind="", on_run="", rows=8, placeholder="")`: SQL query editor.
- `JSONViewer(data, max_height="400px")`: Collapsible JSON tree viewer.
- `FileDownload(filename, content, label="Download")`: Data URI file exporter button.
- `DataUpload(accept=".csv,.json", on_upload="")`: File drag-and-drop target.

### shadcn/ui Styled Components (`pydataui.components.shadcn`)
- `ShadButton(*children, variant="default", size="default", full_width=False)`
- `ShadCard(*children)` / `ShadCardHeader` / `ShadCardTitle` / `ShadCardDescription` / `ShadCardContent` / `ShadCardFooter`
- `ShadInput(placeholder="", type="text")`
- `ShadBadge(*children, variant="default")`
- `ShadAlert(*children, variant="default")`
- `ShadSeparator(orientation="horizontal")`
- `ShadProgress(value=0, max_val=100)`
- `ShadSkeleton()`
- `ShadSwitch(checked=False)`
- `ShadTable(*children)`
- `ShadSelect(*children)`
- `ShadTextarea(rows=4, placeholder="")`
- `ShadLabel(*children)`
- `ShadDialog(*children, open=False)`
- `ShadScrollArea(*children)`
- `ShadTabs(*children)`
- `ShadToast(*children)`
- `ShadAvatar(*children)`
- `ShadHoverCard(*children)`
- `ShadAccordion(*children)`
- `ShadSheet(*children, open=False, side="right")`

### Authentication Components (`pydataui.auth`)
- `LoginPage(logo=None, title="Sign In", subtitle="", redirect_to="/")`
- `UserMenu(user: Optional[User])`
- `APIKeyManager(keys: List[APIKey])`
- `AuthGuard(*children, redirect_to="/login")`

---

## 6. CLI Command Reference

```bash
# Initialize a new project from a starter template
pydataui new <project_name> [--template basic|dashboard|crud|ml-dashboard|data-pipeline|auth]

# Run local development server with auto-reload
pydataui dev [file] [--host 127.0.0.1] [--port 8000] [--reload]

# Run production server
pydataui run [file] [--host 0.0.0.0] [--port 8000] [--workers 4] [--share]

# Package for production and Docker containerization
pydataui build [file] [--output dist]

# Verify syntax and registered routes
pydataui check [file]

# Generate production API key
pydataui generate key --name "KeyName"

# Show installed version
pydataui version

# Open documentation
pydataui docs
```

---

## 7. System HTTP Routes

| Route | Method | Description |
|---|---|---|
| `/docs` | `GET` | Interactive Swagger UI |
| `/openapi.json` | `GET` | OpenAPI 3.0 specification |
| `/api` | `GET` | Catalog of all registered States and REST endpoints |
| `/api/{State}` | `GET` | Full state JSON |
| `/api/{State}` | `PUT` | Update state fields |
| `/api/{State}` | `DELETE` | Reset state to defaults |
| `/api/{State}/{method}`| `POST` | Execute a State method |
| `/api/auth/login` | `POST` | Authenticate user credentials, returns JWT token |
| `/api/auth/logout`| `POST` | Sign out |
| `/api/auth/me` | `GET` | Current user profile |
| `/api/auth/keys` | `GET`, `POST` | List or create API keys |
| `/_pdu/event/{State}/{method}` | `POST` | HTMX reactive SSR event |
| `/_pdu/static/htmx.min.js` | `GET` | Bundled local HTMX JavaScript |
| `/_pdu/static/pydataui.css` | `GET` | Bundled PyDataUI CSS |
| `/_pdu/health` | `GET` | Health check endpoint |
