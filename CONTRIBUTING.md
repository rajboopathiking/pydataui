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
