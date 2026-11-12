from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from .base import Component
from ..utils import escape_html


def sniff_tabular_data(
    data: Any,
    columns: Optional[List[str]] = None,
    headers: Optional[List[str]] = None
) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    """Universal data sniffer converting Polars, Pandas, DuckDB, Arrow, Pydantic,
    dataclasses, dicts, and tuples into uniform records, column keys, and headers."""
    if data is None:
        return [], [], []

    # 1. DuckDB PyRelation
    if hasattr(data, 'df') and hasattr(data, 'description'):  # duckdb.PyRelation
        try:
            df = data.df()
            cols = list(df.columns) if not columns else list(columns)
            records = df[cols].to_dict(orient='records')
            hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
            return records, cols, hdrs
        except Exception:
            pass
    if hasattr(data, 'fetchall') and hasattr(data, 'description') and data.description:
        cols = [d[0] for d in data.description] if not columns else list(columns)
        rows = data.fetchall()
        records = [dict(zip(cols, row)) for row in rows]
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 2. Polars DataFrame / LazyFrame
    if hasattr(data, 'collect') and hasattr(data, 'schema'):  # Polars LazyFrame
        try:
            data = data.collect()
        except Exception:
            pass
    if hasattr(data, 'to_dicts') and hasattr(data, 'columns'):  # Polars DataFrame
        cols = list(data.columns) if not columns else list(columns)
        try:
            records = data.select(cols).to_dicts()
        except Exception:
            records = data.to_dicts()
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 3. Pandas DataFrame / Series
    if hasattr(data, 'to_dict') and hasattr(data, 'columns') and hasattr(data, 'iloc'):
        cols = list(data.columns) if not columns else list(columns)
        records = data[cols].to_dict(orient='records')
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    if hasattr(data, 'to_frame'):  # Pandas Series
        df = data.to_frame()
        cols = list(df.columns) if not columns else list(columns)
        records = df.to_dict(orient='records')
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 4. PyArrow Table / RecordBatch
    if hasattr(data, 'to_pylist') and hasattr(data, 'column_names'):
        cols = list(data.column_names) if not columns else list(columns)
        records = data.to_pylist()
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 5. Columnar dict: {"col1": [1, 2], "col2": [3, 4]}
    if isinstance(data, dict):
        if all(isinstance(v, (list, tuple)) for v in data.values()):
            cols = list(data.keys()) if not columns else list(columns)
            num_rows = min((len(data[c]) for c in cols if c in data), default=0)
            records = [{c: data[c][i] for c in cols if c in data} for i in range(num_rows)]
            hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
            return records, cols, hdrs
        else:
            cols = list(data.keys()) if not columns else list(columns)
            records = [data]
            hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
            return records, cols, hdrs

    # Convert iterables to list
    if not isinstance(data, (list, tuple)):
        try:
            data = list(data)
        except Exception:
            return [], [], []

    if not data:
        return [], [], []

    first = data[0]

    # 6. List of Pydantic models (v1 and v2)
    if hasattr(first, 'model_dump') and callable(getattr(first, 'model_dump')):
        records = [row.model_dump() for row in data]
        cols = list(records[0].keys()) if not columns else list(columns)
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs
    if hasattr(first, 'dict') and callable(getattr(first, 'dict')):
        records = [row.dict() for row in data]
        cols = list(records[0].keys()) if not columns else list(columns)
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 7. List of Dataclasses
    if hasattr(first, '__dataclass_fields__'):
        from dataclasses import asdict
        records = [asdict(row) for row in data]
        cols = list(records[0].keys()) if not columns else list(columns)
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 8. List of NamedTuples
    if hasattr(first, '_asdict') and callable(getattr(first, '_asdict')):
        records = [row._asdict() for row in data]
        cols = list(records[0].keys()) if not columns else list(columns)
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 9. List of Dicts
    if isinstance(first, dict):
        records = list(data)
        cols = list(first.keys()) if not columns else list(columns)
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # 10. List of lists / tuples
    if isinstance(first, (list, tuple)):
        cols = list(columns) if columns else [f"col_{i}" for i in range(len(first))]
        records = [dict(zip(cols, row)) for row in data]
        hdrs = headers or [str(c).replace('_', ' ').title() for c in cols]
        return records, cols, hdrs

    # Primitives list: [1, 2, 3]
    cols = list(columns) if columns else ["value"]
    records = [{"value": val} for val in data]
    hdrs = headers or ["Value"]
    return records, cols, hdrs


class Table(Component):
    tag = 'table'

    def __init__(
        self,
        data=None,
        columns=None,
        headers=None,
        striped=True,
        hoverable=True,
        bordered=False,
        compact=False,
        rows=None,
        **props
    ):
        super().__init__(**props)
        self.data = data if data is not None else (rows or [])
        self.columns = columns
        self.headers = headers
        self.striped = striped
        self.hoverable = hoverable
        self.bordered = bordered
        self.compact = compact

    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-table']
        if self.striped:
            classes.append('pdu-table-striped')
        if self.hoverable:
            classes.append('pdu-table-hover')
        if self.bordered:
            classes.append('pdu-table-bordered')
        if self.compact:
            classes.append('pdu-table-compact')
        return classes

    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        raw_data = self._resolve_value(self.data, state_snapshot)
        records, cols, headers = sniff_tabular_data(raw_data, self.columns, self.headers)

        if not records:
            return f"<{self.tag} {attrs}><tbody><tr><td class='p-4 text-muted-foreground text-center'>No data</td></tr></tbody></{self.tag}>"

        th_html = "".join(f"<th>{escape_html(str(h))}</th>" for h in headers)
        thead = f"<thead><tr>{th_html}</tr></thead>"

        tbody_rows = []
        for row in records:
            tds = []
            for col in cols:
                val = row.get(col, "")
                if isinstance(val, Component):
                    cell_content = val.render(state_snapshot)
                else:
                    cell_content = escape_html(str(self._resolve_value(val, state_snapshot)))
                tds.append(f"<td>{cell_content}</td>")
            tbody_rows.append(f"<tr>{''.join(tds)}</tr>")

        tbody = f"<tbody>{''.join(tbody_rows)}</tbody>"
        return f"<{self.tag} {attrs}>{thead}{tbody}</{self.tag}>"


class DataTable(Table):
    """Universal DataTable with auto-sniffing for Pandas, Polars, DuckDB, Arrow,
    instant client-side search filtering, column sorting, and pagination."""

    def __init__(
        self,
        data=None,
        columns=None,
        headers=None,
        sortable=True,
        searchable=True,
        paginated=False,
        page_size=10,
        striped=True,
        hoverable=True,
        bordered=False,
        compact=False,
        **props
    ):
        super().__init__(
            data=data,
            columns=columns,
            headers=headers,
            striped=striped,
            hoverable=hoverable,
            bordered=bordered,
            compact=compact,
            **props
        )
        self.sortable = sortable
        self.searchable = searchable
        self.paginated = paginated
        self.page_size = page_size

    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-datatable']

    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        raw_data = self._resolve_value(self.data, state_snapshot)
        records, cols, headers = sniff_tabular_data(raw_data, self.columns, self.headers)

        if not records:
            return (
                f"<div class='pdu-datatable-wrapper'>"
                f"<table {attrs}><tbody><tr><td class='p-4 text-muted-foreground text-center'>No data</td></tr></tbody></table>"
                f"</div>"
            )

        controls = []
        if self.searchable:
            controls.append(
                "<div class='pdu-datatable-search relative mb-3'>"
                "<input type='search' placeholder='Search records...' "
                "class='pdu-table-search-input w-full max-w-sm px-3 py-1.5 text-sm border rounded-md "
                "bg-background text-foreground border-input focus:outline-none focus:ring-1 focus:ring-ring' />"
                "</div>"
            )

        controls_html = f"<div class='pdu-datatable-controls flex justify-between items-center'>{''.join(controls)}</div>" if controls else ""

        th_parts = []
        for idx, h in enumerate(headers):
            col_name = cols[idx] if idx < len(cols) else f"col_{idx}"
            sort_attr = f"data-sort='{col_name}' class='cursor-pointer select-none'" if self.sortable else ""
            indicator = " <span class='pdu-sort-indicator text-xs text-muted-foreground opacity-60'>↕</span>" if self.sortable else ""
            th_parts.append(f"<th {sort_attr}>{escape_html(str(h))}{indicator}</th>")
        thead = f"<thead><tr>{''.join(th_parts)}</tr></thead>"

        tbody_rows = []
        for row in records:
            tds = []
            for col in cols:
                val = row.get(col, "")
                if isinstance(val, Component):
                    cell = val.render(state_snapshot)
                else:
                    cell = escape_html(str(self._resolve_value(val, state_snapshot)))
                tds.append(f"<td>{cell}</td>")
            tbody_rows.append(f"<tr>{''.join(tds)}</tr>")
        tbody = f"<tbody>{''.join(tbody_rows)}</tbody>"

        pagination_html = ""
        if self.paginated:
            pagination_html = (
                f"<div class='pdu-datatable-pagination flex items-center justify-between pt-3 text-xs text-muted-foreground' "
                f"data-page-size='{self.page_size}'>"
                f"<span>Showing <span class='pdu-page-info'>1 to {min(self.page_size, len(records))} of {len(records)} entries</span></span>"
                f"<div class='flex gap-1'>"
                f"<button type='button' class='pdu-page-prev px-2.5 py-1 border rounded text-xs disabled:opacity-50' disabled>Prev</button>"
                f"<button type='button' class='pdu-page-next px-2.5 py-1 border rounded text-xs disabled:opacity-50'>Next</button>"
                f"</div>"
                f"</div>"
            )

        return (
            f"<div class='pdu-datatable-wrapper' data-sortable='{str(self.sortable).lower()}' "
            f"data-page-size='{self.page_size if self.paginated else 0}'>"
            f"{controls_html}"
            f"<div class='overflow-x-auto'><table {attrs}>{thead}{tbody}</table></div>"
            f"{pagination_html}"
            f"</div>"
        )


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
