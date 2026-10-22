# CSS Reference for Developers

PyDataUI ships a small, dependency-free CSS layer for its core components and uses Tailwind CSS for utility styling and shadcn/ui tokens. This guide documents that layer for developers who are theming an application, writing custom components, or changing the framework stylesheet.

The stylesheet is a single plain-CSS file:

```text
pydataui/styling/css/pydataui.css
```

There is no Sass, PostCSS, CSS-in-JS, or build step for this file. It is served unchanged at `/_pdu/static/pydataui.css`.

For semantic HTML APIs and generated markup, see the [HTML Reference](HTML_REFERENCE.md). For task-oriented examples, see [UI Customization & Tailwind](CUSTOMIZATION.md).

---

## 1. Stylesheet Architecture

The stylesheet is organized into numbered sections:

| Section | Contents |
|---|---|
| 1 | Reset and base element styles |
| 2 | `--pdu-*` design tokens and dark overrides |
| 3 | Layout: containers, flex, grid, stacks, cards, dividers |
| 4 | Typography |
| 5 | Forms and controls |
| 6 | Data display: tables, lists, badges, stats, avatars |
| 7 | Feedback: alerts, progress, spinners, skeletons, toasts |
| 8 | Navigation: navbar, sidebar, tabs, breadcrumbs, pagination |
| 9 | Overlays: modals, drawers, popovers, dropdowns |
| 10 | Media and icons |
| 11 | Animations and keyframes |
| 12 | Utility classes and responsive visibility |

The layer follows three rules:

1. Framework selectors use the `pdu-` prefix.
2. Values that participate in theming come from CSS custom properties; structural values such as fixed icon sizes may remain local.
3. Application-specific styling should use `class_name` or the `--pdu-*` tokens, not edits to framework selectors.

### Load Order

For a normal application page, styles are applied in this order:

```text
Tailwind Play CDN
  -> generated shadcn CSS variables
  -> App(custom_css=...)
  -> pydataui.css
  -> App(stylesheets=[...])
  -> App(head=...)
```

Consequences:

- `custom_css` is emitted before `pydataui.css`. If both rules have equal specificity, the framework rule wins.
- External stylesheets passed to `App(stylesheets=[...])` load after the framework and are the cleanest place for application overrides.
- Inline styles passed through `style={...}` override both, except for `!important` declarations.
- Tailwind utilities and `pdu-*` classes generally have equal single-class specificity. Avoid relying on source order when they conflict; use a more specific selector, an arbitrary value, or `!` on the Tailwind utility.

---

## 2. Naming Conventions

| Pattern | Meaning | Example |
|---|---|---|
| `pdu` | Base class added to every component | `<h1 class="pdu">` |
| `pdu-<block>` | Block or component | `.pdu-card`, `.pdu-alert` |
| `pdu-<block>-<part>` | Part of a block | `.pdu-card-header`, `.pdu-modal-body` |
| `pdu-<block>-<modifier>` | Variant or state | `.pdu-btn-primary`, `.pdu-tab-active` |
| `pdu-<property>-<value>` | Utility | `.pdu-mt-md`, `.pdu-text-sm`, `.pdu-hidden` |

Names are flat, not BEM-style. Modifiers are separate classes, not descendant selectors, so an element can combine them:

```html
<button class="pdu pdu-btn pdu-btn-primary pdu-btn-lg">Run pipeline</button>
```

Do not use `pdu-*` names for application-only classes. Prefix custom classes with your product or use Tailwind utilities. This avoids collisions during framework upgrades.

---

## 3. Design Tokens

All framework tokens are declared on `:root` and consumed through `var(--pdu-...)`.

### Color Tokens

| Token | Default | Use |
|---|---|---|
| `--pdu-color-primary` | `#3b82f6` | Primary actions, links, focus |
| `--pdu-color-primary-hover` | `#2563eb` | Primary hover state |
| `--pdu-color-primary-light` | `#eff6ff` | Tinted backgrounds and focus rings |
| `--pdu-color-secondary` | `#6b7280` | Secondary actions |
| `--pdu-color-secondary-hover` | `#4b5563` | Secondary hover |
| `--pdu-color-success` | `#22c55e` | Success state |
| `--pdu-color-success-hover` | `#16a34a` | Success hover |
| `--pdu-color-success-light` | `#f0fdf4` | Success background |
| `--pdu-color-danger` | `#ef4444` | Errors and destructive actions |
| `--pdu-color-danger-hover` | `#dc2626` | Danger hover |
| `--pdu-color-danger-light` | `#fef2f2` | Error background |
| `--pdu-color-warning` | `#f59e0b` | Warning state |
| `--pdu-color-warning-hover` | `#d97706` | Warning hover |
| `--pdu-color-warning-light` | `#fffbeb` | Warning background |
| `--pdu-color-info` | `#06b6d4` | Informational state |
| `--pdu-color-info-hover` | `#0891b2` | Info hover |
| `--pdu-color-info-light` | `#ecfeff` | Info background |
| `--pdu-color-bg` | `#ffffff` | Surface background |
| `--pdu-color-bg-secondary` | `#f9fafb` | Subtle surface |
| `--pdu-color-bg-tertiary` | `#f3f4f6` | Stronger surface |
| `--pdu-color-text` | `#111827` | Primary text |
| `--pdu-color-text-secondary` | `#6b7280` | Secondary text |
| `--pdu-color-text-muted` | `#9ca3af` | Muted text |
| `--pdu-color-border` | `#e5e7eb` | Default border |
| `--pdu-color-border-hover` | `#d1d5db` | Hover border |
| `--pdu-color-overlay` | `rgba(0,0,0,0.5)` | Modal and drawer overlay |

### Typography Tokens

| Token | Default |
|---|---|
| `--pdu-font-body` | System UI stack |
| `--pdu-font-heading` | Inherits body font |
| `--pdu-font-mono` | SF Mono / Consolas / monospace stack |
| `--pdu-font-size-xs` | `0.75rem` |
| `--pdu-font-size-sm` | `0.875rem` |
| `--pdu-font-size-md` | `1rem` |
| `--pdu-font-size-lg` | `1.125rem` |
| `--pdu-font-size-xl` | `1.25rem` |
| `--pdu-font-size-2xl` | `1.5rem` |
| `--pdu-font-size-3xl` | `1.875rem` |

### Spacing Tokens

| Token | Default |
|---|---|
| `--pdu-spacing-xs` | `0.25rem` |
| `--pdu-spacing-sm` | `0.5rem` |
| `--pdu-spacing-md` | `1rem` |
| `--pdu-spacing-lg` | `1.5rem` |
| `--pdu-spacing-xl` | `2rem` |
| `--pdu-spacing-2xl` | `3rem` |
| `--pdu-spacing-3xl` | `4rem` |

### Radius and Shadow Tokens

| Token | Default |
|---|---|
| `--pdu-radius-none` | `0` |
| `--pdu-radius-sm` | `0.25rem` |
| `--pdu-radius-md` | `0.375rem` |
| `--pdu-radius-lg` | `0.5rem` |
| `--pdu-radius-xl` | `0.75rem` |
| `--pdu-radius-2xl` | `1rem` |
| `--pdu-radius-full` | `9999px` |
| `--pdu-shadow-sm` | Small elevation |
| `--pdu-shadow-md` | Default card elevation |
| `--pdu-shadow-lg` | Large elevation |
| `--pdu-shadow-xl` | Modal and drawer elevation |

### Overriding Tokens

Use `App(custom_css=...)` for application-wide token changes:

```python
from pydataui import App

app = App(
    title="Operations Portal",
    custom_css="""
    :root {
      --pdu-color-primary: #0f766e;
      --pdu-color-primary-hover: #115e59;
      --pdu-color-primary-light: #ccfbf1;
      --pdu-radius-lg: 0.75rem;
    }
    """,
)
```

Token overrides inherit everywhere the token is referenced. Prefer this over copying and editing component rules.

---

## 4. Theme Layers and Dark Mode

PyDataUI has two related token layers:

| Layer | Variables | Consumed by |
|---|---|---|
| Framework layer | `--pdu-*` | Native `pdu-*` component classes and `pydataui.html` tags |
| shadcn/Tailwind layer | `--background`, `--foreground`, `--primary`, `--card`, `--muted`, `--border`, etc. | shadcn components and Tailwind color utilities such as `bg-card`, `text-muted-foreground` |

`App(theme=...)` controls the shadcn/Tailwind layer:

```python
App(theme="light")  # no dark class
App(theme="dark")   # class="dark" on <html>
App(theme="auto")   # adds class="dark" when the OS prefers dark mode
```

`App(palette=...)` selects the shadcn token values. Available palettes are `zinc`, `slate`, `blue`, `violet`, `green`, `rose`, `orange`, and `emerald`.

The framework layer activates its dark token block through either `.dark` or `[data-theme="dark"]`. This means native `pdu-*` components follow `App(theme="dark")` as well:

```css
[data-theme='dark'], .dark {
  --pdu-color-bg: #111827;
  --pdu-color-bg-secondary: #1f2937;
  --pdu-color-text: #f9fafb;
  --pdu-color-border: #374151;
  /* additional dark values */
}
```

To override framework dark values, put the override under the same selector:

```python
custom_css="""
.dark {
  --pdu-color-primary: #2dd4bf;
  --pdu-color-primary-light: #134e4a;
}
"""
```

Because `custom_css` is loaded before `pydataui.css`, an equal-specificity `.dark` rule would be overwritten by the framework's dark block. Use a more specific selector or a stylesheet that loads after the framework:

```css
html.dark {
  --pdu-color-primary: #2dd4bf;
}
```

### shadcn Token Names

The Tailwind configuration maps these utility colors to CSS variables:

| Tailwind utility family | CSS variables |
|---|---|
| `bg-background`, `text-foreground` | `--background`, `--foreground` |
| `bg-card`, `text-card-foreground` | `--card`, `--card-foreground` |
| `bg-primary`, `text-primary-foreground` | `--primary`, `--primary-foreground` |
| `bg-secondary`, `text-secondary-foreground` | `--secondary`, `--secondary-foreground` |
| `bg-muted`, `text-muted-foreground` | `--muted`, `--muted-foreground` |
| `bg-accent`, `text-accent-foreground` | `--accent`, `--accent-foreground` |
| `bg-destructive`, `text-destructive-foreground` | `--destructive`, `--destructive-foreground` |
| `border-border`, `border-input`, `ring-ring` | `--border`, `--input`, `--ring` |

The shadcn values are HSL channel triplets, for example `--primary: 240 5.9% 10%`. They are consumed through `hsl(var(--primary))`, so overrides must use the same format.

---

## 5. Layout Classes

| Class | Effect |
|---|---|
| `.pdu-box` | `display: block` |
| `.pdu-container` | Full width, auto margins, horizontal padding |
| `.pdu-container-sm` | `max-width: 640px` |
| `.pdu-container-md` | `max-width: 768px` |
| `.pdu-container-lg` | `max-width: 1024px` |
| `.pdu-container-xl` | `max-width: 1280px` |
| `.pdu-container-2xl` | `max-width: 1536px` |
| `.pdu-container-full` | `max-width: 100%` |
| `.pdu-flex` | `display: flex` |
| `.pdu-grid` | `display: grid` |
| `.pdu-stack` | Vertical flex with automatic spacing between children |
| `.pdu-card` | Bordered, rounded surface with shadow |
| `.pdu-card-header` | Card header with bottom border |
| `.pdu-card-body` | Card content padding |
| `.pdu-card-footer` | Card footer with top border |
| `.pdu-divider` | Horizontal rule |
| `.pdu-divider-vertical` | Vertical rule |
| `.pdu-spacer` | `flex-grow: 1` |
| `.pdu-center` | Centers children on both axes |

The container modifiers only set `max-width`. `.pdu-container` supplies the width, centering, and horizontal padding. For example, `Container(max_width="lg")` renders `pdu-container pdu-container-lg`, not a Tailwind `max-w-*` class.

---

## 6. Typography Classes

| Class | Purpose |
|---|---|
| `.pdu-text` | Body font and text color |
| `.pdu-text-xs` … `.pdu-text-3xl` | Font-size scale |
| `.pdu-heading-1` … `.pdu-heading-6` | Heading size, weight, and spacing |
| `.pdu-paragraph` | Paragraph bottom margin |
| `.pdu-link` | Primary-colored link with hover underline |
| `.pdu-code` | Inline code background and border |
| `.pdu-code-block` | Scrollable preformatted block |
| `.pdu-blockquote` | Left-bordered quote |
| `.pdu-label` | Form label typography |
| `.pdu-fw-light` … `.pdu-fw-bold` | Font weights |
| `.pdu-text-left`, `.pdu-text-center`, `.pdu-text-right` | Text alignment |

---

## 7. Form Classes

### Buttons

Base class: `.pdu-btn`

| Variant | Class |
|---|---|
| Primary | `.pdu-btn-primary` |
| Secondary | `.pdu-btn-secondary` |
| Success | `.pdu-btn-success` |
| Danger | `.pdu-btn-danger` |
| Warning | `.pdu-btn-warning` |
| Info | `.pdu-btn-info` |
| Outline | `.pdu-btn-outline` |
| Ghost | `.pdu-btn-ghost` |
| Link | `.pdu-btn-link` |

| Size/state | Class |
|---|---|
| Small | `.pdu-btn-sm` |
| Medium | `.pdu-btn-md` |
| Large | `.pdu-btn-lg` |
| Disabled | `.pdu-btn-disabled` |
| Loading | `.pdu-btn-loading` |

A complete button class list looks like:

```html
<button class="pdu pdu-btn pdu-btn-primary pdu-btn-md">Refresh</button>
```

### Inputs

| Class | Purpose |
|---|---|
| `.pdu-input` | Text-like input |
| `.pdu-textarea` | Textarea |
| `.pdu-select` | Select control with custom arrow |
| `.pdu-input-sm`, `.pdu-input-md`, `.pdu-input-lg` | Input sizes |
| `.pdu-input-error` | Error border and focus ring |
| `.pdu-checkbox`, `.pdu-radio` | Custom checkbox and radio |
| `.pdu-switch` | Toggle switch |
| `.pdu-slider` | Range input |
| `.pdu-form`, `.pdu-form-group` | Form and field wrappers |
| `.pdu-input-helper` | Helper text |
| `.pdu-input-error-text` | Error text |

Native inputs receive focus rings through the `--pdu-color-primary` tokens. If you remove the default outline, provide a visible replacement.

---

## 8. Data Display Classes

### Tables

| Class | Purpose |
|---|---|
| `.pdu-table` | Base table |
| `.pdu-table-striped` | Zebra rows |
| `.pdu-table-hoverable` | Row hover background |
| `.pdu-table-bordered` | Outer and cell borders |
| `.pdu-table-compact` | Reduced cell padding |

Combine modifiers on the same element:

```html
<table class="pdu-table pdu-table-striped pdu-table-hoverable pdu-table-compact">
```

### Lists, Badges, and Stats

| Class | Purpose |
|---|---|
| `.pdu-list`, `.pdu-list-item` | Unstyled list and separated rows |
| `.pdu-badge` | Inline status label |
| `.pdu-badge-primary` | Primary badge |
| `.pdu-badge-success` | Success badge |
| `.pdu-badge-danger` | Danger badge |
| `.pdu-badge-warning` | Warning badge |
| `.pdu-badge-info` | Info badge |
| `.pdu-tag` | Compact tag |
| `.pdu-stat`, `.pdu-stat-label`, `.pdu-stat-value`, `.pdu-stat-help` | Stat block |
| `.pdu-key-value` | Label/value row |
| `.pdu-avatar` | Circular avatar |
| `.pdu-avatar-sm`, `.pdu-avatar-md`, `.pdu-avatar-lg` | Avatar sizes |
| `.pdu-tooltip` | CSS tooltip using `data-tooltip` |

Tooltip example:

```html
<span class="pdu-tooltip" data-tooltip="Last successful run">Healthy</span>
```

---

## 9. Feedback Classes

| Class | Purpose |
|---|---|
| `.pdu-alert` | Base alert |
| `.pdu-alert-info` | Info alert |
| `.pdu-alert-success` | Success alert |
| `.pdu-alert-warning` | Warning alert |
| `.pdu-alert-danger` | Danger alert |
| `.pdu-alert-title` | Alert heading |
| `.pdu-alert-closable` | Right padding for a close control |
| `.pdu-progress` | Progress track |
| `.pdu-progress-bar` | Progress fill |
| `.pdu-progress-striped` | Striped fill |
| `.pdu-progress-animated` | Animated stripes |
| `.pdu-spinner` | Rotating spinner |
| `.pdu-skeleton`, `.pdu-skeleton-text`, `.pdu-skeleton-circle` | Loading placeholders |
| `.pdu-toast` | Fixed toast |
| `.pdu-empty` | Empty-state panel |

Progress markup:

```html
<div class="pdu-progress">
  <div class="pdu-progress-bar" style="width: 72%"></div>
</div>
```

---

## 10. Navigation and Overlay Classes

### Navigation

| Class | Purpose |
|---|---|
| `.pdu-navbar` | Horizontal navigation bar |
| `.pdu-navbar-brand` | Brand link |
| `.pdu-navbar-nav` | Link group |
| `.pdu-navbar-dark` | Dark navbar variant |
| `.pdu-navbar-sticky` | Sticky positioning |
| `.pdu-nav-link`, `.pdu-nav-link-active` | Navigation link and active state |
| `.pdu-sidebar`, `.pdu-sidebar-collapsed` | Sidebar and collapsed width |
| `.pdu-breadcrumb`, `.pdu-breadcrumb-item` | Breadcrumb trail |
| `.pdu-tabs`, `.pdu-tab`, `.pdu-tab-active`, `.pdu-tab-panel` | Tabs |
| `.pdu-pagination`, `.pdu-page-item`, `.pdu-page-link`, `.pdu-page-active` | Pagination |
| `.pdu-menu`, `.pdu-menu-item` | Menu list |

### Overlays

| Class | Purpose |
|---|---|
| `.pdu-modal-wrapper` | Fixed modal viewport |
| `.pdu-modal-overlay` | Backdrop |
| `.pdu-modal` | Dialog surface |
| `.pdu-modal-content`, `.pdu-modal-header`, `.pdu-modal-body`, `.pdu-modal-footer` | Dialog parts |
| `.pdu-modal-sm`, `.pdu-modal-md`, `.pdu-modal-lg` | Dialog widths |
| `.pdu-modal-close` | Close button |
| `.pdu-drawer-wrapper`, `.pdu-drawer-overlay`, `.pdu-drawer` | Drawer shell |
| `.pdu-drawer-left`, `.pdu-drawer-right` | Drawer side |
| `.pdu-popover`, `.pdu-dropdown`, `.pdu-dropdown-menu`, `.pdu-dropdown-item` | Popovers and menus |

Overlay z-index values are intentionally layered: modals use `1000`, drawers `1050`, dropdowns `900`, and tooltips `100`.

---

## 11. Media, Animation, and Utility Classes

### Media

| Class | Purpose |
|---|---|
| `.pdu-image` | Responsive image |
| `.pdu-image-rounded` | Rounded corners |
| `.pdu-image-cover` | `object-fit: cover` |
| `.pdu-icon` | Inline icon sizing |

### Animation

| Name | Used by |
|---|---|
| `pdu-spin` | Spinner and loading buttons |
| `pdu-pulse` | Skeleton loaders |
| `pdu-fade-in` | Overlay backdrops |
| `pdu-slide-in` | Modal surface |
| `pdu-toast-in` | Toast entry |

### Utilities

| Group | Classes |
|---|---|
| Display | `.pdu-hidden`, `.pdu-block`, `.pdu-inline`, `.pdu-inline-block`, `.pdu-flex-display` |
| Margin | `.pdu-m-0`, `.pdu-m-xs`, `.pdu-m-sm`, `.pdu-m-md`, `.pdu-m-lg` |
| Padding | `.pdu-p-0`, `.pdu-p-xs`, `.pdu-p-sm`, `.pdu-p-md`, `.pdu-p-lg` |
| Directional margin | `.pdu-mt-sm`, `.pdu-mb-sm`, `.pdu-mt-md`, `.pdu-mb-md`, `.pdu-mt-lg`, `.pdu-mb-lg` |
| Text overflow | `.pdu-truncate`, `.pdu-break-word` |
| Interaction | `.pdu-pointer`, `.pdu-not-allowed` |
| Width | `.pdu-w-full`, `.pdu-w-auto` |
| Responsive visibility | `.pdu-hidden-sm`, `.pdu-hidden-md`, `.pdu-hidden-lg` |

Display and responsive visibility utilities use `!important`. Use Tailwind for utilities not covered here.

---

## 12. Tailwind CSS and shadcn/ui Integration

Every component accepts `class_name`, which is appended after its framework classes:

```python
from pydataui.html import Section, H2, P

Section(
    H2("Pipeline health", class_name="text-2xl font-semibold tracking-tight"),
    P("Updated two minutes ago", class_name="text-sm text-muted-foreground"),
    class_name="pdu-p-lg max-w-3xl mx-auto bg-card border border-border rounded-xl",
)
```

Use the layers for different jobs:

| Need | Use |
|---|---|
| Standard component appearance | Native component or `pdu-*` class |
| Application spacing, layout, responsive behavior | Tailwind utilities in `class_name` |
| Brand colors and dark-mode colors | `App(palette=...)`, `tailwind_config`, or shadcn token overrides |
| Framework primitive colors | `--pdu-*` token overrides |
| Reusable project component | Subclass `Component` and return `pdu-*` plus project classes |

### Custom Tailwind Theme Values

`App(tailwind_config={...})` deep-merges into the default Tailwind theme used by the Play CDN:

```python
app = App(
    tailwind_config={
        "theme": {
            "extend": {
                "colors": {
                    "brand": "#0ea5e9",
                },
                "fontFamily": {
                    "mono": ["Fira Code", "monospace"],
                },
            }
        }
    }
)
```

After this, `text-brand` and `font-mono` are available in `class_name` values.

### shadcn Component Styles

The shadcn components are styled with Tailwind classes and the shadcn token layer, not with `pdu-*` classes. They follow `App(theme=...)` and `App(palette=...)` directly. To style them consistently with native components, align both token layers rather than overriding individual shadcn component classes.

---

## 13. Extending the CSS Layer

### Adding a New Framework Primitive

1. Add a token to `:root` if the value should be themeable.
2. Add a `.pdu-*` rule in the appropriate numbered section of `pydataui.css`.
3. Reference existing tokens with `var(--pdu-...)` rather than repeating literal values.
4. Add a modifier class for each variant instead of writing one-off selectors in application code.
5. Test in light and dark mode, at mobile and desktop widths, and with keyboard focus.
6. Update this reference if you add a public class.

Example:

```css
.pdu-run-state {
  display: inline-flex;
  align-items: center;
  gap: var(--pdu-spacing-xs);
  padding: var(--pdu-spacing-xs) var(--pdu-spacing-sm);
  border-radius: var(--pdu-radius-full);
  background-color: var(--pdu-color-bg-secondary);
  color: var(--pdu-color-text-secondary);
  font-size: var(--pdu-font-size-xs);
  font-weight: 600;
}

.pdu-run-state-success {
  background-color: var(--pdu-color-success-light);
  color: var(--pdu-color-success-hover);
}
```

### Adding a Custom Component

Prefer composing existing classes:

```python
from pydataui import Component

class RunState(Component):
    tag = "span"

    def __init__(self, label, state="success", **kwargs):
        super().__init__(label, **kwargs)
        self.state = state

    def _get_classes(self):
        return super()._get_classes() + [
            "pdu-run-state",
            f"pdu-run-state-{self.state}",
        ]
```

If the component is reusable beyond one application, add the corresponding styles to the framework stylesheet and cover them with a rendering test. If it is application-specific, keep the CSS in `custom_css` or a stylesheet passed through `App(stylesheets=[...])`.

### Override Strategy

Choose the least invasive option that works:

| Need | Preferred approach |
|---|---|
| One instance | `class_name` with Tailwind utilities or an inline style |
| One application | `custom_css` with a scoped selector or tokens |
| Shared across applications | Framework token override or new reusable component |
| Framework bug or missing primitive | Change `pydataui.css` and add tests |

Avoid targeting generated IDs such as `#pdu-a1b2c3d4`. IDs are instance-specific and are not a stable styling contract. Use classes, semantic elements, or explicit `id` values that you control.

---

## 14. Testing CSS Changes

CSS changes should be verified at three levels:

```bash
# Unit tests for rendering and class contracts
python -m pytest -q --ignore=tests/test_browser_security.py

# Browser tests with a real browser and stylesheet
PYDATAUI_BROWSER_EXECUTABLE="/Applications/ego lite.app/Contents/MacOS/ego lite" \
PYDATAUI_REQUIRE_BROWSER=1 \
PYDATAUI_REQUIRE_REAL_STYLES=1 \
python -m pytest tests/test_browser_security.py -q

# Documentation build
python -m mkdocs build --strict
```

For a manual check:

1. Render a page in light and dark mode.
2. Resize to mobile, tablet, and desktop widths.
3. Confirm text and focus rings meet contrast expectations.
4. Check that components still work when Tailwind's CDN is unavailable; core `pdu-*` styles should remain usable.
5. Inspect the computed value of the relevant `--pdu-*` token.

---

## 15. Source Map

| What you need to change | File |
|---|---|
| Tokens, base styles, framework selectors | `pydataui/styling/css/pydataui.css` |
| Tailwind and shadcn CSS variables | `pydataui/compiler/templates.py` |
| Palette values | `pydataui/compiler/templates.py` (`PALETTES`) |
| App-level `custom_css` and `stylesheets` wiring | `pydataui/config.py`, `pydataui/app.py`, `pydataui/compiler/templates.py` |
| Component class lists | `pydataui/components/*.py` |
| CSS-related browser coverage | `tests/test_browser_security.py` |
| HTML-side rendering contract | [HTML Reference](HTML_REFERENCE.md) |
