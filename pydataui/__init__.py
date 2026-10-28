from __future__ import annotations
import importlib
import sys
from typing import TYPE_CHECKING, Any, Dict, Tuple

__version__ = '1.1.0'

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
