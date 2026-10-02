from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Image(Component):
    tag = 'img'
    def __init__(self, src='', alt='', width=None, height=None, fit='cover', rounded=False, fallback=None, lazy=True, **props):
        super().__init__(**props)
        self.props['src'] = src
        self.props['alt'] = alt
        if lazy: self.props['loading'] = 'lazy'
        self.width = width
        self.height = height
        self.fit = fit
        self.rounded = rounded
        self.fallback = fallback
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-image']
        if self.rounded: classes.append('pdu-image-rounded')
        classes.append(f'pdu-object-{self.fit}')
        return classes
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.width: s += f" width: {self.width};"
        if self.height: s += f" height: {self.height};"
        return s.strip()

class Video(Component):
    tag = 'video'
    def __init__(self, src='', poster=None, controls=True, autoplay=False, muted=False, loop=False, width=None, height=None, **props):
        super().__init__(**props)
        self.props['src'] = src
        if poster: self.props['poster'] = poster
        if controls: self.props['controls'] = 'controls'
        if autoplay: self.props['autoplay'] = 'autoplay'
        if muted: self.props['muted'] = 'muted'
        if loop: self.props['loop'] = 'loop'
        self.width = width
        self.height = height
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-video']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.width: s += f" width: {self.width};"
        if self.height: s += f" height: {self.height};"
        return s.strip()
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        return f"<{self.tag} {attrs}></{self.tag}>"

class Audio(Component):
    tag = 'audio'
    def __init__(self, src='', controls=True, autoplay=False, muted=False, loop=False, **props):
        super().__init__(**props)
        self.props['src'] = src
        if controls: self.props['controls'] = 'controls'
        if autoplay: self.props['autoplay'] = 'autoplay'
        if muted: self.props['muted'] = 'muted'
        if loop: self.props['loop'] = 'loop'
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-audio']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        return f"<{self.tag} {attrs}></{self.tag}>"

class Icon(Component):
    tag = 'span'
    def __init__(self, name='', size='md', color=None, **props):
        super().__init__(**props)
        self.name = name
        self.size = size
        self.color = color
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-icon', f'pdu-icon-{self.size}']
        if self.color: classes.append(f'pdu-text-{self.color}')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        # Assuming SVG rendering or font-icon based on name
        # We output name as text for font-icon support (like Material Icons)
        name = escape_html(str(self._resolve_value(self.name, state_snapshot)))
        return f"<{self.tag} {attrs}>{name}</{self.tag}>"
