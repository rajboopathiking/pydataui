"""
Terminal User Interface (TUI) compiler and runner for PyDataUI.
Renders PyDataUI component trees directly in terminal emulators using Rich,
with fallback ASCII rendering for headless clusters and remote SSH sessions.
"""
from __future__ import annotations
import sys
import time
from typing import Any, Dict, List, Optional, Union

try:
    import rich
    from rich.console import Console, Group
    from rich.panel import Panel
    from rich.table import Table as RichTable
    from rich.columns import Columns
    from rich.text import Text as RichText
    from rich.rule import Rule
    from rich.live import Live
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

from .components.base import Component
from .components.data_display import sniff_tabular_data


def render_to_rich(comp: Any, state_snapshot: Optional[Dict[str, Any]] = None) -> Any:
    """Recursively convert a PyDataUI component into a Rich renderable."""
    if not _HAS_RICH:
        return str(render_to_ascii(comp, state_snapshot))

    snap = state_snapshot or {}

    # Plain primitives
    if not isinstance(comp, Component):
        val = comp.resolve(snap) if hasattr(comp, 'resolve') else comp
        return RichText(str(val))

    c_name = type(comp).__name__

    # 1. Heading
    if c_name in ('Heading', 'ShadCardTitle'):
        level = getattr(comp, 'level', 1)
        txt = getattr(comp, 'text', '')
        if not txt and comp.children:
            txt = str(comp.children[0])
        style = "bold cyan" if level <= 2 else "bold white"
        return RichText(str(txt), style=style)

    # 2. Text / Paragraph / Label
    if c_name in ('Text', 'Paragraph', 'Label', 'ShadCardDescription'):
        txt = getattr(comp, 'text', '')
        if not txt and comp.children:
            txt = str(comp.children[0])
        color = "dim white" if c_name == 'ShadCardDescription' else "white"
        return RichText(str(txt), style=color)

    # 3. MetricCard
    if c_name == 'MetricCard':
        title = getattr(comp, 'title', 'Metric')
        val = getattr(comp, 'value', '')
        delta = getattr(comp, 'delta', None)
        delta_str = f"\n[green]▲ {delta}[/green]" if delta and not str(delta).startswith('-') else (f"\n[red]▼ {delta}[/red]" if delta else "")
        content = f"[bold white]{val}[/bold white]{delta_str}"
        return Panel(content, title=f"[bold cyan]{title}[/bold cyan]", border_style="blue", expand=False)

    # 4. Tables (Table, DataTable, ShadTable)
    if c_name in ('Table', 'DataTable', 'ShadTable'):
        raw_data = getattr(comp, 'data', None)
        if raw_data is None and hasattr(comp, 'props') and 'data' in comp.props:
            raw_data = comp.props['data']
        cols = getattr(comp, 'columns', None)
        hdrs = getattr(comp, 'headers', None)
        records, col_keys, headers = sniff_tabular_data(raw_data, cols, hdrs)

        t = RichTable(show_header=True, header_style="bold magenta", border_style="dim white")
        for h in headers:
            t.add_column(str(h))

        for row in records[:25]:  # Limit terminal rows for smooth display
            row_vals = [str(row.get(k, '')) for k in col_keys]
            t.add_row(*row_vals)

        if len(records) > 25:
            t.caption = f"[dim]Showing 25 of {len(records)} entries[/dim]"
        return t

    # 5. Buttons & Badges
    if c_name in ('Button', 'ShadButton'):
        label = getattr(comp, 'label', '')
        if not label and comp.children:
            label = str(comp.children[0])
        return RichText(f" [ {label} ] ", style="bold white on blue")

    if c_name in ('Badge', 'ShadBadge'):
        txt = getattr(comp, 'text', '')
        if not txt and comp.children:
            txt = str(comp.children[0])
        return RichText(f"[{txt}]", style="bold black on green")

    # 6. Dividers
    if c_name in ('Divider', 'ShadSeparator'):
        return Rule(style="dim white")

    # 7. Card / ShadCard
    if c_name in ('Card', 'ShadCard'):
        title = getattr(comp, 'title', None)
        rendered_children = [render_to_rich(c, snap) for c in comp.children]
        group = Group(*rendered_children)
        return Panel(group, title=f"[bold]{title}[/bold]" if title else None, border_style="cyan")

    # 8. Row / HStack / Columns
    if c_name in ('Row', 'HStack'):
        rendered_children = [render_to_rich(c, snap) for c in comp.children]
        return Columns(rendered_children, equal=False, expand=False)

    # 9. Generic container / Col / VStack
    rendered_children = [render_to_rich(c, snap) for c in comp.children]
    if len(rendered_children) == 1:
        return rendered_children[0]
    return Group(*rendered_children)


def render_to_ascii(comp: Any, state_snapshot: Optional[Dict[str, Any]] = None, indent: int = 0) -> str:
    """Fallback plain text/ASCII renderer for headless terminals without rich."""
    snap = state_snapshot or {}
    sp = "  " * indent

    if not isinstance(comp, Component):
        val = comp.resolve(snap) if hasattr(comp, 'resolve') else comp
        return f"{sp}{val}"

    c_name = type(comp).__name__

    if c_name in ('Heading', 'ShadCardTitle'):
        txt = getattr(comp, 'text', '') or (comp.children[0] if comp.children else '')
        return f"\n{sp}=== {txt} ===\n"

    if c_name in ('Text', 'Paragraph', 'Label', 'ShadCardDescription'):
        txt = getattr(comp, 'text', '') or (comp.children[0] if comp.children else '')
        return f"{sp}{txt}"

    if c_name == 'MetricCard':
        title = getattr(comp, 'title', 'Metric')
        val = getattr(comp, 'value', '')
        delta = f" ({comp.delta})" if getattr(comp, 'delta', None) else ""
        return f"{sp}[ {title}: {val}{delta} ]"

    if c_name in ('Table', 'DataTable', 'ShadTable'):
        records, cols, headers = sniff_tabular_data(getattr(comp, 'data', None), getattr(comp, 'columns', None), getattr(comp, 'headers', None))
        if not records:
            return f"{sp}[Empty Table]"
        hdr_line = " | ".join(headers)
        sep_line = "-" * len(hdr_line)
        lines = [f"{sp}{hdr_line}", f"{sp}{sep_line}"]
        for row in records[:15]:
            row_str = " | ".join(str(row.get(k, '')) for k in cols)
            lines.append(f"{sp}{row_str}")
        return "\n".join(lines)

    if c_name in ('Button', 'ShadButton'):
        label = getattr(comp, 'label', '') or (comp.children[0] if comp.children else 'Button')
        return f"{sp}[ {label} ]"

    if c_name in ('Divider', 'ShadSeparator'):
        return f"{sp}{'-' * 40}"

    # Render children
    child_lines = []
    for c in comp.children:
        child_lines.append(render_to_ascii(c, snap, indent=indent + 1))
    return "\n".join(child_lines)


def run_tui(
    app: Any,
    file_path: Optional[str] = None,
    refresh_interval: float = 1.0,
    page_path: str = "/",
    once: bool = False
) -> None:
    """Launch the application dashboard in interactive Terminal UI mode."""
    routes = getattr(app, 'routes', {})
    handler = routes.get(page_path)
    if not handler and routes:
        page_path = list(routes.keys())[0]
        handler = routes[page_path]

    if not handler:
        print(f"Error: No registered pages found in PyDataUI application.")
        return

    # Check console
    console = Console() if _HAS_RICH else None

    def get_dashboard_view():
        root = handler()
        if _HAS_RICH:
            rendered = render_to_rich(root)
            title = getattr(app, 'title', 'PyDataUI Terminal Dashboard')
            return Panel(
                rendered,
                title=f"[bold green]PyDataUI v1.2.0 • {title}[/bold green]",
                subtitle="[dim]Press Ctrl+C to exit[/dim]",
                border_style="green"
            )
        else:
            txt = render_to_ascii(root)
            return f"\n=== PyDataUI Terminal Dashboard ({page_path}) ===\n\n{txt}\n\n[Press Ctrl+C to exit]\n"

    if once:
        view = get_dashboard_view()
        if console:
            console.print(view)
        else:
            print(view)
        return

    # Interactive live loop
    if console:
        try:
            with Live(get_dashboard_view(), console=console, refresh_per_second=int(1.0 / max(0.2, refresh_interval))) as live:
                while True:
                    time.sleep(refresh_interval)
                    live.update(get_dashboard_view())
        except KeyboardInterrupt:
            console.print("\n[yellow]PyDataUI TUI session closed.[/yellow]")
    else:
        try:
            while True:
                # Clear terminal and print
                sys.stdout.write("\033[2J\033[H")
                sys.stdout.flush()
                print(get_dashboard_view())
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\nPyDataUI TUI session closed.")
