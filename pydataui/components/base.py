from __future__ import annotations
import html as _html
from typing import Any, Dict, List, Optional, Union
from ..types import Children, StyleDict, PropsDict, StateSnapshot, SIZES, VARIANTS
from ..state import StateVarRef, EventHandler
from ..event import EVENT_TRIGGERS, EventSpec
from ..utils import generate_id, escape_html, to_css_value, to_css_class

class Component:
    """Base class for all PyDataUI components."""
    
    tag: str = 'div'
    _class_prefix: str = 'pdu'
    
    def __init__(
        self,
        *children: Children,
        id: Optional[str] = None,
        class_name: Optional[str] = None,
        style: Optional[Union[str, StyleDict]] = None,
        hidden: bool = False,
        **props: Any,
    ):
        self.children = list(children)
        self.id = id or generate_id()
        self.class_name = class_name
        self.style = style
        self.hidden = hidden
        self.props = props
        self._event_props: Dict[str, Union[EventHandler, EventSpec]] = {}
        
        # Extract event props (on_click, on_change, etc.)
        for key in list(props.keys()):
            if key in EVENT_TRIGGERS:
                self._event_props[key] = props.pop(key)
    
    def render(self, state_snapshot: StateSnapshot) -> str:
        """Render component to HTML string."""
        if self.hidden:
            return ''
        
        attrs = self._build_attrs(state_snapshot)
        children_html = self._render_children(state_snapshot)
        
        if self._is_void_element():
            return f'<{self.tag} {attrs}/>' if attrs else f'<{self.tag}/>'
            
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{children_html}</{self.tag}>'
    
    def _build_attrs(self, state_snapshot: StateSnapshot) -> str:
        """Build HTML attributes string."""
        attrs = {}
        attrs['id'] = self.id
        
        # CSS classes
        classes = self._get_classes()
        if self.class_name:
            classes.append(self.class_name)
        if classes:
            attrs['class'] = ' '.join(classes)
        
        # Inline styles
        style_str = self._get_style_string()
        if style_str:
            attrs['style'] = style_str
        
        # HTMX event attributes
        for event_name, handler in self._event_props.items():
            htmx_attrs = self._get_event_htmx_attrs(event_name, handler)
            attrs.update(htmx_attrs)
        
        # Data attributes and other props
        for key, value in self.props.items():
            if key.startswith('data_'):
                attrs[f'data-{key[5:]}'] = self._resolve_value(value, state_snapshot)
            elif key not in EVENT_TRIGGERS:
                html_key = key.replace('_', '-')
                attrs[html_key] = self._resolve_value(value, state_snapshot)
        
        return ' '.join(f'{k}="{escape_html(str(v))}"' for k, v in attrs.items() if v is not None)
    
    def _render_children(self, state_snapshot: StateSnapshot) -> str:
        """Render all children to HTML."""
        parts = []
        for child in self.children:
            if child is None:
                continue
            if isinstance(child, Component):
                parts.append(child.render(state_snapshot))
            elif isinstance(child, StateVarRef):
                resolved = child.resolve(state_snapshot)
                parts.append(escape_html(str(resolved)))
            elif isinstance(child, (list, tuple)):
                for item in child:
                    if isinstance(item, Component):
                        parts.append(item.render(state_snapshot))
                    elif isinstance(item, StateVarRef):
                        parts.append(escape_html(str(item.resolve(state_snapshot))))
                    elif item is not None:
                        parts.append(escape_html(str(item)))
            elif callable(child) and not isinstance(child, type):
                result = child(state_snapshot)
                parts.append(escape_html(str(result)))
            else:
                parts.append(escape_html(str(child)))
        return ''.join(parts)
    
    def _resolve_value(self, value: Any, state_snapshot: StateSnapshot) -> Any:
        """Resolve a value that might be a StateVarRef."""
        if isinstance(value, StateVarRef):
            return value.resolve(state_snapshot)
        if callable(value) and not isinstance(value, (type, Component)):
            return value(state_snapshot)
        return value
    
    def _get_event_htmx_attrs(self, event_name: str, handler: Any) -> Dict[str, str]:
        """Convert event handler to HTMX attributes."""
        trigger = EVENT_TRIGGERS.get(event_name, 'click')
        if isinstance(handler, EventSpec):
            return handler.get_htmx_attrs(trigger=trigger)
        elif isinstance(handler, EventHandler):
            return handler.get_htmx_attrs(trigger=trigger)
        return {}
    
    def _get_classes(self) -> List[str]:
        """Get CSS classes for this component. Override in subclasses."""
        return [self._class_prefix]
    
    def _get_style_string(self) -> str:
        """Convert style prop to CSS string."""
        if isinstance(self.style, str):
            return self.style
        if isinstance(self.style, dict):
            return '; '.join(f'{k}: {to_css_value(v)}' for k, v in self.style.items())
        return ''
    
    def _is_void_element(self) -> bool:
        """Check if this is a void/self-closing HTML element."""
        return self.tag in ('br', 'hr', 'img', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'source', 'track', 'wbr')
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(id={self.id!r})'
