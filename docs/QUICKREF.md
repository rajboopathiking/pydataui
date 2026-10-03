# PyDataUI — Quick Reference Card

## Minimal App

```python
from pydataui import App, State
from pydataui.components import Container, Button, Heading

class MyState(State):
    count: int = 0
    def increment(self): self.count += 1

app = App(title="My App")

@app.page("/")
def home():
    return Container(
        Heading(MyState.count),
        Button("+", on_click=MyState.increment),
    )

app.run()
```

---

## State Rules

```python
class AppState(State):
    # Reactive variables — type-annotated
    name: str = "World"
    count: int = 0
    items: list = []
    active: bool = True

    # Event handlers — regular methods
    def update_name(self, name: str = ""):
        self.name = name

    def add_item(self, text: str = ""):
        self.items.append(text)
```

- Class access `AppState.name` → `StateVarRef` (reactive, use in components)
- Class access `AppState.update_name` → `EventHandler` (use in event props)
- Instance access `AppState().name` → actual Python value

---

## URL Routes

| URL | What it does |
|---|---|
| `GET /` | Your page (from `@app.page("/")`) |
| `GET /docs` | Swagger UI |
| `GET /api/docs` | Swagger UI (alternate) |
| `GET /api` | REST API catalog (all states) |
| `GET /api/health` | Health check |
| `GET /api/{State}` | Full state JSON |
| `GET /api/{State}/{field}` | Single field |
| `PUT /api/{State}` | Update state (JSON body) |
| `DELETE /api/{State}` | Reset to defaults |
| `POST /api/{State}/{method}` | Call method (JSON args in body) |
| `POST /_pdu/event/{State}/{method}` | HTMX internal event (SSR) |
| `GET /_pdu/static/htmx.min.js` | Bundled HTMX |
| `GET /_pdu/static/pydataui.css` | Bundled CSS |

---

## Event Binding

```python
# Direct method reference
Button("Click", on_click=MyState.do_something)

# With captured argument
Button("Del", on_click=lambda id=item_id: MyState.delete(id))

# With options
from pydataui.event import EventSpec
Button("Save", on_click=EventSpec(
    MyState.save,
    confirm="Are you sure?",
    debounce=500,
))
```

---

## Component Quick Reference

### Layout
```python
Container(child, max_width="lg")
Flex(a, b, gap="md", justify="center", align="center")
Grid(a, b, c, columns=3, gap="md")
Box(child, padding="lg", margin="sm")
HStack(a, b, gap="md")
VStack(a, b, gap="md")
Divider()
Spacer()
```

### Typography
```python
Heading("Title", level=1)       # h1-h6
Text("Body text", color="muted")
Paragraph("Long text...")
Code("print('hello')")
Link("Click", href="/page")
```

### Forms
```python
Button("Click", variant="primary", on_click=State.method)
# variants: primary | secondary | success | danger | warning | outline | ghost
# sizes: xs | sm | md | lg | xl

Input("Label", type="text", bind=State.field, placeholder="...")
# types: text | email | password | number | date | tel | url

TextArea("Label", bind=State.content, rows=5)
Select("Label", options=["A","B","C"], bind=State.choice)
Checkbox("Agree", bind=State.agreed)
Switch("Dark Mode", bind=State.dark)
```

### Data
```python
Table(columns=["Name","Email"], data=[["A","a@x.com"]])
Badge("Active", variant="success")
Stat(label="Revenue", value="$12,345", change="+23%", trend="up")
Progress(value=75, max=100)
```

### Feedback
```python
Alert("Message", variant="success")  # success | warning | danger | info
Spinner(size="md")
Skeleton(width="100%", height="20px")
```

### Overlay
```python
Modal(title="...", is_open=State.show, on_close=State.close, children=[...])
Drawer(title="...", is_open=State.show, position="right", children=[...])
```

### Charts
```python
BarChart(labels=["Q1","Q2"], datasets=[{"label":"Sales","data":[100,200]}])
LineChart(labels=[...], datasets=[...])
PieChart(labels=[...], datasets=[...])
```

### Navigation
```python
Navbar(title="App", links=[("Home","/"),("API","/api")])
Sidebar(links=[("Dashboard","/"),("Users","/users")])
Tabs(Tab("Tab1", content=...), Tab("Tab2", content=...))
Breadcrumb(items=[("Home","/"),("Users","/users"),("John",None)])
```

---

## REST API (curl examples)

```bash
# Get state
curl http://localhost:8000/api/MyState

# Call method with no args
curl -X POST http://localhost:8000/api/MyState/increment

# Call method with args
curl -X POST http://localhost:8000/api/MyState/add_item \
  -H "Content-Type: application/json" \
  -d '{"text": "New item"}'

# Update state
curl -X PUT http://localhost:8000/api/MyState \
  -H "Content-Type: application/json" \
  -d '{"count": 99}'

# Reset state
curl -X DELETE http://localhost:8000/api/MyState

# Get single field
curl http://localhost:8000/api/MyState/count

# API catalog
curl http://localhost:8000/api
```

---

## Custom Endpoints

```python
@app.api("/export", method="GET")
def export_csv(request):
    return {"data": [...]}

@app.api("/webhook", method="POST")
def handle_webhook(request):
    data = request.json()
    return {"received": True}
```
