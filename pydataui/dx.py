"""
Simplified Python-first developer experience (DX) module for PyDataUI.
Streamlit-like simplicity while reusing 100% of the existing PyDataUI component
and reactive state engine.

Usage::

    import pydataui as ui

    ui.title("Analytics Dashboard")
    ui.text("Welcome to the real-time overview.")

    def refresh():
        print("Data refreshed!")

    ui.button("Refresh", on_click=refresh)
    ui.run()
"""
from __future__ import annotations
import inspect
from typing import Any, Callable, Dict, List, Optional, Union

from .app import App
from .state import State, EventHandler
from .components.base import Component
from .components.layout import Container, Card, HStack, VStack, Divider
from .components.typography import Heading, Text, Paragraph
from .components.forms import Button, Input, TextArea
from .components.data_science import DataFrameTable, MetricCard
from .components.data_display import DataTable
from .components.advanced import Markdown, CodeEditor, Chat


class ActionState(State):
    """Dynamic action state hosting simplified DX Python callbacks."""
    pass


_callbacks: Dict[str, Callable] = {}
_default_app: Optional[App] = None
_default_page_components: List[Component] = []


def register_callback(func: Callable) -> str:
    """Register a plain Python function as an ActionState method."""
    action_id = f"act_{len(_callbacks)}_{getattr(func, '__name__', 'cb')}"
    _callbacks[action_id] = func

    def action_method(self, **kwargs):
        cb = _callbacks.get(action_id)
        if cb:
            sig = inspect.signature(cb)
            if len(sig.parameters) == 0:
                return cb()
            call_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            return cb(**call_kwargs)

    action_method.__name__ = action_id
    setattr(ActionState, action_id, action_method)
    return action_id


def get_app() -> App:
    """Return the global default App instance, initializing it if necessary."""
    global _default_app
    if _default_app is None:
        _default_app = App(title="PyDataUI App")

        @_default_app.page("/")
        def default_home():
            return Container(
                *_default_page_components,
                class_name="max-w-5xl mx-auto p-6 space-y-4"
            )
    return _default_app


def _add_component(comp: Component) -> Component:
    get_app()  # Ensure app exists
    _default_page_components.append(comp)
    return comp


def title(text: str, **kwargs) -> Heading:
    """Add a top-level page title."""
    app = get_app()
    app.config.title = text
    return _add_component(Heading(text, level=1, **kwargs))


def header(text: str, **kwargs) -> Heading:
    """Add a section header (H2)."""
    return _add_component(Heading(text, level=2, **kwargs))


def subheader(text: str, **kwargs) -> Heading:
    """Add a section subheader (H3)."""
    return _add_component(Heading(text, level=3, **kwargs))


def text(content: str, **kwargs) -> Text:
    """Add a text element."""
    return _add_component(Text(content, **kwargs))


def markdown(content: str, **kwargs) -> Markdown:
    """Add a rendered markdown element."""
    return _add_component(Markdown(content, **kwargs))


def button(label: str, on_click: Optional[Union[Callable, EventHandler]] = None, **kwargs) -> Button:
    """Add an interactive button with a Python event callback."""
    return _add_component(Button(label, on_click=on_click, **kwargs))


def input(label: str = "", value: Any = None, placeholder: str = "", **kwargs) -> Input:
    """Add a text input element."""
    return _add_component(Input(label=label, value=value, placeholder=placeholder, **kwargs))


def textarea(label: str = "", value: Any = None, placeholder: str = "", **kwargs) -> TextArea:
    """Add a multiline text area."""
    return _add_component(TextArea(label=label, value=value, placeholder=placeholder, **kwargs))


def card(*children, **kwargs) -> Card:
    """Add a card container."""
    return _add_component(Card(*children, **kwargs))


def row(*children, **kwargs) -> HStack:
    """Add a horizontal layout row."""
    return _add_component(HStack(*children, **kwargs))


def column(*children, **kwargs) -> VStack:
    """Add a vertical layout column."""
    return _add_component(VStack(*children, **kwargs))


def divider(**kwargs) -> Divider:
    """Add a visual divider."""
    return _add_component(Divider(**kwargs))


def metric(label: str, value: Any, delta: Optional[str] = None, change: Optional[str] = None, **kwargs) -> MetricCard:
    """Add a KPI metric card."""
    d = delta if delta is not None else change
    return _add_component(MetricCard(title=label, value=value, delta=d, **kwargs))


def dataframe(df: Any, max_rows: int = 100, **kwargs) -> DataFrameTable:
    """Add an interactive Pandas / Polars DataFrame table."""
    # Convert Polars DataFrame to Pandas if needed
    if hasattr(df, "to_pandas") and not hasattr(df, "iloc"):
        try:
            df = df.to_pandas()
        except Exception:
            pass
    return _add_component(DataFrameTable(df=df, max_rows=max_rows, **kwargs))


def table(data: Any, columns: Optional[List[str]] = None, **kwargs) -> DataTable:
    """Add a data table."""
    return _add_component(DataTable(data=data, columns=columns, **kwargs))


def code_editor(code: str = "", language: str = "python", theme: str = "dark", on_change: Optional[Callable] = None, **kwargs) -> CodeEditor:
    """Add a Python-first code editor without user JavaScript."""
    return _add_component(CodeEditor(code=code, language=language, theme=theme, on_change=on_change, **kwargs))


def chat(messages: Optional[List[Dict[str, str]]] = None, on_send: Optional[Callable] = None, **kwargs) -> Chat:
    """Add an interactive chat interface for AI agents."""
    return _add_component(Chat(messages=messages, on_send=on_send, **kwargs))


def page(path: str = "/", title: Optional[str] = None, **kwargs):
    """Decorator to register a page route on the default application."""
    app = get_app()
    return app.page(path, title=title, **kwargs)


def run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False, **kwargs):
    """Run the default application server."""
    app = get_app()
    app.run(host=host, port=port, reload=reload, **kwargs)


get_default_app = get_app
