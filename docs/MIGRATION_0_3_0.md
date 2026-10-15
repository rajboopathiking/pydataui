# PyDataUI v0.3.0 — Migration & Developer Experience Guide

PyDataUI v0.3.0 modernizes the framework backend to standard **FastAPI / Starlette ASGI** by default, introduces **native mounting inside existing FastAPI applications**, provides a **Streamlit-like simplified developer experience (`import pydataui as ui`)**, and adds **advanced Python-first components (`Markdown`, `CodeEditor`, `Chat`)** while maintaining **100% backward compatibility** with all existing PyDataUI code.

---

## 🚀 Key Improvements in v0.3.0

1. **FastAPI as Default Backend**:
   - PyDataUI applications now run on standard FastAPI / Starlette ASGI by default (`App()`).
   - Zero compilation or Rust toolchain requirements for default installation.
   - Native integration with standard ASGI servers: Uvicorn, Gunicorn, Hypercorn.

2. **Optional PyRustAPI Backend**:
   - For hyper-performance workloads, PyRustAPI remains fully supported as an optional backend:
     ```python
     app = App(backend="pyrustapi")
     ```
   - Installable via `pip install "pydataui[pyrustapi]"`.

3. **Native Mounting Inside Existing FastAPI Applications**:
   - Seamlessly embed reactive PyDataUI dashboards, admin portals, and data workflows directly inside an existing FastAPI application:
     ```python
     from fastapi import FastAPI
     from pydataui import App, mount

     api = FastAPI(title="Enterprise API")
     dashboard = App(title="Admin Dashboard")

     # Mount dashboard at /dashboard
     mount(api, dashboard, path="/dashboard")
     # or dashboard.mount_to(api, path="/dashboard")
     ```
   - Preserves mount path prefixes for static assets, HTMX fragments, and reactive event callbacks.

4. **Simplified Developer Experience (`import pydataui as ui`)**:
   - Build complete interactive apps with simple procedural scripts:
     ```python
     import pydataui as ui

     ui.title("Sales Intelligence Dashboard")
     ui.metric("Revenue", "$48,250", change="+14.2%")
     ui.button("Refresh Pipeline", on_click=lambda: print("Refreshing..."))

     if __name__ == "__main__":
         ui.run()
     ```
   - Regular Python functions can be passed directly as `on_click` callbacks without requiring custom state classes or JavaScript.

5. **Advanced Python-First Components**:
   - `Markdown`: Render rich markdown with code fences and tables without client-side dependencies.
   - `CodeEditor`: Interactive syntax highlighting container with line numbers, copy-to-clipboard, and optional Python change callback.
   - `Chat`: Conversational UI for AI agents, UnifiedNexus, and LangGraph with user/assistant bubbles and input dispatching.

6. **Ecosystem Compatibility**:
   - Seamless co-hosting with LangGraph / LangChain async streaming endpoints.
   - Native Pydantic validation on custom API endpoints (`@app.api("/endpoint", method="POST")`).
   - Pandas and Polars DataFrame support in `ui.dataframe()`.

---

## 📦 Upgrading to v0.3.0

Install or upgrade PyDataUI:

```bash
pip install --upgrade pydataui
```

To include optional PyRustAPI backend:
```bash
pip install --upgrade "pydataui[pyrustapi]"
```

To include full data science and sharing tools:
```bash
pip install --upgrade "pydataui[all]"
```

---

## 🛠️ Code Examples

### 1. Mounting Inside an Existing FastAPI Microservice

```python
from fastapi import FastAPI
from pydataui import App, mount
from pydataui.components import Container, Heading, Text

api = FastAPI(title="Payment Gateway API")

@api.get("/api/v1/payments")
def list_payments():
    return [{"id": "pay_101", "amount": 250.0}]

# Create PyDataUI dashboard
dash = App(title="Gateway Operations")

@dash.page("/")
def ops_home():
    return Container(
        Heading("Gateway Operations Console"),
        Text("Real-time monitoring of transactions")
    )

# Mount dashboard
mount(api, dash, path="/operations")

# Run with standard uvicorn
# uvicorn main:api --reload
```

### 2. Streamlined AI Chatbot with LangGraph or Gemini

```python
import pydataui as ui

messages = [
    {"role": "assistant", "content": "Hello! I am your AI assistant. How can I help?"}
]

def on_message_send(message: str):
    messages.append({"role": "user", "content": message})
    # Process with LangGraph or LLM here
    messages.append({"role": "assistant", "content": f"Echo: {message}"})

ui.title("AI Assistant")
ui.chat(messages=messages, on_send=on_message_send)

if __name__ == "__main__":
    ui.run()
```

---

## 🛡️ Backward Compatibility

All existing PyDataUI code written for v0.2.1 and v0.2.2 continues to work with zero code modifications:
- Existing `State` classes, event handlers, and public/private variables remain 100% compatible.
- Automatic REST API generation (`/api/{State}`) and Swagger UI (`/docs`) work out of the box.
- Authentication, RBAC, session cookies, and CSRF protection are preserved.
- CLI commands (`pydataui run`, `pydataui new`) operate with the modern FastAPI engine.
