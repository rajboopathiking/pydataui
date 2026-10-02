from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Text(Component):
    tag = 'span'
    def __init__(self, *children, size='md', weight='normal', color=None, align=None, italic=False, underline=False, truncate=False, **props):
        super().__init__(*children, **props)
        self.size = size
        self.weight = weight
        self.color = color
        self.align = align
        self.italic = italic
        self.underline = underline
        self.truncate = truncate
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-text', f'pdu-text-{self.size}', f'pdu-font-{self.weight}']
        if self.color: classes.append(f'pdu-text-{self.color}')
        if self.align: classes.append(f'pdu-text-{self.align}')
        if self.italic: classes.append('pdu-italic')
        if self.underline: classes.append('pdu-underline')
        if self.truncate: classes.append('pdu-truncate')
        return classes

    @property
    def text(self) -> str:
        return str(self.children[0]) if self.children else ""

class Heading(Component):
    def __init__(self, *children, level=1, size=None, weight='bold', color=None, align=None, **props):
        super().__init__(*children, **props)
        self.level = min(max(1, level), 6)
        self.tag = f'h{self.level}'
        self.size = size
        self.weight = weight
        self.color = color
        self.align = align
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-heading', f'pdu-heading-{self.level}', f'pdu-font-{self.weight}']
        if self.size: classes.append(f'pdu-text-{self.size}')
        if self.color: classes.append(f'pdu-text-{self.color}')
        if self.align: classes.append(f'pdu-text-{self.align}')
        return classes

    @property
    def text(self) -> str:
        return str(self.children[0]) if self.children else ""

class Paragraph(Component):
    tag = 'p'
    def __init__(self, *children, size='md', color=None, align=None, **props):
        super().__init__(*children, **props)
        self.size = size
        self.color = color
        self.align = align
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-paragraph', f'pdu-text-{self.size}']
        if self.color: classes.append(f'pdu-text-{self.color}')
        if self.align: classes.append(f'pdu-text-{self.align}')
        return classes

class Link(Component):
    tag = 'a'
    def __init__(self, *children, href='#', external=False, color=None, underline=True, **props):
        super().__init__(*children, **props)
        self.props['href'] = href
        if external:
            self.props['target'] = '_blank'
            self.props['rel'] = 'noopener noreferrer'
        self.color = color
        self.underline = underline
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-link']
        if self.color: classes.append(f'pdu-text-{self.color}')
        if self.underline: classes.append('pdu-underline')
        return classes

class Code(Component):
    tag = 'code'
    def __init__(self, *children, language=None, block=False, **props):
        super().__init__(*children, **props)
        self.language = language
        self.block = block
        if self.block:
            self.tag = 'pre'
            
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + (['pdu-code-block'] if self.block else ['pdu-code'])
        if self.language: classes.append(f'language-{self.language}')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        if self.block:
            return f"<{self.tag} {attrs}><code>{children}</code></{self.tag}>"
        return f"<{self.tag} {attrs}>{children}</{self.tag}>"

class Blockquote(Component):
    tag = 'blockquote'
    def __init__(self, *children, cite=None, **props):
        super().__init__(*children, **props)
        if cite:
            self.props['cite'] = cite
            
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-blockquote']

class Label(Component):
    tag = 'label'
    def __init__(self, *children, html_for=None, required=False, **props):
        super().__init__(*children, **props)
        if html_for:
            self.props['for'] = html_for
        self.required = required
            
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-label']
        if self.required: classes.append('pdu-label-required')
        return classes
