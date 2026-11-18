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
from contextvars import ContextVar
import copy
import functools
import hashlib
import html as _html_mod
import inspect
import io
import json as _json_mod
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .app import App
from .components.advanced import Chat, CodeEditor, Markdown
from .components.base import Component, RawHtml
from .components.charts import Chart, Sparkline
from .components.data_display import Badge, DataTable, KeyValue, Stat, Table, Tooltip
from .components.media import Image, Video, Audio, Icon
from .components.navigation import Navbar, Breadcrumb, Tabs, Tab, NavLink, Sidebar
from .components.overlay import Popover, Modal, Drawer, Dropdown
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
from .components.layout import Box, Card, Col, Container, Divider, HStack, Row, VStack, Flex, Grid, Spacer
from .components.typography import Code, Heading, Paragraph, Text
from .responses import HTMLResponse, RedirectResponse, Response
from .state import EventHandler, ProceduralState, State, _is_event_handling, reactive_state, state
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
_active_container_stack: ContextVar[Optional[List[List[Component]]]] = ContextVar("_active_container_stack", default=None)
_active_page_sidebar: ContextVar[Optional[List[Component]]] = ContextVar("_active_page_sidebar", default=None)
_active_form_stack: List[Any] = []


def _get_container_stack() -> List[List[Component]]:
    """Retrieve the isolated container context stack for current async request, falling back to global."""
    stack = _active_container_stack.get()
    if stack is None:
        return _container_stack
    return stack

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


def _hex_to_hsl_str(hex_code: str) -> str:
    """Convert hex color (#4f46e5 or #fff) to Tailwind/Shadcn HSL string 'H S% L%'."""
    hex_clean = hex_code.lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    try:
        r = int(hex_clean[0:2], 16) / 255.0
        g = int(hex_clean[2:4], 16) / 255.0
        b = int(hex_clean[4:6], 16) / 255.0
    except (ValueError, IndexError):
        return "221.2 83.2% 53.3%"
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c
    l = (max_c + min_c) / 2.0
    if delta == 0:
        h, s = 0.0, 0.0
    else:
        s = delta / (1.0 - abs(2.0 * l - 1.0)) if (1.0 - abs(2.0 * l - 1.0)) != 0 else 0
        if max_c == r:
            h = 60.0 * (((g - b) / delta) % 6)
        elif max_c == g:
            h = 60.0 * (((b - r) / delta) + 2)
        else:
            h = 60.0 * (((r - g) / delta) + 4)
    return f"{round(h, 1)} {round(s * 100, 1)}% {round(l * 100, 1)}%"


def _hex_lightness(hex_code: str) -> float:
    """Return relative perceptual lightness (0.0 to 1.0) of a hex color."""
    hex_clean = hex_code.lstrip("#")
    if len(hex_clean) == 3:
        hex_clean = "".join(c * 2 for c in hex_clean)
    try:
        r = int(hex_clean[0:2], 16) / 255.0
        g = int(hex_clean[2:4], 16) / 255.0
        b = int(hex_clean[4:6], 16) / 255.0
    except Exception:
        return 0.5
    return (max(r, g, b) + min(r, g, b)) / 2.0


def _resolve_theme_css(theme: Union[str, Dict[str, str], Any]) -> str:
    """Generate dynamic CSS variable overrides for built-in presets or unlimited custom palettes."""
    if hasattr(theme, "to_css"):
        return f"<style>{theme.to_css()}</style>"

    if isinstance(theme, dict):
        lines = []
        for k, v in theme.items():
            lines.append(f"  --pdu-color-{k}: {v} !important;")
            lines.append(f"  --{k}: {v} !important;")

        p = theme.get("primary")
        if p and p.startswith("#"):
            hsl_p = _hex_to_hsl_str(p)
            lines.append(f"  --primary: {hsl_p} !important;")
            lines.append(f"  --ring: {hsl_p} !important;")

        accent = theme.get("accent")
        if accent and accent.startswith("#"):
            hsl_accent = _hex_to_hsl_str(accent)
            lines.append(f"  --accent: {hsl_accent} !important;")

        bg = theme.get("bg") or theme.get("background")
        if bg and bg.startswith("#"):
            hsl_bg = _hex_to_hsl_str(bg)
            lines.append(f"  --background: {hsl_bg} !important;")
            lines.append(f"  --pdu-color-bg: {bg} !important;")
            is_light_bg = _hex_lightness(bg) > 0.5
            if is_light_bg:
                if "foreground" not in theme and "text" not in theme:
                    lines.append("  --foreground: 222.2 47.4% 11.2% !important;")
                    lines.append("  --pdu-color-text: #0f172a !important;")
                if "card" not in theme:
                    lines.append("  --card: 0 0% 100% !important;")
                    lines.append("  --card-foreground: 222.2 47.4% 11.2% !important;")
                    lines.append("  --pdu-color-card: #ffffff !important;")
                lines.append("  --border: 214.3 31.8% 88% !important;")
                lines.append("  --muted: 210 40% 96.1% !important;")
                lines.append("  --muted-foreground: 215.4 16.3% 46.9% !important;")
            else:
                if "foreground" not in theme and "text" not in theme:
                    lines.append("  --foreground: 210 40% 98% !important;")
                    lines.append("  --pdu-color-text: #f8fafc !important;")
                if "card" not in theme:
                    lines.append("  --card: 222.2 47.4% 11.2% !important;")
                    lines.append("  --card-foreground: 210 40% 98% !important;")
                    lines.append("  --pdu-color-card: #0f172a !important;")

        card = theme.get("card")
        if card and card.startswith("#"):
            hsl_card = _hex_to_hsl_str(card)
            lines.append(f"  --card: {hsl_card} !important;")
            lines.append(f"  --pdu-color-card: {card} !important;")

        text_col = theme.get("text") or theme.get("foreground")
        if text_col and text_col.startswith("#"):
            hsl_text = _hex_to_hsl_str(text_col)
            lines.append(f"  --foreground: {hsl_text} !important;")
            lines.append(f"  --pdu-color-text: {text_col} !important;")

        global_shell_override = ""
        if bg and bg.startswith("#"):
            text_val = theme.get("text") or ("#0f172a" if _hex_lightness(bg) > 0.5 else "#f8fafc")
            global_shell_override = (
                f"\nhtml, body, .pdu-dx-shell {{\n"
                f"  background-color: {bg} !important;\n"
                f"  color: {text_val} !important;\n"
                f"}}"
            )

        return (
            "<style>:root, .dark, [data-theme='dark'] {\n"
            + "\n".join(lines)
            + "\n}"
            + global_shell_override
            + "\n</style>"
        )

    if isinstance(theme, str):
        theme_clean = theme.strip().lower()
        if theme_clean in THEME_PRESETS:
            p = THEME_PRESETS[theme_clean]["primary"]
            ph = THEME_PRESETS[theme_clean]["primary_hover"]
            a = THEME_PRESETS[theme_clean]["accent"]
            hsl_p = _hex_to_hsl_str(p)
            hsl_a = _hex_to_hsl_str(a)
            return (
                f"<style>:root, .dark, [data-theme='dark'] {{\n"
                f"  --primary: {hsl_p} !important;\n"
                f"  --ring: {hsl_p} !important;\n"
                f"  --accent: {hsl_a} !important;\n"
                f"  --pdu-color-primary: {p} !important;\n"
                f"  --pdu-color-primary-hover: {ph} !important;\n"
                f"  --pdu-color-accent: {a} !important;\n"
                f"}}</style>"
            )
        elif theme.startswith("#"):
            hsl_p = _hex_to_hsl_str(theme)
            return (
                f"<style>:root, .dark, [data-theme='dark'] {{\n"
                f"  --primary: {hsl_p} !important;\n"
                f"  --ring: {hsl_p} !important;\n"
                f"  --pdu-color-primary: {theme} !important;\n"
                f"}}</style>"
            )

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
            if not call_kwargs and kwargs and len(sig.parameters) == 1:
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
            from .state import _current_session
            sess = _current_session.get()
            if sess:
                if "dx_session_state" not in sess.data:
                    sess.data["dx_session_state"] = {}
                return sess.data["dx_session_state"]
        except Exception:
            pass
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

    def __delitem__(self, key: str) -> None:
        del self._get_dict()[key]

    def __contains__(self, key: str) -> bool:
        return key in self._get_dict()

    def __len__(self) -> int:
        return len(self._get_dict())

    def __iter__(self):
        return iter(self._get_dict())

    def __repr__(self) -> str:
        return repr(self._get_dict())

    def get(self, key: str, default: Any = None) -> Any:
        return self._get_dict().get(key, default)

    def setdefault(self, key: str, default: Any = None) -> Any:
        return self._get_dict().setdefault(key, default)

    def pop(self, key: str, default: Any = ...) -> Any:
        if default is ...:
            return self._get_dict().pop(key)
        return self._get_dict().pop(key, default)

    def clear(self) -> None:
        self._get_dict().clear()

    def update(self, *args, **kwargs) -> None:
        self._get_dict().update(*args, **kwargs)

    def keys(self):
        return self._get_dict().keys()

    def values(self):
        return self._get_dict().values()

    def items(self):
        return self._get_dict().items()


session_state = SessionStateProxy()


def _add_flash_banner(comp: Component) -> None:
    """Store feedback notification banner triggered during event handling."""
    try:
        from .state import _current_session
        sess = _current_session.get()
        if sess:
            if "dx_session_state" not in sess.data:
                sess.data["dx_session_state"] = {}
            flashes = sess.data["dx_session_state"].setdefault("_flash_banners", [])
            flashes.append(comp)
            return
    except Exception:
        pass
    flashes = session_state.setdefault("_flash_banners", [])
    flashes.append(comp)


def _pop_flash_banners() -> List[Component]:
    """Retrieve and clear pending feedback notification banners."""
    try:
        from .state import _current_session
        sess = _current_session.get()
        if sess and "dx_session_state" in sess.data:
            return sess.data["dx_session_state"].pop("_flash_banners", [])
    except Exception:
        pass
    return session_state.pop("_flash_banners", [])


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
        
        flash_components = _pop_flash_banners()
        flash_html = "".join(c.render(state_snapshot) for c in flash_components)

        main_html = flash_html + "".join(c.render(state_snapshot) for c in self.main_components)

        if self.sidebar_components:
            sidebar_html = "".join(c.render(state_snapshot) for c in self.sidebar_components)
            return (
                f"{theme_html}"
                f"<div class='pdu-dx-shell flex flex-row min-h-screen w-full bg-background text-foreground' "
                f"style='display: flex !important; flex-direction: row !important; min-height: 100vh; width: 100%; background-color: var(--pdu-color-bg, hsl(var(--background))); color: var(--pdu-color-text, hsl(var(--foreground)));'>"
                f"<aside class='w-72 min-w-[18rem] border-r border-border bg-card/60 backdrop-blur-md p-6 space-y-6 shrink-0 h-screen sticky top-0 overflow-y-auto flex flex-col justify-start z-20 shadow-sm' style='background-color: var(--pdu-color-card, var(--pdu-color-bg-secondary, hsl(var(--card))));'>"
                f"{sidebar_html}"
                f"</aside>"
                f"<div class='flex-1 min-w-0 {content_wrap} flex flex-col min-h-screen' style='flex: 1 1 0%; min-width: 0; background-color: var(--pdu-color-bg, hsl(var(--background))); color: var(--pdu-color-text, hsl(var(--foreground)));'>"
                f"<main class='flex-1 p-6 md:p-8 space-y-6 overflow-y-auto'>{main_html}</main>"
                f"</div>"
                f"</div>"
            )
        else:
            return (
                f"{theme_html}"
                f"<div class='pdu-dx-shell min-h-screen w-full bg-background text-foreground flex flex-col' style='min-height: 100vh; width: 100%; background-color: var(--pdu-color-bg, hsl(var(--background))); color: var(--pdu-color-text, hsl(var(--foreground)));'>"
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
    stack = _get_container_stack()
    if stack:
        stack[-1].append(comp)
    elif _is_event_handling.get():
        _add_flash_banner(comp)
    else:
        _default_page_components.append(comp)
    return comp


class _ContainerContext:
    """Generic context manager for routing widgets to a specific container list."""
    def __init__(self, target_list: List[Component]):
        self.target_list = target_list

    def __enter__(self):
        _get_container_stack().append(self.target_list)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stack = _get_container_stack()
        while stack and stack[-1] is not self.target_list:
            stack.pop()
        if stack and stack[-1] is self.target_list:
            stack.pop()

    def __getattr__(self, name: str) -> Any:
        try:
            import pydataui.dx as dx_mod
            if hasattr(dx_mod, name):
                fn = getattr(dx_mod, name)
                if callable(fn):
                    def method_proxy(*args, **kwargs):
                        with self:
                            return fn(*args, **kwargs)
                    return method_proxy
        except Exception:
            pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


# ============================================================================
# Page Configuration & Theming
# ============================================================================

def set_page_config(
    title: Optional[str] = None,
    layout: str = "centered",
    theme: Union[str, Dict[str, str], Any] = "zinc",
    dark_mode: Optional[bool] = None,
    docs_url: Any = ...,
    openapi_url: Any = ...,
    swagger_ui_parameters: Optional[Dict[str, Any]] = None,
    docs_roles: Optional[List[str]] = None,
    **kwargs
) -> None:
    """
    Configure global app metadata, responsive layout, visual theme tokens, and production FastAPI OpenAPI docs.

    :param title: Browser window title and header.
    :param layout: "centered" (standard 5xl content width) or "wide" (full width).
    :param theme: Theme configuration. Accepts preset name, hex string, or dict.
    :param dark_mode: Enable dark mode by default.
    :param docs_url: Path to Swagger UI docs (e.g. "/docs"), or None to disable in production.
    :param openapi_url: Path to OpenAPI JSON schema, or None to disable in production.
    :param swagger_ui_parameters: Dictionary of Swagger UI settings (e.g. {"filter": True, "syntaxHighlight.theme": "monokai"}).
    :param docs_roles: Restrict /docs access to users with specific roles (e.g. ["admin"]).
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
    if docs_url is not ...:
        app.config.docs_url = docs_url
    if openapi_url is not ...:
        app.config.openapi_url = openapi_url
    if swagger_ui_parameters is not None:
        app.config.swagger_ui_parameters = swagger_ui_parameters
    if docs_roles is not None:
        app.config.docs_roles = docs_roles


def get_fastapi() -> Any:
    """Return the underlying FastAPI application instance."""
    return get_app().fastapi


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
    active_sb = _active_page_sidebar.get()
    target = active_sb if active_sb is not None else _sidebar_components
    return _ContainerContext(target)


class ColumnContext:
    """Context manager representing a single responsive column."""
    def __init__(self, col_span: int = 1):
        self.children: List[Component] = []
        self.col_span = col_span

    def __enter__(self):
        _get_container_stack().append(self.children)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stack = _get_container_stack()
        if stack and stack[-1] is self.children:
            stack.pop()

    def to_component(self) -> Component:
        return Box(*self.children, class_name="flex-1 min-w-0 space-y-4")

    def __getattr__(self, name: str) -> Any:
        try:
            import pydataui.dx as dx_mod
            if hasattr(dx_mod, name):
                fn = getattr(dx_mod, name)
                if callable(fn):
                    def method_proxy(*args, **kwargs):
                        with self:
                            return fn(*args, **kwargs)
                    return method_proxy
        except Exception:
            pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


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
        _get_container_stack().append(self.children)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stack = _get_container_stack()
        if stack and stack[-1] is self.children:
            stack.pop()

    def __getattr__(self, name: str) -> Any:
        try:
            import pydataui.dx as dx_mod
            if hasattr(dx_mod, name):
                fn = getattr(dx_mod, name)
                if callable(fn):
                    def method_proxy(*args, **kwargs):
                        with self:
                            return fn(*args, **kwargs)
                    return method_proxy
        except Exception:
            pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


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
    """Client-side zero-latency tab switcher supporting expand, headless wizards, and pill/line styling."""
    def __init__(
        self,
        tab_names: List[str],
        tab_contexts: List[ColumnContext],
        expand: bool = False,
        hide_tab_buttons: bool = False,
        variant: str = "line",
        active_tab: int = 0,
        key: Optional[str] = None,
    ):
        super().__init__()
        self.tab_names = tab_names
        self.tab_contexts = tab_contexts
        self.expand = expand
        self.hide_tab_buttons = hide_tab_buttons
        self.variant = variant
        self.active_tab = active_tab
        self.key = key
        self.tab_id = generate_id("tabs")

    def render(self, state_snapshot=None) -> str:
        headers = []
        panels = []
        active_idx = self.active_tab
        if self.key and self.key in session_state:
            try:
                active_idx = int(session_state[self.key])
            except (ValueError, TypeError):
                pass

        for i, (name, ctx) in enumerate(zip(self.tab_names, self.tab_contexts)):
            is_active = (i == active_idx)
            display_style = "block" if is_active else "none"
            panel_id = f"{self.tab_id}-panel-{i}"
            btn_id = f"{self.tab_id}-btn-{i}"

            expand_cls = "flex-1 text-center" if self.expand else ""

            if self.variant == "pill":
                active_class = "pdu-tab-active bg-background text-primary font-semibold shadow-xs" if is_active else "text-muted-foreground hover:text-foreground"
                btn_base = "pdu-tab-btn px-4 py-2 text-xs font-medium rounded-lg transition-all cursor-pointer"
            else:
                active_class = "pdu-tab-active border-primary text-primary font-semibold" if is_active else "border-transparent text-muted-foreground hover:text-foreground hover:border-border"
                btn_base = "pdu-tab-btn px-4 py-2.5 text-sm font-medium border-b-2 transition-all cursor-pointer"

            headers.append(
                f"<button id='{btn_id}' type='button' "
                f"onclick=\"(function(){{"
                f"  const parent = document.getElementById('{self.tab_id}');"
                f"  parent.querySelectorAll('.pdu-tab-btn').forEach(b => {{"
                f"    b.classList.remove('pdu-tab-active', 'border-primary', 'text-primary', 'font-semibold', 'bg-background', 'shadow-xs');"
                f"    b.classList.add('border-transparent', 'text-muted-foreground');"
                f"  }});"
                f"  const activeBtn = document.getElementById('{btn_id}');"
                f"  activeBtn.classList.remove('border-transparent', 'text-muted-foreground');"
                f"  activeBtn.classList.add('pdu-tab-active', '{'bg-background text-primary shadow-xs' if self.variant == 'pill' else 'border-primary text-primary'}', 'font-semibold');"
                f"  parent.querySelectorAll('.pdu-tab-panel').forEach(p => p.style.display = 'none');"
                f"  document.getElementById('{panel_id}').style.display = 'block';"
                f"}})()\" "
                f"class='{btn_base} {expand_cls} {active_class}'>"
                f"{escape_html(name)}"
                f"</button>"
            )

            rendered_children = "".join(c.render(state_snapshot) for c in ctx.children)
            panels.append(
                f"<div id='{panel_id}' class='pdu-tab-panel p-4 space-y-4' style='display: {display_style};'>"
                f"{rendered_children}"
                f"</div>"
            )

        nav_style = "style='display: none;'" if self.hide_tab_buttons else ""
        if self.variant == "pill":
            nav_bar = f"<div class='pdu-tabs-pill flex gap-1 p-1 bg-muted/30 border-b border-border w-full select-none' {nav_style}>{''.join(headers)}</div>"
        else:
            nav_bar = f"<div class='flex border-b border-border bg-muted/20 px-2 w-full select-none' {nav_style}>{''.join(headers)}</div>"

        headless_cls = "pdu-tabs-headless" if self.hide_tab_buttons else ""
        expand_cls = "pdu-tabs-expand" if self.expand else ""

        return (
            f"<div id='{self.tab_id}' class='pdu-tabs-container w-full my-4 border border-border rounded-xl bg-card overflow-hidden shadow-sm {headless_cls} {expand_cls}'>"
            f"{nav_bar}"
            f"{''.join(panels)}"
            f"</div>"
        )


def tabs(
    tab_names: List[str],
    expand: bool = False,
    hide_tab_buttons: bool = False,
    variant: str = "line",
    active_tab: int = 0,
    key: Optional[str] = None,
    **kwargs
) -> List[ColumnContext]:
    """
    Create an interactive tabbed view container.

    :param tab_names: List of tab titles.
    :param expand: If True, distributes tab buttons equally across 100% of container width.
    :param hide_tab_buttons: If True, hides tab headers for headless multi-step onboarding & wizards.
    :param variant: Visual tab style ("line" or "pill").
    :param active_tab: Default active tab index.
    :param key: Session state key for programmatic tab switching.

    Example::

        tab_data, tab_chat = pdu.tabs(["Data View", "Agent Chat"], expand=True)
        with tab_data:
            pdu.write(df)
        with tab_chat:
            pdu.write("Chat history...")
    """
    contexts = [ColumnContext() for _ in tab_names]
    _add_component(_TabsWrapper(
        tab_names,
        contexts,
        expand=expand,
        hide_tab_buttons=hide_tab_buttons,
        variant=variant,
        active_tab=active_tab,
        key=key,
    ))
    return contexts


def container(*children: Component, border: bool = False, **kwargs) -> Box:
    """
    Add a scoped container (Streamlit `st.container` equivalent).
    Supports both context manager syntax (`with pdu.container():`) and direct component insertion.
    If border=True, renders with a modern card border, padding, and subtle shadow.
    """
    base_cls = "w-full space-y-4 my-2"
    if border:
        base_cls += " border border-border/80 rounded-2xl bg-card/60 p-6 shadow-sm"
    extra_cls = kwargs.pop("class_name", "")
    full_cls = f"{base_cls} {extra_cls}".strip() if extra_cls else base_cls
    return _add_component(Box(*children, class_name=full_cls, **kwargs))


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
        elif callable(obj):
            dataframe(obj, **kwargs)
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
    color: Optional[str] = None,
    help: Optional[str] = None,
    **kwargs
) -> MetricCard:
    if help:
        help_badge = f"<span class='group relative inline-flex items-center text-muted-foreground/70 hover:text-foreground cursor-help text-[11px] w-3.5 h-3.5 rounded-full border border-border/80 justify-center select-none ml-1'>?<span class='hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2 py-1 text-[11px] font-normal text-popover-foreground bg-popover border border-border/80 rounded-md shadow-lg pointer-events-none whitespace-normal min-w-[140px] max-w-xs text-center z-50'>{escape_html(help)}</span></span>"
        label = f"{label} {help_badge}" 
    """
    Render a high-impact KPI metric card with value, optional change delta, custom accent color, and badges.

    :param label: Title of the metric.
    :param value: Main display value (e.g., "$45,200", "1.4M").
    :param delta: Change indicator (e.g., "+12.4%", "-2.1ms").
    :param delta_color: "normal", "inverse", or "off".
    :param color: Custom accent color (preset name like "emerald", CSS name like "grey", or hex "#6366f1").
    """
    d = delta if delta is not None else change
    delta_type = "positive" if (d and str(d).startswith("+")) else ("negative" if (d and str(d).startswith("-")) else "neutral")
    if delta_color == "inverse":
        delta_type = "negative" if delta_type == "positive" else "positive"
    return _add_component(MetricCard(title=label, value=value, delta=d or "", delta_type=delta_type, color=color, **kwargs))


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

def _resolve_color(c: Any) -> str:
    """Resolve theme preset names, CSS color aliases, or raw hex/rgb into valid color strings."""
    if not isinstance(c, str):
        return str(c)
    clean = c.strip().lower()
    if clean in THEME_PRESETS:
        return THEME_PRESETS[clean]["primary"]
    CSS_COLOR_MAP = {
        "grey": "#71717a",
        "gray": "#71717a",
        "zinc": "#71717a",
        "slate": "#64748b",
        "stone": "#78716c",
        "neutral": "#737373",
        "blue": "#3b82f6",
        "green": "#22c55e",
        "emerald": "#10b981",
        "teal": "#14b8a6",
        "cyan": "#06b6d4",
        "indigo": "#6366f1",
        "violet": "#8b5cf6",
        "purple": "#a855f7",
        "fuchsia": "#d946ef",
        "pink": "#ec4899",
        "rose": "#f43f5e",
        "red": "#ef4444",
        "orange": "#f97316",
        "amber": "#f59e0b",
        "yellow": "#eab308",
        "black": "#09090b",
        "white": "#ffffff",
    }
    return CSS_COLOR_MAP.get(clean, c)


def _color_alpha(hex_or_named: str, alpha: Union[str, float] = "33") -> str:
    """Safely apply alpha transparency to hex, theme tokens, or named colors."""
    col = _resolve_color(hex_or_named)
    alpha_hex = f"{max(0, min(255, int(alpha * 255))):02x}" if isinstance(alpha, (int, float)) else str(alpha)
    if col.startswith("#"):
        c = col.lstrip("#")
        if len(c) == 3:
            c = "".join(x * 2 for x in c)
        if len(c) == 6:
            return f"#{c}{alpha_hex}"
        if len(c) == 8:
            return f"#{c[:6]}{alpha_hex}"
    return col


def _normalize_chart_data(
    data: Any,
    chart_type: str = "line",
    color: Optional[Union[str, List[str]]] = None
) -> Dict[str, Any]:
    """Helper to convert Pandas, list, or dict structures into Chart.js format."""
    theme_val = _page_config.get("theme", "zinc")
    primary_color = "#3b82f6"
    if isinstance(theme_val, str):
        theme_clean = theme_val.strip().lower()
        if theme_clean in THEME_PRESETS:
            primary_color = THEME_PRESETS[theme_clean]["primary"]
        elif theme_val.startswith("#"):
            primary_color = theme_val
    elif isinstance(theme_val, dict) and "primary" in theme_val:
        primary_color = theme_val["primary"]

    default_palette = [primary_color, "#10b981", "#8b5cf6", "#f59e0b", "#ef4444", "#06b6d4"]

    has_custom_color = color is not None
    if isinstance(color, str):
        custom_single = _resolve_color(color)
        colors = [custom_single]
    elif isinstance(color, (list, tuple)) and len(color) > 0:
        custom_single = None
        colors = [_resolve_color(c) for c in color]
    else:
        custom_single = None
        colors = default_palette

    # 1. Pandas DataFrame
    if hasattr(data, "columns") and hasattr(data, "values"):
        labels = [str(x) for x in data.index]
        datasets = []
        for i, col_name in enumerate(data.columns):
            c = custom_single if custom_single else colors[i % len(colors)]
            datasets.append({
                "label": str(col_name),
                "data": [None if (v != v) else v for v in data[col_name].tolist()],
                "borderColor": c,
                "backgroundColor": _color_alpha(c, "40") if chart_type in ("area", "bar") else c,
                "fill": chart_type == "area",
            })
        return {"labels": labels, "datasets": datasets}

    # 2. List or Tuple of numbers
    if isinstance(data, (list, tuple)):
        labels = [str(i + 1) for i in range(len(data))]
        if chart_type == "bar":
            bar_colors = custom_single if custom_single else [colors[i % len(colors)] for i in range(len(data))]
            bg_colors = _color_alpha(custom_single, "40") if custom_single else [_color_alpha(c, "40") for c in bar_colors]
        else:
            bar_colors = custom_single or primary_color
            bg_colors = _color_alpha(bar_colors, "33") if chart_type == "area" else bar_colors

        return {
            "labels": labels,
            "datasets": [{
                "label": "Value",
                "data": list(data),
                "borderColor": bar_colors,
                "backgroundColor": bg_colors,
                "borderWidth": 1,
                "borderRadius": 6 if chart_type == "bar" else 0,
                "fill": chart_type == "area",
            }],
        }

    # 3. Dict of categories or series:
    #    a) {"lat1": 140, "lat2": 110} (Single-series categorical)
    #    b) {"Series A": [10, 20], "Series B": [15, 25]} (Multi-series)
    if isinstance(data, dict):
        if not data:
            return {"labels": [], "datasets": []}

        first_val = next(iter(data.values()))
        if isinstance(first_val, (int, float)) or (isinstance(first_val, str) and not isinstance(first_val, (list, tuple, dict))):
            labels = [str(k) for k in data.keys()]
            vals = [float(v) if isinstance(v, (int, float)) else v for v in data.values()]
            if chart_type == "bar":
                bar_colors = custom_single if custom_single else [colors[i % len(colors)] for i in range(len(vals))]
                bg_colors = _color_alpha(custom_single, "40") if custom_single else [_color_alpha(c, "40") for c in (bar_colors if isinstance(bar_colors, list) else [bar_colors]*len(vals))]
            else:
                bar_colors = custom_single or primary_color
                bg_colors = _color_alpha(bar_colors, "33") if chart_type == "area" else bar_colors

            return {
                "labels": labels,
                "datasets": [{
                    "label": "Value",
                    "data": vals,
                    "borderColor": bar_colors,
                    "backgroundColor": bg_colors,
                    "borderWidth": 1,
                    "borderRadius": 6 if chart_type == "bar" else 0,
                    "fill": chart_type == "area",
                }],
            }

        datasets = []
        max_len = 0
        for i, (k, vals) in enumerate(data.items()):
            if isinstance(vals, (list, tuple)):
                max_len = max(max_len, len(vals))
                c = custom_single if custom_single else colors[i % len(colors)]
                datasets.append({
                    "label": str(k),
                    "data": list(vals),
                    "borderColor": c,
                    "backgroundColor": _color_alpha(c, "40") if chart_type in ("area", "bar") else c,
                    "borderWidth": 1,
                    "borderRadius": 6 if chart_type == "bar" else 0,
                    "fill": chart_type == "area",
                })
        labels = [str(i + 1) for i in range(max_len)]
        return {"labels": labels, "datasets": datasets}

    return {"labels": [], "datasets": []}


def line_chart(
    data: Any,
    width: Optional[str] = None,
    height: str = "320px",
    color: Optional[Union[str, List[str]]] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Chart:
    """Render a responsive multi-series line chart with optional custom color / palette."""
    c = color if color is not None else kwargs.pop("color", None)
    chart_data = _normalize_chart_data(data, "line", color=c)
    opts = {"responsive": True, "maintainAspectRatio": False}
    if len(chart_data.get("datasets", [])) == 1:
        opts["plugins"] = {"legend": {"display": False}}
    if options:
        opts.update(options)
    return _add_component(Chart(type="line", data=chart_data, options=opts, width=width, height=height, **kwargs))


def bar_chart(
    data: Any,
    width: Optional[str] = None,
    height: str = "320px",
    color: Optional[Union[str, List[str]]] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Chart:
    """Render a responsive bar chart with optional custom single color or multiple-color palette."""
    c = color if color is not None else kwargs.pop("color", None)
    chart_data = _normalize_chart_data(data, "bar", color=c)
    opts = {
        "responsive": True,
        "maintainAspectRatio": False,
        "scales": {
            "y": {"beginAtZero": True}
        }
    }
    if len(chart_data.get("datasets", [])) == 1:
        opts["plugins"] = {"legend": {"display": False}}
    if options:
        opts.update(options)
    return _add_component(Chart(type="bar", data=chart_data, options=opts, width=width, height=height, **kwargs))


def area_chart(
    data: Any,
    width: Optional[str] = None,
    height: str = "320px",
    color: Optional[Union[str, List[str]]] = None,
    options: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Chart:
    """Render a responsive filled area chart with optional custom color / palette."""
    c = color if color is not None else kwargs.pop("color", None)
    chart_data = _normalize_chart_data(data, "area", color=c)
    opts = {"responsive": True, "maintainAspectRatio": False}
    if len(chart_data.get("datasets", [])) == 1:
        opts["plugins"] = {"legend": {"display": False}}
    if options:
        opts.update(options)
    return _add_component(Chart(type="line", data=chart_data, options=opts, width=width, height=height, **kwargs))


def scatter_chart(
    data: Any,
    width: Optional[str] = None,
    height: str = "320px",
    color: Optional[Union[str, List[str]]] = None,
    **kwargs
) -> Chart:
    """Render a responsive scatter chart with optional custom color."""
    c = color if color is not None else kwargs.pop("color", None)
    chart_data = _normalize_chart_data(data, "scatter", color=c)
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
    if hasattr(df, "to_pandas") and not hasattr(df, "iloc") and not callable(df):
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
# Input Widgets & Forms
# ============================================================================

class _FormWrapper(Component):
    """
    Renders an HTML5 form container wired to HTMX for batched form submission.
    """
    def __init__(self, key: str, children: List[Component], clear_on_submit: bool = False, border: bool = True, class_name: str = ""):
        super().__init__()
        self.key = key
        self.children_list = children
        self.clear_on_submit = clear_on_submit
        self.border = border
        self.class_name = class_name

    def render(self, state_snapshot=None) -> str:
        rendered_children = "".join(c.render(state_snapshot) for c in self.children_list)
        border_cls = "border border-border/80 rounded-2xl bg-card/60 p-6 space-y-4 shadow-sm" if self.border else "space-y-4"
        reset_attr = " hx-on::after-request='this.reset()'" if self.clear_on_submit else ""
        return (
            f"<form id='form_{escape_html(self.key)}' class='pdu-form {border_cls} {self.class_name}'{reset_attr}>"
            f"<input type='hidden' name='_form_key' value='{escape_html(self.key)}' />"
            f"{rendered_children}"
            f"</form>"
        )


class _FormContext:
    def __init__(self, key: str, clear_on_submit: bool = False, border: bool = True):
        self.key = key
        self.clear_on_submit = clear_on_submit
        self.border = border
        self.children: List[Component] = []

    def __enter__(self):
        _get_container_stack().append(self.children)
        _active_form_stack.append(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if _active_form_stack and _active_form_stack[-1] is self:
            _active_form_stack.pop()
        stack = _get_container_stack()
        if stack and stack[-1] is self.children:
            stack.pop()

    def __getattr__(self, name: str) -> Any:
        try:
            import pydataui.dx as dx_mod
            if hasattr(dx_mod, name):
                fn = getattr(dx_mod, name)
                if callable(fn):
                    def method_proxy(*args, **kwargs):
                        with self:
                            return fn(*args, **kwargs)
                    return method_proxy
        except Exception:
            pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


def form(key: str, clear_on_submit: bool = False, border: bool = True, **kwargs) -> _FormContext:
    """
    Context manager to create a batched form container (Streamlit `st.form` equivalent).
    Widgets inside the form batch their inputs until `form_submit_button` is clicked.

    Example::

        with pdu.form("login_form"):
            pdu.text_input("Username", key="username")
            pdu.text_input("Password", type="password", key="password")
            pdu.form_submit_button("Sign In", on_click=handle_login)
    """
    ctx = _FormContext(key, clear_on_submit=clear_on_submit, border=border)
    _add_component(_FormWrapper(key, ctx.children, clear_on_submit=clear_on_submit, border=border, **kwargs))
    return ctx


class FormSubmitButton(Component):
    """Submit button for a form supporting both callback and boolean evaluation."""
    def __init__(self, label: str, action_id: str, was_submitted: bool = False, type: str = "primary", **kwargs):
        super().__init__()
        self.label = label
        self.action_id = action_id
        self.was_submitted = was_submitted
        self.btn_type = type

    def __bool__(self) -> bool:
        return self.was_submitted

    def render(self, state_snapshot=None) -> str:
        action_attr = (
            f'hx-post="/_pdu/event/ActionState/{self.action_id}" '
            f'hx-target="#pdu-root" '
            f'hx-swap="innerHTML" '
            f'hx-include="closest form" '
        )
        btn_type_cls = (
            "bg-primary text-primary-foreground hover:opacity-90 shadow-sm"
            if self.btn_type == "primary"
            else "bg-secondary text-secondary-foreground hover:bg-secondary/80"
        )
        return (
            f"<button type='submit' {action_attr} "
            f"class='inline-flex items-center justify-center px-4 py-2 rounded-xl text-sm font-medium transition-all cursor-pointer {btn_type_cls}'>"
            f"{escape_html(self.label)}"
            f"</button>"
        )


def form_submit_button(
    label: str = "Submit",
    on_click: Optional[Union[Callable, EventHandler]] = None,
    type: str = "primary",
    **kwargs
) -> FormSubmitButton:
    """
    Submit button for a `pdu.form()` container (Streamlit `st.form_submit_button` equivalent).
    Supports both procedural condition checking (`if pdu.form_submit_button("Submit"): ...`)
    and explicit event callbacks (`pdu.form_submit_button("Submit", on_click=my_func)`).
    """
    form_key = _active_form_stack[-1].key if _active_form_stack else "default"
    submit_flag_key = f"_form_{form_key}_submitted"
    was_submitted = session_state.pop(submit_flag_key, False)

    def _default_submit_handler(**kws):
        session_state[submit_flag_key] = True
        if on_click:
            sig = inspect.signature(on_click)
            if len(sig.parameters) == 0:
                return on_click()
            call_k = {k: v for k, v in kws.items() if k in sig.parameters}
            if not call_k and len(sig.parameters) == 1:
                return on_click(kws)
            return on_click(**call_k)

    action_id = register_callback(_default_submit_handler)
    btn_comp = FormSubmitButton(label=label, action_id=action_id, was_submitted=was_submitted, type=type, **kwargs)
    _add_component(btn_comp)
    return btn_comp


def button(label: str, on_click: Optional[Union[Callable, EventHandler]] = None, **kwargs) -> Button:
    """Add an interactive button with a Python event callback."""
    if _active_form_stack and "hx_include" not in kwargs and "include" not in kwargs:
        kwargs["include"] = "closest form"
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
    actual_value = value
    if key:
        if key in session_state:
            actual_value = session_state[key]
        elif value:
            session_state[key] = value
    return _add_component(Input(label=label, value=actual_value, placeholder=placeholder, name=key, type=type, on_change=on_change, **kwargs))


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
    actual_value = value
    if key:
        if key in session_state:
            actual_value = session_state[key]
        elif value:
            session_state[key] = value
    return _add_component(TextArea(label=label, value=actual_value, placeholder=placeholder, name=key, on_change=on_change, **kwargs))


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
    actual_value = value
    if key:
        if key in session_state:
            try:
                actual_value = float(session_state[key]) if ("." in str(session_state[key])) else int(session_state[key])
            except (ValueError, TypeError):
                actual_value = session_state[key]
        elif value != 0:
            session_state[key] = value
    if step is None:
        if any(isinstance(x, float) for x in (min_value, max_value, actual_value)):
            step = 0.01
        else:
            step = 1
    return _add_component(Input(label=label, value=actual_value, type="number", min=min_value, max=max_value, step=step, name=key, on_change=on_change, **kwargs))


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
    """
    actual_value = value
    if key:
        if key in session_state:
            try:
                actual_value = float(session_state[key]) if ("." in str(session_state[key])) else int(session_state[key])
            except (ValueError, TypeError):
                actual_value = session_state[key]
        elif value is not None:
            session_state[key] = value
    is_float = any(isinstance(x, float) for x in (min_value, max_value, actual_value, step) if x is not None)
    if min_value is None:
        min_value = 0.0 if is_float else 0
    if max_value is None:
        max_value = 100.0 if is_float else 100
    if actual_value is None:
        actual_value = min_value
    if step is None:
        if is_float or any(isinstance(x, float) for x in (min_value, max_value, actual_value)):
            diff = abs(max_value - min_value)
            step = 0.01 if diff <= 1.0 else (0.1 if diff <= 10.0 else 0.01)
        else:
            step = 1
    return _add_component(Slider(label=label, min=min_value, max=max_value, value=actual_value, step=step, name=key, on_change=on_change, **kwargs))


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
    if key and key in session_state:
        val = session_state[key]
    else:
        val = opts[index] if (opts and 0 <= index < len(opts)) else None
        if key and val is not None:
            session_state[key] = val
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
    opts = options or []
    if key and key in session_state:
        val = session_state[key]
    else:
        val = default
        if key and val is not None:
            session_state[key] = val
    return _add_component(Select(label=label, options=opts, value=val, multiple=True, name=key, on_change=on_change, **kwargs))


def checkbox(
    label: str = "",
    value: bool = False,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Checkbox:
    """Add a checkbox toggle widget."""
    actual_value = value
    if key:
        if key in session_state:
            actual_value = bool(session_state[key])
        elif value:
            session_state[key] = value
    return _add_component(Checkbox(label=label, checked=actual_value, name=key, on_change=on_change, **kwargs))


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
    if key and key in session_state:
        selected = session_state[key]
    elif key and selected is not None:
        session_state[key] = selected
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
    actual_value = value
    if key:
        if key in session_state:
            actual_value = bool(session_state[key])
        elif value:
            session_state[key] = value
    return _add_component(Switch(label=label, checked=actual_value, name=key, on_change=on_change, **kwargs))


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
    comp = FileUpload(label=label, accept=accept, multiple=multiple, name=input_name, on_change=cb, **kwargs)
    comp.key = key or input_name
    return _add_component(comp)


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
        bubble_bg = (
            "bg-primary text-primary-foreground rounded-tr-sm"
            if is_user
            else "bg-card text-card-foreground border border-border/80 rounded-tl-sm shadow-sm"
        )
        default_avatar = "👤" if is_user else "🤖"
        avatar_content = self.avatar or default_avatar
        rendered_children = "".join(c.render(state_snapshot) for c in self.children_list)

        if is_user:
            bot_avatar = ""
            user_avatar = f"<div class='w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center text-sm shrink-0 select-none shadow-sm'>{avatar_content}</div>"
        else:
            bot_avatar = f"<div class='w-8 h-8 rounded-full bg-muted border border-border/60 flex items-center justify-center text-sm shrink-0 select-none shadow-sm'>{avatar_content}</div>"
            user_avatar = ""

        return (
            f"<div class='flex gap-3 my-3 {align} items-start'>"
            f"{bot_avatar}"
            f"<div class='max-w-[82%] rounded-2xl px-4 py-3 text-sm shadow-sm space-y-2 {bubble_bg}'>"
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
        _get_container_stack().append(self.children)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stack = _get_container_stack()
        if stack and stack[-1] is self.children:
            stack.pop()

    def __getattr__(self, name: str) -> Any:
        try:
            import pydataui.dx as dx_mod
            if hasattr(dx_mod, name):
                fn = getattr(dx_mod, name)
                if callable(fn):
                    def method_proxy(*args, **kwargs):
                        with self:
                            return fn(*args, **kwargs)
                    return method_proxy
        except Exception:
            pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


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
    position: str = "bottom",
    target: Optional[str] = None,
    swap: Optional[str] = None,
    **kwargs
) -> Component:
    """
    Add a sleek, modern chat input prompt bar.

    Parameters:
    - placeholder: Text shown when input is empty.
    - key: Session state key to bind and store the user's input.
    - on_submit: Python callback invoked when user submits the prompt (receives prompt string).
    - position: 'bottom' (default, docked at the bottom of viewport like ChatGPT/Streamlit)
                or 'inline' (renders directly in the container layout flow).
    - target: HTMX target ID to swap into (defaults to '#pdu-root').
    - swap: HTMX swap strategy (defaults to 'innerHTML').
    """
    input_id = key or generate_id("chat_input")
    target_id = target or "#pdu-root"
    swap_strategy = swap or "innerHTML"

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
    action_attr = (
        f'hx-post="/_pdu/event/ActionState/{action_name}" '
        f'hx-trigger="submit" '
        f'hx-target="{target_id}" '
        f'hx-swap="{swap_strategy}" '
        f'hx-include="this" '
        f'hx-on::after-request="this.reset()" '
        f'hx-on::after-settle="window.scrollTo({{top: document.body.scrollHeight, behavior: \'smooth\'}});"'
    )

    form_id = f"form_{input_id}"
    form_html = (
        f"<form id='{form_id}' class='flex gap-2 items-center w-full p-2 bg-card/95 border border-border/80 rounded-2xl shadow-lg focus-within:ring-2 focus-within:ring-primary/40 focus-within:border-primary transition-all' {action_attr}>"
        f"<input type='text' name='{input_id}' placeholder='{escape_html(placeholder)}' autocomplete='off' "
        f"class='flex-1 bg-transparent px-3.5 py-2 text-sm text-foreground placeholder:text-muted-foreground outline-none' />"
        f"<button type='submit' class='p-2 bg-primary text-primary-foreground rounded-xl hover:opacity-90 transition-opacity cursor-pointer flex items-center justify-center shrink-0'>"
        f"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='m22 2-7 20-4-9-9-4Z'/><path d='M22 2 11 13'/></svg>"
        f"</button>"
        f"</form>"
    )

    if position == "bottom":
        html_code = (
            f"<div class='fixed bottom-0 left-0 right-0 z-40 p-4 bg-gradient-to-t from-background via-background/95 to-transparent backdrop-blur-sm pointer-events-none'>"
            f"  <div class='max-w-3xl mx-auto pointer-events-auto'>"
            f"    {form_html}"
            f"    <div class='text-center text-[10px] text-muted-foreground/60 mt-1.5'>Press Enter to send • PyDataUI Copilot</div>"
            f"  </div>"
            f"</div>"
            f"<div class='h-24 w-full shrink-0'></div>"
        )
    else:
        html_code = f"<div class='w-full my-4'>{form_html}</div>"

    return _add_component(RawHtml(html_code))


def chat(messages: Optional[List[Dict[str, str]]] = None, on_send: Optional[Callable] = None, **kwargs) -> Chat:
    """Add an interactive composite Chat interface component."""
    return _add_component(Chat(messages=messages, on_send=on_send, **kwargs))


# ============================================================================
# Structural Containers & Layout Helpers
# ============================================================================

def card(*children: Component, title: Optional[str] = None, subtitle: Optional[str] = None, **kwargs) -> Card:
    """
    Add an elevated card container.
    Supports both context manager syntax (`with pdu.card():`) and direct component arguments.
    """
    return _add_component(Card(*children, title=title, subtitle=subtitle, **kwargs))


def box(*children: Component, **kwargs) -> Box:
    """
    Add a generic layout box / div container.
    Supports both context manager syntax (`with pdu.box():`) and direct component arguments.
    """
    return _add_component(Box(*children, **kwargs))


def row(*children: Component, **kwargs) -> HStack:
    """
    Add a horizontal layout row.
    Supports both context manager syntax (`with pdu.row():`) and direct component arguments.
    """
    return _add_component(HStack(*children, **kwargs))


def column(*children: Component, **kwargs) -> VStack:
    """
    Add a vertical layout column.
    Supports both context manager syntax (`with pdu.column():`) and direct component arguments.
    """
    return _add_component(VStack(*children, **kwargs))


col = column


def flex(
    *children: Component,
    direction: str = "row",
    align: str = "stretch",
    justify: str = "start",
    gap: Union[int, str] = "4",
    wrap: Union[bool, str] = False,
    **kwargs
) -> Flex:
    """
    Add a flexible Flexbox container supporting row/column direction, alignment, justification, gap, and wrapping.
    Supports both context manager syntax (`with pdu.flex():`) and direct child component arguments.
    """
    return _add_component(Flex(*children, direction=direction, align=align, justify=justify, gap=gap, wrap=wrap, **kwargs))


def grid(
    *children: Component,
    columns: Union[int, str, List[Union[int, float]], Dict[str, int]] = 1,
    gap: Union[int, str] = "4",
    row_gap: Optional[Union[int, str]] = None,
    column_gap: Optional[Union[int, str]] = None,
    min_column_width: Optional[str] = None,
    template_columns: Optional[str] = None,
    template_rows: Optional[str] = None,
    **kwargs
) -> Grid:
    """
    Add a CSS Grid layout container supporting integer columns, fractional ratios, responsive breakpoints,
    auto-fit wrapping (`min_column_width="260px"`), and custom template rules.
    Supports both context manager syntax (`with pdu.grid():`) and direct child component arguments.
    """
    return _add_component(Grid(
        *children,
        columns=columns,
        gap=gap,
        row_gap=row_gap,
        column_gap=column_gap,
        min_column_width=min_column_width,
        template_columns=template_columns,
        template_rows=template_rows,
        **kwargs
    ))


def spacer(
    size: Optional[Union[int, str]] = None,
    height: Optional[Union[int, str]] = None,
    width: Optional[Union[int, str]] = None,
    flex: int = 1,
    **kwargs
) -> Spacer:
    """
    Add an auto-expanding flexible spacer or fixed dimension spacer.
    - `pdu.spacer(height=24)`: inserts a 24px vertical gap.
    - `pdu.spacer(flex=1)`: inside a flex row, pushes subsequent items to the opposite end.
    """
    return _add_component(Spacer(size=size, height=height, width=width, flex=flex, **kwargs))


def divider(
    label: Optional[str] = None,
    orientation: str = "horizontal",
    color: Optional[str] = None,
    thickness: Optional[str] = None,
    **kwargs
) -> Divider:
    """Add a visual divider line, optionally with a centered label."""
    return _add_component(Divider(label=label, orientation=orientation, color=color, thickness=thickness, **kwargs))


def pinned(*children: Component, position: str = "bottom", z_index: int = 40, **kwargs) -> Box:
    """
    Add a pinned container fixed to viewport edges (e.g. pinned footer action bar or header).
    Supports both context manager syntax (`with pdu.pinned():`) and direct component arguments.
    """
    pos_cls = f"fixed {position}-0 left-0 right-0 z-{z_index} p-4 bg-background/90 backdrop-blur border-{'t' if position == 'bottom' else 'b'} border-border shadow-lg"
    extra_cls = kwargs.pop("class_name", "")
    full_cls = f"{pos_cls} {extra_cls}".strip() if extra_cls else pos_cls
    return _add_component(Box(*children, position="fixed", class_name=full_cls, z_index=z_index, **kwargs))


def overlay(*children: Component, blur: bool = True, **kwargs) -> Box:
    """
    Add an absolute overlay container covering its relative parent.
    Supports both context manager syntax (`with pdu.overlay():`) and direct component arguments.
    """
    blur_cls = "backdrop-blur-sm" if blur else ""
    cls = f"absolute inset-0 z-20 flex items-center justify-center bg-background/60 {blur_cls}"
    extra_cls = kwargs.pop("class_name", "")
    full_cls = f"{cls} {extra_cls}".strip() if extra_cls else cls
    return _add_component(Box(*children, position="absolute", inset=0, class_name=full_cls, **kwargs))


def badge(
    label: str,
    color: str = "zinc",
    variant: str = "subtle",
    icon: Optional[str] = None,
    position: Optional[str] = None,
    top: Optional[Union[int, str]] = None,
    bottom: Optional[Union[int, str]] = None,
    left: Optional[Union[int, str]] = None,
    right: Optional[Union[int, str]] = None,
    z_index: Optional[Union[int, str]] = None,
    **kwargs
) -> Component:
    """
    Render a status badge or category tag with optional coordinate positioning and variants.
    """
    resolved_color = _resolve_color(color)
    bg_alpha = _color_alpha(resolved_color, 0.15)
    border_alpha = _color_alpha(resolved_color, 0.3)

    if variant == "solid":
        style_rules = f"background-color: {resolved_color}; color: #ffffff;"
    elif variant == "outline":
        style_rules = f"background-color: transparent; color: {resolved_color}; border: 1px solid {resolved_color};"
    else:  # subtle
        style_rules = f"background-color: {bg_alpha}; color: {resolved_color}; border: 1px solid {border_alpha};"

    pos_rules = []
    if position:
        pos_rules.append(f"position: {position};")
    if top is not None:
        pos_rules.append(f"top: {top}px;" if isinstance(top, (int, float)) or (isinstance(top, str) and top.isdigit()) else f"top: {top};")
    if bottom is not None:
        pos_rules.append(f"bottom: {bottom}px;" if isinstance(bottom, (int, float)) or (isinstance(bottom, str) and bottom.isdigit()) else f"bottom: {bottom};")
    if left is not None:
        pos_rules.append(f"left: {left}px;" if isinstance(left, (int, float)) or (isinstance(left, str) and left.isdigit()) else f"left: {left};")
    if right is not None:
        pos_rules.append(f"right: {right}px;" if isinstance(right, (int, float)) or (isinstance(right, str) and right.isdigit()) else f"right: {right};")
    if z_index is not None:
        pos_rules.append(f"z-index: {z_index};")

    full_style = f"{style_rules} {' '.join(pos_rules)}".strip()
    icon_html = f"<span class='mr-1'>{escape_html(icon)}</span>" if icon else ""

    extra_class = kwargs.pop("class_name", "")
    badge_html = (
        f"<span class='pdu-badge inline-flex items-center justify-center px-2.5 py-0.5 rounded-full text-xs font-semibold select-none shadow-xs transition-all {extra_class}' "
        f"style='{full_style}'>"
        f"{icon_html}<span>{escape_html(str(label))}</span>"
        f"</span>"
    )
    return _add_component(RawHtml(badge_html))


def sparkline(
    data: List[Union[int, float]],
    color: str = "emerald",
    height: int = 32,
    width: Union[str, int] = "100%",
    fill: bool = True,
    **kwargs
) -> Component:
    """
    Render a lightweight, zero-dependency inline SVG sparkline mini-chart.
    """
    if not data or len(data) < 2:
        return _add_component(RawHtml("<div class='pdu-sparkline-empty text-xs text-muted-foreground'>—</div>"))

    resolved_color = _resolve_color(color)
    min_v = min(data)
    max_v = max(data)
    span = (max_v - min_v) if max_v != min_v else 1.0

    view_w = 100
    view_h = height
    pad = 2
    pts = []
    n = len(data)
    for i, v in enumerate(data):
        x = round((i / (n - 1)) * view_w, 2)
        y = round(view_h - pad - ((v - min_v) / span) * (view_h - (pad * 2)), 2)
        pts.append((x, y))

    points_str = " ".join(f"{x},{y}" for x, y in pts)

    fill_polygon = ""
    fill_gradient = ""
    spark_id = generate_id("spark")
    if fill:
        area_pts = f"0,{view_h} {points_str} {view_w},{view_h}"
        fill_gradient = (
            f"<defs><linearGradient id='{spark_id}_grad' x1='0' y1='0' x2='0' y2='1'>"
            f"<stop offset='0%' stop-color='{resolved_color}' stop-opacity='0.28'/>"
            f"<stop offset='100%' stop-color='{resolved_color}' stop-opacity='0.0'/>"
            f"</linearGradient></defs>"
        )
        fill_polygon = f"<polygon points='{area_pts}' fill='url(#{spark_id}_grad)' stroke='none' />"

    w_style = f"width: {width}px;" if isinstance(width, int) or (isinstance(width, str) and width.isdigit()) else f"width: {width};"
    svg_html = (
        f"<svg viewBox='0 0 {view_w} {view_h}' preserveAspectRatio='none' "
        f"class='pdu-sparkline' style='{w_style} height: {height}px; overflow: visible;' "
        f"xmlns='http://www.w3.org/2000/svg'>"
        f"{fill_gradient}"
        f"{fill_polygon}"
        f"<polyline points='{points_str}' fill='none' stroke='{resolved_color}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>"
        f"</svg>"
    )
    return _add_component(RawHtml(svg_html))


def stat_card(
    title: str,
    value: Any,
    change: Optional[str] = None,
    delta: Optional[str] = None,
    sparkline: Optional[List[Union[int, float]]] = None,
    icon: Optional[str] = None,
    color: Optional[str] = None,
    **kwargs
) -> Card:
    """
    Render an executive KPI card with title, large value, optional change delta, category icon, and inline SVG sparkline.
    """
    d = change if change is not None else delta
    resolved_accent = _resolve_color(color) if color else None

    top_row = []
    if icon:
        top_row.append(f"<span class='text-lg'>{escape_html(icon)}</span>")
    top_row.append(f"<span class='text-xs font-medium uppercase tracking-wider text-muted-foreground'>{escape_html(title)}</span>")
    header_html = f"<div class='flex items-center justify-between gap-2 mb-2'>{''.join(top_row)}</div>"

    accent_bar = f"<div class='w-full h-1 rounded-full mb-3' style='background: {resolved_accent};'></div>" if resolved_accent else ""

    delta_badge = ""
    if d:
        d_str = str(d).strip()
        is_pos = d_str.startswith("+")
        is_neg = d_str.startswith("-")
        delta_bg = "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400" if is_pos else ("bg-rose-500/15 text-rose-600 dark:text-rose-400" if is_neg else "bg-muted text-muted-foreground")
        arrow = "↑" if is_pos else ("↓" if is_neg else "")
        delta_badge = f"<span class='inline-flex items-center px-2 py-0.5 rounded-md text-xs font-semibold {delta_bg}'>{arrow} {escape_html(d_str)}</span>"

    sparkline_html = ""
    if sparkline and len(sparkline) >= 2:
        spark_color = color or ("#10b981" if (d and str(d).startswith("+")) else ("#f43f5e" if (d and str(d).startswith("-")) else "#6366f1"))
        min_v, max_v = min(sparkline), max(sparkline)
        span = (max_v - min_v) if max_v != min_v else 1.0
        pts = [
            f"{round((i / (len(sparkline) - 1)) * 80, 2)},{round(28 - 2 - ((v - min_v) / span) * 24, 2)}"
            for i, v in enumerate(sparkline)
        ]
        pts_str = " ".join(pts)
        res_col = _resolve_color(spark_color)
        sparkline_html = (
            f"<svg viewBox='0 0 80 28' class='w-24 h-7 shrink-0' preserveAspectRatio='none'>"
            f"<polyline points='{pts_str}' fill='none' stroke='{res_col}' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/>"
            f"</svg>"
        )

    bottom_html = f"<div class='flex items-center justify-between gap-2 mt-3'>{delta_badge}{sparkline_html}</div>" if (delta_badge or sparkline_html) else ""

    body_html = (
        f"<div class='pdu-stat-body'>"
        f"{accent_bar}"
        f"{header_html}"
        f"<div class='text-2xl font-bold tracking-tight text-foreground'>{escape_html(str(value))}</div>"
        f"{bottom_html}"
        f"</div>"
    )
    extra_class = kwargs.pop("class_name", "")
    card_comp = Card(RawHtml(body_html), padding="md", class_name=f"pdu-stat-card border border-border/80 bg-card/60 shadow-sm rounded-2xl hover:border-primary/40 transition-all {extra_class}".strip(), **kwargs)
    _add_component(card_comp)
    return card_comp


def date_input(
    label: str = "",
    value: Optional[str] = None,
    min_value: Optional[str] = None,
    max_value: Optional[str] = None,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Input:
    """Add a date picker widget bound to session state."""
    actual_value = value or ""
    if key:
        if key in session_state:
            actual_value = session_state[key]
        elif value:
            session_state[key] = value
    return _add_component(Input(
        label=label,
        value=actual_value,
        type="date",
        min=min_value,
        max=max_value,
        name=key,
        on_change=on_change,
        **kwargs
    ))


def time_input(
    label: str = "",
    value: Optional[str] = None,
    key: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Input:
    """Add a time picker widget bound to session state."""
    actual_value = value or ""
    if key:
        if key in session_state:
            actual_value = session_state[key]
        elif value:
            session_state[key] = value
    return _add_component(Input(
        label=label,
        value=actual_value,
        type="time",
        name=key,
        on_change=on_change,
        **kwargs
    ))


def search_input(
    placeholder: str = "Search...",
    value: str = "",
    key: Optional[str] = None,
    on_search: Optional[Callable] = None,
    **kwargs
) -> Component:
    """Add a sleek search bar with instant HTMX callback and magnifying glass icon."""
    input_key = key or generate_id("search")
    actual_val = session_state.get(input_key, value)

    action_attr = ""
    if on_search:
        action_name = register_callback(on_search)
        action_attr = (
            f'hx-post="/_pdu/event/ActionState/{action_name}" '
            f'hx-trigger="keyup changed delay:300ms, search" '
            f'hx-target="#pdu-root" '
            f'hx-swap="innerHTML" '
            f'hx-include="this" '
        )

    search_html = (
        f"<div class='relative w-full max-w-md my-2'>"
        f"<span class='absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-muted-foreground'>"
        f"<svg width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'/><path d='m21 21-4.3-4.3'/></svg>"
        f"</span>"
        f"<input type='search' name='{input_key}' value='{escape_html(str(actual_val))}' placeholder='{escape_html(placeholder)}' "
        f"{action_attr}"
        f"class='w-full pl-9 pr-4 py-2 bg-card border border-border rounded-xl text-sm text-foreground placeholder:text-muted-foreground outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all shadow-xs' />"
        f"</div>"
    )
    return _add_component(RawHtml(search_html))


def pricing_card(
    title: str,
    price: str,
    period: str = "/ mo",
    description: str = "",
    features: Optional[List[str]] = None,
    cta_label: str = "Get Started",
    highlighted: bool = False,
    badge_label: Optional[str] = None,
    on_click: Optional[Callable] = None,
    **kwargs
) -> Card:
    """
    Render a commercial SaaS tier pricing card with features, CTA button, and optional highlighted badge.
    """
    feat_list = features or []
    feat_html = "".join(
        f"<li class='flex items-center gap-2 text-sm text-foreground/90'><span class='text-primary font-bold'>✓</span><span>{escape_html(f)}</span></li>"
        for f in feat_list
    )

    badge_html = ""
    if badge_label or highlighted:
        b_text = badge_label or "MOST POPULAR"
        badge_html = f"<span class='absolute top-3 right-3 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-primary text-primary-foreground tracking-wider uppercase shadow-xs'>{escape_html(b_text)}</span>"

    border_cls = "border-2 border-primary shadow-lg bg-card" if highlighted else "border border-border/80 bg-card/60 shadow-sm"
    btn_type = "primary" if highlighted else "secondary"

    action_attr = ""
    if on_click:
        action_name = register_callback(on_click)
        action_attr = f'hx-post="/_pdu/event/ActionState/{action_name}" hx-target="#pdu-root" hx-swap="innerHTML"'

    body_html = (
        f"<div class='relative p-6 space-y-5'>"
        f"{badge_html}"
        f"<div>"
        f"<h3 class='text-lg font-bold text-foreground'>{escape_html(title)}</h3>"
        f"<p class='text-xs text-muted-foreground mt-1'>{escape_html(description)}</p>"
        f"</div>"
        f"<div class='flex items-baseline gap-1'>"
        f"<span class='text-3xl font-extrabold text-foreground'>{escape_html(price)}</span>"
        f"<span class='text-xs text-muted-foreground'>{escape_html(period)}</span>"
        f"</div>"
        f"<ul class='space-y-2.5 pt-2 border-t border-border/60'>{feat_html}</ul>"
        f"<div class='pt-4'>"
        f"<button type='button' {action_attr} class='w-full py-2.5 px-4 rounded-xl text-sm font-semibold transition-all cursor-pointer "
        f"{'bg-primary text-primary-foreground hover:opacity-90 shadow-sm' if btn_type == 'primary' else 'bg-secondary text-secondary-foreground hover:bg-secondary/80'}'>"
        f"{escape_html(cta_label)}"
        f"</button>"
        f"</div>"
        f"</div>"
    )
    card_comp = Card(RawHtml(body_html), padding="none", class_name=f"pdu-pricing-card rounded-2xl overflow-hidden {border_cls}".strip(), **kwargs)
    _add_component(card_comp)
    return card_comp


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
# Final Version Commercial Extensions (v1.5.0)
# ============================================================================

def navbar(
    *children: Component,
    title: Optional[str] = None,
    brand: Optional[str] = None,
    logo: Optional[str] = None,
    links: Optional[List[Dict[str, str]]] = None,
    search: Union[bool, str] = False,
    user: Optional[Dict[str, Any]] = None,
    sticky: bool = True,
    **kwargs
) -> Navbar:
    """
    Render a modern commercial application header bar with branding, navigation links, instant search, and user profile.
    Supports both context manager syntax (`with pdu.navbar():`) and direct child arguments.
    """
    nav_title = brand or title
    nav_comp = Navbar(
        *children,
        brand=nav_title,
        logo=logo,
        links=links,
        search=search,
        user=user,
        sticky=sticky,
        **kwargs
    )
    return _add_component(nav_comp)


def breadcrumb(
    items: Optional[List[Union[str, Dict[str, str], Tuple[str, str]]]] = None,
    separator: str = "/",
    **kwargs
) -> Breadcrumb:
    """
    Render a clean hierarchical breadcrumb trail (e.g. `pdu.breadcrumb(["Home", "Clusters", "Node 04"])`).
    """
    return _add_component(Breadcrumb(items=items, separator=separator, **kwargs))


def image(
    image: Any,
    caption: Optional[str] = None,
    width: Optional[Union[int, str]] = None,
    height: Optional[Union[int, str]] = None,
    use_container_width: bool = False,
    alt: Optional[str] = None,
    rounded: bool = True,
    **kwargs
) -> Image:
    """
    Display an image from a URL, local path, raw bytes, or PIL Image (Streamlit `st.image` equivalent).
    """
    w = "100%" if use_container_width else width
    return _add_component(Image(
        src=image,
        caption=caption,
        width=w,
        height=height,
        alt=alt,
        rounded=rounded,
        **kwargs
    ))


def video(
    data: Any,
    format: str = "video/mp4",
    caption: Optional[str] = None,
    controls: bool = True,
    autoplay: bool = False,
    muted: bool = False,
    loop: bool = False,
    width: Optional[Union[int, str]] = None,
    **kwargs
) -> Video:
    """
    Display a native HTML5 video player (Streamlit `st.video` equivalent).
    """
    return _add_component(Video(
        src=data,
        caption=caption,
        controls=controls,
        autoplay=autoplay,
        muted=muted,
        loop=loop,
        width=width,
        **kwargs
    ))


def audio(
    data: Any,
    format: str = "audio/mp3",
    caption: Optional[str] = None,
    controls: bool = True,
    autoplay: bool = False,
    muted: bool = False,
    loop: bool = False,
    **kwargs
) -> Audio:
    """
    Display a native HTML5 audio player (Streamlit `st.audio` equivalent).
    """
    return _add_component(Audio(
        src=data,
        caption=caption,
        controls=controls,
        autoplay=autoplay,
        muted=muted,
        loop=loop,
        **kwargs
    ))


def popover(
    label: str = "Options",
    *children: Component,
    position: str = "bottom",
    icon: Optional[str] = None,
    **kwargs
) -> Popover:
    """
    Add a floating popover overlay container (Streamlit `st.popover` equivalent).
    Supports `with pdu.popover("Filter Options"):` syntax to nest controls inside a floating card.
    """
    trigger_text = f"{icon} {label}" if icon else label
    trigger_btn = RawHtml(f"<button type='button' class='inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-xl border border-border bg-card hover:bg-muted text-foreground transition-all shadow-xs cursor-pointer'>{escape_html(trigger_text)} <span class='text-[10px] opacity-70'>▼</span></button>")
    pop_comp = Popover(*children, trigger=trigger_btn, position=position, **kwargs)
    return _add_component(pop_comp)


def tooltip(
    text: str,
    *children: Component,
    position: str = "top",
    **kwargs
) -> Tooltip:
    """
    Render a contextual hover tooltip over child components or as a standalone info marker.
    """
    return _add_component(Tooltip(text=text, position=position, *children, **kwargs))


def write_stream(
    stream: Union[Iterator[Any], AsyncIterator[Any], Callable, Any],
    key: Optional[str] = None,
    **kwargs
) -> str:
    """
    Stream real-time tokens (e.g. from OpenAI, Ollama, LangChain, or custom generators) directly into the UI (Streamlit `st.write_stream` equivalent).
    Consumes the generator, updates markdown in real time, and returns the aggregated text output.
    """
    generator = stream() if callable(stream) and not inspect.isgenerator(stream) else stream

    accumulated = []
    try:
        for chunk in generator:
            if isinstance(chunk, str):
                text_piece = chunk
            elif isinstance(chunk, dict):
                text_piece = chunk.get("content") or chunk.get("delta", {}).get("content") or chunk.get("message", {}).get("content") or str(chunk)
            elif hasattr(chunk, "content"):
                text_piece = str(chunk.content)
            elif hasattr(chunk, "text"):
                text_piece = str(chunk.text)
            else:
                text_piece = str(chunk)
            accumulated.append(text_piece)
    except Exception as e:
        accumulated.append(f"\n[Stream error: {e}]")

    full_text = "".join(accumulated)
    if key:
        session_state[key] = full_text

    write(full_text)
    return full_text


def date_range_picker(
    label: str = "Date Range",
    value: Optional[Tuple[Optional[str], Optional[str]]] = None,
    min_date: Optional[str] = None,
    max_date: Optional[str] = None,
    key: Optional[str] = None,
    help: Optional[str] = None,
    on_change: Optional[Callable] = None,
    **kwargs
) -> Tuple[Optional[str], Optional[str]]:
    """
    Render a dual-date range selector (Start Date → End Date) bound to session state.
    Returns a tuple of `(start_date, end_date)`.
    """
    start_key = f"{key}_start" if key else generate_id("dt_start")
    end_key = f"{key}_end" if key else generate_id("dt_end")

    init_start = value[0] if (value and len(value) >= 1) else None
    init_end = value[1] if (value and len(value) >= 2) else None

    if key:
        if key in session_state and isinstance(session_state[key], (list, tuple)) and len(session_state[key]) >= 2:
            init_start, init_end = session_state[key][0], session_state[key][1]
        else:
            session_state[key] = (init_start, init_end)

    help_html = ""
    if help:
        help_html = f"<span class='group relative inline-flex items-center text-muted-foreground/70 hover:text-foreground cursor-help text-[11px] w-3.5 h-3.5 rounded-full border border-border/80 justify-center select-none ml-1'>?<span class='hidden group-hover:block absolute bottom-full left-1/2 -translate-x-1/2 mb-1.5 px-2 py-1 text-[11px] font-normal text-popover-foreground bg-popover border border-border/80 rounded-md shadow-lg pointer-events-none whitespace-normal min-w-[140px] max-w-xs text-center z-50'>{escape_html(help)}</span></span>"

    min_attr = f"min='{min_date}'" if min_date else ""
    max_attr = f"max='{max_date}'" if max_date else ""
    start_val = escape_html(init_start or "")
    end_val = escape_html(init_end or "")

    picker_html = (
        f"<div class='pdu-date-range-wrapper my-2'>"
        f"<label class='block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-1.5'>{escape_html(label)}{help_html}</label>"
        f"<div class='flex items-center gap-2'>"
        f"<input type='date' name='{start_key}' value='{start_val}' {min_attr} {max_attr} class='px-3 py-1.5 text-xs rounded-xl border border-border bg-card text-foreground focus:ring-1 focus:ring-primary focus:outline-none' />"
        f"<span class='text-muted-foreground text-xs font-bold'>→</span>"
        f"<input type='date' name='{end_key}' value='{end_val}' {min_attr} {max_attr} class='px-3 py-1.5 text-xs rounded-xl border border-border bg-card text-foreground focus:ring-1 focus:ring-primary focus:outline-none' />"
        f"</div>"
        f"</div>"
    )
    _add_component(RawHtml(picker_html))
    return (init_start, init_end)


def data_editor(
    data: Any,
    num_rows: str = "fixed",
    disabled_columns: Optional[List[str]] = None,
    key: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Render an interactive in-place editable spreadsheet table (Streamlit `st.data_editor` equivalent).
    Users can edit cell values inline, with changes synchronizing back to `session_state`.
    """
    records = []
    columns = []

    if hasattr(data, "to_dict"):
        try:
            records = data.to_dict(orient="records")
            columns = list(data.columns)
        except Exception:
            records = []
    elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        records = [dict(r) for r in data]
        columns = list(data[0].keys())
    elif isinstance(data, dict):
        columns = list(data.keys())
        first_col = list(data.values())[0] if data else []
        length = len(first_col) if isinstance(first_col, (list, tuple)) else 1
        records = [{k: data[k][i] for k in columns} for i in range(length)]
    else:
        records = []
        columns = []

    editor_key = key or generate_id("editor")
    current_data = session_state.get(editor_key, records)

    disabled_set = set(disabled_columns or [])

    th_html = "".join(f"<th class='px-3 py-2 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider border-b border-border bg-muted/30'>{escape_html(c)}</th>" for c in columns)

    tr_html = []
    for r_idx, row in enumerate(current_data):
        td_cells = []
        for c in columns:
            val = row.get(c, "")
            is_disabled = c in disabled_set
            dis_attr = "readonly disabled class='w-full px-2 py-1 text-xs bg-muted/20 text-muted-foreground rounded border border-transparent'" if is_disabled else f"name='{editor_key}_{r_idx}_{c}' class='w-full px-2 py-1 text-xs bg-transparent text-foreground rounded border border-transparent focus:border-primary focus:bg-background/80 transition-all outline-none'"
            td_cells.append(f"<td class='p-1 border-b border-border/50'><input type='text' value='{escape_html(str(val))}' {dis_attr} /></td>")
        tr_html.append(f"<tr class='hover:bg-muted/10 transition-colors'>{''.join(td_cells)}</tr>")

    table_html = (
        f"<div class='pdu-data-editor-container my-3 overflow-x-auto rounded-xl border border-border/80 bg-card shadow-sm'>"
        f"<div class='px-4 py-2 border-b border-border/60 flex items-center justify-between text-xs text-muted-foreground font-medium'>"
        f"<span>Interactive Data Editor ({len(current_data)} rows)</span>"
        f"<span class='text-[10px] text-primary/80 uppercase font-semibold'>● Double-click cell to edit</span>"
        f"</div>"
        f"<table class='w-full text-sm border-collapse'>"
        f"<thead><tr>{th_html}</tr></thead>"
        f"<tbody>{''.join(tr_html)}</tbody>"
        f"</table>"
        f"</div>"
    )
    _add_component(RawHtml(table_html))

    if hasattr(data, "iloc"):
        import pandas as pd
        return pd.DataFrame(current_data)
    return current_data


# ============================================================================
# Application Lifecycle & Runner
# ============================================================================

def page_link(page: str, label: Optional[str] = None, icon: Optional[str] = None, **kwargs) -> Component:
    """
    Render a styled navigation link to another page (Streamlit `st.page_link` equivalent).

    Example::

        with pdu.sidebar():
            pdu.page_link("/", label="GPU Telemetry", icon="📊")
            pdu.page_link("/chat", label="Operations Copilot", icon="💬")
    """
    display_label = label or page.replace('/', '').replace('_', ' ').replace('-', ' ').title() or "Home"
    icon_html = f"<span class='text-base select-none shrink-0'>{escape_html(icon)}</span>" if icon else ""
    return _add_component(RawHtml(
        f"<a href='{escape_html(page)}' class='flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted/50 transition-colors w-full'>"
        f"{icon_html}<span>{escape_html(display_label)}</span></a>"
    ))


def switch_page(path: str) -> Response:
    """
    Navigate to a different page route (Streamlit `st.switch_page` equivalent).
    Works seamlessly in both standard HTTP requests and reactive HTMX event callbacks.
    """
    session_state["_redirect_url"] = path
    return HTMLResponse("", status_code=200, headers={"HX-Redirect": path, "Location": path})


def rerun(scope: str = "app") -> Response:
    """
    Rerun the Python script / re-render the view immediately (Streamlit `st.rerun` equivalent).
    """
    session_state["_rerun_requested"] = True
    session_state["_rerun_scope"] = scope
    return HTMLResponse("", status_code=200, headers={"HX-Refresh": "true"} if scope == "app" else {})


class _DialogWrapper(Component):
    """Accessible modal dialog overlay."""
    def __init__(self, title_text: str, children: List[Component], dialog_id: str):
        super().__init__()
        self.title_text = title_text
        self.children_list = children
        self.dialog_id = dialog_id

    def render(self, state_snapshot=None) -> str:
        rendered_children = "".join(c.render(state_snapshot) for c in self.children_list)
        return (
            f"<div id='{self.dialog_id}' class='pdu-dialog-overlay fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4 animate-in fade-in duration-200'>"
            f"<div class='relative w-full max-w-lg rounded-2xl bg-card border border-border p-6 shadow-2xl space-y-4 text-foreground' onclick='event.stopPropagation()'>"
            f"<div class='flex items-center justify-between border-b border-border/60 pb-3'>"
            f"<h3 class='text-lg font-semibold tracking-tight'>{escape_html(self.title_text)}</h3>"
            f"<button type='button' onclick=\"document.getElementById('{self.dialog_id}').remove()\" "
            f"class='p-1 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted text-lg leading-none cursor-pointer'>&times;</button>"
            f"</div>"
            f"<div class='space-y-4'>{rendered_children}</div>"
            f"</div>"
            f"</div>"
        )


class DialogManager:
    """Manages modal dialogs supporting both decorator and context manager syntax."""
    def __init__(self, title: str):
        self.title = title
        self.children: List[Component] = []
        self.dialog_id = generate_id("dialog")

    def __enter__(self):
        _get_container_stack().append(self.children)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stack = _get_container_stack()
        if stack and stack[-1] is self.children:
            stack.pop()
        _add_component(_DialogWrapper(self.title, self.children, self.dialog_id))

    def __call__(self, func: Callable):
        def wrapper(*args, **kwargs):
            with DialogManager(self.title):
                return func(*args, **kwargs)
        return wrapper

    def __getattr__(self, name: str) -> Any:
        try:
            import pydataui.dx as dx_mod
            if hasattr(dx_mod, name):
                fn = getattr(dx_mod, name)
                if callable(fn):
                    def method_proxy(*args, **kwargs):
                        with self:
                            return fn(*args, **kwargs)
                    return method_proxy
        except Exception:
            pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


def dialog(title: str) -> DialogManager:
    """
    Decorator or context manager to create a modal dialog overlay (Streamlit `st.dialog` equivalent).

    Example as context manager::

        with pdu.dialog("Confirm Action"):
            pdu.write("Are you sure?")
            pdu.button("Yes", on_click=do_it)

    Example as decorator::

        @pdu.dialog("User Details")
        def show_user(user):
            pdu.write(user)
    """
    return DialogManager(title)


class _StatusWrapper(Component):
    """Live status container showing progress of multi-step operations."""
    def __init__(self, label: str, state: str, expanded: bool, children: List[Component], status_id: str):
        super().__init__()
        self.label = label
        self.state = state
        self.expanded = expanded
        self.children_list = children
        self.status_id = status_id

    def render(self, state_snapshot=None) -> str:
        icons = {
            "running": "<span class='inline-block animate-spin text-primary'>⏳</span>",
            "complete": "<span class='text-emerald-500 font-bold'>✓</span>",
            "error": "<span class='text-rose-500 font-bold'>✕</span>",
        }
        icon_html = icons.get(self.state, icons["running"])
        border_col = "border-primary/40" if self.state == "running" else ("border-emerald-500/40" if self.state == "complete" else "border-rose-500/40")
        rendered_children = "".join(c.render(state_snapshot) for c in self.children_list)
        open_attr = " open" if self.expanded else ""
        return (
            f"<details id='{self.status_id}' class='pdu-status border {border_col} rounded-2xl bg-card/60 shadow-sm transition-all my-3'{open_attr}>"
            f"<summary class='px-4 py-3 font-medium cursor-pointer text-sm select-none hover:bg-muted/40 transition-colors rounded-2xl flex items-center justify-between text-foreground'>"
            f"<span class='flex items-center gap-2.5'>{icon_html}<span class='font-semibold'>{escape_html(self.label)}</span></span>"
            f"<span class='text-muted-foreground text-xs'>▼</span>"
            f"</summary>"
            f"<div class='px-4 py-3 border-t border-border/50 text-sm space-y-3'>{rendered_children}</div>"
            f"</details>"
        )


class StatusContext:
    def __init__(self, label: str, state: str = "running", expanded: bool = True):
        self.label = label
        self.state = state
        self.expanded = expanded
        self.children: List[Component] = []
        self.status_id = generate_id("status")
        self._wrapper: Optional[_StatusWrapper] = None

    def __enter__(self):
        _get_container_stack().append(self.children)
        self._wrapper = _StatusWrapper(self.label, self.state, self.expanded, self.children, self.status_id)
        _add_component(self._wrapper)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        stack = _get_container_stack()
        if stack and stack[-1] is self.children:
            stack.pop()
        if exc_type is not None:
            self.state = "error"
            if self._wrapper:
                self._wrapper.state = "error"

    def update(self, label: Optional[str] = None, state: Optional[str] = None, expanded: Optional[bool] = None):
        """Update the status label, visual state ('running', 'complete', 'error'), and expanded flag."""
        if label is not None:
            self.label = label
            if self._wrapper:
                self._wrapper.label = label
        if state is not None:
            self.state = state
            if self._wrapper:
                self._wrapper.state = state
        if expanded is not None:
            self.expanded = expanded
            if self._wrapper:
                self._wrapper.expanded = expanded

    def __getattr__(self, name: str) -> Any:
        try:
            import pydataui.dx as dx_mod
            if hasattr(dx_mod, name):
                fn = getattr(dx_mod, name)
                if callable(fn):
                    def method_proxy(*args, **kwargs):
                        with self:
                            return fn(*args, **kwargs)
                    return method_proxy
        except Exception:
            pass
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


def status(label: str, expanded: bool = True, state: str = "running") -> StatusContext:
    """
    Context manager to display multi-step progress with expandable logs (Streamlit `st.status` equivalent).

    Example::

        with pdu.status("Executing agent workflow...", expanded=True) as s:
            pdu.write("Querying telemetry nodes...")
            pdu.write("Synthesizing analysis...")
            s.update(label="Analysis complete!", state="complete", expanded=False)
    """
    return StatusContext(label, state=state, expanded=expanded)


class _EmptyContainer(Component):
    def __init__(self, element_id: str):
        super().__init__()
        self.element_id = element_id
        self.children_list: List[Component] = []

    def render(self, state_snapshot=None) -> str:
        if not self.children_list:
            return f"<div id='{self.element_id}' class='pdu-empty'></div>"
        rendered = "".join(c.render(state_snapshot) for c in self.children_list)
        return f"<div id='{self.element_id}' class='pdu-empty'>{rendered}</div>"


class EmptyPlaceholder:
    def __init__(self):
        self.element_id = generate_id("empty")
        self._container = _EmptyContainer(self.element_id)
        _add_component(self._container)

    def write(self, *args, **kwargs):
        self._container.children_list.clear()
        with _ContainerContext(self._container.children_list):
            write(*args, **kwargs)

    def text(self, content: str, **kwargs):
        self._container.children_list.clear()
        with _ContainerContext(self._container.children_list):
            text(content, **kwargs)

    def empty(self):
        self._container.children_list.clear()

    def container(self) -> _ContainerContext:
        self._container.children_list.clear()
        return _ContainerContext(self._container.children_list)


def empty() -> EmptyPlaceholder:
    """
    Create a single-element placeholder container that can be cleared or overwritten (Streamlit `st.empty` equivalent).
    """
    return EmptyPlaceholder()


# ============================================================================
# Caching Engines (`@pdu.cache_data`, `@pdu.cache_resource`)
# ============================================================================

_DATA_CACHE: Dict[str, Tuple[float, Any]] = {}
_RESOURCE_CACHE: Dict[str, Tuple[float, Any]] = {}

def _cache_func_prefix(func: Callable) -> str:
    return f"{getattr(func, '__module__', '')}:{getattr(func, '__qualname__', getattr(func, '__name__', 'fn'))}:"

def _cache_key(func: Callable, args: tuple, kwargs: dict) -> str:
    prefix = _cache_func_prefix(func)
    try:
        raw_args = f"{str(args)}:{str(sorted(kwargs.items()))}"
    except Exception:
        raw_args = str(id(args))
    args_hash = hashlib.sha256(raw_args.encode("utf-8", errors="ignore")).hexdigest()
    return f"{prefix}{args_hash}"

class _CacheDataDecorator:
    def __init__(self, ttl: Optional[float] = None, max_entries: Optional[int] = None):
        self.ttl = ttl
        self.max_entries = max_entries

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _cache_key(func, args, kwargs)
            now = time.time()
            if key in _DATA_CACHE:
                cached_time, val = _DATA_CACHE[key]
                if self.ttl is None or (now - cached_time) < self.ttl:
                    return copy.deepcopy(val)
            res = func(*args, **kwargs)
            if self.max_entries and len(_DATA_CACHE) >= self.max_entries:
                oldest_key = min(_DATA_CACHE.keys(), key=lambda k: _DATA_CACHE[k][0])
                _DATA_CACHE.pop(oldest_key, None)
            _DATA_CACHE[key] = (now, copy.deepcopy(res))
            return res

        def clear():
            prefix = _cache_func_prefix(func)
            to_del = [k for k in _DATA_CACHE if k.startswith(prefix)]
            for k in to_del:
                _DATA_CACHE.pop(k, None)

        wrapper.clear = clear
        return wrapper

    @staticmethod
    def clear():
        _DATA_CACHE.clear()


class _CacheResourceDecorator:
    def __init__(self, ttl: Optional[float] = None, max_entries: Optional[int] = None):
        self.ttl = ttl
        self.max_entries = max_entries

    def __call__(self, func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = _cache_key(func, args, kwargs)
            now = time.time()
            if key in _RESOURCE_CACHE:
                cached_time, val = _RESOURCE_CACHE[key]
                if self.ttl is None or (now - cached_time) < self.ttl:
                    return val
            res = func(*args, **kwargs)
            if self.max_entries and len(_RESOURCE_CACHE) >= self.max_entries:
                oldest_key = min(_RESOURCE_CACHE.keys(), key=lambda k: _RESOURCE_CACHE[k][0])
                _RESOURCE_CACHE.pop(oldest_key, None)
            _RESOURCE_CACHE[key] = (now, res)
            return res

        def clear():
            prefix = _cache_func_prefix(func)
            to_del = [k for k in _RESOURCE_CACHE if k.startswith(prefix)]
            for k in to_del:
                _RESOURCE_CACHE.pop(k, None)

        wrapper.clear = clear
        return wrapper

    @staticmethod
    def clear():
        _RESOURCE_CACHE.clear()


def cache_data(func: Optional[Callable] = None, *, ttl: Optional[float] = None, max_entries: Optional[int] = None):
    """
    Decorator to cache function results (DataFrames, queries, computations) (Streamlit `st.cache_data` equivalent).
    Supports time-to-live (`ttl` in seconds) and `max_entries` eviction.
    """
    if func is not None and callable(func):
        return _CacheDataDecorator(ttl=ttl, max_entries=max_entries)(func)
    return _CacheDataDecorator(ttl=ttl, max_entries=max_entries)

cache_data.clear = _CacheDataDecorator.clear


def cache_resource(func: Optional[Callable] = None, *, ttl: Optional[float] = None, max_entries: Optional[int] = None):
    """
    Decorator to cache shared global singleton resources (ML models, DB pools, API clients) (Streamlit `st.cache_resource` equivalent).
    """
    if func is not None and callable(func):
        return _CacheResourceDecorator(ttl=ttl, max_entries=max_entries)(func)
    return _CacheResourceDecorator(ttl=ttl, max_entries=max_entries)

cache_resource.clear = _CacheResourceDecorator.clear


# ============================================================================
# Navigation & Menus
# ============================================================================

def navigation(pages: Optional[Union[List[str], Dict[str, List[str]]]] = None) -> Component:
    """
    Render a modern, styled sidebar navigation menu (Streamlit `st.navigation` equivalent).
    Automatically highlights the currently active page and filters by user permissions.

    Example::

        with pdu.sidebar():
            pdu.navigation()  # Auto-discovers all @pdu.page routes
    """
    app = get_app()
    all_pages = app._page_router.get_all_pages()

    curr_path = "/"
    try:
        from .state import _current_session
        sess = _current_session.get()
        if sess and sess.current_page:
            curr_path = sess.current_page
    except Exception:
        pass

    links_html = []

    if isinstance(pages, dict):
        for section, section_pages in pages.items():
            links_html.append(f"<div class='px-3 pt-3 pb-1 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider'>{escape_html(section)}</div>")
            for p_path in section_pages:
                page_obj = app._page_router.get_page(p_path)
                display_label = (page_obj.title if page_obj and page_obj.title else None) or p_path.replace('/', '').replace('_', ' ').replace('-', ' ').title() or "Home"
                active = (p_path == curr_path)
                active_cls = "bg-primary text-primary-foreground font-semibold shadow-sm" if active else "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                links_html.append(
                    f"<a href='{escape_html(p_path)}' class='flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-colors w-full {active_cls}'>"
                    f"<span>{escape_html(display_label)}</span></a>"
                )
    else:
        route_list = pages if isinstance(pages, list) else [p.path for p in all_pages]
        for p_path in route_list:
            page_obj = app._page_router.get_page(p_path)
            display_label = (page_obj.title if page_obj and page_obj.title else None) or p_path.replace('/', '').replace('_', ' ').replace('-', ' ').title() or "Home"
            active = (p_path == curr_path)
            active_cls = "bg-primary text-primary-foreground font-semibold shadow-sm" if active else "text-muted-foreground hover:text-foreground hover:bg-muted/50"
            links_html.append(
                f"<a href='{escape_html(p_path)}' class='flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-colors w-full {active_cls}'>"
                f"<span>{escape_html(display_label)}</span></a>"
            )

    return _add_component(RawHtml(f"<nav class='space-y-1 w-full my-2'>{''.join(links_html)}</nav>"))


# ============================================================================
# Production Authentication Helpers
# ============================================================================

def login(username: str, password: str) -> bool:
    """
    Authenticate a user in procedural Streamlit mode.
    Integrates directly with PyDataUI's AuthManager, sets session JWT tokens, and updates session_state.
    Returns True if authentication succeeded, False otherwise.
    """
    app = get_app()
    from .auth.manager import AuthManager
    if app.auth is None:
        auth_mgr = AuthManager.get_default() or AuthManager()
        app.auth = auth_mgr
        AuthManager.set_default(auth_mgr)
    auth_mgr = app.auth

    token = auth_mgr.authenticate(username, password)
    if token:
        user = auth_mgr.verify_token(token)
        try:
            from .state import _current_session
            sess = _current_session.get()
            if sess:
                sess.data["auth_token"] = token
                sess.data["auth_user_id"] = user.id if user else username
                if "dx_session_state" not in sess.data:
                    sess.data["dx_session_state"] = {}
                sess.data["dx_session_state"]["authenticated"] = True
                sess.data["dx_session_state"]["user"] = user.username if user else username
                sess.data["dx_session_state"]["user_roles"] = list(user.roles) if user else []
        except Exception:
            pass
        session_state["authenticated"] = True
        session_state["user"] = user.username if user else username
        session_state["user_roles"] = list(user.roles) if user else []
        session_state.pop("auth_error", None)
        return True
    else:
        session_state["authenticated"] = False
        session_state["auth_error"] = "Invalid username or password"
        return False


def logout() -> None:
    """
    Sign out the current user and revoke their session.
    """
    try:
        from .state import _current_session
        sess = _current_session.get()
        if sess:
            auth_token = sess.data.get("auth_token")
            if auth_token:
                app = get_app()
                if app.auth:
                    app.auth.revoke_token(auth_token)
            sess.data["auth_token"] = ""
            sess.data["auth_user_id"] = None
            if "dx_session_state" in sess.data:
                sess.data["dx_session_state"]["authenticated"] = False
                sess.data["dx_session_state"]["user"] = None
                sess.data["dx_session_state"]["user_roles"] = []
    except Exception:
        pass
    session_state["authenticated"] = False
    session_state["user"] = None
    session_state["user_roles"] = []


def is_authenticated() -> bool:
    """Return True if a user is currently authenticated in this session."""
    try:
        from .state import _current_session
        sess = _current_session.get()
        if sess and sess.data.get("auth_token"):
            return True
    except Exception:
        pass
    return bool(session_state.get("authenticated", False))


def current_user() -> Optional[Any]:
    """Return the currently authenticated User instance or username."""
    try:
        from .state import _current_session
        sess = _current_session.get()
        if sess and sess.data.get("auth_token"):
            app = get_app()
            if app.auth:
                user = app.auth.verify_token(sess.data["auth_token"])
                if user:
                    return user
    except Exception:
        pass
    return session_state.get("user")


def create_user(username: str, password: str, email: str = "", roles: Optional[List[str]] = None) -> Any:
    """
    Register a new user account with specified roles.
    """
    app = get_app()
    from .auth.manager import AuthManager
    if app.auth is None:
        auth_mgr = AuthManager()
        app.auth = auth_mgr
        AuthManager.set_default(auth_mgr)
    return app.auth.add_user(username, password, email=email, roles=roles or ["user"])


def require_auth(roles: Optional[List[str]] = None, redirect_to: str = "/login") -> bool:
    """
    Procedural authentication guard. Call at the start of a page function.
    If not authenticated or role check fails, immediately switches page to `redirect_to`.
    """
    if not is_authenticated():
        switch_page(redirect_to)
        return False
    if roles:
        user = current_user()
        user_roles = getattr(user, "roles", []) if hasattr(user, "roles") else session_state.get("user_roles", [])
        if not any(r in user_roles for r in roles):
            switch_page(redirect_to)
            return False
    return True


def page(path: str = "/", title: Optional[str] = None, layout: Optional[Callable] = None, *, public: bool = False, roles=(), **kwargs):
    """
    Decorator to register a procedural or component page route on the default application.
    Enables multi-page apps, login/signup flows, and role-based access control.

    Example::

        @pdu.page("/login", public=True)
        def login():
            pdu.title("Sign In")
            pdu.text_input("Email", key="email")
            pdu.button("Sign In", on_click=handle_login)

        @pdu.page("/dashboard", roles=["admin"])
        def dashboard():
            pdu.title("Telemetry Dashboard")
            pdu.metric("ARR", "$1.8M")
    """
    app = get_app()
    def decorator(func: Callable):
        def procedural_page_wrapper(*args, **kws):
            page_components: List[Component] = []
            page_sidebar: List[Component] = []
            page_container_stack: List[List[Component]] = []
            token_sb = _active_page_sidebar.set(page_sidebar)
            token_stack = _active_container_stack.set(page_container_stack)
            try:
                with _ContainerContext(page_components):
                    res = func(*args, **kws)
            finally:
                _active_page_sidebar.reset(token_sb)
                _active_container_stack.reset(token_stack)

            if res is not None:
                return res

            is_wide = _page_config.get("layout") == "wide"
            theme_val = _page_config.get("theme", "zinc")
            theme_css = _resolve_theme_css(theme_val)

            effective_sidebar = page_sidebar if page_sidebar else _sidebar_components

            return _ProceduralPageLayout(
                sidebar_components=effective_sidebar,
                main_components=page_components,
                is_wide=is_wide,
                theme_css=theme_css,
            )

        procedural_page_wrapper.__name__ = getattr(func, "__name__", "page_wrapper")
        return app.page(path, title=title, layout=layout, public=public, roles=roles, **kwargs)(procedural_page_wrapper)
    return decorator


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
    global _default_app, _default_page_components, _sidebar_components, _container_stack, _callbacks, _active_form_stack
    _default_app = None
    _default_page_components.clear()
    _sidebar_components.clear()
    _container_stack.clear()
    _callbacks.clear()
    _active_form_stack.clear()
    for name in list(dir(ActionState)):
        if name.startswith("act_"):
            try:
                delattr(ActionState, name)
            except AttributeError:
                pass
    cache_data.clear()
    cache_resource.clear()
    try:
        from .auth.manager import AuthManager
        AuthManager.set_default(None)
    except Exception:
        pass
    _page_config.update({
        "title": "PyDataUI App",
        "layout": "centered",
        "theme": "zinc",
        "dark_mode": True,
    })


get_default_app = get_app
