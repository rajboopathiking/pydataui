# From HTML, CSS, JavaScript & React to PyDataUI: The Rosetta Stone Guide

If you are a web developer who knows **HTML, CSS, JavaScript, React, or Redux**, or a Python developer looking to understand how PyDataUI works under the hood, this guide is your **Rosetta Stone**.

It breaks down every web concept side-by-side with PyDataUI and reveals the simple mechanics powering server-side rendering, reactivity, and zero-JS interactive dashboards.

---

## 1. Quick Concept Mapping: Web vs. PyDataUI

| Traditional Web / React Concept | What You Write in Web / React | PyDataUI Equivalent | Why PyDataUI Is Simpler |
| :--- | :--- | :--- | :--- |
| **HTML Tags** | `<h1>Title</h1>`, `<p>Text</p>` | `Heading("Title", level=1)`, `Text("Text")` | Pure Python objects; no template tags or strings. |
| **Direct HTML Tags** | `<h1>`, `<p>`, `<div>`, `<span>` | `H1("Title")`, `P("Text")`, `Div()`, `Span()` | Direct semantic tag classes available in `pydataui.components.html`. |
| **Flexbox & Grid Layouts** | `<div class="flex flex-row justify-between gap-4">` | `Row(justify="between", gap="4")` | Pythonic spatial layout shorthands (`Row`, `Col`, `Grid`). |
| **Component Props** | `<button disabled class="btn-primary">` | `Button("Label", variant="primary", disabled=True)` | Type-safe keyword arguments with IDE auto-complete. |
| **Local State (`useState`)** | `const [count, setCount] = useState(0)` | `s = state(count=0)` | Single procedural hook; no array destructuring or setters. |
| **Redux Store & Actions** | Actions + Reducers + Dispatch + Store (5 files) | `@s.action def increment(): s.count += 1` | Zero boilerplate; mutate Python variables directly. |
| **Event Handlers (`onClick`)** | `onClick={() => handleSave()}` | `on_click=handle_save` | Pass Python functions directly; no JS closures. |
| **AJAX / Fetch API** | `fetch('/api/save', { method: 'POST', body: ... })` | Built-in HTMX event wire protocol | Zero JavaScript written; automated DOM partial swaps. |
| **Forms & Validation** | React Hook Form + Zod / Yup schema | `ShadForm.from_pydantic(MyModel)` | Automatic form generation from Python Pydantic models. |
| **Tables & DataFrames** | TanStack Table + custom cell renderers | `DataTable(data=my_df)` | Universal sniffing for Pandas, Polars, DuckDB, Arrow. |
| **Dual Surfaces** | Browser only | Web Browser (`pydataui run`) + Terminal TUI (`pydataui run --tui`) | The exact same code runs in browser and SSH terminals. |

---

## 2. HTML vs. PyDataUI: The Markup Comparison

In PyDataUI, everything you can write in HTML has a direct, clean Python component:

### Headings and Text

```html
<!-- Traditional HTML -->
<h1>System Overview</h1>
<h2>Cluster Health</h2>
<p class="text-gray-500">All 8 worker instances operational.</p>
<code>pip install pydataui</code>
```

```python
# PyDataUI (High-Level Pythonic)
from pydataui import Heading, Text

Heading("System Overview", level=1)
Heading("Cluster Health", level=2)
Text("All 8 worker instances operational.", variant="muted")

# Or direct HTML semantic tags (pydataui.components.html):
from pydataui.components.html import H1, H2, P, CodeTag

H1("System Overview")
H2("Cluster Health")
P("All 8 worker instances operational.", class_name="text-gray-500")
CodeTag("pip install pydataui")
```

---

### Buttons and Inputs

```html
<!-- Traditional HTML -->
<input type="text" placeholder="Search logs..." required />
<button type="button" class="btn btn-primary" onclick="alert('Searching')">Search</button>
```

```python
# PyDataUI
from pydataui import Input, Button

Input(placeholder="Search logs...", required=True)
Button("Search", variant="primary", on_click=search_action)
```

---

### Layouts: Flexbox and Grid

In traditional web development, you write verbose CSS flexbox or Tailwind utility classes:

```html
<!-- Traditional CSS / Tailwind -->
<div style="display: flex; flex-direction: row; justify-content: space-between; align-items: center; gap: 1rem;">
  <h3>Fleet Status</h3>
  <span class="badge badge-success">Online</span>
</div>
```

```python
# PyDataUI (Using Row shorthand)
from pydataui import Row, Heading, Badge

Row(
    Heading("Fleet Status", level=3),
    Badge("Online", variant="success"),
    justify="between",
    align="center",
    gap="4"
)
```

For columns and multi-column grid layouts:

```html
<!-- Traditional CSS Grid (3 Columns) -->
<div class="grid grid-cols-3 gap-6">
  <div class="card">Card 1</div>
  <div class="card">Card 2</div>
  <div class="card">Card 3</div>
</div>
```

```python
# PyDataUI
from pydataui import Grid, Card, Text

Grid(
    Card(title="Node A", children=[Text("Load: 45%")]),
    Card(title="Node B", children=[Text("Load: 62%")]),
    Card(title="Node C", children=[Text("Load: 31%")]),
    columns=3,
    gap="6"
)
```

---

## 3. React & Redux vs. PyDataUI State: Side-by-Side

State management is where traditional React/Redux gets complicated. Let's compare a simple counter with an async API call.

### The React + Redux / Fetch Way (JavaScript)

In React, you have to manage client state, async fetch calls, loading spinners, and re-renders:

```javascript
// React (CountComponent.jsx)
import React, { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(false);

  async function handleIncrement() {
    setLoading(true);
    try {
      const res = await fetch('/api/increment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count })
      });
      const data = await res.json();
      setCount(data.newCount);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card p-4">
      <h2>Count: {count}</h2>
      <button 
        disabled={loading} 
        onClick={handleIncrement}
        className="btn btn-primary"
      >
        {loading ? 'Updating...' : 'Increment'}
      </button>
    </div>
  );
}
```

### The PyDataUI Way (Python)

In PyDataUI, state lives directly in Python on the server. **No JSON APIs, no fetch calls, no useEffect, no Redux boilerplate:**

```python
from pydataui import App, state, Container, Card, Heading, Button

app = App(title="Counter Demo")

# 1. State: Zero-Class Procedural Hook
s = state(count=0, loading=False)

# 2. Action: Mutates Python variables directly
@s.action
def increment():
    s.count += 1

# 3. View: Declarative Layout
@app.page("/")
def home():
    return Container(
        Card(
            Heading(f"Count: {s.count}", level=2),
            Button(
                "Increment",
                on_click=increment,
                variant="primary"
            )
        )
    )

if __name__ == "__main__":
    app.run(port=8000)
```

---

## 4. How PyDataUI Works Under the Hood (HTML, CSS, JS Lifecycle)

A common question from web developers is: **"If I don't write JavaScript, how does it update the page without a full reload?"**

Here is the exact step-by-step wire lifecycle:

```text
[ Browser ]                                       [ PyDataUI Server (Python) ]
     |                                                          |
     | ----- 1. Initial Page Load (GET /) --------------------> |
     |                                                          | App renders initial HTML
     | <---- Returns Full HTML Document (HTML + CSS + HTMX) --- | (Server-Side Rendered)
     |                                                          |
  [User Clicks "Increment" Button]                              |
     |                                                          |
     | ----- 2. HTMX Event POST (/_pdu/event/state/increment) ->|
     |          (Lightweight AJAX request in background)        |
     |                                                          | 1. Runs @s.action (s.count += 1)
     |                                                          | 2. Renders updated HTML fragment
     | <---- 3. Returns HTML Fragment with updated DOM -------- | (e.g. <h2>Count: 1</h2>)
     |                                                          |
  [HTMX Morphs DOM]                                             |
  Zero full-page refresh!                                       |
```

### 1. Initial Load: Server-Side Rendering (SSR)
When you navigate to `http://localhost:8000/`:
- PyDataUI evaluates the `@app.page` function on the server.
- It produces pure, clean HTML containing the pre-rendered UI.
- It injects Tailwind CSS and a lightweight bundled copy of **HTMX** (30KB).
- The browser paints the page instantly with **zero blank screen**, zero heavy React/Webpack JS bundles, and optimal Core Web Vitals (LCP < 100ms).

### 2. User Clicks a Button
When a user clicks a `Button(on_click=increment)`:
- PyDataUI automatically rendered that button as:
  ```html
  <button hx-post="/_pdu/event/s/increment" hx-target="#pdu-root" hx-swap="outerHTML">
    Increment
  </button>
  ```
- The bundled HTMX engine intercepts the click and sends a fast asynchronous HTTP POST request to the server.

### 3. Python Executes the Action
- The PyDataUI server receives the event.
- It restores the user's session state and calls your Python function `increment()`.
- Your Python code mutates `s.count += 1`.

### 4. DOM Morphing (No Page Reload)
- PyDataUI re-renders the page with the new state.
- It returns only the updated HTML fragment back to the browser.
- HTMX smoothly swaps the updated elements directly into the browser DOM in milliseconds.
- **Result:** The user experiences a slick Single-Page App (SPA) feel, but the developer writes 100% Python!

---

## 5. React Hooks vs. PyDataUI State Hooks

| React Hook | React Purpose | PyDataUI Equivalent |
| :--- | :--- | :--- |
| `useState(initialValue)` | Component-level reactive state | `s = state(val=initialValue)` |
| `useReducer(...)` | Complex state transitions | Methods on `class MyState(State): ...` |
| `useEffect(() => {}, [dep])`| Trigger side effects on state change | Put logic directly inside `@s.action` handlers |
| `useContext(...)` | Shared global state | `s = state(...)` accessible across all page functions |
| `useRef(...)` | DOM reference | `id="my-element"` or component `id` property |
| `useMemo(...)` / `useCallback`| Performance memoization | Server-side Python functions (executed on demand) |

---

## 6. CSS & Styling: How Styling Works in PyDataUI

You do **not** need to configure PostCSS, Webpack, or CSS Modules. PyDataUI supports three flexible styling approaches:

### 1. Built-in Semantic Props (Recommended)
Components have built-in props that automatically map to design tokens:

```python
Button("Save", variant="primary", size="lg")
Card(padding="lg", shadow="md", radius="lg", bordered=True)
Badge("Production", variant="success")
```

### 2. Tailwind Utility Classes
You can pass any standard Tailwind CSS class directly via `class_name`:

```python
from pydataui import Box, Text

Box(
    Text("Gradient Banner", class_name="text-white font-extrabold text-2xl"),
    class_name="bg-gradient-to-r from-blue-600 to-indigo-600 p-6 rounded-2xl shadow-xl"
)
```

### 3. Inline Styles
Pass inline CSS styles as a Python dictionary or raw string:

```python
Box(style={"min-height": "400px", "background-color": "#f8fafc"})
```

---

## 7. A Complete Real-World Example: AI Chatbot

Here is a full comparison of building an AI Chatbot with multiline input, suggestion chips, loading dots, and markdown rendering:

### The React Way:
- 1 Node project (`package.json`, `node_modules` ~300MB)
- React markdown library (`react-markdown`, `remark-gfm`)
- Syntax highlighter (`prismjs` or `highlight.js`)
- State management (`useState` or Zustand)
- Fetch / streaming logic with cancellation tokens
- CSS / Tailwind setup
- FastAPI or Express backend route (`/api/chat`)
- **Total: ~8-12 files and hundreds of lines of glue code.**

### The PyDataUI Way:
**Single file, 40 lines of pure Python:**

```python
import httpx
from pydataui import App, state, Container
from pydataui.components import Chat

app = App(title="Enterprise AI Copilot")

# 1. State
s = state(
    messages=[{"role": "assistant", "content": "Hello! How can I assist you today?"}],
    session_id="chat_001",
    loading=False
)

# 2. Async Controller
@s.action
async def handle_message(message: str = "", **kwargs):
    user_msg = (message or kwargs.get("message", "")).strip()
    if not user_msg:
        return

    s.messages.append({"role": "user", "content": user_msg})
    s.loading = True

    try:
        async with httpx.AsyncClient(base_url="http://127.0.0.1:8000", timeout=60.0) as client:
            resp = await client.post("/chat/invoke", json={"id": s.session_id, "message": user_msg})
            reply = resp.json().get("response", "No response.")
    except Exception as e:
        reply = f"Error: {e}"
    finally:
        s.loading = False

    s.messages.append({"role": "assistant", "content": reply})

# 3. View
@app.page("/")
def home():
    return Container(
        Chat(
            messages=s.messages,
            title="Copilot AI",
            subtitle="SLM Agent • Llama-3-8B",
            placeholder="Type your message... (Shift+Enter for newline)",
            on_send=handle_message,
            suggestions=["Check cluster health", "Summarize query logs", "Reset API token"],
            loading=s.loading
        ),
        max_width="lg",
        padding="lg"
    )

if __name__ == "__main__":
    app.run(port=8000)
```

Run it in your web browser:
```bash
pydataui run app.py
```
Or run the **exact same script** inside your terminal:
```bash
pydataui run --tui app.py
```

---

## 8. Summary: Why Developers Love PyDataUI

1. **No Build Steps**: No Webpack, Vite, npm, node_modules, or Babel. Just `pip install pydataui`.
2. **Instant Hot Reloading**: Edit your Python code and watch the browser update in real-time (`pydataui dev app.py`).
3. **No Redux / Fetch Boilerplate**: State updates directly in Python variables; HTMX morphs the DOM automatically.
4. **Data-Native**: Works out-of-the-box with Polars, Pandas, DuckDB, and PyArrow.
5. **Dual-Surface Execution**: The only framework where one file runs simultaneously as a high-performance Web app and a full Terminal UI (TUI).
