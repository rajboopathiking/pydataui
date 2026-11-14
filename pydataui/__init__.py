from __future__ import annotations
import importlib
import sys
from typing import TYPE_CHECKING, Any, Dict, Tuple

__version__ = '1.2.2'

# Mapping of exported symbol names to (submodule_relative_path, attribute_name).
# If attribute_name is None, the submodule itself is returned.
_LAZY_IMPORTS: Dict[str, Tuple[str, str | None]] = {
    # Core Application & State
    'App': ('.app', 'App'),
    'State': ('.state', 'State'),
    'StateVar': ('.state', 'StateVar'),
    'StateVarRef': ('.state', 'StateVarRef'),
    'EventHandler': ('.state', 'EventHandler'),
    'AppConfig': ('.config', 'AppConfig'),
    'state': ('.state', 'state'),
    'reactive_state': ('.state', 'reactive_state'),
    'ProceduralState': ('.state', 'ProceduralState'),

    # Layout Primitives
    'Row': ('.components.layout', 'Row'),
    'Col': ('.components.layout', 'Col'),
    'Grid': ('.components.layout', 'Grid'),
    'Spacer': ('.components.layout', 'Spacer'),
    'Container': ('.components.layout', 'Container'),
    'Box': ('.components.layout', 'Box'),
    'HStack': ('.components.layout', 'HStack'),
    'VStack': ('.components.layout', 'VStack'),
    'Card': ('.components.layout', 'Card'),
    'Divider': ('.components.layout', 'Divider'),

    # Data Display & Universal Sniffing
    'DataTable': ('.components.data_display', 'DataTable'),
    'Table': ('.components.data_display', 'Table'),
    'sniff_tabular_data': ('.components.data_display', 'sniff_tabular_data'),
    'Badge': ('.components.data_display', 'Badge'),
    'Tag': ('.components.data_display', 'Tag'),
    'Stat': ('.components.data_display', 'Stat'),
    'KeyValue': ('.components.data_display', 'KeyValue'),
    'Avatar': ('.components.data_display', 'Avatar'),
    'Tooltip': ('.components.data_display', 'Tooltip'),
    'List': ('.components.data_display', 'List'),
    'ListItem': ('.components.data_display', 'ListItem'),
    'DescriptionList': ('.components.data_display', 'DescriptionList'),
    'MetricCard': ('.components.data_science', 'MetricCard'),

    # Forms & Input
    'Button': ('.components.forms', 'Button'),
    'Input': ('.components.forms', 'Input'),
    'TextArea': ('.components.forms', 'TextArea'),
    'Select': ('.components.forms', 'Select'),
    'Checkbox': ('.components.forms', 'Checkbox'),
    'Radio': ('.components.forms', 'Radio'),
    'RadioGroup': ('.components.forms', 'RadioGroup'),
    'Switch': ('.components.forms', 'Switch'),
    'Slider': ('.components.forms', 'Slider'),
    'Form': ('.components.forms', 'Form'),
    'FileUpload': ('.components.forms', 'FileUpload'),
    'ShadForm': ('.shadcn', 'ShadForm'),

    # Typography
    'Heading': ('.components.typography', 'Heading'),
    'Text': ('.components.typography', 'Text'),
    'Paragraph': ('.components.typography', 'Paragraph'),
    'Link': ('.components.typography', 'Link'),
    'Code': ('.components.typography', 'Code'),
    'Blockquote': ('.components.typography', 'Blockquote'),
    'Label': ('.components.typography', 'Label'),

    # Feedback & Status
    'Alert': ('.components.feedback', 'Alert'),
    'Progress': ('.components.feedback', 'Progress'),
    'Spinner': ('.components.feedback', 'Spinner'),
    'Skeleton': ('.components.feedback', 'Skeleton'),
    'Toast': ('.components.feedback', 'Toast'),
    'Empty': ('.components.feedback', 'Empty'),

    # Navigation Primitives
    'Navbar': ('.components.navigation', 'Navbar'),
    'NavLink': ('.components.navigation', 'NavLink'),
    'Breadcrumb': ('.components.navigation', 'Breadcrumb'),
    'Tabs': ('.components.navigation', 'Tabs'),
    'Tab': ('.components.navigation', 'Tab'),
    'Pagination': ('.components.navigation', 'Pagination'),
    'Menu': ('.components.navigation', 'Menu'),

    # Overlays & Dialogs
    'Modal': ('.components.overlay', 'Modal'),
    'Drawer': ('.components.overlay', 'Drawer'),
    'Popover': ('.components.overlay', 'Popover'),
    'Dropdown': ('.components.overlay', 'Dropdown'),

    # TUI
    'tui': ('.tui', 'run_tui'),
    'run_tui': ('.tui', 'run_tui'),

    
    # Auth
    'AuthManager': ('.auth', 'AuthManager'),
    'User': ('.auth', 'User'),
    'Role': ('.auth', 'Role'),
    'APIKey': ('.auth', 'APIKey'),
    'require_auth': ('.auth', 'require_auth'),
    'require_role': ('.auth', 'require_role'),
    'require_api_key': ('.auth', 'require_api_key'),
    'LoginState': ('.auth', 'LoginState'),
    'current_user': ('.auth', 'current_user'),
    
    # Tunnel & Storage
    'TunnelManager': ('.tunnel', 'TunnelManager'),
    'BaseSessionStore': ('.storage', 'BaseSessionStore'),
    'BaseAuthStore': ('.storage', 'BaseAuthStore'),
    'MemorySessionStore': ('.storage', 'MemorySessionStore'),
    'MemoryAuthStore': ('.storage', 'MemoryAuthStore'),
    'SQLiteSessionStore': ('.storage', 'SQLiteSessionStore'),
    'SQLiteAuthStore': ('.storage', 'SQLiteAuthStore'),
    'PostgresSessionStore': ('.storage', 'PostgresSessionStore'),
    'PostgresAuthStore': ('.storage', 'PostgresAuthStore'),
    'Database': ('.storage', 'Database'),
    'parse_storage_backend': ('.storage', 'parse_storage_backend'),
    'parse_storage_path': ('.storage', 'parse_storage_path'),
    'create_session_store': ('.storage', 'create_session_store'),
    'create_auth_store': ('.storage', 'create_auth_store'),
    
    # Components & Mount
    'Component': ('.components.base', 'Component'),
    'RawHtml': ('.components.base', 'RawHtml'),
    'Html': ('.components.base', 'Html'),
    'Markdown': ('.components.advanced', 'Markdown'),
    'CodeEditor': ('.components.advanced', 'CodeEditor'),
    'Chat': ('.components.advanced', 'Chat'),
    'mount': ('.mount', 'mount'),
    
    # HTTP Responses
    'Response': ('.responses', 'Response'),
    'HTMLResponse': ('.responses', 'HTMLResponse'),
    'JSONResponse': ('.responses', 'JSONResponse'),
    'PlainTextResponse': ('.responses', 'PlainTextResponse'),
    'RedirectResponse': ('.responses', 'RedirectResponse'),
    'StreamingResponse': ('.responses', 'StreamingResponse'),
    
    # DX Declarative Helpers
    'title': ('.dx', 'title'),
    'header': ('.dx', 'header'),
    'subheader': ('.dx', 'subheader'),
    'text': ('.dx', 'text'),
    'markdown': ('.dx', 'markdown'),
    'button': ('.dx', 'button'),
    'input': ('.dx', 'input'),
    'textarea': ('.dx', 'textarea'),
    'card': ('.dx', 'card'),
    'row': ('.dx', 'row'),
    'column': ('.dx', 'column'),
    'divider': ('.dx', 'divider'),
    'metric': ('.dx', 'metric'),
    'dataframe': ('.dx', 'dataframe'),
    'table': ('.dx', 'table'),
    'code_editor': ('.dx', 'code_editor'),
    'chat': ('.dx', 'chat'),
    'page': ('.dx', 'page'),
    'run': ('.dx', 'run'),
    'get_app': ('.dx', 'get_app'),
    'get_default_app': ('.dx', 'get_default_app'),
    
    # Modern Dashboards & Extensibility
    'DashboardLayout': ('.shadcn', 'DashboardLayout'),
    'Sidebar': ('.shadcn', 'Sidebar'),
    'Header': ('.shadcn', 'Header'),
    'NavGroup': ('.shadcn', 'NavGroup'),
    'NavItem': ('.shadcn', 'NavItem'),
    'create_shadcn_component': ('.shadcn', 'create_shadcn_component'),
    'from_jsx': ('.shadcn', 'from_jsx'),
    'from_html': ('.shadcn', 'from_html'),
    
    # Shell & Native
    'init_tauri': ('.shell', 'init_tauri'),
    'init_capacitor': ('.shell', 'init_capacitor'),
    'open_desktop_window': ('.shell', 'open_desktop_window'),
    'get_preview_html': ('.shell', 'get_preview_html'),
    'JNIBridge': ('.shell', 'JNIBridge'),
    'dispatch_in_process': ('.shell', 'dispatch_in_process'),
    'NativeRenderer': ('.compiler.native', 'NativeRenderer'),
    'NativeWidgetNode': ('.compiler.native', 'NativeWidgetNode'),
    'compile_native': ('.compiler.native', 'compile_native'),
    
    # Submodules
    'html': ('.html', None),
    'shadcn': ('.shadcn', None),
    'templates': ('.templates', None),
    'components': ('.components', None),
    
    # Exceptions
    'PyDataUIError': ('.exceptions', 'PyDataUIError'),
    'StateError': ('.exceptions', 'StateError'),
    'ComponentError': ('.exceptions', 'ComponentError'),
    'SessionError': ('.exceptions', 'SessionError'),
    'EventError': ('.exceptions', 'EventError'),
    'ConfigError': ('.exceptions', 'ConfigError'),
    'RenderError': ('.exceptions', 'RenderError'),
    'APIError': ('.exceptions', 'APIError'),
    'ConcurrencyError': ('.exceptions', 'ConcurrencyError'),
    'AuthenticationThrottledError': ('.exceptions', 'AuthenticationThrottledError'),
}

__all__ = sorted(list(_LAZY_IMPORTS.keys()) + ['__version__'])


def __getattr__(name: str) -> Any:
    """PEP 562 lazy module attribute loader for fast cold starts."""
    if name in _LAZY_IMPORTS:
        submod, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(submod, package=__package__)
        val = getattr(mod, attr_name) if attr_name is not None else mod
        globals()[name] = val
        return val

    # Fallback: check if name is any submodule in pydataui package
    try:
        mod = importlib.import_module(f".{name}", package=__package__)
        globals()[name] = mod
        return mod
    except ModuleNotFoundError:
        pass

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:
    """Ensure dir(pydataui) includes all lazily loadable attributes."""
    return sorted(set(list(globals().keys()) + list(_LAZY_IMPORTS.keys())))


if TYPE_CHECKING:
    # Full static type hints for type checkers (Mypy, Pyright, VS Code) without runtime overhead
    from .app import App
    from .state import State, StateVar, StateVarRef, EventHandler
    from .config import AppConfig
    from .exceptions import (
        PyDataUIError, StateError, ComponentError, SessionError, EventError,
        ConfigError, RenderError, APIError, ConcurrencyError, AuthenticationThrottledError
    )
    from .auth import (
        AuthManager, User, Role, APIKey,
        require_auth, require_role, require_api_key,
        LoginState, current_user
    )
    from .tunnel import TunnelManager
    from .storage import (
        BaseSessionStore, BaseAuthStore,
        MemorySessionStore, MemoryAuthStore,
        SQLiteSessionStore, SQLiteAuthStore,
        PostgresSessionStore, PostgresAuthStore,
        Database, parse_storage_backend, parse_storage_path,
        create_session_store, create_auth_store
    )
    from .components.base import Component, RawHtml, Html
    from .components.advanced import Markdown, CodeEditor, Chat
    from .components.layout import Row, Col, Grid, Spacer, Container, Box, HStack, VStack, Card, Divider
    from .components.typography import Heading, Text, Paragraph, Link, Code, Blockquote, Label
    from .components.forms import Button, Input, TextArea, Select, Checkbox, Radio, RadioGroup, Switch, Slider, Form, FileUpload
    from .components.data_display import DataTable, Table, Badge, Tag, Stat, KeyValue, Avatar, Tooltip, List, ListItem, DescriptionList
    from .components.feedback import Alert, Progress, Spinner, Skeleton, Toast, Empty
    from .components.navigation import Navbar, NavLink, Breadcrumb, Tabs, Tab, Pagination, Menu
    from .components.overlay import Modal, Drawer, Popover, Dropdown
    from .mount import mount
    from .shell import init_tauri, init_capacitor, open_desktop_window, get_preview_html
    from .responses import (
        Response, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse, StreamingResponse
    )
    from .dx import (
        title, header, subheader, text, markdown, button, input, textarea,
        card, row, column, divider, metric, dataframe, table, code_editor,
        chat, page, run, get_app, get_default_app
    )
    from . import html, templates, components
