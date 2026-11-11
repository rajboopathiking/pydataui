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
        classes = super()._get_classes() + ['pdu-container', f'pdu-container-{self.max_width}', f'pdu-p-{self.padding}']
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
        self.gap = str(gap)
        self.template_columns = template_columns
        self.template_rows = template_rows
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-grid']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.template_columns:
            tc = self.template_columns
        elif isinstance(self.columns, int):
            tc = f"repeat({self.columns}, minmax(0, 1fr))"
        else:
            tc = f"repeat({self.columns}, 1fr)"
        tr = f"grid-template-rows: {self.template_rows};" if self.template_rows else ""
        gap_style = f"gap: {int(self.gap)*0.25}rem;" if self.gap.isdigit() else f"gap: var(--pdu-spacing-{self.gap}, {self.gap});"
        return f"{s} display: grid; grid-template-columns: {tc}; {tr} {gap_style}".strip()

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

class Row(Flex):
    """Pythonic horizontal layout row shorthand with intuitive gap and alignment."""
    def __init__(
        self,
        *children,
        gap='4',
        align='center',
        justify='start',
        wrap=False,
        **props
    ):
        wrap_val = 'wrap' if wrap else 'nowrap'
        gap_str = str(gap)
        super().__init__(*children, direction='row', align=align, justify=justify, gap=gap_str, wrap=wrap_val, **props)

    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-row']

    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.gap.isdigit():
            gap_rem = float(self.gap) * 0.25
            s = f"{s} gap: {gap_rem}rem;"
        return s.strip()

class Col(Flex):
    """Pythonic vertical layout column shorthand with responsive span/width."""
    def __init__(
        self,
        *children,
        span: Optional[int] = None,
        width: Optional[str] = None,
        gap='4',
        align='stretch',
        justify='start',
        **props
    ):
        gap_str = str(gap)
        super().__init__(*children, direction='column', align=align, justify=justify, gap=gap_str, **props)
        self.span = span
        self.width = width

    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-col']
        if self.span is not None:
            classes.append(f'pdu-col-span-{self.span}')
        return classes

    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        styles = []
        if self.gap.isdigit():
            gap_rem = float(self.gap) * 0.25
            styles.append(f"gap: {gap_rem}rem;")
        if self.span is not None:
            pct = round((self.span / 12) * 100, 4)
            styles.append(f"flex: 0 0 {pct}%; max-width: {pct}%;")
        elif self.width is not None:
            if self.width == 'full':
                styles.append("width: 100%;")
            elif '/' in self.width:
                parts = self.width.split('/')
                pct = round((float(parts[0]) / float(parts[1])) * 100, 4)
                styles.append(f"flex: 0 0 {pct}%; max-width: {pct}%;")
            else:
                styles.append(f"width: {self.width};")
        else:
            styles.append("flex: 1 1 0%; min-width: 0;")
        return f"{s} {' '.join(styles)}".strip()


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
    """Auto-expanding flexible spacer or fixed dimension spacer."""
    tag = 'div'
    def __init__(self, size: Optional[Any] = None, flex: int = 1, **props):
        super().__init__(**props)
        self.size = size
        self.flex = flex

    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-spacer']
        if self.size is not None and isinstance(self.size, str) and not self.size.isdigit() and not self.size.endswith(('px', 'rem', 'em', '%')):
            classes.append(f'pdu-m-{self.size}')
        return classes

    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.size is None:
            return f"{s} flex: {self.flex} {self.flex} auto;".strip()
        val = f"{self.size}px" if isinstance(self.size, int) or (isinstance(self.size, str) and self.size.isdigit()) else str(self.size)
        return f"{s} width: {val}; height: {val}; flex-shrink: 0;".strip()


class Center(Flex):
    """Centers content both horizontally and vertically."""
    def __init__(self, *children, **props):
        super().__init__(*children, align='center', justify='center', **props)

class Wrap(Flex):
    """Flexbox with wrap."""
    def __init__(self, *children, gap='md', **props):
        super().__init__(*children, wrap='wrap', gap=gap, **props)
