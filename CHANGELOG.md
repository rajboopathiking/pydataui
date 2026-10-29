# CHANGELOG

## [1.1.0] - 2026-10-29 - High-Performance Mobile & Native Architecture Release

- **Native Offline Parity (Standalone Mobile Default)**: Decoupled Standalone mode from Wi-Fi sync in `pydataui.shell.capacitor`. By default, builds omit the `server` block from `capacitor.config.json`, serving bundled assets (`assets/public/`) directly from device flash memory at `https://localhost/` with <150 ms cold start. Completely eliminates `net::ERR_CONNECTION_REFUSED` ("Web page not available") in Airplane mode and offline environments.
- **Automated Native Android Scaffolding**: Added `install_android_scaffolding()` which automatically installs `PyDataUIBridgePlugin.java`, `PyDataUIWebViewInterceptor.java`, and `MainActivity.java` into Android native projects during `pydataui mobile build`.
- **Standalone vs Live-Sync CLI**: Added `--standalone` (default: True) and `--live-sync` flags to `pydataui mobile build`.
- **Module Auto-Discovery in JNI Bridge**: Added entry point auto-discovery (`mobile_app`, `app`, `main`) in `pydataui.shell.bridge.JNIBridge.get_app()`, guaranteeing automatic app instance resolution inside Chaquopy APKs.
- **PEP 562 Lazy Package Imports**: Completely eliminated eager top-level dependency loading in `pydataui/__init__.py`. Top-level cold-start import time dropped from **562.89 ms** down to **10.68 ms** (**−98.1% / 52× faster**), cutting mobile Chaquopy startup by ~2–3 seconds while maintaining complete static typing and autocompletion via `TYPE_CHECKING`.
- **Component-Level Dirty Tracking & Partial SSR Re-rendering**: Added reactive mutation tracking (`_mark_dirty`, `is_dirty()`, `get_dirty_fields()`, `clear_dirty()`) and fluent event targeting (`target_to()`). Subtree searches via `find_component_by_id` render only modified component fragments rather than full-page `#pdu-root` replacements, with `X-PDU-Dirty` mutation telemetry.
- **Auto-Generated Minimal Payloads**: Eliminated global `hx-include="#pdu-root"` DOM serialization across buttons, cards, and containers. Form inputs are now scoped strictly to `hx-include="this"`, reducing network interaction payloads from tens of kilobytes down to bytes.
- **Mobile Mode Preset**: Added `mobile_mode=True` and `gzip=True` to `AppConfig` (and `PYDATAUI_MOBILE_MODE=1`). Automatically mounts Starlette `GZipMiddleware(minimum_size=500)` compressing responses by 70–85%, while completely stripping PWA service-worker and manifest boilerplate inside native mobile wrappers.
- **In-Process JNI Bridge (Chaquopy Direct ASGI Dispatch)**: Added native zero-socket in-process request routing (`pydataui.shell.bridge.dispatch_in_process`, `PyDataUIWebViewInterceptor.java`, and `PyDataUIBridgePlugin.java`). Captures `/_pdu/*` requests directly in native Android code, bypassing Uvicorn, port binding, and loopback TCP sockets for an extra 5–15 ms latency reduction.
- **Native Renderer Backend Prototype**: Added `pydataui.compiler.native` (`NativeRenderer`, `NativeWidgetNode`, `compile_native`) mapping PyDataUI components to Flutter (Flet) and BeeWare (Toga) widget trees for 60fps gestures and React Native-level parity.

## [1.0.0] - 2026-10-28 - Official Production / Stable Release

- **Graduation to Stable (v1.0.0)**: PyDataUI reaches official Production/Stable release maturity on PyPI with complete enterprise-grade full-stack features.
- **FastAPI First-Class Citizen**: Native ASGI sub-application mounting via `mount(api, app, path="/dashboard")` with complete route isolation, independent Swagger UI (`/dashboard/docs`), internal static sandboxing (`/_pdu/static/*`), and cryptographic session scoping (`pdu-session`).
- **Dual Developer Experience (DX)**: Declarative production component architecture (`App`, `State`, `DataTable`, `MetricCard`, `Modal`) or rapid procedural script mode (`import pydataui as ui; ui.title(); ui.button()`).
- **Zero-Touch Live Auto-Reload**: Headless Uvicorn ASGI factory reloading (`_app_factory()`) monitoring both workspace and parent directories, with automatic simulator iframe refresh.
- **Cross-Platform Mobile & Desktop**: Direct headless Android `.apk` and iOS `.ipa` packaging with automated local Wi-Fi LAN IP detection, plus Tauri 2.0 / OS native window runner (`--desktop`).
- **High-Throughput Compiled Engine**: Default FastAPI core with optional plug-and-play PyRustAPI engine (Tokio/Hyper) delivering sub-millisecond latencies and up to 34,000+ req/sec.

## [0.3.6] - 2026-10-28

- **True Live Auto-Reload**: Added dynamic ASGI factory reloading (`_app_factory()`) for `pydataui mobile preview` and `pydataui dev`, monitoring both parent directories and workspace roots.
- **Server Instance Lifecycle Tracking**: Unique random `boot_id` generated per server boot and exposed via `/_pdu/health`.
- **Mobile Simulator Live Refresh**: In-browser preview simulator automatically polls server health, reloads iframe on code change, and displays `🟢 Auto-Reload: ON` status with live toast banners.
- **Standalone Web & Phone Live Reload**: Automatic reload watcher injected during dev mode for direct browser views and physical phone testing via QR code.
- **Headless Mobile Pipeline**: Added automated local Wi-Fi LAN IP detection and direct `.apk` / `.ipa` packaging without Xcode or Android Studio GUI requirements.
- **FastAPI Mounting & Conflict Sandboxing**: Documented native ASGI delegation, route isolation, independent Swagger UI (`/dashboard/docs`), static sandboxing (`/_pdu/static/*`), and cryptographic session scoping.

## [0.3.5] - 2026-10-28

- Full Project URLs & PyPI display metadata: Homepage, Documentation, Repository, and Bug Tracker.
- Modernized Groovy DSL syntax in `android/app/build.gradle` and silenced deprecation warnings with `org.gradle.warning.mode=none`.
- Clean APK verification and ADB mobile device installation flow.

## [0.3.4] - 2026-10-28

- Robust Android Gradle builds: automated JDK 17/21 discovery (`find_java_home()`), explicit `-Dorg.gradle.java.home` routing to prevent Class 69 incompatibilities on Java 25+, and automatic Gradle `afterEvaluate` compileOptions override.
- Headless Android APK generation: dynamic patching of Capacitor 7's generated `JavaVersion.VERSION_21` down to `VERSION_17`.
- Enhanced `pydataui mobile install`: automatic `adb` discovery across Android SDK directories and clear detection of connected devices with actionable developer feedback.
- Clean stale APK handling: prevents false success reporting on failed Gradle compilation passes.

## [0.3.3] - 2026-10-28

- Add In-Browser Mobile Device Simulator (`/_pdu/preview`, `pydataui mobile preview`, `--mobile-preview`) with iPhone 15 Pro, Pixel 8, and iPad Mini frames, fast reload, and real physical device testing via instant QR code without Xcode or Android Studio.
- Add Progressive Web App (PWA) manifest and service worker generation (`/_pdu/manifest.json`, `/_pdu/sw.js`, `viewport-fit=cover`).
- Add Capacitor mobile integration with headless Android APK compilation (`pydataui mobile build android`) and direct device install (`pydataui mobile install android`).
- Add Tauri 2.0 native shell scaffolding and standalone desktop window runner (`pydataui run --desktop`).
- Add comprehensive Documentation Developer Guide for Markdown, HTML, and automated GitHub Pages deployment.
- Add `pydataui.templates` with analyst, data-quality, pipeline-operations, and ML-registry page templates.
- Add a deterministic static template gallery, sample data builders, and runnable four-page example app.
- Add developer HTML and CSS references covering rendering, attributes, escaping, tokens, class names, theme layers, and testing.
- Fix framework dark tokens so `.dark` and `[data-theme="dark"]` apply the intended values.
- Include request-body limits, upload handling, Markdown sanitization, and browser security test hardening.


## [0.2.1] — 2026-10-04 (source update)

- Add pluggable storage engine (`pydataui.storage`) supporting `MemoryStore` and high-performance `SQLiteStore` with Write-Ahead Logging (WAL) mode.
- Remove single-process isolation bottleneck: enable cross-process multi-worker support (`workers=4+`) and container volume sharing with zero external infrastructure.
- Add `Session.to_dict()` and `Session.from_dict()` for full state tree and data persistence across worker processes.
- Add `_UsersDictProxy`, `_ApiKeysDictProxy`, and `_UsersByUsernameProxy` to `AuthManager` for seamless transparent persistence on SQLite.
- Protect generated APIs, custom APIs, browser actions, and pages when auth is configured.
- Isolate REST state per signed session; remove implicit class-store synchronization.
- Add state action allowlists, API opt-out, private fields, typed/atomic inputs, and role gates.
- Disable public registration by default and reject caller-supplied roles.
- Hide password hashes; enforce key ownership/scopes; retain only API key digests.
- Use randomly salted password hashes and random default auth/session secrets.
- Rotate browser sessions at login, implement token/session logout, and reject inactive users.
- Wire per-session CSRF tokens into HTMX and protect cookie-bearing mutation endpoints.
- Escape authentication UI values and suppress production error details.
- Refuse to delete nonempty CLI build output directories.
- Add dispatcher regressions, optional Chromium coverage, and migration documentation.

See `docs/MIGRATION_0_2_1.md` and `docs/PRODUCTION_READINESS.md` for compatibility changes and deployment guides.
This source version has not been published to PyPI by this change.


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
