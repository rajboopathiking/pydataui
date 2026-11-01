# UI Customization Guide: Tailwind CSS, shadcn/ui & HTML

PyDataUI gives you complete design freedom. Whether you prefer utility-first styling with **Tailwind CSS**, pre-built **shadcn/ui** components, semantic **HTML tags in pure Python**, or direct **raw HTML/SVG templates**, you can build any interface without feeling boxed into rigid defaults.

!!! tip "Developer references"
    For the full tag and attribute contract, see the [HTML Reference](HTML_REFERENCE.md). For framework tokens, class names, dark mode, and cascade rules, see the [CSS Reference](CSS_REFERENCE.md).

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

All shadcn components can be imported directly from `pydataui.shadcn`, `pydataui.components.shadcn`, or `pydataui.components`:

```python
from pydataui.shadcn import (
    ShadButton,
    ShadCard, ShadCardHeader, ShadCardTitle, ShadCardDescription, ShadCardContent, ShadCardFooter,
    ShadInput, ShadBadge, ShadDialog, ShadSheet, ShadTabs, ShadSwitch
)
```

#### Buttons
```python
from pydataui.shadcn import ShadButton

ShadButton("Primary Button", variant="default")
ShadButton("Destructive Action", variant="destructive")
ShadButton("Outline Option", variant="outline")
ShadButton("Secondary", variant="secondary")
ShadButton("Ghost", variant="ghost")
ShadButton("Link Style", variant="link")
```
Supported sizes: `size="default"`, `size="sm"`, `size="lg"`, `size="icon"`.

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;">
    <button type="button" style="background: #fafafa; color: #09090b; font-weight: 500; font-size: 0.875rem; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">Primary Button</button>
    <button type="button" style="background: #ef4444; color: #fafafa; font-weight: 500; font-size: 0.875rem; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer;">Destructive Action</button>
    <button type="button" style="background: transparent; color: #fafafa; font-weight: 500; font-size: 0.875rem; padding: 0.5rem 1rem; border-radius: 0.375rem; border: 1px solid #27272a; cursor: pointer;">Outline Option</button>
    <button type="button" style="background: #27272a; color: #fafafa; font-weight: 500; font-size: 0.875rem; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer;">Secondary</button>
    <button type="button" style="background: transparent; color: #a1a1aa; font-weight: 500; font-size: 0.875rem; padding: 0.5rem 1rem; border-radius: 0.375rem; border: none; cursor: pointer;">Ghost</button>
    <button type="button" style="background: transparent; color: #fafafa; font-weight: 500; font-size: 0.875rem; padding: 0.5rem 0.5rem; border-radius: 0.375rem; border: none; text-decoration: underline; cursor: pointer;">Link Style</button>
  </div>
</div>

#### Cards
```python
from pydataui.shadcn import (
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

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="max-width: 24rem; background: #18181b; border: 1px solid #27272a; border-radius: 0.5rem; padding: 1.5rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
      <div>
        <h4 style="margin: 0; font-size: 1.125rem; font-weight: 600; color: #fafafa; letter-spacing: -0.025em;">Model Deployment</h4>
        <p style="margin: 0.25rem 0 0 0; font-size: 0.875rem; color: #a1a1aa;">Manage endpoint scaling and compute clusters.</p>
      </div>
      <span style="display: inline-flex; align-items: center; padding: 0.125rem 0.5rem; font-size: 0.75rem; font-weight: 600; border-radius: 9999px; background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3);">v1.1.1</span>
    </div>
    <div style="padding: 1rem 0; color: #e4e4e7; font-size: 0.875rem; border-top: 1px solid #27272a; border-bottom: 1px solid #27272a; margin: 0.75rem 0;">
      Current status: <strong style="color: #4ade80;">Healthy</strong> across 3 replicas (sub-15ms latency).
    </div>
    <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 1rem;">
      <button type="button" style="background: transparent; color: #fafafa; border: 1px solid #27272a; padding: 0.375rem 0.75rem; font-size: 0.875rem; border-radius: 0.375rem; cursor: pointer;">Settings</button>
      <button type="button" style="background: #fafafa; color: #09090b; border: none; padding: 0.375rem 0.75rem; font-size: 0.875rem; font-weight: 500; border-radius: 0.375rem; cursor: pointer;">Scale Up</button>
    </div>
  </div>
</div>

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
from pydataui.shadcn import (
    ShadInput, ShadTextarea, ShadSelect, ShadCheckbox, ShadSwitch, ShadBadge
)

ShadInput(bind=FormState.search_query, placeholder="Search tables...")
ShadSelect(options=["PostgreSQL", "BigQuery", "Snowflake"], bind=FormState.db_type)
ShadSwitch(checked=FormState.enable_cache, label="Enable Query Cache")
ShadBadge("Production", variant="default")
```

<div style="margin: 1rem 0 2rem 0; padding: 1.5rem; background: #09090b; border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #71717a; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview</div>
  <div style="max-width: 24rem; display: flex; flex-direction: column; gap: 1rem;">
    <div>
      <label style="display: block; font-size: 0.875rem; font-weight: 500; color: #fafafa; margin-bottom: 0.35rem;">Search Query</label>
      <input type="text" placeholder="Search tables..." value="warehouse_analytics_prod" readonly style="width: 100%; box-sizing: border-box; background: #09090b; border: 1px solid #27272a; color: #fafafa; padding: 0.5rem 0.75rem; font-size: 0.875rem; border-radius: 0.375rem; outline: none;">
    </div>
    <div style="display: flex; items-center; justify-content: space-between;">
      <span style="font-size: 0.875rem; color: #fafafa;">Target Database</span>
      <select style="background: #18181b; border: 1px solid #27272a; color: #fafafa; padding: 0.375rem 0.75rem; font-size: 0.875rem; border-radius: 0.375rem; outline: none;">
        <option>PostgreSQL</option>
        <option>BigQuery</option>
        <option>Snowflake</option>
      </select>
    </div>
    <div style="display: flex; align-items: center; justify-content: space-between;">
      <span style="font-size: 0.875rem; color: #fafafa;">Enable Query Cache</span>
      <div style="width: 2.75rem; height: 1.5rem; background: #fafafa; border-radius: 9999px; position: relative; cursor: pointer;">
        <div style="width: 1.25rem; height: 1.25rem; background: #09090b; border-radius: 9999px; position: absolute; right: 0.125rem; top: 0.125rem;"></div>
      </div>
    </div>
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.25rem;">
      <span style="font-size: 0.875rem; color: #a1a1aa;">Environment:</span>
      <span style="display: inline-flex; align-items: center; padding: 0.125rem 0.6rem; font-size: 0.75rem; font-weight: 600; border-radius: 9999px; background: #fafafa; color: #09090b;">Production</span>
      <span style="display: inline-flex; align-items: center; padding: 0.125rem 0.6rem; font-size: 0.75rem; font-weight: 600; border-radius: 9999px; background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3);">99.9% SLI</span>
    </div>
  </div>
</div>

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

<div style="margin: 1rem 0 2rem 0; padding: 2rem; background: radial-gradient(circle at 50% 50%, #1e1b4b 0%, #09090b 100%); border: 1px solid #27272a; border-radius: 0.75rem;">
  <div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; color: #818cf8; margin-bottom: 1rem; font-weight: 700;">Rendered UI Preview (Glassmorphism)</div>
  <div style="max-width: 22rem; background: rgba(24, 24, 27, 0.65); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.12); border-radius: 1rem; padding: 1.5rem; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5);">
    <h3 style="margin: 0; font-size: 1.125rem; font-weight: 700; color: #fafafa;">Custom Glass Component</h3>
    <p style="margin: 0.5rem 0 0 0; font-size: 0.875rem; color: #a1a1aa; line-height: 1.4;">Encapsulated styling with blur and glowing border that can be reused across pages.</p>
  </div>
</div>

---

## 8. Advanced Animations with GSAP (GreenSock)

PyDataUI has **zero limitations** on client-side animation and script libraries. You can integrate **GSAP (GreenSock)**, ScrollTrigger, Anime.js, Lucide Icons, Canvas Confetti, and Three.js with full reactive state support.

### Loading GSAP in `App`
Pass the official GSAP CDN links directly to the `scripts` parameter:

```python
from pydataui import App

app = App(
    title="GSAP Animated App",
    theme="dark",
    palette="zinc",
    scripts=[
        "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js",
        "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js",
    ]
)
```

### Staggered Entrance & Micro-Interactions
Attach standard CSS classes (`gsap-hero`, `gsap-card`) to any PyDataUI or shadcn component, and embed your animation logic using `Html`:

```python
from pydataui.html import Div, H1, P, Html
from pydataui.shadcn import ShadCard, ShadButton

@app.page("/")
def home():
    return Div(
        H1("Fluid Animations", class_name="gsap-hero text-5xl font-extrabold tracking-tight"),
        P("60fps physics-based motion with zero configuration.", class_name="gsap-hero text-muted-foreground mt-2"),
        
        Div(
            ShadCard(H3("Card 1"), class_name="gsap-card p-6"),
            ShadCard(H3("Card 2"), class_name="gsap-card p-6"),
            ShadCard(H3("Card 3"), class_name="gsap-card p-6"),
            class_name="grid grid-cols-3 gap-6 mt-8"
        ),

        # Embedded GSAP Script
        Html("""
        <script>
            function runAnimations() {
                // Staggered hero text entrance
                gsap.from(".gsap-hero", {
                    y: -30,
                    opacity: 0,
                    duration: 0.9,
                    stagger: 0.15,
                    ease: "power4.out"
                });

                // Spring entrance for cards
                gsap.from(".gsap-card", {
                    scale: 0.88,
                    opacity: 0,
                    duration: 0.8,
                    delay: 0.3,
                    stagger: 0.18,
                    ease: "back.out(1.7)"
                });
            }

            // Execute on initial page load
            document.addEventListener("DOMContentLoaded", runAnimations);

            // Re-trigger after HTMX partial page swaps (reactive updates)
            document.addEventListener("htmx:afterSwap", runAnimations);
        </script>
        """),
        class_name="min-h-screen p-12 bg-background text-foreground"
    )
```

### Coordinating GSAP with Reactive Server State (HTMX)
When Python updates state on the server (e.g. via HTMX swaps), simply listen to `htmx:afterSwap` or `htmx:afterSettle`:
- Initial render: `DOMContentLoaded` runs the entrance timeline.
- Dynamic data refresh: `htmx:afterSwap` animates updated numbers, flash badges, or newly inserted list rows.

---

## 9. Working Example

See the full working showcase in [`examples/custom_ui_app.py`](file:///Users/boopathiraj/Downloads/AI_Browsers/Full-Web-Framework/examples/custom_ui_app.py):

```bash
python examples/custom_ui_app.py
```
Open [http://127.0.0.1:8080](http://127.0.0.1:8080) to inspect the dark theme, violet palette, interactive progress bars, and custom SVG animations.
