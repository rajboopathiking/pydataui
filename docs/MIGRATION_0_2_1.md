# PyDataUI 0.2.1: security and session-isolation migration

This source release fixes the vulnerabilities reproduced against commit
f77d21b. Install this checkout with `python -m pip install -e '.[dev]'`.
The version in this checkout is not a claim that 0.2.1 has been published on PyPI.

## Authentication and route protection

```python
from pydataui import App, AuthManager
from pydataui.auth import LoginPage, current_user
from pydataui.components import Heading

app = App(cookie_secure=True)  # HTTPS deployment; leave False for local HTTP
# Set PYDATAUI_AUTH_SECRET to a random secret of at least 32 bytes.
auth = AuthManager()
auth.add_user("alice", "replace-with-a-strong-password")
app.setup_auth(auth)

@app.page("/login")
def login():
    return LoginPage()

@app.page("/")
def dashboard():
    return Heading(f"Welcome, {current_user.username}")

@app.page("/about", public=True)
def about():
    return Heading("Public information")

@app.api("/admin/status", roles=("admin",))
def admin_status():
    return {"status": "ok"}
```

When auth is configured, generated state APIs, custom `app.api` routes, pages,
and browser events require authentication by default. `/login` is public;
other public pages/APIs must explicitly set `public=True`. Static files, health,
Swagger/OpenAPI, and CSRF bootstrap remain public. Do not put secrets in route
metadata or defaults. `State.__roles__` restricts state APIs/events; page roles
protect page access, not actions belonging to unrelated states.

Registration is disabled by default. `setup_auth(auth, allow_registration=True)`
enables ordinary-user registration; callers cannot assign roles. Assign roles
through trusted server code. API key management requires user sign-in, not an
API key. Key scopes are `read` and `write`; a read key cannot mutate state or
call actions. Key deletion is limited to the owner.

## Passwords, tokens, and keys

Password hashes use PBKDF2-SHA256 with 600,000 iterations and a random per-user
salt. Legacy fixed-salt hashes are deliberately not accepted: recreate demo
accounts/reset passwords when migrating any custom persistence.

AuthManager defaults to a random process-local signing secret. Set
`PYDATAUI_AUTH_SECRET` for stable configuration. JWT verification checks active
users and logout revokes the token within this manager. Raw API keys are returned
only when created; the manager retains SHA-256 digests and listing returns metadata.
Copy new keys once; existing in-memory keys must be recreated after restart.

Browser login rotates the signed session cookie and stores the token server-side;
no authentication token is serialized into UI state. Logout deletes the session.
Cookies have HttpOnly and SameSite=Lax; enable `cookie_secure=True` under HTTPS.

## State, APIs, and inputs

Cookie-less REST calls create isolated sessions. Keep the returned `pdu-session`
cookie to continue state. They no longer read/write shared class state. Two users
(or two browser contexts) never implicitly share a state instance.

```python
from pydataui import State

class EvaluationState(State):
    __actions__ = ("evaluate",)  # Only this user method is remotely callable
    __private_fields__ = ("connection_string",)
    __readonly_fields__ = ("result",)
    __input_fields__ = ("threshold",)
    threshold: float = 0.5
    result: str = ""
    connection_string: str = ""

    def evaluate(self):
        self.result = f"Threshold: {self.threshold}"
```

`State.to_dict()` and catalogs exclude declared private fields and common secret
field names (password, password_hash, token, access_token, refresh_token, api_key,
secret, secret_key). `to_dict(include_private=True)` is only for trusted server code.
Use explicit private declarations for other sensitive fields.

`__api__ = False` keeps a state off generated REST endpoints; events still work.
`App(auto_api=False)` disables generated state endpoints globally. LoginState is
not exposed as REST state. Private methods and framework helpers cannot be called
through dynamic routes. By default public user methods and reset remain actions
for compatibility; set `__actions__` to explicitly narrow that list. This action
allowlist does not validate the business safety of your method implementation.

Inputs are validated against declared types using Pydantic. Unknown/read-only
fields are rejected by REST PUT. Browser events update only the targeted state's
editable fields; they cannot write fields across every registered state. Declare
`__input_fields__` to limit form input. Server-written results need
`__readonly_fields__` or omission from `__input_fields__`.

## CSRF and errors

Full HTML pages include a per-session CSRF token. HTMX inherits X-CSRF-Token
from the body automatically. Browser events require that token. Cookie-bearing
REST mutations also require it; bearer-token clients are exempt.

For a custom fetch or a cookie-based API client, GET `/_pdu/csrf`, retain its
Set-Cookie value, and send its returned token as X-CSRF-Token on mutations.
Login rotates the session: fetch a fresh token afterward. Do not use the
pre-login token after rotation. Existing cookies must not be reused with another
signed-in user's bearer token.

Production error responses omit traceback/exception details. `App(debug=True)`
shows details for local debugging. Full-page rendering failures return HTTP 500;
event failures retain an inline generic action-error banner.

## Verification

```sh
python -m pip install -e '.[dev]'
python -m pytest -q
# Optional real-browser test:
python -m pip install -e '.[dev,browser]'
python -m playwright install chromium
python -m pytest -q tests/test_browser_security.py
```

## Pluggable Storage & Multi-Worker Scaling

PyDataUI v0.2.1 includes a zero-infrastructure SQLite WAL storage engine (`pydataui.storage`):
- **MemoryStore**: Ultra-fast default storage for single-worker processes and unit tests.
- **SQLite WAL Store**: High-concurrency persistent cross-process storage using standard library `sqlite3` with Write-Ahead Logging (WAL) mode. Multiple worker processes (`workers=4+`) and container replicas sharing a disk volume share sessions, registered users, API keys, and token revocations with zero external Redis or database services.
- Configure via `App(storage="sqlite:///path/to/storage.db")` or `export PYDATAUI_STORAGE="sqlite:///path/to/storage.db"`. When `workers > 1`, PyDataUI auto-configures SQLite WAL storage.

## Remaining limitations

These fixes are not a complete security audit. Login throttling, identity-provider
integration, compiled Tailwind assets, background jobs, large-data table behavior,
and a full browser/platform verification matrix still need work. The runtime
Tailwind CDN remains in the UI shell; do not claim an offline production bundle.
