> **0.2.1:** Read [the migration guide](MIGRATION_0_2_1.md) for changed defaults,
> registration, protected routes, CSRF, key storage, and session lifetimes.

# Authentication, Authorization & API Keys Guide

PyDataUI provides a built-in enterprise authentication system designed for data platforms, analytics portals, and automated ETL pipelines.

---

## 1. Core Architecture

PyDataUI's auth module (`pydataui.auth`) supports:
- **Session & JWT Authentication**: Sign in via web form or REST API to obtain signed JWT tokens.
- **Role-Based Access Control (RBAC)**: Assign roles to users and enforce role permissions on pages and endpoints.
- **Production API Keys (`pdu_live_...`)**: Generate scoped API keys for Airflow, Prefect, Cron jobs, and external data consumers.
- **Zero Heavy Dependencies**: Uses standard library `hashlib.pbkdf2_hmac` for password hashing and `PyJWT` for JWT signing.

---

## 2. Setup & Configuration

```python
from pydataui import App
from pydataui.auth import AuthManager, Role

app = App(title="Corporate Analytics")
auth = AuthManager(
    secret_key="your-secure-random-secret-key-min-32-chars!",
    token_expire_hours=24
)

# Seed initial users
admin = auth.add_user(
    username="admin",
    password="SuperSecurePassword123!",
    email="admin@company.com",
    roles=[Role.ADMIN, Role.DATA_ENGINEER]
)

analyst = auth.add_user(
    username="jane",
    password="JanePassword456!",
    email="jane@company.com",
    roles=[Role.DATA_ANALYST]
)

# Attach auth routes and handlers to app
app.setup_auth(auth)
```

Calling `app.setup_auth(auth)` automatically mounts the following REST endpoints:
- `POST /api/auth/login` → Authenticates credentials, returns `{ "token": "<jwt>" }`
- `POST /api/auth/logout` → Invalidate session
- `GET /api/auth/me` → Returns user profile and assigned roles
- `POST /api/auth/register` → Register new user account
- `GET /api/auth/keys` → List user's active API keys
- `POST /api/auth/keys` → Generate a new API key
- `DELETE /api/auth/keys/{key_id}` → Revoke an API key

---

## 3. Pre-Built UI Components

PyDataUI includes ready-to-use authentication components styled with Tailwind CSS:

### `LoginPage`
```python
from pydataui.auth import LoginPage

@app.page("/login")
def login_view():
    return LoginPage(
        title="Enterprise Data Portal",
        subtitle="Sign in with your team credentials",
        redirect_to="/"
    )
```

### `UserMenu`
Renders the authenticated user's avatar, username, role badges, and an instant logout button:
```python
from pydataui.auth import UserMenu

@app.page("/")
def dashboard():
    return Container(
        Flex(
            Heading("Dashboard"),
            UserMenu(current_user.get()),
            justify="space-between", align="center"
        )
    )
```

### `APIKeyManager`
Provides a complete UI for listing keys, generating new keys, and revoking keys:
```python
from pydataui.auth import APIKeyManager

@app.page("/settings/keys")
def keys_page():
    user = auth.require_auth_middleware(request)
    keys = auth.list_api_keys(user.id) if user else []
    return Container(
        APIKeyManager(keys=keys)
    )
```

### `AuthGuard`
Conditionally renders child components only if the session is authenticated:
```python
from pydataui.auth import AuthGuard

@app.page("/secret-reports")
def secret_view():
    return AuthGuard(
        Container(Heading("Confidential Sales Projections")),
        redirect_to="/login"
    )
```

---

## 4. Protecting Routes & Endpoints

### Protecting Pages with `@require_auth` & `@require_role`
```python
from pydataui.auth import require_auth, require_role, Role

@app.page("/admin-console")
@require_auth(redirect_to="/login")
@require_role(Role.ADMIN)
def admin_panel(request):
    return Container(Heading("Administrator Console"))
```

### Protecting API Endpoints with `@require_api_key`
```python
from pydataui.auth import require_api_key

@app.api("/api/warehouse/sync", method="POST")
@require_api_key(scopes=["write"])
def trigger_sync(request):
    # Executed only if valid API key with 'write' scope is supplied
    return {"status": "sync_triggered"}
```

---

## 5. API Key Management via CLI

Generate API keys directly from the terminal without opening a browser:

```bash
pydataui generate key --name "AirflowDAG-DailyIngest"
```
Output:
```
🔑 Generated PyDataUI API Key:
   Name:   AirflowDAG-DailyIngest
   Token:  pdu_live_819dd41a93870327fdc57311d0080755
   Header: Authorization: Bearer pdu_live_819dd41a93870327fdc57311d0080755
```

---

## 6. Calling Protected Endpoints with Curl / Python

### With API Key:
```bash
curl -H "Authorization: Bearer pdu_live_819dd41a93870327fdc57311d0080755" \
     http://localhost:8000/api/warehouse/sync
```

### With JWT Token:
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"SuperSecurePassword123!"}' | jq -r .token)

# 2. Access protected endpoint
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me
```
