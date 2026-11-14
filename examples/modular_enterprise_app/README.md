# Enterprise Operations Hub - PyDataUI Modular Reference Architecture

This reference application demonstrates how to architect a production-grade, multi-page application with **PyDataUI** using clean separation of concerns inspired by React/Next.js.

It eliminates common developer confusion regarding state mutation, form serialization, and component organization.

---

## Architecture & Project Structure

A clean, un-messy PyDataUI application strictly isolates **State**, **Logic**, **Components**, and **Pages**:

```text
examples/modular_enterprise_app/
├── app.py                  # Main entrypoint: initializes App and registers page routes
├── state.py                # Pure reactive state definitions (Single Source of Truth)
├── actions.py              # Business logic & event mutation handlers (@s.action)
├── components/             # Reusable UI presentation components
│   ├── __init__.py         # Component exports
│   ├── layout.py           # AppShell, AppHeader, NavItem (shared visual chrome)
│   └── kpi_card.py         # Reusable analytical metric card with trend indicators
├── pages/                  # Page route definitions (View layer)
│   ├── __init__.py         # Page exports
│   ├── dashboard.py        # Analytics dashboard with live KPI grid & controls
│   ├── data_hub.py         # Tabular data management with DataTable & filters
│   ├── copilot.py          # AI Copilot chat interface
│   └── settings.py         # Configuration form with input controls
├── test_modular_app.py     # End-to-end integration test suite
└── README.md               # Architecture and developer guide
```

---

## Comparison: React vs Streamlit vs PyDataUI

| Dimension | React / Next.js | Streamlit | PyDataUI Modular Pattern |
| :--- | :--- | :--- | :--- |
| **State Management** | Redux, Zustand, `useState()` | Session State (`st.session_state`) | `pdu.state(...)` in `state.py` |
| **Mutations / Logic** | Actions, Reducers, API Handlers | Inline script logic | `@s.action` in `actions.py` |
| **Component Model** | JSX Functional Components | Procedural script commands | Composable Python Classes (`Component`) |
| **Re-rendering** | Virtual DOM reconciliation | Entire script re-runs top-to-bottom | Hyper-granular HTMX fragment swaps |
| **Form Serialization** | Controlled Inputs (`onChange`) | `st.form` + `st.form_submit_button` | Standard HTML Forms (`name="..."`) |
| **Multi-page Routing** | Next.js App Router (`/app/page.tsx`) | `pages/` directory conventions | Explicit `@app.page("/path")` decorators |

---

## The Golden Rules of PyDataUI Architecture

### 1. The Mandatory `name="..."` Rule for Forms
In HTML and HTMX, an `<input>` element **must have a `name="..."` attribute** to be serialized in HTTP POST payloads:

```python
# ❌ INCORRECT (Lacks name attribute, browser sends empty payload {})
pdu.Input(placeholder="Enter email", bind=s.email)

# ✅ CORRECT (name="email" ensures data is sent to the action)
pdu.Input(placeholder="Enter email", name="email", value=s.email)
```

When wrapped in a `pdu.Form(..., on_submit=save_settings)`, PyDataUI automatically maps the submitted form fields as keyword arguments to your action function:

```python
# actions.py
@settings_state.action
def save_settings(email: str = "", **kwargs):
    settings_state.email = email
```

### 2. StateVarRef vs Evaluated Values
When you pass a state variable into a component layout:
```python
pdu.Heading(s.count, level=2)
```
`s.count` is a **`StateVarRef`** (a reactive reference). When an action increments `s.count += 1`, PyDataUI identifies which DOM elements depend on `s.count` and automatically updates them over HTMX without reloading the entire page.

If you need the primitive Python value for math inside a non-action function, convert it explicitly with `int(s.count)` or `str(s.name)`.

### 3. Decouple Layout (`pages/`) from Logic (`actions.py`)
Never write raw business logic or database calls directly inside your page render functions. Pages should only describe **what the UI looks like**:

```python
# pages/dashboard.py
pdu.Button("Scale Up", on_click=scale_up_workers, variant="primary")
```

All logic belongs in `actions.py`:
```python
# actions.py
@dashboard_state.action
def scale_up_workers():
    dashboard_state.active_workers += 4
    dashboard_state.throughput_k = round(dashboard_state.throughput_k * 1.15, 1)
```

---

## Running the Application

### 1. Web Mode (Fast, Reactive Web Server)
```bash
python examples/modular_enterprise_app/app.py
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

### 2. Terminal UI Mode (Interactive Terminal Dashboard)
```bash
python examples/modular_enterprise_app/app.py --tui
```
Runs the same application in your terminal with rich keyboard navigation!

### 3. Running Automated Tests
```bash
python examples/modular_enterprise_app/test_modular_app.py
```
Validates:
- GET `/` (Dashboard KPI grid)
- GET `/data` (Data Hub table)
- GET `/copilot` (AI Chat)
- GET `/settings` (Settings form)
- Live HTMX action event triggering and state mutation
- Form submission with field serialization and server-side response rendering
