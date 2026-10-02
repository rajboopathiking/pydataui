from __future__ import annotations
from typing import Dict, Any, Optional

class Style:
    """CSS-in-Python style builder."""
    _properties: Dict[str, str]

    def __init__(self, **kwargs: str):
        # Convert python_case to css-case
        self._properties = {}
        for k, v in kwargs.items():
            css_key = k.replace('_', '-')
            self._properties[css_key] = str(v)

    def __str__(self) -> str:
        """Returns CSS inline style string."""
        return "; ".join([f"{k}: {v}" for k, v in self._properties.items()])

    def __repr__(self) -> str:
        return f"Style({self.__str__()})"

    def merge(self, other: 'Style') -> 'Style':
        """Merge another style into a new Style object."""
        merged = self._properties.copy()
        merged.update(other._properties)
        style = Style()
        style._properties = merged
        return style

    def to_dict(self) -> Dict[str, str]:
        """Return the dictionary of properties."""
        return self._properties.copy()

    @staticmethod
    def flex(direction: str = 'row', align: str = 'stretch', justify: str = 'start', gap: Optional[str] = None, wrap: Optional[str] = None) -> 'Style':
        """Create a flex container style."""
        s = Style(display='flex', flex_direction=direction, align_items=align, justify_content=justify)
        if gap:
            s._properties['gap'] = gap
        if wrap:
            s._properties['flex-wrap'] = wrap
        return s

    @staticmethod
    def grid(columns: Any = 1, gap: Optional[str] = None, template: Optional[str] = None) -> 'Style':
        """Create a grid container style."""
        s = Style(display='grid')
        if template:
            s._properties['grid-template-columns'] = template
        elif isinstance(columns, int):
            s._properties['grid-template-columns'] = f"repeat({columns}, minmax(0, 1fr))"
        if gap:
            s._properties['gap'] = gap
        return s

    @staticmethod
    def text(size: Optional[str] = None, weight: Optional[str] = None, color: Optional[str] = None, align: Optional[str] = None) -> 'Style':
        """Create a text style."""
        s = Style()
        if size: s._properties['font-size'] = size
        if weight: s._properties['font-weight'] = weight
        if color: s._properties['color'] = color
        if align: s._properties['text-align'] = align
        return s

    @staticmethod
    def box(padding: Optional[str] = None, margin: Optional[str] = None, bg: Optional[str] = None, border: Optional[str] = None, radius: Optional[str] = None, shadow: Optional[str] = None) -> 'Style':
        """Create a box style."""
        s = Style()
        if padding: s._properties['padding'] = padding
        if margin: s._properties['margin'] = margin
        if bg: s._properties['background'] = bg
        if border: s._properties['border'] = border
        if radius: s._properties['border-radius'] = radius
        if shadow: s._properties['box-shadow'] = shadow
        return s

    @staticmethod
    def size(width: Optional[str] = None, height: Optional[str] = None, min_width: Optional[str] = None, min_height: Optional[str] = None, max_width: Optional[str] = None, max_height: Optional[str] = None) -> 'Style':
        """Create a sizing style."""
        s = Style()
        if width: s._properties['width'] = width
        if height: s._properties['height'] = height
        if min_width: s._properties['min-width'] = min_width
        if min_height: s._properties['min-height'] = min_height
        if max_width: s._properties['max-width'] = max_width
        if max_height: s._properties['max-height'] = max_height
        return s

def sx(**kwargs: str) -> str:
    """Shortcut to create inline style string from keyword args."""
    return str(Style(**kwargs))
