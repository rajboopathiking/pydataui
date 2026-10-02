from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Table(Component):
    tag = 'table'
    def __init__(self, data=None, columns=None, headers=None, striped=True, hoverable=True, bordered=False, compact=False, **props):
        super().__init__(**props)
        self.data = data or []
        self.columns = columns
        self.headers = headers
        self.striped = striped
        self.hoverable = hoverable
        self.bordered = bordered
        self.compact = compact
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-table']
        if self.striped: classes.append('pdu-table-striped')
        if self.hoverable: classes.append('pdu-table-hover')
        if self.bordered: classes.append('pdu-table-bordered')
        if self.compact: classes.append('pdu-table-compact')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        data = self._resolve_value(self.data, state_snapshot) or []
        
        if not data:
            return f"<{self.tag} {attrs}><tbody><tr><td>No data</td></tr></tbody></{self.tag}>"
            
        first_row = data[0]
        is_dict = isinstance(first_row, dict)
        
        cols = self.columns
        if not cols:
            if is_dict: cols = list(first_row.keys())
            else: cols = list(range(len(first_row)))
            
        headers = self.headers or [str(c).title() for c in cols]
        
        th_html = "".join(f"<th>{escape_html(str(h))}</th>" for h in headers)
        thead = f"<thead><tr>{th_html}</tr></thead>"
        
        tbody_rows = []
        for row in data:
            tds = []
            for col in cols:
                val = row.get(col, "") if is_dict else (row[col] if col < len(row) else "")
                tds.append(f"<td>{escape_html(str(val))}</td>")
            tbody_rows.append(f"<tr>{''.join(tds)}</tr>")
            
        tbody = f"<tbody>{''.join(tbody_rows)}</tbody>"
        return f"<{self.tag} {attrs}>{thead}{tbody}</{self.tag}>"

class DataTable(Table):
    def __init__(self, data=None, columns=None, sortable=False, searchable=False, paginated=False, page_size=10, **props):
        super().__init__(data=data, columns=columns, **props)
        self.sortable = sortable
        self.searchable = searchable
        self.paginated = paginated
        self.page_size = page_size
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-datatable']
        
    def render(self, state_snapshot: dict) -> str:
        # Full DataTable with HTMX logic would be complex.
        # This is a stubbed implementation wrapping the base Table.
        table_html = super().render(state_snapshot)
        controls = []
        if self.searchable: controls.append("<input type='search' placeholder='Search...' class='pdu-input pdu-mb-md' />")
        # Add pagination logic etc if needed
        controls_html = f"<div class='pdu-datatable-controls'>{''.join(controls)}</div>" if controls else ""
        return f"<div class='pdu-datatable-wrapper'>{controls_html}{table_html}</div>"

class ListItem(Component):
    """List item component."""
    tag = 'li'
    def __init__(self, *children, **props):
        super().__init__(*children, **props)

    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-list-item']

class List(Component):
    def __init__(self, *children, items=None, ordered=False, style_type=None, **props):
        super().__init__(*children, **props)
        self.tag = 'ol' if ordered else 'ul'
        self.items = items if items is not None else list(children)
        self.style_type = style_type
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-list']
        if self.style_type:
            classes.append(f'pdu-list-{self.style_type}')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        items = self._resolve_value(self.items, state_snapshot) or []
        
        li_html = []
        for item in items:
            if isinstance(item, ListItem):
                li_html.append(item.render(state_snapshot))
            elif isinstance(item, Component):
                li_html.append(f"<li>{item.render(state_snapshot)}</li>")
            else:
                li_html.append(f"<li>{escape_html(str(item))}</li>")
                
        return f"<{self.tag} {attrs}>{''.join(li_html)}</{self.tag}>"

class DescriptionList(Component):
    tag = 'dl'
    def __init__(self, items=None, **props):
        super().__init__(**props)
        self.items = items or []
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-description-list']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        items = self._resolve_value(self.items, state_snapshot) or []
        
        dl_html = []
        for term, desc in items:
            dl_html.append(f"<dt>{escape_html(str(term))}</dt><dd>{escape_html(str(desc))}</dd>")
            
        return f"<{self.tag} {attrs}>{''.join(dl_html)}</{self.tag}>"

class Badge(Component):
    tag = 'span'
    def __init__(self, text='', variant='primary', size='sm', rounded=True, **props):
        super().__init__(**props)
        self.text = text
        self.variant = variant
        self.size = size
        self.rounded = rounded
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-badge', f'pdu-badge-{self.variant}', f'pdu-badge-{self.size}']
        if self.rounded: classes.append('pdu-badge-rounded')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        txt = self._resolve_value(self.text, state_snapshot)
        return f"<{self.tag} {attrs}>{escape_html(str(txt))}</{self.tag}>"

class Tag(Badge):
    def __init__(self, text='', variant='primary', size='sm', closable=False, on_close=None, **props):
        super().__init__(text=text, variant=variant, size=size, rounded=False, **props)
        self.closable = closable
        if on_close:
            self._event_props['on_close'] = on_close
            
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes()
        if 'pdu-badge' in classes: classes.remove('pdu-badge')
        classes.append('pdu-tag')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        html = super().render(state_snapshot)
        if self.closable:
            close_btn = f"<button class='pdu-tag-close'>&times;</button>"
            html = html.replace(f"</{self.tag}>", f"{close_btn}</{self.tag}>")
        return html

class Stat(Component):
    tag = 'div'
    def __init__(self, label='', value='', help_text=None, trend=None, trend_type='up', **props):
        super().__init__(**props)
        self.label = label
        self.value = value
        self.help_text = help_text
        self.trend = trend
        self.trend_type = trend_type
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-stat']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        lbl = self._resolve_value(self.label, state_snapshot)
        val = self._resolve_value(self.value, state_snapshot)
        
        parts = [
            f"<div class='pdu-stat-label'>{escape_html(str(lbl))}</div>",
            f"<div class='pdu-stat-value'>{escape_html(str(val))}</div>"
        ]
        
        if self.trend:
            t = self._resolve_value(self.trend, state_snapshot)
            parts.append(f"<div class='pdu-stat-trend pdu-trend-{self.trend_type}'>{escape_html(str(t))}</div>")
            
        if self.help_text:
            ht = self._resolve_value(self.help_text, state_snapshot)
            parts.append(f"<div class='pdu-stat-help'>{escape_html(str(ht))}</div>")
            
        return f"<{self.tag} {attrs}>{''.join(parts)}</{self.tag}>"

class KeyValue(Component):
    tag = 'div'
    def __init__(self, label='', value='', **props):
        super().__init__(**props)
        self.label = label
        self.value = value
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-key-value']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        lbl = escape_html(str(self._resolve_value(self.label, state_snapshot)))
        val = escape_html(str(self._resolve_value(self.value, state_snapshot)))
        return f"<{self.tag} {attrs}><span class='pdu-kv-label'>{lbl}</span><span class='pdu-kv-value'>{val}</span></{self.tag}>"

class Avatar(Component):
    tag = 'div'
    def __init__(self, src=None, name=None, size='md', rounded=True, **props):
        super().__init__(**props)
        self.src = src
        self.name = name
        self.size = size
        self.rounded = rounded
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-avatar', f'pdu-avatar-{self.size}']
        if self.rounded: classes.append('pdu-avatar-rounded')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        src = self._resolve_value(self.src, state_snapshot)
        name = self._resolve_value(self.name, state_snapshot)
        
        if src:
            return f"<{self.tag} {attrs}><img src='{escape_html(src)}' alt='{escape_html(name or '')}' /></{self.tag}>"
        elif name:
            initials = "".join([part[0] for part in str(name).split()[:2]]).upper()
            return f"<{self.tag} {attrs}><span class='pdu-avatar-text'>{escape_html(initials)}</span></{self.tag}>"
        return f"<{self.tag} {attrs}></{self.tag}>"

class Tooltip(Component):
    tag = 'div'
    def __init__(self, text='', position='top', *children, **props):
        super().__init__(*children, **props)
        self.text = text
        self.position = position
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-tooltip-wrapper']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        txt = escape_html(str(self._resolve_value(self.text, state_snapshot)))
        return f"<{self.tag} {attrs}>{children}<span class='pdu-tooltip pdu-tooltip-{self.position}'>{txt}</span></{self.tag}>"
