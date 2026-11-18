from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from .base import Component
from ..utils import escape_html

ALIGN_MAP = {
    'start': 'flex-start',
    'flex-start': 'flex-start',
    'end': 'flex-end',
    'flex-end': 'flex-end',
    'center': 'center',
    'stretch': 'stretch',
    'baseline': 'baseline',
}

JUSTIFY_MAP = {
    'start': 'flex-start',
    'flex-start': 'flex-start',
    'end': 'flex-end',
    'flex-end': 'flex-end',
    'center': 'center',
    'between': 'space-between',
    'space-between': 'space-between',
    'around': 'space-around',
    'space-around': 'space-around',
    'evenly': 'space-evenly',
    'space-evenly': 'space-evenly',
}

def _resolve_gap_str(gap_val: Any) -> str:
    if gap_val is None:
        return ""
    g = str(gap_val).strip()
    if g.isdigit():
        return f"{float(g) * 0.25}rem"
    if g.endswith(('px', 'rem', 'em', '%', 'vh', 'vw')):
        return g
    return f"var(--pdu-spacing-{g}, {g})"

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
    """Flexbox container supporting alignment, justification, gap, and wrapping."""
    tag = 'div'
    def __init__(
        self,
        *children,
        direction: str = 'row',
        align: str = 'stretch',
        justify: str = 'start',
        gap: Union[int, str] = 'md',
        wrap: Union[bool, str] = 'nowrap',
        **props
    ):
        super().__init__(*children, **props)
        self.direction = direction
        self.align = align
        self.justify = justify
        self.gap = gap
        self.wrap = 'wrap' if wrap is True else ('nowrap' if wrap is False else str(wrap))
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-flex']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        align_css = ALIGN_MAP.get(str(self.align).lower(), self.align)
        justify_css = JUSTIFY_MAP.get(str(self.justify).lower(), self.justify)
        gap_css = _resolve_gap_str(self.gap)
        gap_part = f"gap: {gap_css};" if gap_css else ""
        return f"{s} display: flex; flex-direction: {self.direction}; align-items: {align_css}; justify-content: {justify_css}; {gap_part} flex-wrap: {self.wrap};".strip()

class Grid(Component):
    """CSS Grid container supporting responsive templates, column counts, auto-fit, and gaps."""
    tag = 'div'
    def __init__(
        self,
        *children,
        columns: Union[int, str, List[Union[int, float]], Dict[str, int]] = 1,
        gap: Union[int, str] = 'md',
        row_gap: Optional[Union[int, str]] = None,
        column_gap: Optional[Union[int, str]] = None,
        min_column_width: Optional[str] = None,
        template_columns: Optional[str] = None,
        template_rows: Optional[str] = None,
        **props
    ):
        super().__init__(*children, **props)
        self.columns = columns
        self.gap = gap
        self.row_gap = row_gap
        self.column_gap = column_gap
        self.min_column_width = min_column_width
        self.template_columns = template_columns
        self.template_rows = template_rows
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-grid']
        if isinstance(self.columns, dict):
            for bp, cols in self.columns.items():
                classes.append(f'pdu-grid-{bp}-{cols}')
        return classes
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.template_columns:
            tc = self.template_columns
        elif self.min_column_width:
            mcw = self.min_column_width if str(self.min_column_width).endswith(('px', 'rem', 'em', '%')) else f"{self.min_column_width}px"
            tc = f"repeat(auto-fit, minmax({mcw}, 1fr))"
        elif isinstance(self.columns, (list, tuple)):
            tc = " ".join(f"{w}fr" if isinstance(w, (int, float)) else str(w) for w in self.columns)
        elif isinstance(self.columns, int):
            tc = f"repeat({self.columns}, minmax(0, 1fr))"
        elif isinstance(self.columns, str) and self.columns.isdigit():
            tc = f"repeat({self.columns}, minmax(0, 1fr))"
        else:
            tc = f"repeat({self.columns}, 1fr)"
            
        tr = f"grid-template-rows: {self.template_rows};" if self.template_rows else ""
        
        gap_css = _resolve_gap_str(self.gap)
        gap_style = f"gap: {gap_css};" if gap_css else ""
        if self.row_gap is not None:
            rg = _resolve_gap_str(self.row_gap)
            gap_style += f" row-gap: {rg};"
        if self.column_gap is not None:
            cg = _resolve_gap_str(self.column_gap)
            gap_style += f" column-gap: {cg};"
            
        return f"{s} display: grid; grid-template-columns: {tc}; {tr} {gap_style}".strip()

class Stack(Flex):
    """Vertical/horizontal stack."""
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-stack']

class HStack(Flex):
    """Horizontal stack."""
    def __init__(self, *children, gap='md', align='center', **props):
        super().__init__(*children, direction='row', gap=gap, align=align, **props)

    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-hstack', 'pdu-row']

class VStack(Flex):
    """Vertical stack."""
    def __init__(self, *children, gap='md', align='stretch', **props):
        super().__init__(*children, direction='column', gap=gap, align=align, **props)

    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-vstack', 'pdu-col']

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
        
    def render(self, state_snapshot: Optional[Any] = None) -> str:
        if self.hidden:
            return ""
        if state_snapshot is None:
            state_snapshot = {}
        header_html = ""
        if self.title or self.subtitle:
            t = f"<h3>{escape_html(self.title)}</h3>" if self.title else ""
            s = f"<p>{escape_html(self.subtitle)}</p>" if self.subtitle else ""
            header_html = f"<div class='pdu-card-header'>{t}{s}</div>"
        
        attrs = self._build_attrs(state_snapshot)
        children_html = self._render_children(state_snapshot)
        return f"<{self.tag} {attrs}>{header_html}<div class='pdu-card-body'>{children_html}</div></{self.tag}>"

class Divider(Component):
    """HR or vertical divider with optional centered label."""
    tag = 'hr'
    def __init__(self, label: Optional[str] = None, orientation='horizontal', color=None, thickness=None, **props):
        super().__init__(**props)
        self.label = label
        self.orientation = orientation
        self.color = color
        self.thickness = thickness
        if self.label:
            self.tag = 'div'
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-divider', f'pdu-divider-{self.orientation}']
        if self.label:
            classes.append('pdu-divider-with-label')
        return classes

    def render(self, state_snapshot: Optional[Any] = None) -> str:
        if self.hidden:
            return ""
        if not self.label:
            return super().render(state_snapshot)
        attrs = self._build_attrs(state_snapshot or {})
        return (
            f"<{self.tag} {attrs}>"
            f"<span class='pdu-divider-line'></span>"
            f"<span class='pdu-divider-text'>{escape_html(str(self.label))}</span>"
            f"<span class='pdu-divider-line'></span>"
            f"</{self.tag}>"
        )

class Spacer(Component):
    """Auto-expanding flexible spacer or fixed dimension spacer."""
    tag = 'div'
    def __init__(
        self,
        size: Optional[Any] = None,
        height: Optional[Any] = None,
        width: Optional[Any] = None,
        flex: int = 1,
        **props
    ):
        super().__init__(**props)
        self.size = size
        self.height = height
        self.width = width
        self.flex = flex

    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-spacer']
        if self.size is not None and isinstance(self.size, str) and not self.size.isdigit() and not self.size.endswith(('px', 'rem', 'em', '%')):
            classes.append(f'pdu-m-{self.size}')
        return classes

    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.height is not None:
            h = f"{self.height}px" if isinstance(self.height, (int, float)) or (isinstance(self.height, str) and self.height.isdigit()) else str(self.height)
            return f"{s} height: {h}; width: 100%; flex-shrink: 0;".strip()
        if self.width is not None:
            w = f"{self.width}px" if isinstance(self.width, (int, float)) or (isinstance(self.width, str) and self.width.isdigit()) else str(self.width)
            return f"{s} width: {w}; height: 100%; flex-shrink: 0;".strip()
        if self.size is not None:
            val = f"{self.size}px" if isinstance(self.size, (int, float)) or (isinstance(self.size, str) and self.size.isdigit()) else str(self.size)
            return f"{s} width: {val}; height: {val}; flex-shrink: 0;".strip()
        return f"{s} flex: {self.flex} {self.flex} auto;".strip()


class Center(Flex):
    """Centers content both horizontally and vertically."""
    def __init__(self, *children, **props):
        super().__init__(*children, align='center', justify='center', **props)

class Wrap(Flex):
    """Flexbox with wrap."""
    def __init__(self, *children, gap='md', **props):
        super().__init__(*children, wrap='wrap', gap=gap, **props)
