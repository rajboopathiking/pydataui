"""
Data science / data domain components for PyDataUI.
Designed for data engineers, analysts, and ML engineers who use Python.

Components:
  - DataFrameTable    — pandas DataFrame as interactive table
  - MetricCard        — KPI card (value + delta)
  - ModelMetrics      — ML eval metrics grid
  - PipelineStatus    — Data pipeline step tracker
  - ConfusionMatrix   — Coloured confusion matrix
  - JSONViewer        — Pretty JSON display
  - CodeBlock         — Syntax-aware code block
  - FileDownload      — Download link for data files
  - DataUpload        — Drag-and-drop file upload area
  - SQLEditor         — SQL textarea + run button
  - PlotlyChart       — Plotly Figure embed
  - DataTimeline      — Event / run timeline
  - FeatureImportance — Horizontal bar chart
  - SchemaViewer      — DataFrame / schema column inspector
"""
from __future__ import annotations
import json as _json
import html as _html_mod
from typing import Any, Dict, List, Optional, Union
from .base import Component
from ..utils import escape_html, generate_id


class DataFrameTable(Component):
    """
    Render a pandas DataFrame as a styled, scrollable HTML table.

    Usage::

        DataFrameTable(df=my_df, max_rows=50)
    """

    def __init__(self, df: Any, max_rows: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.df = df
        self.max_rows = max_rows

    def render(self, state_snapshot=None) -> str:
        try:
            import pandas as pd
        except ImportError:
            return ('<div class="text-destructive p-4 border rounded-lg bg-card">'
                    '⚠ pandas is not installed. Run: <code>pip install pandas</code></div>')

        if not isinstance(self.df, pd.DataFrame):
            return ('<div class="text-destructive p-4 border rounded-lg bg-card">'
                    'DataFrameTable: provided data is not a pandas DataFrame.</div>')

        slice_df = self.df.head(self.max_rows)
        raw_html = slice_df.to_html(border=0, index=True, escape=True)

        # Style the raw pandas HTML to match shadcn/ui table
        raw_html = raw_html.replace('<table ', '<table class="w-full caption-bottom text-sm" ')
        raw_html = raw_html.replace('<thead>', '<thead class="[&_tr]:border-b">')
        raw_html = raw_html.replace('<tbody>', '<tbody class="[&_tr:last-child]:border-0">')
        raw_html = raw_html.replace('<tr>', '<tr class="border-b transition-colors hover:bg-muted/50">')
        raw_html = raw_html.replace('<th>', '<th class="h-10 px-4 text-left align-middle font-medium text-muted-foreground">')
        raw_html = raw_html.replace('<td>', '<td class="p-4 align-middle">')

        rows, cols = slice_df.shape
        total = len(self.df)
        note = (f'<p class="text-xs text-muted-foreground mt-2">Showing {rows} of {total} rows '
                f'× {cols} columns</p>' if total > self.max_rows else
                f'<p class="text-xs text-muted-foreground mt-2">{rows} rows × {cols} columns</p>')

        return (f'<div id="{self.id}" class="w-full overflow-auto rounded-md border bg-card p-2">'
                f'{raw_html}{note}</div>')


class MetricCard(Component):
    """
    KPI card with title, value, optional delta and icon.

    Usage::

        MetricCard(title="Accuracy", value=0.956, format=".1%",
                   delta="+2.3%", delta_type="increase", icon="📈")
    """

    def __init__(self, title: str, value: Any, format: str = '',
                 delta: str = '', delta_type: str = 'neutral',
                 icon: str = '', description: str = '', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.value = value
        self.fmt = format
        self.delta = delta
        self.delta_type = delta_type
        self.icon = icon
        self.description = description

    def render(self, state_snapshot=None) -> str:
        DELTA_COLORS = {
            'increase': 'text-green-600 dark:text-green-400',
            'decrease': 'text-destructive',
            'neutral':  'text-muted-foreground',
        }
        delta_cls = DELTA_COLORS.get(self.delta_type, DELTA_COLORS['neutral'])

        display = self.value
        if self.fmt and isinstance(self.value, (int, float)):
            try:
                display = f'{self.value:{self.fmt}}'
            except (ValueError, TypeError):
                display = str(self.value)

        icon_html = (f'<span class="text-2xl leading-none text-muted-foreground">{self.icon}</span>'
                     if self.icon else '')
        delta_html = (f'<p class="text-xs {delta_cls} mt-1 flex items-center gap-1">{self.delta}</p>'
                      if self.delta else '')
        desc_html = (f'<p class="text-xs text-muted-foreground mt-1">{escape_html(self.description)}</p>'
                     if self.description else '')

        return f'''<div id="{self.id}" class="rounded-xl border bg-card text-card-foreground shadow">
  <div class="p-6 flex flex-row items-center justify-between space-y-0 pb-2">
    <h3 class="tracking-tight text-sm font-medium text-muted-foreground">{escape_html(self.title)}</h3>
    {icon_html}
  </div>
  <div class="p-6 pt-0">
    <div class="text-2xl font-bold">{escape_html(str(display))}</div>
    {delta_html}{desc_html}
  </div>
</div>'''


class ModelMetrics(Component):
    """
    Grid of MetricCards for ML model evaluation.

    Usage::

        ModelMetrics(metrics={"Accuracy": 0.95, "F1": 0.92, "AUC": 0.98})
    """

    def __init__(self, metrics: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.metrics = metrics

    def render(self, state_snapshot=None) -> str:
        cards = []
        for name, val in self.metrics.items():
            fmt = '.4f' if isinstance(val, float) else ''
            cards.append(MetricCard(title=name, value=val, format=fmt).render(state_snapshot))
        cols = min(len(self.metrics), 4)
        return (f'<div id="{self.id}" class="grid gap-4 '
                f'grid-cols-1 sm:grid-cols-2 lg:grid-cols-{cols}">{"".join(cards)}</div>')


class PipelineStatus(Component):
    """
    Step-by-step pipeline tracker.

    Usage::

        PipelineStatus(steps=[
            {"name": "Extract", "status": "success"},
            {"name": "Transform", "status": "running"},
            {"name": "Load", "status": "pending"},
        ])
    """

    STATUS_COLORS = {
        'success': 'bg-green-500',
        'running': 'bg-blue-500 animate-pulse',
        'pending': 'bg-muted-foreground/40',
        'failed':  'bg-destructive',
        'skipped': 'bg-yellow-400',
    }
    STATUS_ICONS = {
        'success': '✓', 'running': '…', 'pending': '○',
        'failed': '✕', 'skipped': '⊘',
    }

    def __init__(self, steps: List[Dict[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.steps = steps

    def render(self, state_snapshot=None) -> str:
        items = []
        for i, step in enumerate(self.steps):
            status = step.get('status', 'pending')
            name = step.get('name', f'Step {i+1}')
            msg = step.get('message', '')
            dot_cls = self.STATUS_COLORS.get(status, self.STATUS_COLORS['pending'])
            icon = self.STATUS_ICONS.get(status, '○')
            line = ('<div class="absolute left-[11px] top-6 h-full w-0.5 bg-border -bottom-6"></div>'
                    if i < len(self.steps) - 1 else '')
            msg_html = f'<p class="text-xs text-muted-foreground">{escape_html(msg)}</p>' if msg else ''
            items.append(f'''<div class="relative flex items-start space-x-3 pb-6 last:pb-0">
  {line}
  <div class="relative flex h-6 w-6 items-center justify-center rounded-full {dot_cls} text-white text-xs ring-4 ring-background flex-shrink-0">{icon}</div>
  <div class="flex flex-col min-w-0">
    <p class="text-sm font-medium">{escape_html(name)}</p>
    <p class="text-xs text-muted-foreground capitalize">{escape_html(status)}</p>
    {msg_html}
  </div>
</div>''')

        return (f'<div id="{self.id}" class="p-4 border rounded-lg bg-card">'
                f'{"".join(items)}</div>')


class ConfusionMatrix(Component):
    """
    Confusion matrix with heat-map coloring.

    Usage::

        ConfusionMatrix(matrix=[[50,2],[3,45]], labels=["Cat","Dog"])
    """

    def __init__(self, matrix: List[List[int]], labels: List[str], **kwargs):
        super().__init__(**kwargs)
        self.matrix = matrix
        self.labels = labels

    def render(self, state_snapshot=None) -> str:
        all_vals = [v for row in self.matrix for v in row]
        max_val = max(all_vals) if all_vals else 1

        thead = ('<thead><tr><th class="p-2 text-right text-xs text-muted-foreground border-b border-r">'
                 'Actual \\ Predicted</th>' +
                 ''.join(f'<th class="p-2 font-medium text-center text-xs border-b">'
                         f'{escape_html(str(l))}</th>' for l in self.labels) +
                 '</tr></thead>')

        tbody_rows = []
        for i, row in enumerate(self.matrix):
            label = self.labels[i] if i < len(self.labels) else str(i)
            cells = [f'<th class="p-2 font-medium text-right text-xs border-r">{escape_html(str(label))}</th>']
            for j, val in enumerate(row):
                intensity = (val / max_val) if max_val > 0 else 0
                # diagonal = TP/TN → blue, off-diagonal = FP/FN → orange
                if i == j:
                    bg = f'rgba(59,130,246,{intensity * 0.7:.2f})'
                else:
                    bg = f'rgba(239,68,68,{intensity * 0.5:.2f})'
                cells.append(f'<td class="p-4 text-center text-sm font-mono border" '
                              f'style="background:{bg}">{val}</td>')
            tbody_rows.append(f'<tr>{"".join(cells)}</tr>')

        return (f'<div id="{self.id}" class="w-full overflow-auto rounded-md border bg-card">'
                f'<table class="w-full text-sm">{thead}<tbody>{"".join(tbody_rows)}</tbody></table>'
                f'</div>')


class JSONViewer(Component):
    """
    Pretty-printed, scrollable JSON viewer.

    Usage::

        JSONViewer(data={"key": "value", "nested": {...}})
    """

    def __init__(self, data: Union[Dict, List, Any], max_height: str = '400px', **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.max_height = max_height

    def render(self, state_snapshot=None) -> str:
        try:
            formatted = _json.dumps(self.data, indent=2, default=str)
        except Exception as e:
            return f'<div class="text-destructive p-4 border rounded">Error: {escape_html(str(e))}</div>'

        safe = escape_html(formatted)
        return (f'<div id="{self.id}" class="rounded-md bg-zinc-950 overflow-auto" '
                f'style="max-height:{self.max_height}">'
                f'<pre class="p-4 text-sm text-zinc-100 leading-relaxed"><code>{safe}</code></pre>'
                f'</div>')


class CodeBlock(Component):
    """
    Syntax-highlighted code display (static, no JS dependency).

    Usage::

        CodeBlock(code="SELECT * FROM users;", language="sql")
    """

    def __init__(self, code: str, language: str = 'python', **kwargs):
        super().__init__(**kwargs)
        self.code = code
        self.language = language

    def render(self, state_snapshot=None) -> str:
        safe = escape_html(self.code)
        copy_btn = (
            '<button onclick="navigator.clipboard.writeText(this.closest(\'div\').querySelector(\'code\').textContent)" '
            'class="absolute top-2 right-12 text-zinc-400 hover:text-zinc-100 text-xs px-2 py-1 rounded '
            'border border-zinc-700 hover:border-zinc-500 transition-colors">Copy</button>'
        )
        return (f'<div id="{self.id}" class="relative rounded-md bg-zinc-950 overflow-x-auto">'
                f'<span class="absolute top-2 right-2 text-xs text-zinc-500 font-mono">{escape_html(self.language)}</span>'
                f'{copy_btn}'
                f'<pre class="pt-8 pb-4 px-4 text-sm text-zinc-100 leading-relaxed">'
                f'<code>{safe}</code></pre></div>')


class FileDownload(Component):
    """
    Download link rendered as a button. Content is base64 data URI.

    Usage::

        FileDownload(filename="data.csv", content=csv_string, label="Download CSV")
    """

    def __init__(self, filename: str, content: str, label: str = 'Download',
                 mime_type: str = 'text/plain', **kwargs):
        super().__init__(**kwargs)
        self.filename = filename
        self.content = content
        self.label = label
        self.mime_type = mime_type

    def render(self, state_snapshot=None) -> str:
        import base64
        b64 = base64.b64encode(self.content.encode('utf-8')).decode('utf-8')
        uri = f'data:{self.mime_type};base64,{b64}'
        dl_icon = ('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" '
                   'fill="none" stroke="currentColor" stroke-width="2" class="mr-2 h-4 w-4">'
                   '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
                   '<polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>')
        return (f'<a id="{self.id}" href="{uri}" download="{escape_html(self.filename)}" '
                f'class="inline-flex items-center justify-center whitespace-nowrap rounded-md '
                f'text-sm font-medium border border-input bg-background hover:bg-accent '
                f'hover:text-accent-foreground h-10 px-4 py-2 transition-colors">'
                f'{dl_icon}{escape_html(self.label)}</a>')


class DataUpload(Component):
    """
    Drag-and-drop file upload area.

    Usage::

        DataUpload(accept=".csv,.json,.parquet", on_upload=MyState.handle_file)
    """

    def __init__(self, accept: str = '.csv,.json', **kwargs):
        super().__init__(**kwargs)
        self.accept = accept

    def render(self, state_snapshot=None) -> str:
        # Event props handled by base class via on_change/on_submit
        uid = self.id
        return (f'<div id="{uid}" class="flex items-center justify-center w-full">'
                f'<label class="flex flex-col items-center justify-center w-full h-48 border-2 '
                f'border-dashed rounded-lg cursor-pointer bg-muted/50 border-muted-foreground/25 '
                f'hover:bg-muted/80 transition-colors">'
                f'<div class="flex flex-col items-center justify-center pt-5 pb-6">'
                f'<svg class="w-8 h-8 mb-4 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" '
                f'fill="none" viewBox="0 0 20 16">'
                f'<path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" '
                f'stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 '
                f'5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 '
                f'15V6m0 0L8 8m2-2 2 2"/></svg>'
                f'<p class="mb-2 text-sm text-muted-foreground">'
                f'<span class="font-semibold">Click to upload</span> or drag and drop</p>'
                f'<p class="text-xs text-muted-foreground/75">Accepted: {escape_html(self.accept)}</p>'
                f'</div>'
                f'<input type="file" class="hidden" accept="{escape_html(self.accept)}" />'
                f'</label></div>')


class SQLEditor(Component):
    """
    SQL query editor — textarea with Run button.

    Usage::

        SQLEditor(bind=MyState.query, on_run=MyState.execute_query)
    """

    def __init__(self, placeholder: str = 'SELECT * FROM table...', rows: int = 8, **kwargs):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self.rows = rows

    def render(self, state_snapshot=None) -> str:
        uid = self.id
        # Extract bind and on_run from event_props / props
        bind_val = self.props.get('bind', '')
        on_run = self._event_props.get('on_click', None)
        htmx = ''
        if on_run:
            from ..state import EventHandler
            if isinstance(on_run, EventHandler):
                attrs = on_run.get_htmx_attrs(trigger='click')
                htmx = ' '.join(f'{k}="{v}"' for k, v in attrs.items())

        run_icon = ('<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" '
                    'fill="none" stroke="currentColor" stroke-width="2" class="mr-1">'
                    '<polygon points="5 3 19 12 5 21 5 3"/></svg>')

        return (f'<div id="{uid}" class="rounded-md border bg-card text-card-foreground shadow-sm overflow-hidden">'
                f'<div class="p-3 border-b bg-muted/50 flex justify-between items-center">'
                f'<span class="text-sm font-medium font-mono text-muted-foreground">SQL Editor</span>'
                f'<button {htmx} class="inline-flex items-center rounded-md text-xs font-medium '
                f'bg-primary text-primary-foreground hover:bg-primary/90 h-7 px-2 py-1">'
                f'{run_icon}Run Query</button></div>'
                f'<textarea rows="{self.rows}" class="flex w-full rounded-b-md border-0 '
                f'bg-zinc-950 text-zinc-100 p-4 font-mono text-sm focus-visible:outline-none resize-y" '
                f'placeholder="{escape_html(self.placeholder)}"></textarea>'
                f'</div>')


class PlotlyChart(Component):
    """
    Embed a Plotly Figure into the page.

    Usage::

        import plotly.express as px
        fig = px.bar(df, x="month", y="revenue")
        PlotlyChart(figure=fig)
    """

    def __init__(self, figure: Any, height: int = 400, **kwargs):
        super().__init__(**kwargs)
        self.figure = figure
        self.height = height

    def render(self, state_snapshot=None) -> str:
        try:
            import plotly.io as pio
            html_div = pio.to_html(
                self.figure,
                full_html=False,
                include_plotlyjs='cdn',
                config={'responsive': True},
                default_height=self.height,
            )
            return (f'<div id="{self.id}" class="w-full overflow-hidden rounded-md border bg-card">'
                    f'{html_div}</div>')
        except ImportError:
            return ('<div class="p-6 border rounded-lg bg-card text-center">'
                    '<p class="text-muted-foreground text-sm">Plotly is not installed.</p>'
                    '<code class="text-xs bg-muted px-2 py-1 rounded mt-2 inline-block">'
                    'pip install plotly</code></div>')
        except Exception as e:
            return f'<div class="text-destructive p-4 border rounded">PlotlyChart error: {escape_html(str(e))}</div>'


class DataTimeline(Component):
    """
    Vertical timeline of events or pipeline runs.

    Usage::

        DataTimeline(events=[
            {"time": "10:00 AM", "label": "Job started", "status": "success"},
            {"time": "10:05 AM", "label": "Processing...", "status": "running"},
        ])
    """

    STATUS_COLORS = {
        'success': 'bg-green-500',
        'error':   'bg-destructive',
        'failed':  'bg-destructive',
        'running': 'bg-blue-500 animate-pulse',
        'pending': 'bg-muted-foreground/40',
        'info':    'bg-primary',
    }

    def __init__(self, events: List[Dict[str, str]], **kwargs):
        super().__init__(**kwargs)
        self.events = events

    def render(self, state_snapshot=None) -> str:
        items = []
        for i, ev in enumerate(self.events):
            time = ev.get('time', '')
            label = ev.get('label', '')
            status = ev.get('status', 'info')
            desc = ev.get('description', '')
            dot_cls = self.STATUS_COLORS.get(status, self.STATUS_COLORS['info'])
            line = ('<div class="absolute left-2.5 top-5 -ml-px h-full w-0.5 bg-border"></div>'
                    if i < len(self.events) - 1 else '')
            desc_html = (f'<p class="text-xs text-muted-foreground mt-0.5">{escape_html(desc)}</p>'
                         if desc else '')
            items.append(f'''<li class="relative pb-8 last:pb-0">
  {line}
  <div class="relative flex items-start space-x-3">
    <div class="relative">
      <span class="flex h-5 w-5 items-center justify-center rounded-full {dot_cls} ring-4 ring-background">
        <span class="h-1.5 w-1.5 rounded-full bg-white"></span>
      </span>
    </div>
    <div class="min-w-0 flex-1 py-0">
      <p class="text-sm font-medium text-foreground">{escape_html(label)}</p>
      <p class="text-xs text-muted-foreground">{escape_html(time)}</p>
      {desc_html}
    </div>
  </div>
</li>''')

        return (f'<div id="{self.id}">'
                f'<ul role="list" class="m-0 p-4 border rounded-lg bg-card">{"".join(items)}</ul>'
                f'</div>')


class FeatureImportance(Component):
    """
    Horizontal bar chart for ML feature importances.

    Usage::

        FeatureImportance(features={"age": 0.30, "income": 0.25, "tenure": 0.18})
    """

    def __init__(self, features: Dict[str, float], title: str = 'Feature Importance', **kwargs):
        super().__init__(**kwargs)
        self.features = features
        self.title = title

    def render(self, state_snapshot=None) -> str:
        sorted_f = sorted(self.features.items(), key=lambda x: x[1], reverse=True)
        max_val = max((v for _, v in sorted_f), default=0.001)

        bars = []
        for feat, imp in sorted_f:
            pct = (imp / max_val) * 100
            bars.append(f'''<div class="flex items-center gap-2 mt-2">
  <div class="w-1/3 text-xs text-right truncate text-muted-foreground" title="{escape_html(feat)}">{escape_html(feat)}</div>
  <div class="w-2/3 flex items-center gap-2">
    <div class="h-4 bg-primary rounded-sm transition-all" style="width:{pct:.1f}%;min-width:2px"></div>
    <span class="text-xs text-muted-foreground font-mono">{imp:.4f}</span>
  </div>
</div>''')

        return (f'<div id="{self.id}" class="rounded-xl border bg-card text-card-foreground shadow p-6">'
                f'<h3 class="font-semibold leading-none tracking-tight mb-4">{escape_html(self.title)}</h3>'
                f'{"".join(bars)}</div>')


class SchemaViewer(Component):
    """
    Display DataFrame or dict schema (columns, types, nulls, uniques).

    Usage::

        SchemaViewer(df=my_df)
        SchemaViewer(schema={"user_id": "int64", "name": "object", "score": "float64"})
    """

    def __init__(self, df: Any = None, schema: Optional[Dict[str, str]] = None, **kwargs):
        super().__init__(**kwargs)
        self.df = df
        self.schema = schema

    def render(self, state_snapshot=None) -> str:
        rows = []

        if self.df is not None:
            try:
                import pandas as pd
                if isinstance(self.df, pd.DataFrame):
                    for col in self.df.columns:
                        dtype = str(self.df[col].dtype)
                        nulls = int(self.df[col].isna().sum())
                        unique = int(self.df[col].nunique())
                        pct_null = f'{(nulls / len(self.df) * 100):.1f}%' if len(self.df) > 0 else '0%'
                        rows.append(
                            f'<tr class="border-b hover:bg-muted/50">'
                            f'<td class="p-2 font-mono text-sm">{escape_html(str(col))}</td>'
                            f'<td class="p-2 text-xs font-mono text-primary">{escape_html(dtype)}</td>'
                            f'<td class="p-2 text-xs text-center">{nulls} ({pct_null})</td>'
                            f'<td class="p-2 text-xs text-center">{unique}</td>'
                            f'</tr>'
                        )
                else:
                    return ('<div class="text-destructive p-4 border rounded">'
                            'SchemaViewer: not a DataFrame</div>')
            except ImportError:
                return ('<div class="text-destructive p-4 border rounded">'
                        '⚠ pandas is not installed: <code>pip install pandas</code></div>')
        elif self.schema:
            for col, dtype in self.schema.items():
                rows.append(
                    f'<tr class="border-b hover:bg-muted/50">'
                    f'<td class="p-2 font-mono text-sm">{escape_html(str(col))}</td>'
                    f'<td class="p-2 text-xs font-mono text-primary">{escape_html(str(dtype))}</td>'
                    f'<td class="p-2 text-xs text-center">—</td>'
                    f'<td class="p-2 text-xs text-center">—</td>'
                    f'</tr>'
                )
        else:
            return '<div class="text-muted-foreground p-4">No schema or DataFrame provided.</div>'

        return (f'<div id="{self.id}" class="w-full overflow-auto rounded-md border bg-card">'
                f'<table class="w-full text-sm text-left">'
                f'<thead class="bg-muted text-muted-foreground border-b">'
                f'<tr>'
                f'<th class="p-2 font-medium">Column Name</th>'
                f'<th class="p-2 font-medium">Type</th>'
                f'<th class="p-2 font-medium text-center">Null Count</th>'
                f'<th class="p-2 font-medium text-center">Unique Values</th>'
                f'</tr></thead>'
                f'<tbody>{"".join(rows)}</tbody>'
                f'</table></div>')
