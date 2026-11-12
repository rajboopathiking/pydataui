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


def _find_chat_component(comp: Any) -> Optional[Any]:
    """Recursively search for a Chat component in the component tree."""
    if comp is None:
        return None
    if type(comp).__name__ == 'Chat':
        return comp
    children = getattr(comp, 'children', None)
    if children and isinstance(children, (list, tuple)):
        for child in children:
            found = _find_chat_component(child)
            if found:
                return found
    return None


def _dispatch_action(act_fn: Any, scls: Any = None, **kwargs) -> Any:
    """Safely invoke an action (sync or async) passing arguments matched by signature."""
    import inspect
    import asyncio
    from .session import Session
    from .state import _current_session

    if act_fn is None:
        return None

    if _current_session.get() is None:
        _current_session.set(Session(session_id="tui_action_session"))

    # Inspect signature
    sig = None
    try:
        sig = inspect.signature(act_fn)
    except (ValueError, TypeError):
        pass

    call_args = []
    call_kwargs = {}

    if scls is not None and sig and len(sig.parameters) > 0:
        first_param = list(sig.parameters.values())[0]
        if first_param.name in ('self', 'cls', 'state', 'self_inst'):
            call_args.append(scls)

    if sig:
        has_var_kw = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
        if has_var_kw:
            call_kwargs.update(kwargs)
        else:
            for p_name, param in sig.parameters.items():
                if p_name in ('self', 'cls', 'state', 'self_inst'):
                    continue
                if p_name in kwargs:
                    call_kwargs[p_name] = kwargs[p_name]
                elif p_name in ('message', 'user_input', 'prompt', 'text', 'query', 'content'):
                    for text_key in ('message', 'user_input', 'prompt', 'text', 'query', 'content'):
                        if text_key in kwargs:
                            call_kwargs[p_name] = kwargs[text_key]
                            break
    else:
        call_kwargs.update(kwargs)

    try:
        res = act_fn(*call_args, **call_kwargs)
    except TypeError:
        try:
            res = act_fn(**call_kwargs)
        except TypeError:
            first_val = next(iter(kwargs.values())) if kwargs else None
            res = act_fn(first_val) if first_val is not None else act_fn()

    if inspect.isawaitable(res) or inspect.iscoroutine(res):
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                return asyncio.run_coroutine_threadsafe(res, loop).result(timeout=120)
            else:
                return loop.run_until_complete(res)
        except RuntimeError:
            return asyncio.run(res)
    return res


def _resolve_chat_action(chat_comp: Any, actions_map: Dict[str, Any]) -> tuple[Optional[Any], Optional[Any]]:
    """Determine the action function and state class associated with a Chat component."""
    from .state import EventHandler, StateMeta

    # 1. Check Chat's on_send event prop
    on_send = getattr(chat_comp, '_event_props', {}).get('on_send') if hasattr(chat_comp, '_event_props') else None
    if on_send is None and hasattr(chat_comp, 'props'):
        on_send = chat_comp.props.get('on_send')

    if isinstance(on_send, EventHandler):
        scls_name = getattr(on_send, 'state_cls_name', None)
        method_name = getattr(on_send, 'method_name', None)
        if scls_name and scls_name in StateMeta._registry:
            scls = StateMeta._registry[scls_name]
            handlers = scls.get_event_handlers() if hasattr(scls, 'get_event_handlers') else {}
            if method_name in handlers:
                return handlers[method_name], scls
            if hasattr(scls, method_name):
                return getattr(scls, method_name), scls
    elif callable(on_send):
        return on_send, None

    # 2. Check candidate action names in actions_map
    for cand in ('handle_message', 'send_message', 'on_send', 'chat', 'message', 'reply', 'process_input', 'submit_prompt'):
        if cand in actions_map:
            sname, scls, act_fn = actions_map[cand]
            return act_fn, scls

    # 3. Fallback to first available action
    if actions_map:
        first_act = list(actions_map.keys())[0]
        return actions_map[first_act][2], actions_map[first_act][1]

    return None, None


def _run_chat_tui(app: Any, handler: Any, current_page: str, initial_chat_comp: Any, console: Any) -> None:
    """Run an intuitive, streamlined conversational Terminal UI for Chat applications."""
    title = getattr(app, 'title', 'PyDataUI Chatbot')
    chat_title = getattr(initial_chat_comp, 'chat_title', title)
    suggestions = getattr(initial_chat_comp, 'suggestions', []) or []

    if _HAS_RICH and console:
        console.clear()
        header = (
            f"[bold green]● {chat_title}[/bold green] • [dim]PyDataUI v1.2.1 Chat Mode[/dim]\n"
            f"[dim]Type your message and press Enter to chat. Type [bold yellow]q[/bold yellow] or [bold yellow]exit[/bold yellow] to quit. Type [bold yellow]/clear[/bold yellow] to reset.[/dim]"
        )
        console.print(Panel(header, border_style="cyan", expand=False))
        if suggestions:
            badges = [f"[bold yellow][{i+1}][/bold yellow] {s}" for i, s in enumerate(suggestions)]
            console.print(Panel("  |  ".join(badges), title="[bold cyan]💡 Quick Suggestions[/bold cyan]", border_style="dim blue", expand=False))
        console.print()
    else:
        print(f"\n=== {chat_title} • PyDataUI Chat Mode ===")
        print("Type your message and press Enter. Type 'q' to quit. Type '/clear' to reset.\n")
        if suggestions:
            print("Quick Suggestions: " + " | ".join(f"[{i+1}] {s}" for i, s in enumerate(suggestions)) + "\n")

    # Initial history
    raw_msgs = getattr(initial_chat_comp, 'messages', [])
    msgs = initial_chat_comp._resolve_value(raw_msgs, {}) if hasattr(initial_chat_comp, '_resolve_value') else raw_msgs
    printed_count = 0
    if msgs:
        for m in msgs:
            role = m.get('role', 'user')
            content = m.get('content', '')
            if role == 'user':
                if _HAS_RICH and console:
                    console.print(f"[bold green]You:[/bold green] {content}")
                else:
                    print(f"You: {content}")
            else:
                if _HAS_RICH and console:
                    console.print(f"[bold cyan]{chat_title}:[/bold cyan] {content}\n")
                else:
                    print(f"{chat_title}: {content}\n")
        printed_count = len(msgs)

    while True:
        try:
            if _HAS_RICH and console:
                user_input = Prompt.ask("[bold green]You[/bold green]", console=console).strip()
            else:
                user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            if console:
                console.print("\n[yellow]Exited PyDataUI chat session.[/yellow]")
            else:
                print("\nExited PyDataUI chat session.")
            break

        if not user_input:
            continue

        if user_input.lower() in ('q', 'quit', 'exit', ':q', '/quit'):
            if console:
                console.print("[yellow]Exited PyDataUI chat session.[/yellow]")
            else:
                print("Exited PyDataUI chat session.")
            break

        # Suggestion selection by number
        if user_input.isdigit() and suggestions:
            s_idx = int(user_input) - 1
            if 0 <= s_idx < len(suggestions):
                user_input = suggestions[s_idx]
                if console:
                    console.print(f"[dim]Selected: {user_input}[/dim]")

        # /clear command
        if user_input.lower() in ('/clear', 'clear'):
            root = handler()
            chat_comp = _find_chat_component(root) or initial_chat_comp
            clear_fn = getattr(chat_comp, '_event_props', {}).get('on_clear')
            if clear_fn:
                try:
                    _dispatch_action(clear_fn)
                except Exception:
                    pass
            if _HAS_RICH and console:
                console.clear()
                console.print(Panel(header, border_style="cyan", expand=False))
            else:
                print("\n=== Chat Cleared ===")
            printed_count = 0
            continue

        # Re-resolve actions and chat component
        actions_map = _collect_actions()
        root = handler()
        chat_comp = _find_chat_component(root) or initial_chat_comp
        act_fn, scls = _resolve_chat_action(chat_comp, actions_map)

        if not act_fn:
            if console:
                console.print("[bold red]No chat action handler found.[/bold red]\n")
            else:
                print("No chat action handler found.\n")
            continue

        try:
            if _HAS_RICH and console:
                with console.status(f"[bold cyan]{chat_title} is thinking...[/bold cyan]", spinner="dots"):
                    _dispatch_action(act_fn, scls, message=user_input, user_input=user_input, text=user_input, prompt=user_input)
            else:
                print(f"{chat_title} is thinking...")
                _dispatch_action(act_fn, scls, message=user_input, user_input=user_input, text=user_input, prompt=user_input)
        except Exception as e:
            if console:
                console.print(f"[bold red]Chat error: {e}[/bold red]\n")
            else:
                print(f"Chat error: {e}\n")
            continue

        # Re-render to fetch new messages
        root = handler()
        chat_comp = _find_chat_component(root) or initial_chat_comp
        raw_msgs = getattr(chat_comp, 'messages', [])
        current_msgs = chat_comp._resolve_value(raw_msgs, {}) if hasattr(chat_comp, '_resolve_value') else raw_msgs

        if current_msgs and len(current_msgs) > printed_count:
            for m in current_msgs[printed_count:]:
                role = m.get('role', 'user')
                content = m.get('content', '')
                if role != 'user':
                    if _HAS_RICH and console:
                        console.print(f"[bold cyan]{chat_title}:[/bold cyan] {content}\n")
                    else:
                        print(f"{chat_title}: {content}\n")
            printed_count = len(current_msgs)
        elif current_msgs:
            printed_count = len(current_msgs)


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
    from .session import Session
    from .state import _current_session
    if _current_session.get() is None:
        _current_session.set(Session(session_id="tui_session"))
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

    # Check for Chat Component in active page - if present, run streamlined conversational Chat TUI
    root = handler()
    chat_comp = _find_chat_component(root)
    if chat_comp is not None:
        _run_chat_tui(app, handler, current_page, chat_comp, console)
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
            for act_candidate in ('submit_prompt', 'process_input', 'on_submit', 'handle_message', 'send_message', 'chat'):
                if act_candidate in actions_map:
                    sname, scls, act_fn = actions_map[act_candidate]
                    _dispatch_action(act_fn, scls, message=user_val, user_input=user_val, text=user_val, prompt=user_val)
                    dispatched = True
                    break
            if not dispatched and actions_map:
                first_act = list(actions_map.keys())[0]
                _dispatch_action(actions_map[first_act][2], actions_map[first_act][1], message=user_val, user_input=user_val, text=user_val, prompt=user_val)
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
                _dispatch_action(act_fn, scls)
            except Exception:
                pass
            continue

        # Fallback: Treat unrecognized text as chat/input query
        input_candidates = ('chat', 'send', 'send_message', 'handle_message', 'message', 'reply', 'submit_prompt', 'process_input', 'on_submit')
        dispatched = False
        for cand in input_candidates:
            if cand in actions_map:
                sname, scls, act_fn = actions_map[cand]
                try:
                    _dispatch_action(act_fn, scls, message=cmd, user_input=cmd, text=cmd, prompt=cmd)
                    dispatched = True
                    break
                except Exception:
                    pass
        if not dispatched and len(actions_map) == 1:
            only_act = list(actions_map.keys())[0]
            sname, scls, act_fn = actions_map[only_act]
            try:
                _dispatch_action(act_fn, scls, message=cmd, user_input=cmd, text=cmd, prompt=cmd)
            except Exception:
                pass
