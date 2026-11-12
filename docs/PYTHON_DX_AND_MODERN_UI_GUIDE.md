# Modern Python DX & Commercial UI/UX Guide
## Eliminating React, Node & JS for Enterprise Internal Tools, AI Apps, and TUI

---

## 🎯 Executive Overview: The Python-First Promise

Historically, Python developers building data tools, LLM agents, or internal operations dashboards were caught in a dilemma:
1. **Low-code Python frameworks (Streamlit/Gradio)**: Fast prototypes, but brittle state, heavy rerun loops, rigid layouts, and difficult to customize for enterprise workflows.
2. **Full-stack JS/React (Next.js, Tailwind, Shadcn)**: Beautiful commercial-grade UX, but high complexity: Node/NPM build chains, state duplication between Python and TypeScript, hydration bugs, and double the maintenance.

**PyDataUI eliminates this trade-off.** 

It provides:
- **Server-Side Rendering (SSR) + HTMX reactive event delegation**: Instant sub-15ms HTML updates with zero user JavaScript.
- **Tailwind CSS + shadcn/ui design system**: Commercial, production-grade aesthetics out of the box.
- **Zero-Class Procedural State Hook (`state(**defaults)`)**: Eliminates boilerplate state classes.
- **Native Multi-Target Compilation**: The **exact same Python code** runs as:
  - **Production Web Application** (FastAPI SSR)
  - **Headless GPU / SSH Dashboard** (Rich Terminal TUI)
  - **Native Desktop App** (Tauri 2.0)
  - **Mobile App / Simulator** (Capacitor / PWA)

---

## ⚠️ The 5 Anti-Patterns & Learning Curve Traps

When developers transition from React or older frameworks, they often write awkward, high-friction Python code. Here is how to avoid the most common traps:

### 1. The `on_change` Two-Way Binding Trap
- **Anti-Pattern**: Attaching an `on_change` listener to every `Input` or `TextArea` to manually sync state.
- **PyDataUI Way**: In SSR and HTMX, forms and event handlers pass input values directly into the action arguments:
  ```python
  @s.action
  def submit_query(message: str = ""):
      s.response = f"Echo: {message}"
  ```

### 2. The `children=[...]` Keyword Nesting Trap
- **Anti-Pattern**: Passing lists to `children=[...]` like Flutter/React.
- **PyDataUI Way**: Components accept variable positional arguments `*children`:
  ```python
  # Clean & Pythonic
  Card(
      Heading("Overview", level=2),
      Text("Welcome to the operations center."),
      title="System Status"
  )
  ```

### 3. Static Class State Ceremony
- **Anti-Pattern**: Creating `class MyState(State):` with explicit getters and setters for small tools or scripts.
- **PyDataUI Way**: Use the zero-class procedural state hook `s = state(**defaults)` with `@s.action`.

### 4. Nested Card Chat Anti-Pattern
- **Anti-Pattern**: Rendering chat messages as stacked generic gray `Card` components with list comprehensions.
- **PyDataUI Way**: Use the high-level `Chat` macro primitive, which automatically renders commercial chat bubbles, avatar indicators, auto-scroll, and Enter-key sending.

### 5. Fragmenting Web and Terminal Logic
- **Anti-Pattern**: Writing separate scripts for Web (`app.py`) and Terminal (`cli.py`).
- **PyDataUI Way**: Write one app. Run it in the browser with `pydataui run app.py` or in the terminal with `pydataui tui app.py`.

---

## 💬 Pattern: Production-Grade AI Customer Support Chat

Here is the recommended production architecture for building LLM chatbots and agent support consoles:

```python
from pydataui import App, state, Container
from pydataui.components import Chat
import httpx

app = App(title="AI Customer Support")

# 1. Zero-Class Reactive State
s = state(
    messages=[
        {"role": "assistant", "content": "Hello! I am your AI Support Assistant. Ask me anything."}
    ],
    session_id="sess_001",
)

# 2. Asynchronous Message Dispatcher
@s.action
async def handle_chat(message: str = "", **kwargs):
    user_msg = message or kwargs.get("message", "").strip()
    if not user_msg:
        return

    # Instantly reflect user message in conversation
    s.messages.append({"role": "user", "content": user_msg})

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=120.0) as client:
            resp = await client.post(
                "/chat/invoke",
                json={"id": s.session_id, "message": user_msg}
            )
            resp.raise_for_status()
            reply = resp.json().get("response", "Thank you for reaching out.")
    except Exception as e:
        reply = f"Temporary service notice: {e}"

    # Push assistant response
    s.messages.append({"role": "assistant", "content": reply})

# 3. Clean Layout
@app.page("/")
def home():
    return Container(
        Chat(
            messages=s.messages,
            title="Customer Support AI",
            placeholder="Type your message and press Enter...",
            on_send=handle_chat,
        ),
        max_width="lg",
        padding="lg",
    )

if __name__ == "__main__":
    app.run(port=8000)
```

---

## 🖥️ Terminal User Interface (TUI) Integration

PyDataUI v1.2.0 includes a real-time Terminal UI runner powered by Rich. The exact same application above runs interactively in any remote SSH session or headless GPU cluster:

```bash
# Launch interactive terminal UI dashboard
pydataui tui app.py

# Single-shot render (for CI/CD logs or batch jobs)
pydataui tui --once app.py
```

### Interactive TUI Commands:
- **`1` – `N`**: Switch between auto-discovered pages instantly.
- **`<message>`** or **`input <text>`**: Send input directly to your chatbot or model.
- **`<action_name>`**: Trigger any registered `@s.action` function.
- **`set <key>=<value>`**: Update procedural state variables live.
- **`q`** / **`exit`**: Cleanly exit the session with a single command.

---

## 📊 Universal Tabular Sniffing for Data & Internal Tools

Internal tools revolve around tabular data. PyDataUI's `DataTable` accepts any Python data structure directly without manual conversion:

```python
from pydataui import DataTable
import duckdb, polars as pl, pandas as pd, pyarrow as pa
from pydantic import BaseModel

# 1. Polars
DataTable(pl.DataFrame({"model": ["Llama-3", "Mistral-7B"], "score": [79.6, 60.8]}))

# 2. Pandas
DataTable(pd.DataFrame({"lr": [1e-4, 3e-4], "loss": [0.42, 0.31]}))

# 3. DuckDB SQL
DataTable(duckdb.sql("SELECT 'H100' as gpu, 8 as count, 'ACTIVE' as status"))

# 4. PyArrow
DataTable(pa.table({"shard": ["shard_1.parquet", "shard_2.parquet"], "rows": [1000, 2000]}))

# 5. Pydantic Models & Dataclasses
class Worker(BaseModel):
    hostname: str
    load: float

DataTable([Worker(hostname="node-01", load=0.45), Worker(hostname="node-02", load=0.88)])
```

---

## 📐 Pythonic Spatial Layout Shorthands

Avoid verbose CSS and raw flex strings:

```python
from pydataui import Row, Col, Spacer, Card, Text

Row(
    Col(Card(Text("Sidebar")), span=4),        # 4/12 grid span
    Spacer(),                                  # Auto-flex expanding spacer
    Col(Card(Text("Main Dashboard")), width="1/2"), # 50% fraction width
    gap="6",
    align="start"
)
```

---

## 📱 Multi-Target Deployment Reference

| Target | Command | Technology |
| :--- | :--- | :--- |
| **Web Dev** | `pydataui dev app.py` | FastAPI + Live Reload + HTMX |
| **Web Prod** | `pydataui run app.py --workers 4` | Uvicorn ASGI behind NGINX |
| **Terminal TUI** | `pydataui tui app.py` | Rich ANSI/ASCII Engine |
| **Desktop App** | `pydataui desktop dev app.py` | Tauri 2.0 Rust Shell |
| **Mobile App** | `pydataui mobile dev app.py` | Capacitor / Android / iOS |
