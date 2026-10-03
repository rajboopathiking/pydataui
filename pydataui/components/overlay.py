from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Modal(Component):
    """
    Accessible Modal Dialog Component.
    
    Renders a fixed backdrop and centered dialog card.
    The backdrop captures clicks outside to close (if close_on_overlay=True),
    while the dialog card and its inputs are strictly on top (higher z-index)
    and fully interactive.
    """
    tag = 'div'
    
    SIZE_CLASSES = {
        'sm': 'max-w-sm',
        'md': 'max-w-lg',
        'lg': 'max-w-2xl',
        'xl': 'max-w-4xl',
        'full': 'max-w-full m-4',
    }

    SIZE_MAX_WIDTHS = {
        'sm': '400px',
        'md': '600px',
        'lg': '800px',
        'xl': '1000px',
        'full': '95vw',
    }

    def __init__(
        self,
        *children,
        title: Optional[Any] = None,
        is_open: bool = False,
        on_close: Optional[Any] = None,
        size: str = 'md',
        close_on_overlay: bool = True,
        **props
    ):
        super().__init__(*children, **props)
        self.title = title
        self.is_open = is_open
        self.size = size
        self.close_on_overlay = close_on_overlay
        # Store on_close separately so it does NOT attach to the outer wrapper
        self.on_close = on_close

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        is_open = self._resolve_value(self.is_open, snap)
        if not is_open:
            return ""

        children_html = self._render_children(snap)
        
        # Build HTMX attributes for close triggers
        close_attrs_str = ""
        overlay_close_str = ""
        if self.on_close:
            htmx_close = self._get_event_htmx_attrs('on_click', self.on_close)
            close_attrs_str = " ".join(f'{k}="{v}"' for k, v in htmx_close.items())
            if self.close_on_overlay:
                overlay_close_str = close_attrs_str

        # Modal Header
        header_html = ""
        if self.title:
            t = escape_html(str(self._resolve_value(self.title, snap)))
            header_html = (
                f'<div class="pdu-modal-header flex items-center justify-between p-4 border-b border-border bg-card">'
                f'<h3 class="text-lg font-semibold leading-none tracking-tight">{t}</h3>'
                f'<button type="button" class="pdu-modal-close text-muted-foreground hover:text-foreground text-xl font-bold p-1 rounded transition-colors" {close_attrs_str}>&times;</button>'
                f'</div>'
            )

        max_width = self.SIZE_MAX_WIDTHS.get(self.size, '600px')
        tailwind_size = self.SIZE_CLASSES.get(self.size, 'max-w-lg')

        return f'''<div id="{self.id}" class="pdu-modal-wrapper fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto" style="position:fixed;inset:0;z-index:1000;display:flex;align-items:center;justify-content:center;padding:1rem;">
  <!-- Dark transparent backdrop overlay -->
  <div class="pdu-modal-overlay fixed inset-0 transition-opacity" style="position:fixed;inset:0;background-color:rgba(0,0,0,0.5);z-index:1;" {overlay_close_str}></div>

  <!-- Dialog content card: positioned strictly above the backdrop overlay (z-index: 10) -->
  <div class="pdu-modal pdu-modal-content pdu-modal-{self.size} relative z-10 w-full {tailwind_size} rounded-xl border bg-card text-card-foreground shadow-2xl overflow-hidden flex flex-col" style="position:relative;z-index:10;width:100%;max-width:{max_width};max-height:90vh;background-color:var(--pdu-color-bg,#ffffff);border-radius:0.75rem;box-shadow:var(--pdu-shadow-xl,0 20px 25px -5px rgba(0,0,0,0.2));border:1px solid var(--pdu-color-border,#e5e7eb);">
    {header_html}
    <div class="pdu-modal-body p-6 overflow-y-auto flex-1">
      {children_html}
    </div>
  </div>
</div>'''


class Drawer(Component):
    """
    Accessible Slide-over Drawer Component.
    """
    tag = 'div'

    def __init__(
        self,
        *children,
        title: Optional[Any] = None,
        is_open: bool = False,
        on_close: Optional[Any] = None,
        position: str = 'right',
        size: str = 'md',
        close_on_overlay: bool = True,
        **props
    ):
        super().__init__(*children, **props)
        self.title = title
        self.is_open = is_open
        self.position = position
        self.size = size
        self.close_on_overlay = close_on_overlay
        self.on_close = on_close

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        is_open = self._resolve_value(self.is_open, snap)
        if not is_open:
            return ""

        children_html = self._render_children(snap)

        close_attrs_str = ""
        overlay_close_str = ""
        if self.on_close:
            htmx_close = self._get_event_htmx_attrs('on_click', self.on_close)
            close_attrs_str = " ".join(f'{k}="{v}"' for k, v in htmx_close.items())
            if self.close_on_overlay:
                overlay_close_str = close_attrs_str

        header_html = ""
        if self.title:
            t = escape_html(str(self._resolve_value(self.title, snap)))
            header_html = (
                f'<div class="pdu-drawer-header flex items-center justify-between p-4 border-b border-border bg-card">'
                f'<h3 class="text-lg font-semibold">{t}</h3>'
                f'<button type="button" class="pdu-drawer-close text-muted-foreground hover:text-foreground text-xl font-bold p-1 rounded" {close_attrs_str}>&times;</button>'
                f'</div>'
            )

        pos_style = "right:0;" if self.position == 'right' else "left:0;"

        return f'''<div id="{self.id}" class="pdu-drawer-wrapper fixed inset-0 z-50" style="position:fixed;inset:0;z-index:1000;">
  <!-- Backdrop -->
  <div class="pdu-drawer-overlay fixed inset-0" style="position:fixed;inset:0;background-color:rgba(0,0,0,0.5);z-index:1;" {overlay_close_str}></div>

  <!-- Drawer Panel: on top of backdrop -->
  <div class="pdu-drawer pdu-drawer-{self.position} fixed top-0 bottom-0 z-10 w-80 max-w-full bg-card text-card-foreground shadow-2xl flex flex-col" style="position:fixed;top:0;bottom:0;{pos_style}z-index:10;width:340px;background-color:var(--pdu-color-bg,#ffffff);box-shadow:var(--pdu-shadow-xl);">
    {header_html}
    <div class="pdu-drawer-body p-6 overflow-y-auto flex-1">
      {children_html}
    </div>
  </div>
</div>'''


class Popover(Component):
    tag = 'div'
    def __init__(self, *children, trigger=None, content=None, position='bottom', **props):
        super().__init__(*children, **props)
        self.trigger = trigger
        self.content = content
        self.position = position
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-popover-wrapper']
        
    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        attrs = self._build_attrs(snap)
        trigger_html = self.trigger.render(snap) if isinstance(self.trigger, Component) else escape_html(str(self.trigger))
        content_html = self.content.render(snap) if isinstance(self.content, Component) else escape_html(str(self.content))
        return f"<{self.tag} {attrs}><div class='pdu-popover-trigger'>{trigger_html}</div><div class='pdu-popover-content pdu-popover-{self.position}'>{content_html}</div></{self.tag}>"


class Dropdown(Component):
    tag = 'div'
    def __init__(self, *children, trigger=None, items=None, position='bottom-start', **props):
        super().__init__(*children, **props)
        self.trigger = trigger
        self.items = items or []
        self.position = position
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-dropdown-wrapper']
        
    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        attrs = self._build_attrs(snap)
        trigger_html = self.trigger.render(snap) if isinstance(self.trigger, Component) else escape_html(str(self.trigger))
        items = self._resolve_value(self.items, snap)
        li_html = []
        for item in items:
            lbl = escape_html(str(item.get('label', '')))
            href = escape_html(str(item.get('href', '#')))
            li_html.append(f"<a href='{href}' class='pdu-dropdown-item'>{lbl}</a>")
            
        menu_html = f"<div class='pdu-dropdown-menu pdu-dropdown-{self.position}'>{''.join(li_html)}</div>"
        return f"<{self.tag} {attrs}><div class='pdu-dropdown-trigger'>{trigger_html}</div>{menu_html}</{self.tag}>"
