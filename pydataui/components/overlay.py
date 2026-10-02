from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Modal(Component):
    tag = 'div'
    def __init__(self, *children, title=None, is_open=False, on_close=None, size='md', close_on_overlay=True, **props):
        super().__init__(*children, **props)
        self.title = title
        self.is_open = is_open
        self.size = size
        self.close_on_overlay = close_on_overlay
        if on_close:
            self._event_props['on_close'] = on_close
            
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-modal']
        if self._resolve_value(self.is_open, {}):
            classes.append('pdu-modal-open')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        is_open = self._resolve_value(self.is_open, state_snapshot)
        if not is_open:
            return ""
            
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        overlay_attrs = "class='pdu-modal-overlay'"
        close_btn_attrs = "class='pdu-modal-close'"
        
        if 'on_close' in self._event_props:
            htmx = self._get_event_htmx_attrs('on_close', self._event_props['on_close'])
            htmx_str = " ".join([f"{k}='{v}'" for k,v in htmx.items()])
            if self.close_on_overlay:
                overlay_attrs += f" {htmx_str}"
            close_btn_attrs += f" {htmx_str}"
            
        header = ""
        if self.title:
            t = escape_html(str(self._resolve_value(self.title, state_snapshot)))
            header = f"<div class='pdu-modal-header'><h3>{t}</h3><button {close_btn_attrs}>&times;</button></div>"
            
        content = f"<div class='pdu-modal-content pdu-modal-{self.size}'>{header}<div class='pdu-modal-body'>{children}</div></div>"
        return f"<{self.tag} {attrs}><div {overlay_attrs}></div>{content}</{self.tag}>"

class Drawer(Component):
    tag = 'div'
    def __init__(self, *children, title=None, is_open=False, on_close=None, position='right', size='md', **props):
        super().__init__(*children, **props)
        self.title = title
        self.is_open = is_open
        self.position = position
        self.size = size
        if on_close:
            self._event_props['on_close'] = on_close
            
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-drawer', f'pdu-drawer-{self.position}', f'pdu-drawer-{self.size}']
        if self._resolve_value(self.is_open, {}):
            classes.append('pdu-drawer-open')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        is_open = self._resolve_value(self.is_open, state_snapshot)
        if not is_open:
            return ""
            
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        overlay_attrs = "class='pdu-drawer-overlay'"
        close_btn_attrs = "class='pdu-drawer-close'"
        
        if 'on_close' in self._event_props:
            htmx = self._get_event_htmx_attrs('on_close', self._event_props['on_close'])
            htmx_str = " ".join([f"{k}='{v}'" for k,v in htmx.items()])
            overlay_attrs += f" {htmx_str}"
            close_btn_attrs += f" {htmx_str}"
            
        header = ""
        if self.title:
            t = escape_html(str(self._resolve_value(self.title, state_snapshot)))
            header = f"<div class='pdu-drawer-header'><h3>{t}</h3><button {close_btn_attrs}>&times;</button></div>"
            
        content = f"<div class='pdu-drawer-content'>{header}<div class='pdu-drawer-body'>{children}</div></div>"
        return f"<{self.tag} {attrs}><div {overlay_attrs}></div>{content}</{self.tag}>"

class Popover(Component):
    tag = 'div'
    def __init__(self, *children, trigger=None, content=None, position='bottom', **props):
        super().__init__(*children, **props)
        self.trigger = trigger
        self.content = content
        self.position = position
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-popover-wrapper']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        
        trigger_html = self.trigger.render(state_snapshot) if isinstance(self.trigger, Component) else escape_html(str(self.trigger))
        content_html = self.content.render(state_snapshot) if isinstance(self.content, Component) else escape_html(str(self.content))
        
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
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        trigger_html = self.trigger.render(state_snapshot) if isinstance(self.trigger, Component) else escape_html(str(self.trigger))
        
        items = self._resolve_value(self.items, state_snapshot)
        li_html = []
        for item in items:
            lbl = escape_html(str(item.get('label', '')))
            href = escape_html(str(item.get('href', '#')))
            li_html.append(f"<a href='{href}' class='pdu-dropdown-item'>{lbl}</a>")
            
        menu_html = f"<div class='pdu-dropdown-menu pdu-dropdown-{self.position}'>{''.join(li_html)}</div>"
        
        return f"<{self.tag} {attrs}><div class='pdu-dropdown-trigger'>{trigger_html}</div>{menu_html}</{self.tag}>"
