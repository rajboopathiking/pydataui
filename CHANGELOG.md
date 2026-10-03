# CHANGELOG

## [0.1.1] — 2024-10-03

### 🐛 Critical Bug Fixes

#### HTMX not executing in browser (UI not responding)
- **Root cause:** `pyrustapi`'s `Response(content=string)` wraps the string body in JSON
  double-quotes when `Content-Type: application/javascript`. The browser received
  `"(function...)()"` — a JSON string literal — instead of executable JavaScript.
  HTMX silently failed to initialise, so no button clicks produced any network requests.
- **Fix:** Changed static file serving in `_setup_internal_routes` to use
  `StreamingResponse(iter([bytes_content]))` for all `.js` and `.css` files.
  `StreamingResponse` passes raw bytes to pyrustapi's Rust core unchanged, preserving
  the correct content.
- **Files changed:** `pydataui/app.py`

#### Buttons not wiring up (`hx-include` crash)
- **Root cause:** `_get_event_htmx_attrs` defaulted to
  `hx-include="closest form, input, select, textarea"`. HTMX's `closest` modifier
  expects a single CSS selector. With a comma-separated list the function returned
  `null` for elements not inside a `<form>`, causing a fatal JS `TypeError` on click.
- **Fix:** Changed default to `hx-include="#pdu-root"`. Since every PyDataUI page
  wraps content in `<div id="pdu-root">`, HTMX finds it immediately and collects all
  named inputs inside it without errors.
- **Files changed:** `pydataui/components/base.py`

### ✨ New Features

#### REST API catalog at `/api`
- `GET /api` and `GET /api/` now return a JSON catalog listing all registered states,
  their fields, methods, default values, and both REST endpoint URLs.

#### Dual REST route pattern
- All state endpoints are now accessible via both
  `/api/{StateName}` (short form) and `/api/state/{StateName}` (legacy form).

#### Swagger UI on both `/docs` and `/api/docs`
- Both routes serve the interactive Swagger UI directly (no redirect).
- Both `/openapi.json` and `/api/openapi.json` return the full OpenAPI schema.

#### Early API endpoint registration
- State REST endpoints are now registered in `App.__init__` (not only on `app.run()`),
  so they are available immediately after creating the `App` object.

#### Local HTMX bundle with CDN fallback
- HTMX is bundled locally at `pydataui/styling/js/htmx.min.js` and served via
  `/_pdu/static/htmx.min.js`.
- Template includes `onerror` CDN fallback to `cdn.jsdelivr.net` for offline safety.

#### Robust body parsing in event handler
- Added `urllib.parse.parse_qs` fallback in `_handle_event` to parse
  `application/x-www-form-urlencoded` bodies (what HTMX sends for `hx-vals`).
- `pyrustapi`'s `request.json()` raises an exception for urlencoded bodies — this is
  now caught silently and the parse_qs path handles it instead.

#### Single-parameter argument remapping
- When HTMX sends `id=1` (from `hx-vals`) but the method signature uses `user_id`,
  the framework automatically remaps the single kwarg to the single accepted parameter.

#### Enhanced `APIGenerator`
- Added `_registered_states` set to prevent double-registration of routes.
- Added `_sync_to_class_store` for stateless REST calls to propagate changes to the
  shared class-level store.
- REST responses now include `Set-Cookie` headers to start/continue sessions.

### 🛠 Improvements

- `pyproject.toml`: Added `"styling/js/*.js"` to `package-data` so `htmx.min.js` is
  included when the package is installed via pip.
- `static_handler` now matches by file extension (`.js`, `.css`) instead of exact
  filename, enabling future additional static assets.
- State auto-update loop in `_handle_event` now only updates fields that exist in the
  state's declared `get_state_vars()` to prevent accidental property injection.

### 🧪 Tests

- Added `tests/test_bff_and_events.py` with 1 async integration test covering:
  - Static JS/CSS serving
  - Page rendering with correct HTMX attributes
  - SSR fragment update on event
  - API catalog, Swagger docs, OpenAPI spec
  - State CRUD REST endpoints (GET, POST method, GET field, PUT, DELETE)

---

## [0.1.0] — 2024-10-02

### Initial Release

- PyDataUI full-stack framework with pyrustapi backend
- 70+ production-ready components
- Reactive state management with `State`
- SSR + HTMX event system
- Automatic REST API for all states
- Multi-page routing
- Session management
- CLI (`pydataui new`, `pydataui dev`, `pydataui run`)
- Examples: counter, todo, CRUD, dashboard, hello world
- Full test suite
