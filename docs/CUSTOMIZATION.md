# UI Customization Guide: Tailwind CSS, shadcn/ui & HTML

PyDataUI gives you complete design freedom. Whether you prefer utility-first styling with **Tailwind CSS**, pre-built **shadcn/ui** components, semantic **HTML tags in pure Python**, or direct **raw HTML/SVG templates**, you can build any interface without feeling boxed into rigid defaults.

---

## 1. Quick Overview

| Customization Layer | How to Use | Example |
|---|---|---|
| **Tailwind CSS** | Pass `class_name="..."` to any component | `Box(class_name="p-6 bg-slate-900 rounded-2xl shadow-xl hover:scale-105 transition-all")` |
| **shadcn/ui Components** | Import `ShadCard`, `ShadButton`, `ShadDialog`, etc. | `ShadButton("Save", variant="default", size="lg")` |
| **Theme Palettes** | Set `palette="..."` on `App()` | `App(theme="dark", palette="violet")` |
| **Semantic HTML in Python** | Import from `pydataui.html` | `from pydataui.html import Section, Header, Nav, Svg, Path, H1, P` |
| **Raw HTML & SVG** | Use `Html("""<svg>...</svg>""")` | `Html('<div class="badge">Live</div>')` |
| **Custom Tailwind Config** | Pass `tailwind_config={...}` to `App()` | `App(tailwind_config={"theme": {"extend": {"colors": {"brand": "#ff5722"}}}}) ` |
| **External Styles & Scripts** | Pass `stylesheets` and `scripts` to `App()` | `App(stylesheets=["https://fonts.googleapis.com/..."])` |

---

## 2. Tailwind CSS Styling

Tailwind CSS Play CDN is loaded by default. **Every component** accepts the `class_name` parameter.

### Responsive Breakpoints & Flex/Grid
```python
from pydataui import Component, Text
from pydataui.html import Div

grid_layout = Div(
    Div(Text("Sidebar"), class_name="w-full md:w-64 bg-slate-100 p-4 rounded-xl"),
    Div(Text("Main Content"), class_name="flex-1 bg-white p-6 rounded-xl shadow-sm"),
    class_name="flex flex-col md:flex-row gap-6 p-6 max-w-7xl mx-auto"
)
```

### Arbitrary Tailwind Values
You can use Tailwind arbitrary value syntax (`[...]`):
```python
Div(
    class_name="h-[450px] w-[95%] bg-[#0a0f1d] border border-cyan-500/30 rounded-[1.5rem] backdrop-blur-md shadow-[0_20px_50px_rgba(8,_112,_184,_0.2)]"
)
```

### Interactive Hover & Transition States
```python
from pydataui.components.shadcn import ShadButton

btn = ShadButton(
    "Explore Models",
    class_name="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white font-semibold px-6 py-3 rounded-xl shadow-lg hover:shadow-violet-500/25 active:scale-95 transition-all duration-200"
)
```

---

## 3. shadcn/ui Theme Palettes & Components

PyDataUI comes with built-in support for shadcn/ui color palettes and design tokens.

### Selecting a Theme Palette
Choose a palette when initializing your `App`:
```python
from pydataui import App

app = App(
    title="Data Studio",
    theme="dark",      # Options: 'light', 'dark', 'auto' (detects system dark mode)
    palette="violet"   # Options: 'zinc', 'slate', 'blue', 'violet', 'green', 'rose', 'orange'
)
```

Each palette automatically configures CSS variables for `:root` and `.dark`:
- `--primary` & `--primary-foreground`
- `--secondary` & `--secondary-foreground`
- `--card` & `--card-foreground`
- `--muted` & `--muted-foreground`
- `--accent` & `--accent-foreground`
- `--destructive` & `--destructive-foreground`
- `--border`, `--input`, `--ring`, `--radius`

### Built-In shadcn/ui Components

All shadcn components can be imported from `pydataui.components.shadcn` or `pydataui.components`:

#### Buttons
```python
from pydataui.components.shadcn import ShadButton

ShadButton("Primary Button", variant="default")
ShadButton("Destructive Action", variant="destructive")
ShadButton("Outline Option", variant="outline")
ShadButton("Secondary", variant="secondary")
ShadButton("Ghost", variant="ghost")
ShadButton("Link Style", variant="link")
```
Supported sizes: `size="default"`, `size="sm"`, `size="lg"`, `size="icon"`.

#### Cards
```python
from pydataui.components.shadcn import (
    ShadCard, ShadCardHeader, ShadCardTitle, ShadCardDescription,
    ShadCardContent, ShadCardFooter, ShadButton
)

card = ShadCard(
    ShadCardHeader(
        ShadCardTitle("Model Deployment"),
        ShadCardDescription("Manage endpoint scaling and compute clusters.")
    ),
    ShadCardContent(
        Text("Current status: Healthy across 3 replicas.")
    ),
    ShadCardFooter(
        ShadButton("Scale Up", variant="default")
    ),
    class_name="max-w-md shadow-md"
)
```

#### Modals & Drawers (Dialog & Sheet)
Driven by pure Python state without writing JavaScript:
```python
from pydataui import State
from pydataui.components.shadcn import ShadDialog, ShadSheet, ShadButton

class ModalState(State):
    is_open: bool = False
    
    def open_modal(self):
        self.is_open = True
        
    def close_modal(self):
        self.is_open = False

dialog = ShadDialog(
    Text("Do you want to delete this dataset? This action cannot be undone."),
    title="Confirm Action",
    description="Permanent deletion warning",
    open=ModalState.is_open,
    on_close=ModalState.close_modal
)
```

#### Inputs, Selects, Switches, & Forms
```python
from pydataui.components.shadcn import (
    ShadInput, ShadTextarea, ShadSelect, ShadCheckbox, ShadSwitch, ShadBadge
)

ShadInput(bind=FormState.search_query, placeholder="Search tables...")
ShadSelect(options=["PostgreSQL", "BigQuery", "Snowflake"], bind=FormState.db_type)
ShadSwitch(checked=FormState.enable_cache, label="Enable Query Cache")
ShadBadge("Production", variant="default")
```

---

## 4. Semantic HTML in Pure Python (`pydataui.html`)

Instead of being restricted to high-level widgets, you can compose standard semantic HTML tags directly in Python using `pydataui.html`:

```python
from pydataui.html import (
    Header, Nav, Main, Section, Footer, Article, Aside,
    Div, Span, P, H1, H2, H3, H4, A, Ul, Li,
    Svg, Path, Circle, Rect
)

page_layout = Section(
    Header(
        Nav(
            Span("My Brand", class_name="font-extrabold text-xl"),
            A("Documentation", href="/docs", class_name="text-sm hover:underline"),
            class_name="flex justify-between items-center max-w-7xl mx-auto p-4"
        ),
        class_name="border-b bg-card/80 backdrop-blur-md"
    ),
    Main(
        H1("Semantic HTML in Python", class_name="text-3xl font-bold tracking-tight"),
        P("Write native tags with Tailwind classes and Python reactivity.", class_name="text-muted-foreground mt-2"),
        class_name="p-8 max-w-7xl mx-auto"
    ),
    Footer(
        P("© 2026 PyDataUI", class_name="text-center text-xs text-muted-foreground"),
        class_name="border-t p-4"
    ),
    class_name="min-h-screen bg-background"
)
```

### SVG Icons & Vector Graphics
Create clean vector icons without external asset bundles:
```python
from pydataui.html import Svg, Path

bolt_icon = Svg(
    Path(d="M13 10V3L4 14h7v7l9-11h-7z"),
    viewBox="0 0 24 24",
    fill="currentColor",
    class_name="w-6 h-6 text-amber-500"
)
```

### HTML5 Boolean Attributes
PyDataUI intelligently formats HTML boolean attributes according to HTML5 standards:
- `disabled=True` renders as `disabled`
- `disabled=False` is completely omitted (no invalid `disabled="False"`)
- `required=True`, `checked=True`, `readonly=True`, `autofocus=True` work out of the box.

---

## 5. Raw HTML & Custom Templates (`Html` / `RawHtml`)

If you have existing HTML snippets, complex SVG graphics, or third-party web embeds, use `Html`:

```python
from pydataui import Html

custom_embed = Html("""
<div class="relative overflow-hidden rounded-2xl bg-slate-900 p-8 text-white shadow-2xl">
    <div class="absolute -right-10 -top-10 h-40 w-40 rounded-full bg-violet-600/30 blur-3xl"></div>
    <h3 class="text-xl font-bold">Hardware Accelerated Streaming</h3>
    <p class="text-slate-400 text-sm mt-2">Zero JavaScript required on the client side.</p>
</div>
""")
```

---

## 6. Application-Level Customization (`App` Configuration)

Customize fonts, third-party libraries, and Tailwind themes directly when creating the `App`:

```python
from pydataui import App

app = App(
    title="Analytics Portal",
    theme="dark",          # 'light', 'dark', or 'auto'
    palette="blue",        # 'zinc', 'slate', 'blue', 'violet', 'green', 'rose', 'orange'
    
    # Custom Tailwind extensions
    tailwind_config={
        "theme": {
            "extend": {
                "colors": {
                    "brand": "#0ea5e9",
                    "accent-glow": "#38bdf8"
                },
                "fontFamily": {
                    "mono": ["Fira Code", "monospace"]
                }
            }
        }
    },
    
    # Custom Google Fonts or external CSS
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600&display=swap"
    ],
    
    # External JavaScript CDN libraries (e.g. Canvas Confetti, Lucide)
    scripts=[
        "https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"
    ],
    
    # Custom global CSS rules
    custom_css="""
    body { font-family: 'Inter', sans-serif; }
    code, pre { font-family: 'Fira Code', monospace; }
    """,
    
    # Custom <head> tags (e.g. meta tags, OpenGraph, favicon)
    head="""
    <meta name="description" content="Production Analytics Portal powered by PyDataUI">
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🚀</text></svg>">
    """
)
```

---

## 7. Creating Reusable Custom Components

You can encapsulate your own custom UI design system components by subclassing `Component`:

```python
from pydataui import Component

class GlassCard(Component):
    """Reusable Glassmorphism Card with Tailwind CSS."""
    tag = "div"

    def _get_classes(self):
        return [
            "backdrop-blur-xl bg-card/60 border border-border/50",
            "rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300"
        ]

# Usage:
card = GlassCard(
    H2("Custom Glass Component", class_name="text-lg font-bold"),
    P("Encapsulated styling that can be reused across pages.")
)
```

---

## 8. Working Example

See the full working showcase in [`examples/custom_ui_app.py`](file:///Users/boopathiraj/Downloads/AI_Browsers/Full-Web-Framework/examples/custom_ui_app.py):

```bash
python examples/custom_ui_app.py
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) to inspect the dark theme, violet palette, interactive progress bars, and custom SVG animations.
