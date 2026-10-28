# Contributing to PyDataUI

Thank you for your interest in contributing to **PyDataUI**!  
We are excited to build the premier full-stack Python framework for data professionals together.

---

## 🛠️ Development Setup

### 1. Clone Repository & Setup Virtual Environment
```bash
git clone https://github.com/rajboopathiking/pydataui.git
cd pydataui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install editable development dependencies
pip install -e ".[all,dev]"
```

### 2. Run Test Suite
Ensure all tests pass before making any changes:
```bash
pytest -v
```

---

## 🏗️ Project Structure

```
pydataui/
├── __init__.py           # Package exports & version
├── app.py                # Main App class & HTTP lifecycle
├── config.py             # AppConfig & environment variables
├── state.py              # State, StateVar, StateVarRef, EventHandler
├── api.py                # Automatic REST API generator
├── tunnel.py             # Port forwarding manager (share=True)
├── session.py            # Session management & cookie encoding
├── event.py              # Event triggers & EventSpec
├── auth/                 # Authentication & authorization module
│   ├── manager.py        # AuthManager (JWT & API Keys)
│   ├── models.py         # User, Role, APIKey dataclasses
│   ├── state.py          # LoginState
│   ├── decorators.py     # @require_auth, @require_role, @require_api_key
│   └── components.py     # LoginPage, UserMenu, APIKeyManager, AuthGuard
├── cli/                  # CLI tools
│   ├── main.py           # pydataui commands
│   └── templates.py      # Starter project templates
├── compiler/             # SSR renderer & HTML templates
│   ├── renderer.py       # Renderer engine
│   └── templates.py      # Base HTML shell with Tailwind & HTMX
├── components/           # 80+ UI components
│   ├── base.py           # Base Component class & render pipeline
│   ├── shadcn.py         # shadcn/ui styled components
│   ├── data_science.py   # DataFrameTable, PlotlyChart, ML metrics, etc.
│   ├── layout.py         # Container, Flex, Grid, Stack, Box
│   ├── forms.py          # Button, Input, Select, Checkbox
│   └── ...
└── styling/              # Bundled assets
    ├── css/pydataui.css  # Framework stylesheet
    └── js/htmx.min.js    # Bundled HTMX JavaScript
```

---

## 🎨 Component Development Guidelines

When creating a new component:
1. Inherit from `Component` in `pydataui/components/base.py`.
2. Implement `_get_classes(self) -> List[str]` to return default Tailwind CSS utility classes.
3. If custom HTML structure is required, implement `render(self, state_snapshot=None) -> str`.
4. Ensure all child components and State variables are resolved via `self._render_children(state_snapshot)`.
5. Export the new component in `pydataui/components/__init__.py`.
6. Add unit tests in `tests/`.

---

## 🧪 Testing Guidelines

- PyDataUI tests are written using `pytest` and `anyio`.
- All tests must pass before submitting a pull request:
  ```bash
  pytest -v
  ```
- Any new features (components, auth logic, CLI options) must be accompanied by new test coverage.

### Browser Tests

`tests/test_browser_security.py` uses Playwright from the `browser` extra but
does not download Chromium. Point it at an installed Chromium-compatible
executable:

```bash
PYDATAUI_BROWSER_EXECUTABLE="/path/to/chrome-or-chromium" \
  pytest tests/test_browser_security.py -v
```

On macOS with EgoLite installed:

```bash
PYDATAUI_BROWSER_EXECUTABLE="/Applications/ego lite.app/Contents/MacOS/ego lite" \
PYDATAUI_REQUIRE_BROWSER=1 \
PYDATAUI_REQUIRE_REAL_STYLES=1 \
  pytest tests/test_browser_security.py -v
```

`PYDATAUI_REQUIRE_REAL_STYLES=1` requires the real Tailwind Play CDN stylesheet
and fails the run if it cannot load; without it, that one test skips. Most other
browser tests stub the CDN so they can run offline.

`PYDATAUI_BROWSER_CDP_ENDPOINT` can connect Playwright to a Chromium instance
already running with remote debugging on localhost. Without a browser the
tests skip; set `PYDATAUI_REQUIRE_BROWSER=1` to fail instead. CI installs the
`browser` extra and runs the browser suite with both requirement flags enabled.

---

## 📚 Documentation, Markdown & HTML Guidelines

PyDataUI documentation is built using **Material for MkDocs** and published to **GitHub Pages** via GitHub Actions.

For complete styling patterns and HTML/Markdown embedding rules, see [Documentation Developer Guide](docs/DOCS_DEVELOPER_GUIDE.md).

### 1. Previewing Docs Locally
Install documentation dependencies:
```bash
pip install mkdocs mkdocs-material pymdown-extensions
```
Start the live hot-reloading server:
```bash
mkdocs serve
```
Open `http://127.0.0.1:8000/` in your browser.

### 2. Markdown & HTML Rules
- **Markdown (`.md`)**: Use standard GFM, admonitions (`!!! note`), tabbed code blocks (`=== "Python"`), and Mermaid diagrams (````mermaid ... ````).
- **HTML (`.html`)**: Raw HTML tags are supported via `md_in_html`. When putting Markdown inside an HTML block (like `<div style="...">...</div>`), always add the `markdown="1"` attribute.
- **Navigation**: If you add a new `.md` document under `docs/`, register it in [`mkdocs.yml`](mkdocs.yml) under `nav:`.

### 3. Verify Before Committing
Run a strict build to ensure no broken links or orphaned pages:
```bash
mkdocs build --strict
```

### 4. GitHub Pages Deployment
- Merging or pushing to `main` with changes in `docs/**` or `mkdocs.yml` automatically triggers [`.github/workflows/deploy-docs.yml`](.github/workflows/deploy-docs.yml).
- GitHub Actions builds the site and pushes it to the `gh-pages` branch, serving it live at [https://rajboopathiking.github.io/pydataui/](https://rajboopathiking.github.io/pydataui/).

---

## 📦 Pull Request Process

1. Fork the repo and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Follow standard Python PEP 8 conventions.
3. Ensure no trailing whitespace and all imports are clean.
4. Run tests and verify exit code 0:
   ```bash
   pytest
   ```
5. Submit your Pull Request with a clear description of the feature or bugfix.
