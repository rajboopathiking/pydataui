from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Box(Component):
    """Generic div wrapper."""
    tag = 'div'
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-box']

class Container(Component):
    """Centered container with max-width."""
    tag = 'div'
    def __init__(self, *children, max_width='lg', padding='md', center=True, **props):
        super().__init__(*children, **props)
        self.max_width = max_width
        self.padding = padding
        self.center = center
    
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-container', f'pdu-max-w-{self.max_width}', f'pdu-p-{self.padding}']
        if self.center:
            classes.append('pdu-mx-auto')
        return classes

class Flex(Component):
    """Flexbox container."""
    tag = 'div'
    def __init__(self, *children, direction='row', align='stretch', justify='start', gap='md', wrap='nowrap', **props):
        super().__init__(*children, **props)
        self.direction = direction
        self.align = align
        self.justify = justify
        self.gap = gap
        self.wrap = wrap
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-flex']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        return f"{s} display: flex; flex-direction: {self.direction}; align-items: {self.align}; justify-content: {self.justify}; gap: var(--pdu-spacing-{self.gap}, {self.gap}); flex-wrap: {self.wrap};".strip()

class Grid(Component):
    """CSS Grid container."""
    tag = 'div'
    def __init__(self, *children, columns=1, gap='md', template_columns=None, template_rows=None, **props):
        super().__init__(*children, **props)
        self.columns = columns
        self.gap = gap
        self.template_columns = template_columns
        self.template_rows = template_rows
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-grid']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        tc = self.template_columns or f"repeat({self.columns}, 1fr)"
        tr = f"grid-template-rows: {self.template_rows};" if self.template_rows else ""
        return f"{s} display: grid; grid-template-columns: {tc}; {tr} gap: var(--pdu-spacing-{self.gap}, {self.gap});".strip()

class Stack(Flex):
    """Vertical/horizontal stack."""
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-stack']

class HStack(Flex):
    """Horizontal stack."""
    def __init__(self, *children, gap='md', align='center', **props):
        super().__init__(*children, direction='row', gap=gap, align=align, **props)

class VStack(Flex):
    """Vertical stack."""
    def __init__(self, *children, gap='md', align='stretch', **props):
        super().__init__(*children, direction='column', gap=gap, align=align, **props)

class Card(Component):
    """Card container with optional header."""
    tag = 'div'
    def __init__(self, *children, title=None, subtitle=None, padding='lg', shadow='md', radius='md', bordered=True, **props):
        super().__init__(*children, **props)
        self.title = title
        self.subtitle = subtitle
        self.padding = padding
        self.shadow = shadow
        self.radius = radius
        self.bordered = bordered
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-card', f'pdu-p-{self.padding}', f'pdu-shadow-{self.shadow}', f'pdu-radius-{self.radius}']
        if self.bordered:
            classes.append('pdu-border')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        header_html = ""
        if self.title or self.subtitle:
            t = f"<h3>{escape_html(self.title)}</h3>" if self.title else ""
            s = f"<p>{escape_html(self.subtitle)}</p>" if self.subtitle else ""
            header_html = f"<div class='pdu-card-header'>{t}{s}</div>"
        
        attrs = self._build_attrs(state_snapshot)
        children_html = self._render_children(state_snapshot)
        return f"<{self.tag} {attrs}>{header_html}<div class='pdu-card-body'>{children_html}</div></{self.tag}>"

class Divider(Component):
    """HR or vertical divider."""
    tag = 'hr'
    def __init__(self, orientation='horizontal', color=None, thickness=None, **props):
        super().__init__(**props)
        self.orientation = orientation
        self.color = color
        self.thickness = thickness
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-divider', f'pdu-divider-{self.orientation}']

class Spacer(Component):
    """Empty space."""
    tag = 'div'
    def __init__(self, size='md', **props):
        super().__init__(**props)
        self.size = size
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-spacer', f'pdu-m-{self.size}']

class Center(Flex):
    """Centers content both horizontally and vertically."""
    def __init__(self, *children, **props):
        super().__init__(*children, align='center', justify='center', **props)

class Wrap(Flex):
    """Flexbox with wrap."""
    def __init__(self, *children, gap='md', **props):
        super().__init__(*children, wrap='wrap', gap=gap, **props)
