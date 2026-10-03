# PyDataUI Troubleshooting & Architecture Guide

A definitive guide to diagnosing, resolving, and understanding UI responsiveness, reactivity, and distinguishing **Framework-Level Issues** from **Application/Usage-Level Issues**.

---

## 1. How PyDataUI Reactivity Works

PyDataUI combines **Rust Tokio/Hyper** (`pyrustapi`), **HTMX** (reactive SSR), **Tailwind CSS**, and **shadcn/ui**:

```
┌────────────────────────────────────────────────────────┐
│                      Client Browser                    │
│                                                        │
│  User clicks button or changes input                   │
│  HTMX intercepts event (hx-post, hx-trigger="click")   │
│  Serializes all form inputs via `hx-include="#pdu-root"`│
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP POST /_pdu/event/{State}/{method}
                           │ Body: application/x-www-form-urlencoded / JSON
                           ▼
┌────────────────────────────────────────────────────────┐
│                   pyrustapi Server Core                │
│                                                        │
│  1. Restores Session from Cookie (`pdu-session`)       │
│  2. Deserializes form fields into State variables      │
│  3. Invokes state method: `State.method(**kwargs)`     │
│  4. Re-renders page fragment: `render_fragment()`      │
│  5. Returns HTML with updated state values (200 OK)    │
└──────────────────────────┬─────────────────────────────┘
                           │ HTTP 200 OK (HTML fragment)
                           ▼
┌────────────────────────────────────────────────────────┐
│                      Client Browser                    │
│                                                        │
│  HTMX swaps `#pdu-root` innerHTML with new HTML       │
│  Tailwind applies updated styles instantaneously       │
│  DOM reflects mutated State without full page reload   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Framework vs. Usage Diagnostic Matrix

| Symptom | Layer | Root Cause | Resolution |
| :--- | :--- | :--- | :--- |
| **DevTools Console: `TypeError: Cannot read property of undefined` in `htmx.min.js`** | **Framework** | Selector missing or invalid target (e.g. `closest form` when not in `<form>`). | Fixed in v0.2.0: Unified `hx-include="#pdu-root"`. |
| **Network Tab: 404 on `/_pdu/static/htmx.min.js` or `.css`** | **Framework** | Static route handler only handling root files or missing MIME type. | Fixed in v0.2.0: Streaming response with 18 MIME types and subfolder routing. |
| **Black transparent overlay blocks clicks to inputs/buttons** | **Framework** | Backdrop z-index stacking above modal dialog card. | Fixed in v0.2.0: Backdrop at `z-index: 1`, content strictly at `z-index: 10`. |
| **Server prints HTTP 500 without application traceback** | **Framework** | Method invocation or page render lacked error boundaries. | Fixed in v0.2.0: Error boundaries return `#pdu-action-error` toast instead of 500. |
| **Clicking button does not send any network request** | **Usage** | Button lacks `on_click` or called method with parentheses: `on_click=State.save()` instead of `on_click=State.save`. | Pass method reference: `on_click=State.save`. |
| **Form values are not saved / input value is empty on submit** | **Usage** | Input missing `bind` or `name`: `<input>` without `name` cannot be serialized by HTML/HTMX. | Add `bind=State.my_var` or `name="my_var"`. |
| **State updates on server but UI displays old data** | **Usage** | Referenced variable directly `my_var` instead of State class reference `State.my_var`. | Use `Heading(State.count)` instead of reading `inst.count`. |
| **Changes not reflected after code edits** | **Usage** | Running from different Python environment with old PyDataUI package. | Ensure `pip install -e .` is installed in your active Python env. |

---

## 3. Framework-Level Guarantees (PyDataUI v0.2.0)

1. **Zero Client-Side JavaScript Required**:
   Data developers never write JavaScript. All interactivity is declaratively compiled to HTMX attributes.

2. **Self-Healing Error Boundaries**:
   If an exception occurs in your state method (e.g., database connection failure, validation error):
   * The server **never crashes** with HTTP 500.
   * Full traceback is logged to your terminal console.
   * The UI remains interactive and displays an alert toast banner (`#pdu-action-error`) on the screen.

3. **Safe Multi-Environment Static Asset Serving**:
   Static assets (`htmx.min.js`, `pydataui.css`, SVGs, fonts) are served with `StreamingResponse` to prevent Rust string-escaping and include CDN fallback `onerror` handlers.

4. **Descriptor & Falsy Binding Safety**:
   `bind=State.field` safely retains the descriptor binding even when initial state values are empty strings `""`, `0`, or `False`.

---

## 4. Usage Best Practices

### ✅ Rule 1: Always Pass Method References (No Parentheses)
```python
# ❌ INCORRECT (Executes during page render!):
Button("Save", on_click=MyState.save())

# ✅ CORRECT (Passes EventHandler descriptor to HTMX):
Button("Save", on_click=MyState.save)
```

### ✅ Rule 2: Pass Parameters Using `with_args()` or Lambdas
```python
# Option A: with_args
Button("Edit", on_click=MyState.edit_item.with_args(item_id="123"))

# Option B: lambda with default argument
Button("Delete", on_click=lambda id=item.id: MyState.delete_item(id))
```

### ✅ Rule 3: Always Provide `bind` or `name` on Form Inputs
```python
# ❌ INCORRECT (Will not serialize into request body!):
Input("Your Name")

# ✅ CORRECT (Automatically sets name="user_name" and binds state):
Input("Your Name", bind=MyState.user_name)

# ✅ ALSO CORRECT:
Input("Your Name", name="user_name")
```

### ✅ Rule 4: Use Accessible Modals and Dialogs
```python
Modal(
    title="Create Entry",
    is_open=MyState.show_modal,
    on_close=MyState.close_modal,
    children=[
        Input("Title", bind=MyState.title),
        Button("Save", on_click=MyState.save),
    ]
)
```
Overlay backdrops automatically capture outside clicks to trigger `on_close`, while inputs inside the dialog card are fully interactive.
