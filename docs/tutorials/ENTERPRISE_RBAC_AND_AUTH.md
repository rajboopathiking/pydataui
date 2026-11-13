# Tutorial: Enterprise Authentication & Role-Based Access Control (RBAC)

In this tutorial, you will configure an enterprise-grade security architecture in PyDataUI. You will learn how to set up JSON Web Tokens (JWT), configure Role-Based Access Control (RBAC), hash passwords securely, protect routes with decorators, and manage machine-to-machine API keys.

---

## 🔒 Security Architecture Overview

```mermaid
sequenceDiagram
    participant User as Browser Client
    participant Auth as AuthManager (JWT)
    participant Guard as @require_role Decorator
    participant Page as Protected Route Handler

    User->>Auth: POST /_pdu/auth/login {username, password}
    Auth->>Auth: Verify PBKDF2 Password Hash
    Auth-->>User: Set-Cookie: pdu_session=<JWT_Token>; HttpOnly; SameSite=Lax
    User->>Guard: GET /admin/dashboard (Cookie attached)
    Guard->>Auth: Decode & Verify JWT Signature
    Auth-->>Guard: Decoded User {username: "alice", role: "admin"}
    alt Role matches "admin"
        Guard->>Page: Execute handler()
        Page-->>User: Render Admin Dashboard
    else Role insufficient (e.g. "viewer")
        Guard-->>User: 403 Forbidden / Redirect to Login
    end
```

---

## 📦 Step 1: Initialize the AuthManager

Create a file named `secure_app.py`:

```python
import pydataui as pdu
from pydataui.auth.manager import AuthManager
from pydataui.auth.models import Role, User
from pydataui.auth.decorators import require_auth, require_role, require_api_key

app = pdu.App(title="Secured Enterprise Portal", theme="slate")

# Initialize AuthManager with cryptographic secret and expiration
auth = AuthManager(
    app=app,
    secret_key="enterprise-secret-key-change-in-production",
    token_expiry_hours=12,
    cookie_name="pdu_auth_token"
)
```

---

## 👥 Step 2: Configure Roles and Register Users

PyDataUI provides built-in user models with hashed credentials:

```python
# 1. Define Hierarchical Roles
auth.add_role(Role(name="viewer", permissions=["read:reports"]))
auth.add_role(Role(name="analyst", permissions=["read:reports", "query:duckdb"]))
auth.add_role(Role(name="admin", permissions=["*"]))

# 2. Register Users with PBKDF2 / SHA-256 Hashing
auth.register_user(
    username="alice_admin",
    password="SuperAdminPassword123!",
    role="admin",
    email="alice@company.internal"
)

auth.register_user(
    username="bob_analyst",
    password="AnalystPassword456!",
    role="analyst",
    email="bob@company.internal"
)

auth.register_user(
    username="charlie_viewer",
    password="ViewerPassword789!",
    role="viewer",
    email="charlie@company.internal"
)
```

---

## 🛡️ Step 3: Protecting Routes with Decorators

PyDataUI decorators intercept requests before page rendering or action dispatch:

```python
# Public Homepage (Accessible by anyone)
@app.page("/")
def public_home():
    return pdu.Container(
        pdu.Heading("Welcome to Enterprise Data Hub", level=1),
        pdu.Text("Please sign in to access cluster telemetry and SQL workspaces."),
        pdu.Button("Sign In to Portal", on_click="/login", variant="default"),
        class_name="py-12 max-w-3xl"
    )

# Protected Route: Any Authenticated User
@app.page("/reports")
@require_auth(redirect_to="/login")
def reports_page(current_user: User):
    return pdu.Container(
        pdu.Row(
            pdu.Heading(f"Reports Hub (Welcome, {current_user.username})", level=1),
            pdu.Button("Log Out", on_click="/_pdu/auth/logout", variant="outline"),
            class_name="justify-between items-center mb-6"
        ),
        pdu.Card(
            pdu.Text("Daily ETL summary and data lake throughput metrics."),
            class_name="p-4"
        ),
        class_name="py-8 max-w-4xl"
    )

# Strictly Protected Route: Admin Role Only
@app.page("/admin/cluster")
@require_role("admin", redirect_to="/unauthorized")
def admin_cluster_page(current_user: User):
    return pdu.Container(
        pdu.Heading("Cluster Administration Console", level=1),
        pdu.Badge("Admin Access Granted", variant="secondary", class_name="mb-4"),
        pdu.Grid(
            pdu.Card(pdu.Text("Rebalance Shards"), class_name="p-4"),
            pdu.Card(pdu.Text("Manage Worker Nodes"), class_name="p-4"),
            columns=2,
            class_name="gap-4"
        ),
        class_name="py-8 max-w-4xl"
    )
```

---

## 🔑 Step 4: Machine-to-Machine API Keys

In addition to user browser sessions, data platforms frequently need automated ETL scripts and cron jobs to submit telemetry.

### Register an API Key
```python
api_key = auth.create_api_key(
    name="Airflow Pipeline Runner",
    role="analyst",
    expires_in_days=90
)
print("Generated API Key:", api_key.key_token)
```

### Protect REST Endpoints with `@require_api_key`
```python
from fastapi import Request

@app.api.post("/api/v1/metrics/ingest")
@require_api_key(required_role="analyst")
async def ingest_pipeline_telemetry(request: Request):
    payload = await request.json()
    # Process metrics securely
    return {"status": "success", "ingested": len(payload)}
```
External scripts pass the key via header:
```bash
curl -X POST https://your-server.com/api/v1/metrics/ingest \
  -H "X-API-Key: pdu_live_9f823a..." \
  -H "Content-Type: application/json" \
  -d '{"batch_id": 402, "records": 50000}'
```

---

## 📋 Security Best Practices Checklist

| Security Control | Implementation in PyDataUI |
| :--- | :--- |
| **Session Fixation Prevention** | Tokens regenerated upon every authentication event. |
| **Cookie Hardening** | `HttpOnly=True`, `SameSite=Lax`, and `Secure=True` in production HTTPS. |
| **Timing Attack Mitigation** | Password hash verification uses constant-time string comparisons (`hmac.compare_digest`). |
| **XSS & Injection Protection** | All dynamic component text is automatically HTML-escaped via `escape_html()`. |
| **CSRF Defense** | State mutating actions are bound to signed session contexts and HTMX request headers. |
