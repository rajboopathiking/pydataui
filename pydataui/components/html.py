"""
Semantic HTML elements and SVG helpers for PyDataUI.
Provides full freedom to construct custom HTML structures with Tailwind CSS and reactive bindings.
"""
from __future__ import annotations
from typing import Any, Optional, Union
from .base import Component, RawHtml, Html


class Div(Component):
    tag = 'div'


class Span(Component):
    tag = 'span'


class Section(Component):
    tag = 'section'


class Article(Component):
    tag = 'article'


class Header(Component):
    tag = 'header'


class Footer(Component):
    tag = 'footer'


class Main(Component):
    tag = 'main'


class Nav(Component):
    tag = 'nav'


class Aside(Component):
    tag = 'aside'


class P(Component):
    tag = 'p'


class H1(Component):
    tag = 'h1'


class H2(Component):
    tag = 'h2'


class H3(Component):
    tag = 'h3'


class H4(Component):
    tag = 'h4'


class H5(Component):
    tag = 'h5'


class H6(Component):
    tag = 'h6'


class A(Component):
    tag = 'a'
    def __init__(self, *children, href: str = '#', **kwargs):
        super().__init__(*children, **kwargs)
        self.props['href'] = href


class Ul(Component):
    tag = 'ul'


class Ol(Component):
    tag = 'ol'


class Li(Component):
    tag = 'li'


class Strong(Component):
    tag = 'strong'


class Em(Component):
    tag = 'em'


class CodeTag(Component):
    tag = 'code'


class Pre(Component):
    tag = 'pre'


class Hr(Component):
    tag = 'hr'


class Br(Component):
    tag = 'br'


class Svg(Component):
    tag = 'svg'
    def __init__(self, *children, viewBox: str = '0 0 24 24', fill: str = 'none', stroke: str = 'currentColor', **kwargs):
        super().__init__(*children, **kwargs)
        self.props['viewBox'] = viewBox
        self.props['fill'] = fill
        self.props['stroke'] = stroke


class Path(Component):
    tag = 'path'
    def __init__(self, d: str = '', **kwargs):
        super().__init__(**kwargs)
        if d:
            self.props['d'] = d


class Circle(Component):
    tag = 'circle'
    def __init__(self, cx: Any = '', cy: Any = '', r: Any = '', **kwargs):
        super().__init__(**kwargs)
        if cx: self.props['cx'] = cx
        if cy: self.props['cy'] = cy
        if r: self.props['r'] = r


class Rect(Component):
    tag = 'rect'
    def __init__(self, x: Any = '', y: Any = '', width: Any = '', height: Any = '', **kwargs):
        super().__init__(**kwargs)
        if x: self.props['x'] = x
        if y: self.props['y'] = y
        if width: self.props['width'] = width
        if height: self.props['height'] = height


class Line(Component):
    tag = 'line'
    def __init__(self, x1: Any = '', y1: Any = '', x2: Any = '', y2: Any = '', **kwargs):
        super().__init__(**kwargs)
        if x1: self.props['x1'] = x1
        if y1: self.props['y1'] = y1
        if x2: self.props['x2'] = x2
        if y2: self.props['y2'] = y2


class FormTag(Component):
    tag = 'form'


class ButtonTag(Component):
    tag = 'button'
    def __init__(self, *children, type: str = 'button', **kwargs):
        super().__init__(*children, **kwargs)
        self.props['type'] = type


class InputTag(Component):
    tag = 'input'
    def __init__(self, type: str = 'text', **kwargs):
        super().__init__(**kwargs)
        self.props['type'] = type


class LabelTag(Component):
    tag = 'label'


class TextareaTag(Component):
    tag = 'textarea'


class SelectTag(Component):
    tag = 'select'


class OptionTag(Component):
    tag = 'option'
    def __init__(self, *children, value: str = '', **kwargs):
        super().__init__(*children, **kwargs)
        self.props['value'] = value


class TableTag(Component):
    tag = 'table'


class TheadTag(Component):
    tag = 'thead'


class TbodyTag(Component):
    tag = 'tbody'


class TrTag(Component):
    tag = 'tr'


class ThTag(Component):
    tag = 'th'


class TdTag(Component):
    tag = 'td'


__all__ = [
    'Component', 'RawHtml', 'Html',
    'Div', 'Span', 'Section', 'Article', 'Header', 'Footer', 'Main', 'Nav', 'Aside',
    'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
    'A', 'Ul', 'Ol', 'Li', 'Strong', 'Em', 'CodeTag', 'Pre', 'Hr', 'Br',
    'Svg', 'Path', 'Circle', 'Rect', 'Line',
    'FormTag', 'ButtonTag', 'InputTag', 'LabelTag', 'TextareaTag', 'SelectTag', 'OptionTag',
    'TableTag', 'TheadTag', 'TbodyTag', 'TrTag', 'ThTag', 'TdTag',
]
