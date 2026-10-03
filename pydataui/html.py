"""
pydataui.html: Semantic HTML elements and SVG tag helpers.
Allows writing standard semantic HTML with Tailwind CSS and full reactive bindings in Python.

Usage:
    from pydataui.html import Section, Header, Nav, Div, Span, Svg, Path, P, H1, H2, A, Html

    # Or:
    import pydataui.html as h
    card = h.Div(h.H2("Custom Title"), h.P("Description"), class_name="p-6 bg-slate-900 text-white rounded-xl")
"""
from .components.html import (
    Div, Span, Section, Article, Header, Footer, Main, Nav, Aside,
    P, H1, H2, H3, H4, H5, H6,
    A, Ul, Ol, Li, Strong, Em, CodeTag, Pre, Hr, Br,
    Svg, Path, Circle, Rect, Line,
    FormTag, ButtonTag, InputTag, LabelTag, TextareaTag, SelectTag, OptionTag,
    TableTag, TheadTag, TbodyTag, TrTag, ThTag, TdTag,
    RawHtml, Html
)

__all__ = [
    'Div', 'Span', 'Section', 'Article', 'Header', 'Footer', 'Main', 'Nav', 'Aside',
    'P', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
    'A', 'Ul', 'Ol', 'Li', 'Strong', 'Em', 'CodeTag', 'Pre', 'Hr', 'Br',
    'Svg', 'Path', 'Circle', 'Rect', 'Line',
    'FormTag', 'ButtonTag', 'InputTag', 'LabelTag', 'TextareaTag', 'SelectTag', 'OptionTag',
    'TableTag', 'TheadTag', 'TbodyTag', 'TrTag', 'ThTag', 'TdTag',
    'RawHtml', 'Html'
]
