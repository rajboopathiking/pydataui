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
        passed_children = list(children)
        if 'children' in props:
            kw_children = props.pop('children')
            if isinstance(kw_children, (list, tuple)):
                passed_children.extend(kw_children)
            elif kw_children is not None:
                passed_children.append(kw_children)
        self.children = passed_children
        self.id = id or generate_id()
        self.class_name = class_name
        self.style = style
        self.hidden = hidden
        if 'tag' in props:
            self.tag = props.pop('tag')
        self.props = props
        self._event_props: Dict[str, Union[EventHandler, EventSpec]] = {}
        
        # Extract event props (on_click, on_change, etc.)
        for key in list(props.keys()):
            if key in EVENT_TRIGGERS:
                self._event_props[key] = props.pop(key)
    
    def render(self, state_snapshot: Optional[StateSnapshot] = None) -> str:
        """Render component to HTML string."""
        if self.hidden:
            return ''
        if state_snapshot is None:
            state_snapshot = {}
        
        attrs = self._build_attrs(state_snapshot)
        children_html = self._render_children(state_snapshot)
        
        if self._is_void_element():
            return f'<{self.tag} {attrs}/>' if attrs else f'<{self.tag}/>'
            
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{children_html}</{self.tag}>'

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Component):
            return self.tag == other.tag and self.children == other.children
        return False
    
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
            if key == 'bind':
                continue
            resolved = self._resolve_value(value, state_snapshot)
            if resolved is None or resolved is False:
                continue
            if key.startswith('data_'):
                attrs[f'data-{key[5:]}'] = '' if resolved is True else resolved
            elif key not in EVENT_TRIGGERS:
                html_key = key.replace('_', '-')
                attrs[html_key] = '' if resolved is True else resolved
        
        BOOLEAN_HTML_ATTRS = {
            'disabled', 'required', 'readonly', 'checked', 'selected',
            'autofocus', 'multiple', 'hidden', 'open', 'novalidate',
            'defer', 'async', 'loop', 'autoplay', 'controls', 'muted'
        }
        rendered_attrs = []
        for k, v in attrs.items():
            if v is None or v is False:
                continue
            if k in BOOLEAN_HTML_ATTRS and (v is True or v == '' or v == k):
                rendered_attrs.append(k)
            else:
                rendered_attrs.append(f'{k}="{escape_html(str(v))}"')
        return ' '.join(rendered_attrs)
    
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
        """Resolve a value that might be a StateVarRef or container of StateVarRefs."""
        if isinstance(value, StateVarRef):
            return value.resolve(state_snapshot)
        if isinstance(value, dict):
            return {k: self._resolve_value(v, state_snapshot) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_value(v, state_snapshot) for v in value]
        if isinstance(value, tuple):
            return tuple(self._resolve_value(v, state_snapshot) for v in value)
        if callable(value) and not isinstance(value, (type, Component)):
            return value(state_snapshot)
        return value
    
    def _get_event_htmx_attrs(self, event_name: str, handler: Any) -> Dict[str, str]:
        """Convert event handler to HTMX attributes."""
        trigger = EVENT_TRIGGERS.get(event_name, 'click')
        attrs = {}
        if isinstance(handler, EventSpec):
            attrs = handler.get_htmx_attrs(trigger=trigger)
        elif isinstance(handler, EventHandler):
            attrs = handler.get_htmx_attrs(trigger=trigger)
        elif callable(handler):
            from ..state import StateMeta, EventHandler as EH
            qual = getattr(handler, '__qualname__', '')
            parts = qual.split('.')
            if len(parts) >= 2 and parts[-2] in StateMeta._registry:
                attrs = EH(parts[-2], parts[-1]).get_htmx_attrs(trigger=trigger)
            elif getattr(handler, '__name__', '') == '<lambda>':
                co_names = handler.__code__.co_names
                state_cls_name = None
                method_name = None
                for name in co_names:
                    if name in StateMeta._registry:
                        state_cls_name = name
                        break
                if state_cls_name:
                    cls = StateMeta._registry[state_cls_name]
                    for name in co_names:
                        if hasattr(cls, name) and name != state_cls_name:
                            method_name = name
                            break
                if state_cls_name and method_name:
                    args_dict = {}
                    if handler.__defaults__:
                        for param_name, default_val in zip(handler.__code__.co_varnames, handler.__defaults__):
                            args_dict[param_name] = default_val
                    attrs = EventSpec(EH(state_cls_name, method_name), args=args_dict).get_htmx_attrs(trigger=trigger)
        if attrs and 'hx-include' not in attrs:
            attrs['hx-include'] = '#pdu-root'
        return attrs
    
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


class RawHtml(Component):
    """
    Renders raw, unescaped HTML markup directly.
    Useful for embedding custom HTML templates, SVG icons, or custom third-party widgets.
    """
    tag = ''

    def __init__(self, content: Any = '', **props):
        super().__init__(**props)
        self.raw_content = content

    def render(self, state_snapshot: Optional[StateSnapshot] = None) -> str:
        if self.hidden:
            return ''
        return str(self._resolve_value(self.raw_content, state_snapshot or {}))


# Friendly alias
Html = RawHtml
