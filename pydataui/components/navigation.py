from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Navbar(Component):
    tag = 'nav'
    def __init__(self, *children, brand=None, title=None, logo=None, brand_href='/', links=None, search=False, user=None, sticky=True, variant='dark', **props):
        if brand is None and title is not None:
            brand = title
        super().__init__(*children, **props)
        self.brand = brand
        self.logo = logo
        self.brand_href = brand_href
        self.links = links or []
        self.search = search
        self.user = user
        self.sticky = sticky
        self.variant = variant
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-navbar', f'pdu-navbar-{self.variant}', 'w-full', 'px-6', 'py-3', 'flex', 'items-center', 'justify-between', 'border-b', 'border-border/60', 'bg-background/95', 'backdrop-blur']
        if self.sticky: classes.append('sticky top-0 z-40')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        # Brand (Logo + Title)
        brand_parts = []
        if self.logo:
            brand_parts.append(f"<span class='text-xl mr-2'>{escape_html(str(self.logo))}</span>")
        if self.brand:
            b = self.brand.render(state_snapshot) if isinstance(self.brand, Component) else escape_html(str(self.brand))
            brand_parts.append(f"<span class='font-bold text-lg tracking-tight text-foreground'>{b}</span>")
        
        brand_html = ""
        if brand_parts:
            brand_html = f"<a href='{escape_html(self.brand_href)}' class='flex items-center no-underline hover:opacity-90 transition-opacity'>{''.join(brand_parts)}</a>"

        # Links
        links_html = ""
        if self.links:
            link_tags = []
            for lnk in self.links:
                lbl = escape_html(str(lnk.get('label', lnk.get('title', ''))))
                hrf = escape_html(str(lnk.get('href', '#')))
                act = "text-primary font-semibold" if lnk.get('active') else "text-muted-foreground hover:text-foreground"
                link_tags.append(f"<a href='{hrf}' class='text-sm {act} transition-colors'>{lbl}</a>")
            links_html = f"<div class='hidden md:flex items-center gap-6 ml-8'>{''.join(link_tags)}</div>"

        # Search Bar
        search_html = ""
        if self.search:
            ph = self.search if isinstance(self.search, str) else "Search anything..."
            search_html = f"<div class='relative max-w-xs w-full ml-4'><input type='search' placeholder='{escape_html(ph)}' class='w-full text-xs px-3 py-1.5 rounded-lg border border-border/80 bg-muted/40 focus:bg-background focus:outline-none focus:ring-1 focus:ring-primary text-foreground'/></div>"

        # User Menu / Avatar
        user_html = ""
        if self.user:
            uname = escape_html(str(self.user.get('name', self.user.get('username', 'User'))))
            uavatar = self.user.get('avatar')
            urole = self.user.get('role', self.user.get('roles', [''])[0] if isinstance(self.user.get('roles'), list) and self.user.get('roles') else '')
            role_badge = f"<span class='text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-primary/10 text-primary'>{escape_html(urole)}</span>" if urole else ""
            
            if uavatar:
                av_html = f"<img src='{escape_html(uavatar)}' class='w-7 h-7 rounded-full object-cover border border-border/80'/>"
            else:
                initial = uname[0].upper() if uname else "U"
                av_html = f"<div class='w-7 h-7 rounded-full bg-primary/20 text-primary font-bold text-xs flex items-center justify-center'>{initial}</div>"
            user_html = f"<div class='flex items-center gap-2.5 ml-4 pl-4 border-l border-border/60'>{av_html}<span class='text-xs font-medium text-foreground'>{uname}</span>{role_badge}</div>"
            
        return f"<{self.tag} {attrs}><div class='flex items-center'>{brand_html}{links_html}</div><div class='flex items-center gap-3'>{search_html}{children}{user_html}</div></{self.tag}>"

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
    def __init__(self, *children, links=None, width='250px', collapsible=False, collapsed=False, position='left', **props):
        child_list = list(children)
        if links:
            for l in links:
                if isinstance(l, dict):
                    child_list.append(NavLink(text=l.get('label', ''), href=l.get('href', '#')))
                elif isinstance(l, Component):
                    child_list.append(l)
        super().__init__(*child_list, **props)
        self.links = links
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
        return super()._get_classes() + ['pdu-breadcrumb', 'my-2']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        raw_items = self._resolve_value(self.items, state_snapshot) or []
        
        ol_html = []
        for i, item in enumerate(raw_items):
            if isinstance(item, str):
                lbl = escape_html(item)
                href = None
            elif isinstance(item, dict):
                lbl = escape_html(str(item.get('label', item.get('title', ''))))
                href = item.get('href')
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                lbl = escape_html(str(item[0]))
                href = str(item[1])
            else:
                lbl = escape_html(str(item))
                href = None
                
            is_last = (i == len(raw_items) - 1)
            sep_html = f"<span class='pdu-breadcrumb-separator mx-2 text-muted-foreground/60 select-none'>{escape_html(self.separator)}</span>" if not is_last else ""
            if not is_last and href:
                ol_html.append(f"<li class='pdu-breadcrumb-item inline-flex items-center text-xs font-medium text-muted-foreground hover:text-foreground transition-colors'><a href='{escape_html(href)}'>{lbl}</a>{sep_html}</li>")
            elif not is_last:
                ol_html.append(f"<li class='pdu-breadcrumb-item inline-flex items-center text-xs font-medium text-muted-foreground'>{lbl}{sep_html}</li>")
            else:
                ol_html.append(f"<li class='pdu-breadcrumb-item pdu-breadcrumb-active inline-flex items-center text-xs font-semibold text-foreground' aria-current='page'>{lbl}</li>")
                
        return f"<{self.tag} {attrs}><ol class='flex items-center flex-wrap gap-0.5'>{''.join(ol_html)}</ol></{self.tag}>"

class Tabs(Component):
    tag = 'div'
    def __init__(self, *children, active_tab=0, variant='line', expand=False, hide_tab_buttons=False, on_change=None, **props):
        super().__init__(*children, **props)
        self.active_tab = active_tab
        self.variant = variant
        self.expand = expand
        self.hide_tab_buttons = hide_tab_buttons
        if on_change:
            self._event_props['on_change'] = on_change
            
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-tabs', f'pdu-tabs-{self.variant}']
        if self.expand:
            classes.append('pdu-tabs-expand')
        if self.hide_tab_buttons:
            classes.append('pdu-tabs-headless')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        
        nav_html = []
        content_html = []
        
        active_idx = self._resolve_value(self.active_tab, state_snapshot)
        
        for i, child in enumerate(self.children):
            if isinstance(child, Tab):
                is_active = i == active_idx
                active_cls = "pdu-tab-active" if is_active else ""
                expand_cls = "flex-1 text-center" if self.expand else ""
                
                nav_html.append(f"<button class='pdu-tab-btn {active_cls} {expand_cls}'>{escape_html(str(child.label))}</button>")
                
                content_cls = "pdu-tab-content-active" if is_active else "pdu-tab-content-hidden"
                content_html.append(f"<div class='pdu-tab-panel {content_cls}'>{child._render_children(state_snapshot)}</div>")
                
        nav_style = " style='display: none;'" if self.hide_tab_buttons else ""
        return f"<{self.tag} {attrs}><div class='pdu-tabs-nav'{nav_style}>{''.join(nav_html)}</div><div class='pdu-tabs-body'>{''.join(content_html)}</div></{self.tag}>"

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


class Footer(Component):
    """
    Modern responsive application footer bar.
    Displays branding, copyright, status indicator, and legal/navigation links.
    """
    tag = 'footer'

    def __init__(
        self,
        *children,
        copyright: Optional[str] = None,
        links: Optional[List[Dict[str, str]]] = None,
        brand: Optional[str] = None,
        logo: Optional[str] = None,
        **props
    ):
        super().__init__(*children, **props)
        self.copyright = copyright
        self.links = links or []
        self.brand = brand
        self.logo = logo

    def _get_classes(self) -> List[str]:
        return super()._get_classes() + [
            'pdu-footer', 'w-full', 'px-6', 'py-6', 'border-t', 'border-border/60',
            'bg-card/40', 'backdrop-blur', 'flex', 'flex-col', 'md:flex-row',
            'items-center', 'justify-between', 'gap-4', 'text-xs', 'text-muted-foreground', 'mt-auto'
        ]

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        attrs = self._build_attrs(state_snapshot or {})
        children_html = self._render_children(state_snapshot or {})

        left_parts = []
        if self.logo:
            left_parts.append(f"<span class='text-base mr-1.5'>{escape_html(str(self.logo))}</span>")
        if self.brand:
            left_parts.append(f"<span class='font-bold text-sm tracking-tight text-foreground mr-3'>{escape_html(str(self.brand))}</span>")
        if self.copyright:
            left_parts.append(f"<span>{escape_html(str(self.copyright))}</span>")
        left_html = f"<div class='flex items-center flex-wrap gap-1'>{''.join(left_parts)}</div>"

        links_html = ""
        if self.links:
            tags = []
            for lnk in self.links:
                lbl = escape_html(str(lnk.get('label', lnk.get('title', ''))))
                hrf = escape_html(str(lnk.get('href', '#')))
                tags.append(f"<a href='{hrf}' class='hover:text-foreground transition-colors'>{lbl}</a>")
            links_html = f"<div class='flex items-center gap-6'>{''.join(tags)}</div>"

        return f"<{self.tag} {attrs}>{left_html}{children_html}{links_html}</{self.tag}>"
