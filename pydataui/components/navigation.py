from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Navbar(Component):
    tag = 'nav'
    def __init__(self, *children, brand=None, brand_href='/', sticky=True, variant='dark', **props):
        super().__init__(*children, **props)
        self.brand = brand
        self.brand_href = brand_href
        self.sticky = sticky
        self.variant = variant
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-navbar', f'pdu-navbar-{self.variant}']
        if self.sticky: classes.append('pdu-navbar-sticky')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        brand_html = ""
        if self.brand:
            b = self.brand.render(state_snapshot) if isinstance(self.brand, Component) else escape_html(str(self.brand))
            brand_html = f"<a href='{escape_html(self.brand_href)}' class='pdu-navbar-brand'>{b}</a>"
            
        return f"<{self.tag} {attrs}><div class='pdu-navbar-container'>{brand_html}<div class='pdu-navbar-content'>{children}</div></div></{self.tag}>"

class NavLink(Component):
    tag = 'a'
    def __init__(self, text='', href='#', active=False, disabled=False, **props):
        super().__init__(**props)
        self.text = text
        self.props['href'] = href
        self.active = active
        self.disabled = disabled
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-navlink']
        if self.active: classes.append('pdu-navlink-active')
        if self.disabled: classes.append('pdu-navlink-disabled')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        txt = escape_html(str(self._resolve_value(self.text, state_snapshot)))
        return f"<{self.tag} {attrs}>{txt}</{self.tag}>"

class Sidebar(Component):
    tag = 'aside'
    def __init__(self, *children, width='250px', collapsible=False, collapsed=False, position='left', **props):
        super().__init__(*children, **props)
        self.width = width
        self.collapsible = collapsible
        self.collapsed = collapsed
        self.position = position
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-sidebar', f'pdu-sidebar-{self.position}']
        if self.collapsed: classes.append('pdu-sidebar-collapsed')
        return classes
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if not self.collapsed:
            s += f" width: {self.width};"
        return s.strip()

class Breadcrumb(Component):
    tag = 'nav'
    def __init__(self, items=None, separator='/', **props):
        super().__init__(**props)
        self.items = items or []
        self.separator = separator
        self.props['aria-label'] = 'Breadcrumb'
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-breadcrumb']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        items = self._resolve_value(self.items, state_snapshot)
        
        ol_html = []
        for i, item in enumerate(items):
            lbl = escape_html(str(item.get('label', '')))
            href = item.get('href')
            
            if i < len(items) - 1:
                ol_html.append(f"<li class='pdu-breadcrumb-item'><a href='{escape_html(href or '#')}'>{lbl}</a><span class='pdu-breadcrumb-separator'>{escape_html(self.separator)}</span></li>")
            else:
                ol_html.append(f"<li class='pdu-breadcrumb-item pdu-breadcrumb-active' aria-current='page'>{lbl}</li>")
                
        return f"<{self.tag} {attrs}><ol>{''.join(ol_html)}</ol></{self.tag}>"

class Tabs(Component):
    tag = 'div'
    def __init__(self, *children, active_tab=0, variant='line', on_change=None, **props):
        super().__init__(*children, **props)
        self.active_tab = active_tab
        self.variant = variant
        if on_change:
            self._event_props['on_change'] = on_change
            
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-tabs', f'pdu-tabs-{self.variant}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        
        nav_html = []
        content_html = []
        
        active_idx = self._resolve_value(self.active_tab, state_snapshot)
        
        for i, child in enumerate(self.children):
            if isinstance(child, Tab):
                is_active = i == active_idx
                active_cls = "pdu-tab-active" if is_active else ""
                
                nav_html.append(f"<button class='pdu-tab-btn {active_cls}'>{escape_html(str(child.label))}</button>")
                
                content_cls = "pdu-tab-content-active" if is_active else "pdu-tab-content-hidden"
                content_html.append(f"<div class='pdu-tab-panel {content_cls}'>{child._render_children(state_snapshot)}</div>")
                
        return f"<{self.tag} {attrs}><div class='pdu-tabs-nav'>{''.join(nav_html)}</div><div class='pdu-tabs-body'>{''.join(content_html)}</div></{self.tag}>"

class Tab(Component):
    tag = 'div'
    def __init__(self, label='', *children, disabled=False, **props):
        super().__init__(*children, **props)
        self.label = label
        self.disabled = disabled
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-tab']

class Pagination(Component):
    tag = 'nav'
    def __init__(self, total_pages=1, current_page=1, on_page_change=None, show_edges=True, siblings=1, **props):
        super().__init__(**props)
        self.total_pages = total_pages
        self.current_page = current_page
        self.show_edges = show_edges
        self.siblings = siblings
        if on_page_change:
            self._event_props['on_page_change'] = on_page_change
            
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-pagination']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        tp = int(self._resolve_value(self.total_pages, state_snapshot) or 1)
        cp = int(self._resolve_value(self.current_page, state_snapshot) or 1)
        
        items = []
        if self.show_edges:
            items.append(f"<button class='pdu-page-btn' {'disabled' if cp == 1 else ''}>&laquo;</button>")
            
        items.append(f"<button class='pdu-page-btn' {'disabled' if cp == 1 else ''}>&lsaquo;</button>")
        
        start = max(1, cp - self.siblings)
        end = min(tp, cp + self.siblings)
        
        for p in range(start, end + 1):
            active = "pdu-page-active" if p == cp else ""
            items.append(f"<button class='pdu-page-btn {active}'>{p}</button>")
            
        items.append(f"<button class='pdu-page-btn' {'disabled' if cp == tp else ''}>&rsaquo;</button>")
        
        if self.show_edges:
            items.append(f"<button class='pdu-page-btn' {'disabled' if cp == tp else ''}>&raquo;</button>")
            
        return f"<{self.tag} {attrs}>{''.join(items)}</{self.tag}>"

class Menu(Component):
    tag = 'ul'
    def __init__(self, items=None, **props):
        super().__init__(**props)
        self.items = items or []
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-menu']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        items = self._resolve_value(self.items, state_snapshot)
        
        li_html = []
        for item in items:
            lbl = escape_html(str(item.get('label', '')))
            href = item.get('href', '#')
            icon = item.get('icon', '')
            
            icon_html = f"<span class='pdu-menu-icon'>{icon}</span>" if icon else ""
            li_html.append(f"<li class='pdu-menu-item'><a href='{escape_html(href)}'>{icon_html}<span class='pdu-menu-label'>{lbl}</span></a></li>")
            
        return f"<{self.tag} {attrs}>{''.join(li_html)}</{self.tag}>"
