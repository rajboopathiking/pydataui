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
python3 -m venv .venv
source .venv/bin/activate

# Install editable development & documentation dependencies
pip install --upgrade pip
pip install -e ".[dev,docs]"
```

### 2. Run Test Suite
Ensure all tests pass before making any changes:
```bash
pytest tests/ -q --ignore=tests/test_browser_security.py
```

### 3. Verify Documentation Site
PyDataUI uses **Material for MkDocs** for 100% pure Markdown documentation:
```bash
mkdocs serve
# Run strict build validation:
mkdocs build --strict
```

---

## 🏗️ Project Structure

```
pydataui/
├── __init__.py           # Package exports & version
├── app.py                # Main App class, HTTP lifecycle, and FastAPI mounting
├── config.py             # Global AppConfig & environment variables
├── state.py              # Reactive Proxy State, StateVarRef, EventHandler
├── tui.py                # Dual-engine Terminal UI (Rich & ASCII fallback)
├── api.py                # Automatic REST/OpenAPI route generator
├── session.py            # Session management & per-client isolation
├── event.py              # Event triggers & client-server RPC signals
├── auth/                 # Enterprise Auth (JWT, RBAC, API Keys)
│   ├── manager.py        # AuthManager
│   ├── models.py         # User, Role, APIKey dataclasses
│   └── decorators.py     # @require_auth, @require_role, @require_api_key
├── compiler/             # SSR renderer & HTML templates
│   ├── renderer.py       # AST compiler
│   └── templates.py      # Base HTML shell with Tailwind & HTMX
├── components/           # 80+ UI components
│   ├── base.py           # Base Component class & render pipeline
│   ├── shadcn.py         # Modern shadcn/ui primitives
│   ├── data_science.py   # Universal DataTable, PlotlyChart, ML metrics
│   ├── layout.py         # Container, Row, Col, Grid, Card
│   └── forms.py          # Button, Input, Select, Checkbox, Slider
└── styling/              # Bundled assets
    ├── css/pydataui.css  # Framework stylesheet
    └── js/htmx.min.js    # Bundled HTMX JavaScript
```

---

## 🎨 Component Development Guidelines

When creating a new component:
1. Inherit from `Component` in `pydataui/components/base.py`.
2. Implement `render(self, state_snapshot=None) -> str` to produce clean, accessible HTML.
3. Resolve dynamic state variables using `val.resolve(state_snapshot)` if applicable.
4. Export the new component in `pydataui/components/__init__.py` and `pydataui/__init__.py`.
5. Add unit tests in `tests/test_components.py` or a dedicated test file.

---

## 🧪 Testing Guidelines

- PyDataUI tests are written using `pytest` and `anyio`.
- All tests must pass before submitting a pull request:
  ```bash
  pytest tests/ -q --ignore=tests/test_browser_security.py
  ```
- **Browser tests**:
  ```bash
  pip install -e ".[browser]"
  python -m playwright install --with-deps chromium
  pytest tests/test_browser_security.py -v
  ```

---

## 📚 Documentation Guidelines

- **Pure Markdown**: All documentation in `docs/` must be pure Markdown (`.md`).
- **Brand Hygiene**: Never use legacy or personal project handles or names in code, examples, or documentation. Always use `pydataui` or `PyDataUI Platform`.
- **Strict Verification**: Always run `mkdocs build --strict` before submitting code.

---

## 📦 Pull Request Process

1. Fork the repo and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-feature
   ```
2. Follow standard Python PEP 8 conventions.
3. Ensure no trailing whitespace and all imports are clean.
4. Verify tests and docs:
   ```bash
   pytest tests/ -q --ignore=tests/test_browser_security.py
   mkdocs build --strict
   ```
5. Submit your Pull Request referencing any open issues.
