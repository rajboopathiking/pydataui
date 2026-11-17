"""
Streamlit-Grade Developer Experience (DX) Engine for PyDataUI.

Enables zero-boilerplate, procedural Python app development for rapid prototyping
and enterprise internal tooling, backed by PyDataUI's high-performance ASGI runtime,
SSR HTMX surgical DOM swaps, session isolation, and automatic FastAPI REST engines.

Usage::

    import pydataui as pdu
    import pandas as pd

    pdu.set_page_config(title="AI & Sales Intelligence", layout="wide", theme="zinc")

    with pdu.sidebar():
        pdu.title("Controls")
        model = pdu.selectbox("Model", ["Llama-3", "GPT-4o", "DeepSeek-R1"])
        temp = pdu.slider("Temperature", 0.0, 1.0, 0.7)
        pdu.theme_toggle()

    col1, col2, col3 = pdu.columns([1, 1, 1])
    with col1:
        pdu.metric("Active Sessions", "1,420", delta="+8.2%")
    with col2:
        pdu.metric("Inference Latency", "14ms", delta="-3.1ms")
    with col3:
        pdu.metric("Throughput", "4,800 req/s", delta="+12%")

    tab1, tab2 = pdu.tabs(["Data Explorer", "Agent Chat"])
    with tab1:
        df = pd.DataFrame({"Revenue": [100, 150, 220], "Cost": [60, 80, 110]})
        pdu.write(df)
        pdu.line_chart(df)

    with tab2:
        with pdu.chat_message("assistant"):
            pdu.write("Hello! How can I assist your team today?")
        pdu.chat_input("Ask a question...")

    if __name__ == "__main__":
        pdu.run(share=True)
"""
from __future__ import annotations

import base64
import html as _html_mod
import inspect
import io
import json as _json_mod
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .app import App
from .components.advanced import Chat, CodeEditor, Markdown
from .components.base import Component, RawHtml
from .components.charts import Chart, Sparkline
from .components.data_display import Badge, DataTable, KeyValue, Stat, Table
from .components.data_science import DataFrameTable, JSONViewer, MetricCard, PlotlyChart
from .components.feedback import Alert, Progress, Spinner, Toast
from .components.forms import (
    Button,
    Checkbox,
    FileUpload,
    Input,
    Radio,
    Select,
    Slider,
    Switch,
    TextArea,
)
from .components.layout import Box, Card, Col, Container, Divider, HStack, Row, VStack
from .components.typography import Code, Heading, Paragraph, Text
from .state import EventHandler, ProceduralState, State, reactive_state, state
from .utils import escape_html, generate_id


# ============================================================================
# Dynamic Callback Host State
# ============================================================================

class ActionState(State):
    """Dynamic action state hosting procedural DX Python callbacks."""
    pass


_callbacks: Dict[str, Callable] = {}
_default_app: Optional[App] = None
_default_page_components: List[Component] = []
_sidebar_components: List[Component] = []
_container_stack: List[List[Component]] = []

_page_config: Dict[str, Any] = {
    "title": "PyDataUI App",
    "layout": "centered",  # "centered" or "wide"
    "theme": "zinc",
    "dark_mode": True,
}

# 20 Official Built-in Color Presets (all standard Shadcn / Tailwind palettes)
# Developers are NEVER limited to these: custom hex colors or full dict palettes are supported.
THEME_PRESETS: Dict[str, Dict[str, str]] = {
    "zinc": {"primary": "#18181b", "primary_hover": "#27272a", "accent": "#71717a"},
    "slate": {"primary": "#0f172a", "primary_hover": "#1e293b", "accent": "#64748b"},
    "stone": {"primary": "#1c1917", "primary_hover": "#292524", "accent": "#78716c"},
    "neutral": {"primary": "#171717", "primary_hover": "#262626", "accent": "#737373"},
    "gray": {"primary": "#111827", "primary_hover": "#1f2937", "accent": "#6b7280"},
    "emerald": {"primary": "#059669", "primary_hover": "#10b981", "accent": "#34d399"},
    "green": {"primary": "#16a34a", "primary_hover": "#22c55e", "accent": "#4ade80"},
    "teal": {"primary": "#0d9488", "primary_hover": "#14b8a6", "accent": "#2dd4bf"},
    "cyan": {"primary": "#0891b2", "primary_hover": "#06b6d4", "accent": "#22d3ee"},
    "blue": {"primary": "#2563eb", "primary_hover": "#3b82f6", "accent": "#60a5fa"},
    "indigo": {"primary": "#4f46e5", "primary_hover": "#6366f1", "accent": "#818cf8"},
    "violet": {"primary": "#7c3aed", "primary_hover": "#8b5cf6", "accent": "#a78bfa"},
    "purple": {"primary": "#9333ea", "primary_hover": "#a855f7", "accent": "#c084fc"},
    "fuchsia": {"primary": "#c026d3", "primary_hover": "#d946ef", "accent": "#e879f9"},
    "pink": {"primary": "#db2777", "primary_hover": "#ec4899", "accent": "#f472b6"},
    "rose": {"primary": "#e11d48", "primary_hover": "#f43f5e", "accent": "#fb7185"},
    "red": {"primary": "#dc2626", "primary_hover": "#ef4444", "accent": "#f87171"},
    "orange": {"primary": "#ea580c", "primary_hover": "#f97316", "accent": "#fb923c"},
    "amber": {"primary": "#d97706", "primary_hover": "#f59e0b", "accent": "#fbbf24"},
    "yellow": {"primary": "#ca8a04", "primary_hover": "#eab308", "accent": "#fde047"},
}


def _resolve_theme_css(theme: Union[str, Dict[str, str], Any]) -> str:
    """Generate dynamic CSS variable overrides for built-in presets or unlimited custom palettes."""
    if hasattr(theme, "to_css"):
        return f"<style>{theme.to_css()}</style>"

    if isinstance(theme, dict):
        lines = [f"  --pdu-color-{k}: {v}; --{k}: {v};" for k, v in theme.items()]
        return "<style>:root {\n" + "\n".join(lines) + "\n}</style>"

    if isinstance(theme, str):
        theme_clean = theme.strip().lower()
        if theme_clean in THEME_PRESETS:
            p = THEME_PRESETS[theme_clean]["primary"]
            ph = THEME_PRESETS[theme_clean]["primary_hover"]
            a = THEME_PRESETS[theme_clean]["accent"]
            return f"<style>:root {{ --primary: {p}; --primary-hover: {ph}; --accent: {a}; --pdu-color-primary: {p}; --pdu-color-primary-hover: {ph}; }}</style>"
        elif theme.startswith("#") or theme.startswith("rgb") or theme.startswith("hsl"):
            return f"<style>:root {{ --primary: {theme}; --pdu-color-primary: {theme}; }}</style>"

    return ""


def register_callback(func: Callable) -> str:
    """Register a plain Python function as an ActionState method."""
    action_id = f"act_{len(_callbacks)}_{getattr(func, '__name__', 'cb')}"
    _callbacks[action_id] = func

    def action_method(self=None, *args, **kwargs):
        cb = _callbacks.get(action_id)
        if cb:
            sig = inspect.signature(cb)
            if len(sig.parameters) == 0:
                return cb()
            has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            if has_var_keyword:
                return cb(*args, **kwargs)
            call_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            if not call_kwargs and kwargs:
                return cb(next(iter(kwargs.values())))
            return cb(**call_kwargs)

    action_method.__name__ = action_id
    setattr(ActionState, action_id, action_method)
    return action_id


# ============================================================================
# Session State Proxy (Streamlit `st.session_state` equivalent)
# ============================================================================

class SessionStateProxy:
    """
    Reactive session state proxy.
    Allows dict and attribute access (pdu.session_state.key or pdu.session_state['key']).
    In request scope, reads and writes from session.data['dx_session_state'].
    Outside request scope (e.g. initial script import), falls back to local dictionary.
    """
    def __init__(self):
        self._local_fallback: Dict[str, Any] = {}

    def _get_dict(self) -> Dict[str, Any]:
        try:
            from .request import current_request
            req = current_request.get()
            if req:
                app = get_app()
                session = app._get_session(req)
                if "dx_session_state" not in session.data:
                    session.data["dx_session_state"] = {}
                return session.data["dx_session_state"]
        except Exception:
            pass
        return self._local_fallback

    def __getattr__(self, name: str) -> Any:
        d = self._get_dict()
        if name in d:
            return d[name]
        raise AttributeError(f"session_state has no key {name!r}")

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "_local_fallback":
            super().__setattr__(name, value)
        else:
            self._get_dict()[name] = value

    def __getitem__(self, key: str) -> Any:
        return self._get_dict()[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self._get_dict()[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._get_dict()

    def get(self, key: str, default: Any = None) -> Any:
        return self._get_dict().get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        return self._get_dict().setdefault(key, default)


session_state = SessionStateProxy()


# ============================================================================
# Core Container Stack & App Engine
# ============================================================================

class _ProceduralPageLayout(Component):
    """Clean full-page layout supporting sticky sidebar and responsive main content."""
    def __init__(
        self,
        sidebar_components: List[Component],
        main_components: List[Component],
        is_wide: bool = False,
        theme_css: str = "",
    ):
        super().__init__()
        self.sidebar_components = sidebar_components
        self.main_components = main_components
        self.is_wide = is_wide
        self.theme_css = theme_css

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        theme_html = f"<style>{self.theme_css}</style>" if self.theme_css and not self.theme_css.startswith("<style>") else self.theme_css
        content_wrap = "w-full" if self.is_wide else "max-w-6xl mx-auto"
        
        main_html = "".join(c.render(state_snapshot) for c in self.main_components)

        if self.sidebar_components:
            sidebar_html = "".join(c.render(state_snapshot) for c in self.sidebar_components)
            return (
                f"{theme_html}"
                f"<div class='pdu-dx-shell flex flex-row min-h-screen w-full bg-background text-foreground' "
                f"style='display: flex !important; flex-direction: row !important; min-height: 100vh; width: 100%;'>"
                f"<aside class='w-72 min-w-[18rem] border-r border-border bg-card/60 backdrop-blur-md p-6 space-y-6 shrink-0 h-screen sticky top-0 overflow-y-auto flex flex-col justify-start z-20 shadow-sm'>"
                f"{sidebar_html}"
                f"</aside>"
                f"<div class='flex-1 min-w-0 {content_wrap} flex flex-col min-h-screen' style='flex: 1 1 0%; min-width: 0;'>"
                f"<main class='flex-1 p-6 md:p-8 space-y-6 overflow-y-auto'>{main_html}</main>"
                f"</div>"
                f"</div>"
            )
        else:
            return (
                f"{theme_html}"
                f"<div class='pdu-dx-shell min-h-screen w-full bg-background text-foreground flex flex-col' style='min-height: 100vh; width: 100%;'>"
                f"<div class='{content_wrap} p-6 md:p-8 space-y-6 flex-1'>"
                f"<main class='space-y-6'>{main_html}</main>"
                f"</div>"
                f"</div>"
            )


def get_app() -> App:
    """Return the global default App instance, initializing it if necessary."""
    global _default_app
    if _default_app is None:
        init_theme = "dark" if _page_config.get("dark_mode", True) else "light"
        init_palette = _page_config.get("theme", "zinc")
        if not isinstance(init_palette, str) or init_palette not in THEME_PRESETS:
            init_palette = "zinc"
        _default_app = App(
            title=_page_config.get("title", "PyDataUI App"),
            theme=init_theme,
            palette=init_palette,
        )

        @_default_app.page("/")
        def default_home():
            is_wide = _page_config.get("layout") == "wide"
            theme_val = _page_config.get("theme", "zinc")
            theme_css = _resolve_theme_css(theme_val)

            return _ProceduralPageLayout(
                sidebar_components=_sidebar_components,
                main_components=_default_page_components,
                is_wide=is_wide,
                theme_css=theme_css,
            )
    return _default_app


def _add_component(comp: Component) -> Component:
    """Add a component to the currently active container on the context stack."""
    get_app()  # Ensure app exists
    if _container_stack:
        _container_stack[-1].append(comp)
    else:
        _default_page_components.append(comp)
    return comp


class _ContainerContext:
    """Generic context manager for routing widgets to a specific container list."""
    def __init__(self, target_list: List[Component]):
        self.target_list = target_list

    def __enter__(self):
        _container_stack.append(self.target_list)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _container_stack and _container_stack[-1] is self.target_list:
            _container_stack.pop()


# ============================================================================
# Page Configuration & Theming
# ============================================================================

def set_page_config(
    title: Optional[str] = None,
    layout: str = "centered",
    theme: Union[str, Dict[str, str], Any] = "zinc",
    dark_mode: Optional[bool] = None,
    **kwargs
) -> None:
    """
    Configure global app metadata, responsive layout, and visual theme tokens.

    :param title: Browser window title and header.
    :param layout: "centered" (standard 5xl content width) or "wide" (full width).
    :param theme: Theme configuration. Accepts:
                  1. Any of 20 built-in presets: "zinc", "slate", "stone", "neutral", "gray",
                     "emerald", "green", "teal", "cyan", "blue", "indigo", "violet", "purple",
                     "fuchsia", "pink", "rose", "red", "orange", "amber", "yellow".
                  2. A custom hex code: e.g., "#4f46e5".
                  3. A custom dictionary palette: e.g., {"primary": "#6366f1", "bg": "#0f172a"}.
                  4. A full `Theme` instance.
    :param dark_mode: Enable dark mode by default.
    """
    if title:
        _page_config["title"] = title
    _page_config["layout"] = layout
    _page_config["theme"] = theme
    if dark_mode is not None:
        _page_config["dark_mode"] = dark_mode

    app = get_app()
    if title:
        app.config.title = title
    if dark_mode is not None:
        app.config.theme = "dark" if dark_mode else "light"
    if isinstance(theme, str) and theme.strip().lower() in THEME_PRESETS:
        app.config.palette = theme.strip().lower()


def theme_toggle(**kwargs) -> Component:
    """One-click modern dark/light theme switch button."""
    return _add_component(RawHtml(
        "<button type='button' onclick=\"document.documentElement.classList.toggle('dark'); localStorage.setItem('pdu-theme', document.documentElement.classList.contains('dark') ? 'dark' : 'light');\" "
        "class='p-2 rounded-xl border border-border hover:bg-muted text-foreground transition-all flex items-center gap-2 text-xs font-medium cursor-pointer shadow-sm'>"
        "<span>🌓</span><span>Toggle Theme</span>"
        "</button>"
    ))


# ============================================================================
# Layout Primitives & Context Managers
# ============================================================================

def sidebar() -> _ContainerContext:
    """
    Context manager to route subsequent widgets into the application sidebar.

    Example::

        with pdu.sidebar():
            pdu.title("Controls")
            pdu.slider("Temp", 0.0, 1.0)
    """
    return _ContainerContext(_sidebar_components)


class ColumnContext:
    """Context manager representing a single responsive column."""
    def __init__(self, col_span: int = 1):
        self.children: List[Component] = []
        self.col_span = col_span

    def __enter__(self):
        _container_stack.append(self.children)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _container_stack and _container_stack[-1] is self.children:
            _container_stack.pop()

    def to_component(self) -> Component:
        return Box(*self.children, class_name="flex-1 min-w-0 space-y-4")


class _ColumnWrapper(Component):
    """Wrapper that renders multiple ColumnContext children side by side."""
    def __init__(self, cols: List[ColumnContext]):
        super().__init__()
        self.cols = cols

    def render(self, state_snapshot=None) -> str:
        cols_html = "".join(
            f"<div class='flex-1 min-w-0 space-y-4'>{c.to_component().render(state_snapshot)}</div>"
            for c in self.cols
        )
        return f"<div class='flex flex-col md:flex-row gap-6 w-full items-start my-3'>{cols_html}</div>"


def columns(spec: Union[int, List[Union[int, float]]]) -> List[ColumnContext]:
    """
    Split the current layout into flexible side-by-side columns.

    Example::

        col1, col2 = pdu.columns([1, 2])
        with col1:
            pdu.metric("Users", "10,400")
        with col2:
            pdu.line_chart(user_growth)
    """
    if isinstance(spec, int):
        spec = [1] * spec
    cols = [ColumnContext(int(w)) for w in spec]
    _add_component(_ColumnWrapper(cols))
    return cols


class _ExpanderWrapper(Component):
    """Wrapper that renders a styled, accessible HTML5 details/summary accordion."""
    def __init__(self, label: str, expanded: bool, children: List[Component]):
        super().__init__()
        self.label = label
        self.expanded = expanded
        self.children_list = children

    def render(self, state_snapshot=None) -> str:
        rendered_children = "".join(c.render(state_snapshot) for c in self.children_list)
        open_attr = " open" if self.expanded else ""
        return (
            f"<details class='pdu-expander border border-border rounded-xl bg-card/60 shadow-sm transition-all my-3'{open_attr}>"
            f"<summary class='px-4 py-3 font-medium cursor-pointer text-sm select-none hover:bg-muted/40 transition-colors rounded-xl flex items-center justify-between text-foreground'>"
            f"<span>{escape_html(self.label)}</span>"
            f"<span class='text-muted-foreground text-xs'>▼</span>"
            f"</summary>"
            f"<div class='px-4 py-4 border-t border-border/50 space-y-4'>{rendered_children}</div>"
            f"</details>"
        )


class _ExpanderContext:
    def __init__(self, label: str, expanded: bool = False):
        self.label = label
        self.expanded = expanded
        self.children: List[Component] = []

    def __enter__(self):
        _container_stack.append(self.children)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _container_stack and _container_stack[-1] is self.children:
            _container_stack.pop()


def expander(label: str, expanded: bool = False) -> _ExpanderContext:
    """
    Context manager to wrap widgets in a collapsible accordion panel.

    Example::

        with pdu.expander("Raw API JSON Response", expanded=False):
            pdu.write(raw_payload)
    """
    ctx = _ExpanderContext(label, expanded)
    _add_component(_ExpanderWrapper(label, expanded, ctx.children))
    return ctx


class _TabsWrapper(Component):
    """Client-side zero-latency tab switcher."""
    def __init__(self, tab_names: List[str], tab_contexts: List[ColumnContext]):
        super().__init__()
        self.tab_names = tab_names
        self.tab_contexts = tab_contexts
        self.tab_id = generate_id("tabs")

    def render(self, state_snapshot=None) -> str:
        headers = []
        panels = []
        for i, (name, ctx) in enumerate(zip(self.tab_names, self.tab_contexts)):
            active_class = "border-primary text-primary font-semibold" if i == 0 else "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
            display_style = "block" if i == 0 else "none"
            panel_id = f"{self.tab_id}-panel-{i}"
            btn_id = f"{self.tab_id}-btn-{i}"

            headers.append(
                f"<button id='{btn_id}' "
                f"onclick=\"(function(){{"
                f"  const parent = document.getElementById('{self.tab_id}');"
                f"  parent.querySelectorAll('.pdu-tab-btn').forEach(b => b.className = b.className.replace('border-primary text-primary font-semibold', 'border-transparent text-muted-foreground'));"
                f"  document.getElementById('{btn_id}').className += ' border-primary text-primary font-semibold';"
                f"  parent.querySelectorAll('.pdu-tab-panel').forEach(p => p.style.display = 'none');"
                f"  document.getElementById('{panel_id}').style.display = 'block';"
                f"}})()\" "
                f"class='pdu-tab-btn px-4 py-2.5 text-sm font-medium border-b-2 transition-all cursor-pointer {active_class}'>"
                f"{escape_html(name)}"
                f"</button>"
            )

            rendered_children = "".join(c.render(state_snapshot) for c in ctx.children)
            panels.append(
                f"<div id='{panel_id}' class='pdu-tab-panel p-4 space-y-4' style='display: {display_style};'>"
                f"{rendered_children}"
                f"</div>"
            )

        return (
            f"<div id='{self.tab_id}' class='w-full my-4 border border-border rounded-xl bg-card overflow-hidden shadow-sm'>"
            f"<div class='flex border-b border-border bg-muted/20 px-2'>{''.join(headers)}</div>"
            f"{''.join(panels)}"
            f"</div>"
        )


def tabs(tab_names: List[str]) -> List[ColumnContext]:
    """
    Create an interactive tabbed view container.

    Example::

        tab_data, tab_chat = pdu.tabs(["Data View", "Agent Chat"])
        with tab_data:
            pdu.write(df)
        with tab_chat:
            pdu.write("Chat history...")
    """
    contexts = [ColumnContext() for _ in tab_names]
    _add_component(_TabsWrapper(tab_names, contexts))
    return contexts


def container() -> _ContainerContext:
    """Create a scoped container context."""
    cont_list: List[Component] = []
    _add_component(Box(cont_list, class_name="w-full space-y-4 my-2"))
    return _ContainerContext(cont_list)


# ============================================================================
# Polymorphic Auto-Inspector: `pdu.write()`
# ============================================================================

def write(*args: Any, **kwargs: Any) -> None:
    """
    Polymorphic auto-renderer. Automatically inspects passed objects and renders
    the optimal interactive component (DataFrames, Plotly, JSON, Markdown, Images, Text).

    Example::

        pdu.write("# Report Header")  # Rendered as Markdown
        pdu.write(df)                 # Rendered as interactive paginated table
        pdu.write({"status": "ok"})   # Rendered as interactive JSON tree viewer
        pdu.write(fig)                # Rendered as interactive Plotly or Matplotlib chart
    """
    for obj in args:
        if isinstance(obj, Component):
            _add_component(obj)
        elif hasattr(obj, "to_pandas") or hasattr(obj, "iloc") or (type(obj).__name__ in ("DataFrame", "Table")):
            dataframe(obj, **kwargs)
        elif hasattr(obj, "to_plotly_json") or type(obj).__name__ == "Figure":
            plotly_chart(obj, **kwargs)
        elif hasattr(obj, "savefig") or hasattr(obj, "figure"):
            pyplot(obj, **kwargs)
        elif isinstance(obj, (dict, list)):
            json(obj, **kwargs)
        elif isinstance(obj, str):
            if any(sig in obj for sig in ("# ", "## ", "```", "* ", "- ", "1. ", "**", "|")):
                markdown(obj, **kwargs)
            else:
                text(obj, **kwargs)
        else:
            text(str(obj), **kwargs)


# ============================================================================
# Typography & Code
# ============================================================================

def title(text_content: str, **kwargs) -> Heading:
    """Add a top-level page title (H1)."""
    app = get_app()
    app.config.title = text_content
    return _add_component(Heading(text_content, level=1, class_name="text-3xl font-bold tracking-tight text-foreground", **kwargs))


def header(text_content: str, **kwargs) -> Heading:
    """Add a section header (H2)."""
    return _add_component(Heading(text_content, level=2, class_name="text-2xl font-semibold tracking-tight text-foreground", **kwargs))


def subheader(text_content: str, **kwargs) -> Heading:
    """Add a section subheader (H3)."""
    return _add_component(Heading(text_content, level=3, class_name="text-xl font-medium tracking-tight text-foreground", **kwargs))


def caption(text_content: str, **kwargs) -> Text:
    """Add small caption text."""
    return _add_component(Text(text_content, class_name="text-xs text-muted-foreground", **kwargs))


def text(content: str, **kwargs) -> Text:
    """Add body text element."""
    return _add_component(Text(content, class_name="text-sm text-foreground leading-relaxed", **kwargs))


def markdown(content: str, **kwargs) -> Markdown:
    """Add rendered GitHub-flavored markdown."""
    return _add_component(Markdown(content, **kwargs))


def code(content: str, language: str = "python", **kwargs) -> Code:
    """Add a styled code block."""
    return _add_component(Code(content, language=language, **kwargs))


# ============================================================================
# Metric & KPI Display
# ============================================================================

def metric(
    label: str,
    value: Any,
    delta: Optional[str] = None,
    delta_color: str = "normal",
    change: Optional[str] = None,
    **kwargs
) -> MetricCard:
    """
    Render a high-impact KPI metric card with value, optional change delta, and badges.

    :param label: Title of the metric.
    :param value: Main display value (e.g., "$45,200", "1.4M").
    :param delta: Change indicator (e.g., "+12.4%", "-2.1ms").
    :param delta_color: "normal", "inverse", or "off".
    """
    d = delta if delta is not None else change
    delta_type = "positive" if (d and str(d).startswith("+")) else ("negative" if (d and str(d).startswith("-")) else "neutral")
    if delta_color == "inverse":
        delta_type = "negative" if delta_type == "positive" else "positive"
    return _add_component(MetricCard(title=label, value=value, delta=d or "", delta_type=delta_type, **kwargs))


# ============================================================================
# Status & Feedback Notifications
# ============================================================================

def success(message: str, icon: str = "✓") -> Component:
    """Display a green success banner."""
    return _add_component(RawHtml(
        f"<div class='p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-600 dark:text-emerald-400 flex items-center gap-3 text-sm my-2 shadow-sm'>"
        f"<span class='font-bold select-none'>{escape_html(icon)}</span><span>{escape_html(message)}</span></div>"
    ))


def info(message: str, icon: str = "ℹ") -> Component:
    """Display a blue informational banner."""
    return _add_component(RawHtml(
        f"<div class='p-4 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-600 dark:text-blue-400 flex items-center gap-3 text-sm my-2 shadow-sm'>"
        f"<span class='font-bold select-none'>{escape_html(icon)}</span><span>{escape_html(message)}</span></div>"
    ))


def warning(message: str, icon: str = "⚠") -> Component:
    """Display an amber warning banner."""
    return _add_component(RawHtml(
        f"<div class='p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-600 dark:text-amber-400 flex items-center gap-3 text-sm my-2 shadow-sm'>"
        f"<span class='font-bold select-none'>{escape_html(icon)}</span><span>{escape_html(message)}</span></div>"
    ))


def error(message: str, icon: str = "✕") -> Component:
    """Display a red error banner."""
    return _add_component(RawHtml(
        f"<div class='p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-600 dark:text-rose-400 flex items-center gap-3 text-sm my-2 shadow-sm'>"
        f"<span class='font-bold select-none'>{escape_html(icon)}</span><span>{escape_html(message)}</span></div>"
    ))


def toast(message: str, icon: str = "🔔") -> Component:
    """Trigger a floating toast banner."""
    return _add_component(RawHtml(
        f"<div class='pdu-toast fixed bottom-6 right-6 z-50 bg-foreground text-background px-4 py-3 rounded-xl shadow-2xl flex items-center gap-3 text-sm font-medium animate-bounce'>"
        f"<span>{escape_html(icon)}</span><span>{escape_html(message)}</span></div>"
    ))


class _SpinnerContext:
    def __init__(self, text_msg: str = "Loading..."):
        self.text_msg = text_msg

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def spinner(text_msg: str = "Loading...") -> _SpinnerContext:
    """Context manager for long-running operations."""
    return _SpinnerContext(text_msg)


def progress(value: int, text_label: str = "") -> Component:
    """Display a smooth progress bar."""
    return _add_component(Progress(value=value, max=100, show_label=bool(text_label)))


# ============================================================================
# Interactive Charts & Data Science Visualizations
# ============================================================================

def _normalize_chart_data(data: Any, chart_type: str = "line") -> Dict[str, Any]:
    """Helper to convert Pandas, list, or dict structures into Chart.js format."""
    colors = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4"]

    # 1. Pandas DataFrame
    if hasattr(data, "columns") and hasattr(data, "values"):
        labels = [str(x) for x in data.index]
        datasets = []
        for i, col in enumerate(data.columns):
            color = colors[i % len(colors)]
            datasets.append({
                "label": str(col),
                "data": [None if (v != v) else v for v in data[col].tolist()],
                "borderColor": color,
                "backgroundColor": color + "33" if chart_type in ("area", "bar") else color,
                "fill": chart_type == "area",
            })
        return {"labels": labels, "datasets": datasets}

    # 2. List or Tuple of numbers
    if isinstance(data, (list, tuple)):
        labels = [str(i + 1) for i in range(len(data))]
        return {
            "labels": labels,
            "datasets": [{
                "label": "Value",
                "data": list(data),
                "borderColor": "#3b82f6",
                "backgroundColor": "#3b82f633" if chart_type in ("area", "bar") else "#3b82f6",
                "fill": chart_type == "area",
            }],
        }

    # 3. Dict of series: {"A": [1, 2, 3], "B": [4, 5, 6]}
    if isinstance(data, dict):
        datasets = []
        max_len = 0
        for i, (k, vals) in enumerate(data.items()):
            if isinstance(vals, (list, tuple)):
                max_len = max(max_len, len(vals))
                color = colors[i % len(colors)]
                datasets.append({
                    "label": str(k),
                    "data": list(vals),
                    "borderColor": color,
                    "backgroundColor": color + "33" if chart_type in ("area", "bar") else color,
                    "fill": chart_type == "area",
                })
        labels = [str(i + 1) for i in range(max_len)]
        return {"labels": labels, "datasets": datasets}

    return {"labels": [], "datasets": []}


def line_chart(data: Any, width: Optional[str] = None, height: str = "320px", **kwargs) -> Chart:
    """Render a responsive multi-series line chart."""
    chart_data = _normalize_chart_data(data, "line")
    return _add_component(Chart(type="line", data=chart_data, width=width, height=height, **kwargs))


def bar_chart(data: Any, width: Optional[str] = None, height: str = "320px", **kwargs) -> Chart:
    """Render a responsive bar chart."""
    chart_data = _normalize_chart_data(data, "bar")
    return _add_component(Chart(type="bar", data=chart_data, width=width, height=height, **kwargs))


def area_chart(data: Any, width: Optional[str] = None, height: str = "320px", **kwargs) -> Chart:
    """Render a responsive filled area chart."""
    chart_data = _normalize_chart_data(data, "area")
    return _add_component(Chart(type="line", data=chart_data, width=width, height=height, **kwargs))


def scatter_chart(data: Any, width: Optional[str] = None, height: str = "320px", **kwargs) -> Chart:
    """Render a responsive scatter chart."""
    chart_data = _normalize_chart_data(data, "scatter")
    return _add_component(Chart(type="scatter", data=chart_data, width=width, height=height, **kwargs))


def plotly_chart(figure: Any, use_container_width: bool = True, height: int = 400, **kwargs) -> Component:
    """Render an interactive Plotly figure."""
    return _add_component(PlotlyChart(figure=figure, height=height, **kwargs))


def pyplot(fig: Any = None, **kwargs) -> Component:
    """Render a Matplotlib or Seaborn figure cleanly as high-res PNG."""
    if fig is None:
        try:
            import matplotlib.pyplot as plt
            fig = plt.gcf()
        except Exception:
            return _add_component(Text("Matplotlib is not installed. Run: pip install matplotlib"))
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    return _add_component(RawHtml(f"<img src='data:image/png;base64,{b64}' class='rounded-xl border border-border shadow-sm max-w-full my-3' />"))


def dataframe(df: Any, max_rows: int = 100, **kwargs) -> DataFrameTable:
    """Render a Pandas / Polars DataFrame as an interactive, styled table."""
    if hasattr(df, "to_pandas") and not hasattr(df, "iloc"):
        try:
            df = df.to_pandas()
        except Exception:
            pass
    return _add_component(DataFrameTable(df=df, max_rows=max_rows, **kwargs))


def table(data: Any, columns: Optional[List[str]] = None, **kwargs) -> DataTable:
    """Render a structured data table."""
    return _add_component(DataTable(data=data, columns=columns, **kwargs))


def read_csv(source: Any, **kwargs) -> Any:
    """
    Convenience helper to read CSV data from an UploadedFile, string, bytes, or file path into a pandas DataFrame.

    Example::

        def handle_upload(file):
            df = pdu.read_csv(file)  # or pd.read_csv(file)
            pdu.session_state.df = df
    """
    import io
    import pandas as pd
    if hasattr(source, "to_pandas"):
        return source.to_pandas(**kwargs)
    if hasattr(source, "content"):
        return pd.read_csv(io.BytesIO(source.content), **kwargs)
    if isinstance(source, bytes):
        return pd.read_csv(io.BytesIO(source), **kwargs)
    if isinstance(source, str):
        if "\n" in source or "," in source:
            return pd.read_csv(io.StringIO(source), **kwargs)
        return pd.read_csv(source, **kwargs)
    return pd.read_csv(source, **kwargs)


def json(data: Any, max_height: str = "400px", **kwargs) -> Component:
    """Render an interactive, collapsible JSON tree viewer."""
    return _add_component(JSONViewer(data=data, max_height=max_height, **kwargs))


# ============================================================================
# Input Widgets
# ============================================================================

def button(label: str, on_click: Optional[Union[Callable, EventHandler]] = None, **kwargs) -> Button:
    """Add an interactive button with a Python event callback."""
    return _add_component(Button(label, on_click=on_click, **kwargs))


def text_input(
    label: str = "",
    value: Any = "",
    placeholder: str = "",
    key: Optional[str] = None,
    type: str = "text",
    on_change: Optional[Callable] = None,
    **kwargs
) -> Input:
    """Add a single-line text input field."""
    return _add_component(Input(label=label, value=value, placeholder=placeholder, name=key, type=type, on_change=on_change, **kwargs))


input = text_input


def text_area(
    label: str = "",
    value: Any = "",
    placeholder: str = "",
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> TextArea:
    """Add a multiline text area."""
    return _add_component(TextArea(label=label, value=value, placeholder=placeholder, name=key, on_change=on_change, **kwargs))


textarea = text_area


def number_input(
    label: str = "",
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    value: float = 0,
    step: Optional[float] = None,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Input:
    """Add a numerical input widget."""
    if step is None:
        if any(isinstance(x, float) for x in (min_value, max_value, value)):
            step = 0.01
        else:
            step = 1
    return _add_component(Input(label=label, value=value, type="number", min=min_value, max=max_value, step=step, name=key, on_change=on_change, **kwargs))


def slider(
    label: str = "",
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    value: Optional[float] = None,
    step: Optional[float] = None,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Slider:
    """
    Add an interactive slider widget supporting both integer and floating-point ranges.

    If min_value, max_value, or value is a float and step is omitted, step automatically
    defaults to 0.01 (or 0.1 for ranges <= 10.0), matching Streamlit behavior.
    """
    is_float = any(isinstance(x, float) for x in (min_value, max_value, value, step) if x is not None)
    if min_value is None:
        min_value = 0.0 if is_float else 0
    if max_value is None:
        max_value = 100.0 if is_float else 100
    if value is None:
        value = min_value
    if step is None:
        if is_float or any(isinstance(x, float) for x in (min_value, max_value, value)):
            diff = abs(max_value - min_value)
            step = 0.01 if diff <= 1.0 else (0.1 if diff <= 10.0 else 0.01)
        else:
            step = 1
    return _add_component(Slider(label=label, min=min_value, max=max_value, value=value, step=step, name=key, on_change=on_change, **kwargs))


def selectbox(
    label: str = "",
    options: Optional[List[Any]] = None,
    index: int = 0,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Select:
    """Add a dropdown selectbox widget."""
    opts = options or []
    val = opts[index] if (opts and 0 <= index < len(opts)) else None
    return _add_component(Select(label=label, options=opts, value=val, name=key, on_change=on_change, **kwargs))


def multiselect(
    label: str = "",
    options: Optional[List[Any]] = None,
    default: Optional[List[Any]] = None,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Select:
    """Add a multi-select dropdown widget."""
    return _add_component(Select(label=label, options=options or [], value=default, multiple=True, name=key, on_change=on_change, **kwargs))


def checkbox(
    label: str = "",
    value: bool = False,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Checkbox:
    """Add a checkbox toggle widget."""
    return _add_component(Checkbox(label=label, checked=value, name=key, on_change=on_change, **kwargs))


def radio(
    label: str = "",
    options: Optional[List[Any]] = None,
    index: int = 0,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Component:
    """Add a radio button selection group."""
    opts = options or []
    selected = opts[index] if (opts and 0 <= index < len(opts)) else None
    radios = [Radio(label=str(opt), value=opt, checked=(opt == selected), name=key, on_change=on_change) for opt in opts]
    return _add_component(VStack(Text(label, class_name="font-medium text-sm"), *radios, class_name="space-y-2 my-2"))


def switch(
    label: str = "",
    value: bool = False,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Switch:
    """Add a toggle switch widget."""
    return _add_component(Switch(label=label, checked=value, name=key, on_change=on_change, **kwargs))


toggle = switch


def file_uploader(
    label: str = "Choose file",
    accept: Optional[List[str]] = None,
    multiple: bool = False,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> FileUpload:
    """
    Add a drag-and-drop file upload input.

    When a file is uploaded, it is automatically saved to `session_state[key]`
    and passed directly to `on_change(file)` if provided.
    """
    input_name = key or "file"

    def _file_callback(file=None, **kws):
        val = file or (next(iter(kws.values())) if kws else None)
        if key:
            session_state[key] = val
        session_state["last_uploaded_file"] = val
        if on_change:
            sig = inspect.signature(on_change)
            if len(sig.parameters) == 0:
                return on_change()
            call_k = {k: v for k, v in kws.items() if k in sig.parameters}
            if not call_k and len(sig.parameters) == 1:
                return on_change(val)
            return on_change(**call_k)

    cb = _file_callback if (on_change or key) else None
    return _add_component(FileUpload(label=label, accept=accept, multiple=multiple, name=input_name, on_change=cb, **kwargs))


# ============================================================================
# AI & Chat Primitives
# ============================================================================

class _ChatMessageWrapper(Component):
    """Wrapper that renders a chat bubble for user or AI assistant."""
    def __init__(self, name: str, avatar: Optional[str], children: List[Component]):
        super().__init__()
        self.name = name.lower()
        self.avatar = avatar
        self.children_list = children

    def render(self, state_snapshot=None) -> str:
        is_user = self.name == "user"
        align = "justify-end" if is_user else "justify-start"
        bubble_bg = "bg-primary text-primary-foreground" if is_user else "bg-muted text-foreground border border-border/50"
        default_avatar = "👤" if is_user else "🤖"
        avatar_content = self.avatar or default_avatar
        rendered_children = "".join(c.render(state_snapshot) for c in self.children_list)

        if is_user:
            bot_avatar = ""
            user_avatar = f"<div class='w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center text-sm shrink-0 select-none shadow-sm'>{avatar_content}</div>"
        else:
            bot_avatar = f"<div class='w-8 h-8 rounded-full bg-muted flex items-center justify-center text-sm shrink-0 select-none shadow-sm'>{avatar_content}</div>"
            user_avatar = ""

        return (
            f"<div class='flex gap-3 my-3 {align} items-start'>"
            f"{bot_avatar}"
            f"<div class='max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-sm space-y-2 {bubble_bg}'>"
            f"{rendered_children}"
            f"</div>"
            f"{user_avatar}"
            f"</div>"
        )


class _ChatMessageContext:
    def __init__(self, name: str, avatar: Optional[str] = None):
        self.name = name
        self.avatar = avatar
        self.children: List[Component] = []

    def __enter__(self):
        _container_stack.append(self.children)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _container_stack and _container_stack[-1] is self.children:
            _container_stack.pop()


def chat_message(name: str = "assistant", avatar: Optional[str] = None) -> _ChatMessageContext:
    """
    Context manager to render a conversational message bubble (user or assistant).

    Example::

        with pdu.chat_message("user"):
            pdu.write("Explain RAG.")

        with pdu.chat_message("assistant"):
            pdu.write("Retrieval-Augmented Generation is...")
    """
    ctx = _ChatMessageContext(name, avatar)
    _add_component(_ChatMessageWrapper(name, avatar, ctx.children))
    return ctx


def chat_input(
    placeholder: str = "Type a message...",
    key: Optional[str] = None,
    on_submit: Optional[Callable] = None,
    **kwargs
) -> Component:
    """
    Add a sleek, modern chat input prompt bar.

    When submitted, user input is passed to `on_submit(prompt)` and automatically
    stored in `pdu.session_state[key]` and `pdu.session_state["last_chat_input"]`.
    The input bar auto-resets on submit.
    """
    input_id = key or generate_id("chat_input")
    action_attr = ""
    if on_submit or key:
        def _chat_callback(msg=None, **kws):
            text_val = msg or (next(iter(kws.values())) if kws else "")
            if key:
                session_state[key] = text_val
            session_state["last_chat_input"] = text_val
            if on_submit:
                sig = inspect.signature(on_submit)
                if len(sig.parameters) == 0:
                    return on_submit()
                call_k = {k: v for k, v in kws.items() if k in sig.parameters}
                if not call_k and len(sig.parameters) == 1:
                    return on_submit(text_val)
                return on_submit(**call_k)

        action_name = register_callback(_chat_callback)
        action_attr = f'hx-post="/_pdu/event/ActionState/{action_name}" hx-trigger="submit" hx-include="this" hx-on::after-request="this.reset()"'

    form_id = f"form_{input_id}"
    return _add_component(RawHtml(
        f"<form id='{form_id}' class='flex gap-2 items-center w-full my-4 p-2 bg-card border border-border rounded-2xl shadow-sm focus-within:ring-2 focus-within:ring-primary/40 transition-all' {action_attr}>"
        f"<input type='text' name='{input_id}' placeholder='{escape_html(placeholder)}' autocomplete='off' "
        f"class='flex-1 bg-transparent px-3 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none' />"
        f"<button type='submit' class='p-2 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity cursor-pointer flex items-center justify-center'>"
        f"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m22 2-7 20-4-9-9-4Z'/><path d='M22 2 11 13'/></svg>"
        f"</button>"
        f"</form>"
    ))


def chat(messages: Optional[List[Dict[str, str]]] = None, on_send: Optional[Callable] = None, **kwargs) -> Chat:
    """Add an interactive composite Chat interface component."""
    return _add_component(Chat(messages=messages, on_send=on_send, **kwargs))


# ============================================================================
# Structural Containers & Layout Helpers
# ============================================================================

def card(*children: Component, **kwargs) -> Card:
    """Add an elevated card container."""
    return _add_component(Card(*children, **kwargs))


def row(*children: Component, **kwargs) -> HStack:
    """Add a horizontal layout row."""
    return _add_component(HStack(*children, **kwargs))


def column(*children: Component, **kwargs) -> VStack:
    """Add a vertical layout column."""
    return _add_component(VStack(*children, **kwargs))


def divider(**kwargs) -> Divider:
    """Add a visual divider line."""
    return _add_component(Divider(**kwargs))


def code_editor(
    code_content: str = "",
    language: str = "python",
    theme: str = "dark",
    on_change: Optional[Callable] = None,
    **kwargs
) -> CodeEditor:
    """Add an interactive code editor."""
    return _add_component(CodeEditor(code=code_content, language=language, theme=theme, on_change=on_change, **kwargs))


# ============================================================================
# Application Lifecycle & Runner
# ============================================================================

def page(path: str = "/", title: Optional[str] = None, **kwargs):
    """Decorator to register a custom page route on the default application."""
    app = get_app()
    return app.page(path, title=title, **kwargs)


def run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False, share: bool = False, **kwargs) -> None:
    """
    Launch the high-performance ASGI application server.

    :param host: Host address to bind (default 127.0.0.1).
    :param port: Port number to bind (default 8000).
    :param reload: Enable auto-reloading during development.
    :param share: Launch zero-config public HTTPS tunnel (e.g. for demos).
    """
    app = get_app()
    app.run(host=host, port=port, reload=reload, share=share, **kwargs)


def reset() -> None:
    """Reset the global procedural DX state (useful for test isolation or script re-execution)."""
    global _default_app, _default_page_components, _sidebar_components, _container_stack, _callbacks
    _default_app = None
    _default_page_components.clear()
    _sidebar_components.clear()
    _container_stack.clear()
    _callbacks.clear()
    _page_config.update({
        "title": "PyDataUI App",
        "layout": "centered",
        "theme": "zinc",
        "dark_mode": True,
    })


get_default_app = get_app
