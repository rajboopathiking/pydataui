from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .components.base import Component

# Type aliases
StyleValue = Union[str, int, float]
StyleDict = Dict[str, StyleValue]
Children = Union['Component', str, int, float, list, None]
EventCallback = Callable[..., None]
RenderResult = str
StateSnapshot = Dict[str, Dict[str, Any]]
PropsDict = Dict[str, Any]

# Size/variant enums as string literals
SIZES = ('xs', 'sm', 'md', 'lg', 'xl', '2xl', '3xl')
VARIANTS = ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'outline', 'ghost', 'link')
ALIGN = ('start', 'center', 'end', 'stretch', 'baseline')
JUSTIFY = ('start', 'center', 'end', 'between', 'around', 'evenly')
DIRECTION = ('row', 'column', 'row-reverse', 'column-reverse')
WRAP = ('nowrap', 'wrap', 'wrap-reverse')
