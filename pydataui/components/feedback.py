from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Alert(Component):
    tag = 'div'
    def __init__(self, *children, variant='info', title=None, closable=False, icon=True, on_close=None, **props):
        super().__init__(*children, **props)
        self.variant = variant
        self.title = title
        self.closable = closable
        self.icon = icon
        if on_close:
            self._event_props['on_close'] = on_close
            
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-alert', f'pdu-alert-{self.variant}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        parts = []
        if self.icon:
            parts.append("<div class='pdu-alert-icon'></div>")
            
        content = []
        if self.title:
            t = self._resolve_value(self.title, state_snapshot)
            content.append(f"<div class='pdu-alert-title'>{escape_html(str(t))}</div>")
        content.append(f"<div class='pdu-alert-body'>{children}</div>")
        
        parts.append(f"<div class='pdu-alert-content'>{''.join(content)}</div>")
        
        if self.closable:
            close_attrs = ""
            if 'on_close' in self._event_props:
                htmx = self._get_event_htmx_attrs('on_close', self._event_props['on_close'])
                close_attrs = " ".join([f"{k}='{v}'" for k,v in htmx.items()])
            parts.append(f"<button class='pdu-alert-close' {close_attrs}>&times;</button>")
            
        return f"<{self.tag} {attrs}>{''.join(parts)}</{self.tag}>"

class Progress(Component):
    tag = 'div'
    def __init__(self, value=0, max=100, size='md', variant='primary', show_label=False, striped=False, animated=False, **props):
        super().__init__(**props)
        self.value = value
        self.max = max
        self.size = size
        self.variant = variant
        self.show_label = show_label
        self.striped = striped
        self.animated = animated
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-progress', f'pdu-progress-{self.size}', f'pdu-progress-{self.variant}']
        if self.striped: classes.append('pdu-progress-striped')
        if self.animated: classes.append('pdu-progress-animated')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        val = float(self._resolve_value(self.value, state_snapshot) or 0)
        m = float(self._resolve_value(self.max, state_snapshot) or 100)
        pct = min(100, max(0, (val / m) * 100 if m > 0 else 0))
        
        bar_html = f"<div class='pdu-progress-bar' style='width: {pct}%' role='progressbar' aria-valuenow='{val}' aria-valuemin='0' aria-valuemax='{m}'></div>"
        
        if self.show_label:
            return f"<div class='pdu-progress-wrapper'><div class='pdu-progress-label'>{pct:.0f}%</div><{self.tag} {attrs}>{bar_html}</{self.tag}></div>"
        return f"<{self.tag} {attrs}>{bar_html}</{self.tag}>"

class Spinner(Component):
    tag = 'div'
    def __init__(self, size='md', variant='primary', label=None, **props):
        super().__init__(**props)
        self.size = size
        self.variant = variant
        self.label = label
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-spinner', f'pdu-spinner-{self.size}', f'pdu-spinner-{self.variant}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        spinner = f"<{self.tag} {attrs} role='status'></{self.tag}>"
        
        if self.label:
            lbl = escape_html(str(self._resolve_value(self.label, state_snapshot)))
            return f"<div class='pdu-spinner-wrapper'>{spinner}<span class='pdu-spinner-label'>{lbl}</span></div>"
        return spinner

class Skeleton(Component):
    tag = 'div'
    def __init__(self, width=None, height=None, variant='rectangle', lines=1, **props):
        super().__init__(**props)
        self.width = width
        self.height = height
        self.variant = variant
        self.lines = lines
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-skeleton', f'pdu-skeleton-{self.variant}']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.width: s += f" width: {self.width};"
        if self.height: s += f" height: {self.height};"
        return s.strip()
        
    def render(self, state_snapshot: dict) -> str:
        if self.lines > 1 and self.variant == 'text':
            lines = []
            for _ in range(self.lines):
                lines.append(super().render(state_snapshot))
            return f"<div class='pdu-skeleton-lines'>{''.join(lines)}</div>"
        return super().render(state_snapshot)

class Toast(Component):
    tag = 'div'
    def __init__(self, message='', variant='info', duration=3000, position='top-right', **props):
        super().__init__(**props)
        self.message = message
        self.variant = variant
        self.duration = duration
        self.position = position
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-toast', f'pdu-toast-{self.variant}', f'pdu-toast-{self.position}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        msg = escape_html(str(self._resolve_value(self.message, state_snapshot)))
        
        # Adding a bit of inline script for duration removal is standard if pure CSS is not used
        script = f"<script>setTimeout(function(){{ document.getElementById('{self.id}').remove(); }}, {self.duration});</script>" if self.duration > 0 else ""
        
        return f"<{self.tag} {attrs}><div class='pdu-toast-message'>{msg}</div><button class='pdu-toast-close' onclick='this.parentElement.remove()'>&times;</button></{self.tag}>{script}"

class Empty(Component):
    tag = 'div'
    def __init__(self, title='No data', description=None, icon=None, *children, **props):
        super().__init__(*children, **props)
        self.title = title
        self.description = description
        self.icon = icon
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-empty']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        parts = []
        if self.icon:
            parts.append(f"<div class='pdu-empty-icon'>{self.icon}</div>")
            
        if self.title:
            t = escape_html(str(self._resolve_value(self.title, state_snapshot)))
            parts.append(f"<div class='pdu-empty-title'>{t}</div>")
            
        if self.description:
            d = escape_html(str(self._resolve_value(self.description, state_snapshot)))
            parts.append(f"<div class='pdu-empty-description'>{d}</div>")
            
        if children:
            parts.append(f"<div class='pdu-empty-actions'>{children}</div>")
            
        return f"<{self.tag} {attrs}>{''.join(parts)}</{self.tag}>"
