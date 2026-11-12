"""
Terminal User Interface (TUI) compiler and runner for PyDataUI.
Renders PyDataUI component trees directly in terminal emulators using Rich,
with fallback ASCII rendering for headless clusters and remote SSH sessions,
and interactive command dock for real-time input/output and action dispatching.
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
    from rich.prompt import Prompt
    _HAS_RICH = True
except ImportError:
    _HAS_RICH = False

from .components.base import Component
from .components.data_display import sniff_tabular_data


def render_to_rich(comp: Any, state_snapshot: Optional[Dict[str, Any]] = None) -> Any:
    """Recursively convert a PyDataUI component into a Rich renderable."""
    if not _HAS_RICH:
        return str(render_to_ascii(comp, state_snapshot))

    if comp is None:
        return RichText("")

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

    # 6. Inputs & Interactive Form Fields
    if c_name in ('Input', 'ShadInput'):
        label = getattr(comp, 'label', '') or (comp.props.get('label') if hasattr(comp, 'props') else '')
        val = getattr(comp, 'value', '') or (comp.props.get('value') if hasattr(comp, 'props') else '')
        val_str = str(val.resolve(snap) if hasattr(val, 'resolve') else val) if val is not None else ''
        ph = getattr(comp, 'placeholder', '') or (comp.props.get('placeholder') if hasattr(comp, 'props') else '')
        display_val = val_str if val_str else f"[dim]{ph or 'Enter text...'}[/dim]"
        lbl_prefix = f"[bold cyan]{label}: [/bold cyan]" if label else ""
        return Panel(f"{lbl_prefix}[bold yellow]{display_val}[/bold yellow]", border_style="cyan", expand=False)

    if c_name in ('TextArea', 'ShadTextarea'):
        label = getattr(comp, 'label', '') or (comp.props.get('label') if hasattr(comp, 'props') else '')
        val = getattr(comp, 'value', '') or (comp.props.get('value') if hasattr(comp, 'props') else '')
        val_str = str(val.resolve(snap) if hasattr(val, 'resolve') else val) if val is not None else ''
        ph = getattr(comp, 'placeholder', '') or (comp.props.get('placeholder') if hasattr(comp, 'props') else '')
        display_val = val_str if val_str else f"[dim]{ph or 'Enter multiline text...'}[/dim]"
        return Panel(f"[bold yellow]{display_val}[/bold yellow]", title=f"[bold cyan]{label or 'Text Area'}[/bold cyan]", border_style="cyan", expand=False)

    if c_name == 'ShadSlider':
        name = getattr(comp, 'name', '') or (comp.props.get('name') if hasattr(comp, 'props') else 'Slider')
        val = getattr(comp, 'value', 0)
        min_v = getattr(comp, 'min', 0)
        max_v = getattr(comp, 'max', 100)
        return Panel(f"[bold green]Value: {val}[/bold green] [dim](Range: {min_v}..{max_v})[/dim]", title=f"[bold cyan]Slider: {name}[/bold cyan]", border_style="yellow", expand=False)

    # 6b. Interactive Chat
    if c_name == 'Chat':
        raw_msgs = getattr(comp, 'messages', [])
        msgs = comp._resolve_value(raw_msgs, snap) if hasattr(comp, '_resolve_value') else raw_msgs
        title = getattr(comp, 'chat_title', 'AI Assistant')
        lines = []
        for m in msgs:
            role = m.get('role', 'user')
            content = m.get('content', '')
            if role == 'user':
                lines.append(f"[bold green]You:[/bold green] {content}")
            else:
                lines.append(f"[bold cyan]{title}:[/bold cyan] {content}")
        if not lines:
            lines.append("[dim]No messages yet. Start conversation below![/dim]")
        return Panel("\n\n".join(lines), title=f"[bold green]● {title}[/bold green]", border_style="cyan")

    # 7. Dividers
    if c_name in ('Divider', 'ShadSeparator'):
        return Rule(style="dim white")

    # 8. Card / ShadCard
    if c_name in ('Card', 'ShadCard'):
        title = getattr(comp, 'title', None)
        rendered_children = [render_to_rich(c, snap) for c in comp.children]
        group = Group(*rendered_children)
        return Panel(group, title=f"[bold]{title}[/bold]" if title else None, border_style="cyan")

    # 9. Row / HStack / Columns
    if c_name in ('Row', 'HStack'):
        rendered_children = [render_to_rich(c, snap) for c in comp.children]
        return Columns(rendered_children, equal=False, expand=False)

    # 10. Generic container / Col / VStack
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

    if c_name in ('Input', 'ShadInput'):
        label = getattr(comp, 'label', '') or (comp.props.get('label') if hasattr(comp, 'props') else 'Input')
        val = getattr(comp, 'value', '') or (comp.props.get('value') if hasattr(comp, 'props') else '')
        return f"{sp}[Input {label}: '{val}']"

    if c_name in ('TextArea', 'ShadTextarea'):
        label = getattr(comp, 'label', '') or (comp.props.get('label') if hasattr(comp, 'props') else 'Text Area')
        val = getattr(comp, 'value', '') or (comp.props.get('value') if hasattr(comp, 'props') else '')
        return f"{sp}[TextArea {label}: '{val}']"

    if c_name == 'ShadSlider':
        name = getattr(comp, 'name', '') or (comp.props.get('name') if hasattr(comp, 'props') else 'Slider')
        val = getattr(comp, 'value', 0)
        return f"{sp}[Slider {name}: {val}]"

    if c_name == 'Chat':
        raw_msgs = getattr(comp, 'messages', [])
        msgs = comp._resolve_value(raw_msgs, snap) if hasattr(comp, '_resolve_value') else raw_msgs
        title = getattr(comp, 'chat_title', 'AI Assistant')
        lines = [f"\n{sp}=== {title} ==="]
        for m in msgs:
            lines.append(f"{sp}{m.get('role', 'user').title()}: {m.get('content', '')}")
        return "\n".join(lines)

    if c_name in ('Divider', 'ShadSeparator'):
        return f"{sp}{'-' * 40}"

    # Render children
    child_lines = []
    for c in comp.children:
        child_lines.append(render_to_ascii(c, snap, indent=indent + 1))
    return "\n".join(child_lines)


def _collect_actions() -> Dict[str, Any]:
    """Collect all callable event handler actions registered across procedural states."""
    from .state import StateMeta
    actions = {}
    for sname, scls in StateMeta._registry.items():
        handlers = scls.get_event_handlers() if hasattr(scls, 'get_event_handlers') else {}
        for hname, hfn in handlers.items():
            if hname != 'reset':
                actions[hname] = (sname, scls, hfn)
    return actions


def run_tui(
    app: Any,
    file_path: Optional[str] = None,
    refresh_interval: float = 1.0,
    page_path: str = "/",
    once: bool = False,
    interactive: Optional[bool] = None,
) -> None:
    """Launch the application dashboard in interactive Terminal UI mode.

    Supports interactive commands, getting input, running actions, page switching,
    and live reactive output updates.
    """
    routes = getattr(app, 'routes', {})
    current_page = page_path if page_path in routes else (list(routes.keys())[0] if routes else "/")
    handler = routes.get(current_page)

    if not handler and routes:
        current_page = list(routes.keys())[0]
        handler = routes[current_page]

    if not handler:
        print("Error: No registered pages found in PyDataUI application.")
        return

    console = Console() if _HAS_RICH else None

    # Fast single-shot output
    if once:
        root = handler()
        if _HAS_RICH and console:
            rendered = render_to_rich(root)
            title = getattr(app, 'title', 'PyDataUI Terminal Dashboard')
            console.print(Panel(
                rendered,
                title=f"[bold green]PyDataUI v1.2.0 • {title}[/bold green]",
                subtitle="[dim]PyDataUI Single-Shot Output[/dim]",
                border_style="green"
            ))
        else:
            print(render_to_ascii(root))
        return

    # Auto-detect interactive mode: interactive when standard input is a terminal
    if interactive is None:
        interactive = sys.stdin.isatty()

    # Passive Live Refresh Loop (non-interactive / watch mode)
    if not interactive:
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
                return f"\n=== PyDataUI Terminal Dashboard ({current_page}) ===\n\n{txt}\n\n[Press Ctrl+C to exit]\n"

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
                    sys.stdout.write("\033[2J\033[H")
                    sys.stdout.flush()
                    print(get_dashboard_view())
                    time.sleep(refresh_interval)
            except KeyboardInterrupt:
                print("\nPyDataUI TUI session closed.")
        return

    # Interactive TUI REPL Loop with Input/Output Dock
    page_list = getattr(app, 'discovered_pages', [])
    if not page_list:
        page_list = [{'path': p, 'title': p.replace('/', '').title() or 'Home'} for p in routes.keys()]

    while True:
        handler = routes.get(current_page)
        if not handler:
            current_page = list(routes.keys())[0]
            handler = routes[current_page]

        actions_map = _collect_actions()
        root = handler()
        title = getattr(app, 'title', 'PyDataUI Terminal Dashboard')

        if _HAS_RICH and console:
            # Clear terminal screen
            console.clear()

            rendered = render_to_rich(root)
            dashboard_panel = Panel(
                rendered,
                title=f"[bold green]PyDataUI v1.2.0 • {title} • Active: {current_page}[/bold green]",
                subtitle="[dim]PyDataUI Interactive Terminal Dashboard[/dim]",
                border_style="green"
            )
            console.print(dashboard_panel)

            # Build Interactive Command Dock
            nav_badges = [f"[bold white][{i+1}][/bold white] {p['title']}" for i, p in enumerate(page_list[:6])]
            act_names = list(actions_map.keys())[:8]
            act_badges = [f"[bold yellow]{act}[/bold yellow]" for act in act_names]

            dock_lines = [
                f"[cyan]Pages:[/cyan] {' | '.join(nav_badges)}",
                f"[green]Actions:[/green] {', '.join(act_badges) if act_badges else 'None'}",
                f"[dim]Commands: [1-{len(page_list)}] Page | <action> Execute | input <text> | set <k>=<v> | r (refresh) | q (exit)[/dim]"
            ]
            console.print(Panel("\n".join(dock_lines), title="[bold yellow]Interactive TUI Command Dock[/bold yellow]", border_style="yellow"))

            try:
                cmd = Prompt.ask("[bold cyan]PyDataUI >[/bold cyan]", default="r", console=console).strip()
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]PyDataUI interactive TUI closed.[/yellow]")
                break
        else:
            sys.stdout.write("\033[2J\033[H")
            sys.stdout.flush()
            txt = render_to_ascii(root)
            print(f"\n=== PyDataUI Interactive Dashboard ({current_page}) ===\n\n{txt}\n")
            print("Commands: [1-N] Page | <action> Execute | input <text> | set <k>=<v> | r (refresh) | q (exit)")
            try:
                cmd = input("PyDataUI > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nPyDataUI interactive TUI closed.")
                break

        if not cmd or cmd.lower() in ('r', 'refresh'):
            continue

        if cmd.lower() in ('q', 'quit', 'exit'):
            if console:
                console.print("[yellow]Exited PyDataUI TUI session.[/yellow]")
            else:
                print("Exited PyDataUI TUI session.")
            break

        # Navigation by page number
        if cmd.isdigit():
            idx = int(cmd) - 1
            if 0 <= idx < len(page_list):
                current_page = page_list[idx]['path']
                continue

        # Navigation by route slug or title
        cmd_lower = cmd.lower()
        matched_page = None
        for p in page_list:
            if cmd_lower in (p['path'].lower(), p['title'].lower(), p['path'].lstrip('/').lower()):
                matched_page = p['path']
                break
        if matched_page:
            current_page = matched_page
            continue

        # Explicit Input Command (e.g. `input Explain LoRA`)
        if cmd_lower.startswith(('input ', 'prompt ', 'ask ', 'query ')):
            parts = cmd.split(None, 1)
            user_val = parts[1].strip() if len(parts) > 1 else ""
            dispatched = False
            for act_candidate in ('submit_prompt', 'process_input', 'on_submit'):
                if act_candidate in actions_map:
                    sname, scls, act_fn = actions_map[act_candidate]
                    act_fn(scls, user_input=user_val)
                    dispatched = True
                    break
            if not dispatched and actions_map:
                first_act = list(actions_map.keys())[0]
                actions_map[first_act][2](actions_map[first_act][1], user_input=user_val)
            continue

        # Set Variable Command (e.g. `set active_workers=14`)
        if cmd_lower.startswith('set '):
            expr = cmd[4:].strip()
            if '=' in expr:
                k, v = expr.split('=', 1)
                k = k.strip()
                v = v.strip()
                if v.isdigit():
                    v = int(v)
                elif v.replace('.', '', 1).isdigit():
                    v = float(v)
                elif v.lower() in ('true', 'false'):
                    v = v.lower() == 'true'
                from .state import StateMeta
                for sname, scls in StateMeta._registry.items():
                    if k in scls.get_state_vars():
                        setattr(scls, k, v)
                        if hasattr(scls, '_class_store'):
                            scls._class_store[k] = v
            continue

        # Direct Action Execution (e.g. `scale_up`, `scale_down`, `reset_cluster`, `clear_history`)
        matched_act = None
        for act_name in actions_map:
            if cmd_lower == act_name.lower():
                matched_act = act_name
                break
        if matched_act:
            sname, scls, act_fn = actions_map[matched_act]
            try:
                act_fn(scls)
            except Exception:
                pass
            continue

        # Fallback: Treat unrecognized text as chat/input query
        input_candidates = ('chat', 'send', 'send_message', 'message', 'reply', 'submit_prompt', 'process_input', 'on_submit')
        dispatched = False
        for cand in input_candidates:
            if cand in actions_map:
                sname, scls, act_fn = actions_map[cand]
                try:
                    act_fn(scls, user_input=cmd)
                    dispatched = True
                    break
                except Exception:
                    pass
        if not dispatched and len(actions_map) == 1:
            only_act = list(actions_map.keys())[0]
            sname, scls, act_fn = actions_map[only_act]
            try:
                act_fn(scls, user_input=cmd)
            except Exception:
                pass
