from typing import Callable, Optional
from ..config import AppConfig
from ..types import StateSnapshot
from .templates import get_base_html, get_fragment_html
from ..components.base import Component
from ..state import _current_snapshot

class Renderer:
    """Renders component trees to HTML."""
    def __init__(self, config: AppConfig):
        self.config = config
        
    def render_page(self, page_func: Callable, state_snapshot: StateSnapshot, title: Optional[str] = None) -> str:
        """Render a full page: call page_func, get component tree, render to HTML, wrap in shell."""
        token = _current_snapshot.set(state_snapshot)
        try:
            component = page_func()
            content = component.render(state_snapshot) if isinstance(component, Component) else str(component)
        finally:
            _current_snapshot.reset(token)
        css_url = f'{self.config.internal_prefix}/static/pydataui.css'
        htmx_url = f'{self.config.internal_prefix}/static/htmx.min.js'
        return get_base_html(
            title=title or self.config.title,
            content=content,
            css_url=css_url,
            htmx_url=htmx_url,
            theme=getattr(self.config, 'theme', 'light'),
            palette=getattr(self.config, 'palette', 'zinc'),
            tailwind_config=getattr(self.config, 'tailwind_config', None),
            custom_css=getattr(self.config, 'custom_css', None),
            stylesheets=getattr(self.config, 'stylesheets', None) or [],
            scripts=getattr(self.config, 'scripts', None) or [],
            extra_head=getattr(self.config, 'head', '') or '',
        )
        
    def render_fragment(self, page_func: Callable, state_snapshot: StateSnapshot) -> str:
        """Render just the inner content for HTMX partial updates."""
        token = _current_snapshot.set(state_snapshot)
        try:
            component = page_func()
            content = component.render(state_snapshot) if isinstance(component, Component) else str(component)
        finally:
            _current_snapshot.reset(token)
        return get_fragment_html(content)
