"""
shadcn/ui-inspired components for PyDataUI.
Uses Tailwind CSS utility classes matching the shadcn/ui design system.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from .base import Component
from ..utils import escape_html, generate_id


class ShadButton(Component):
    """shadcn/ui Button — Tailwind-styled button with variant + size."""
    tag = 'button'

    VARIANT_CLASSES = {
        'default':     'bg-primary text-primary-foreground hover:bg-primary/90',
        'destructive': 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        'outline':     'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        'secondary':   'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        'ghost':       'hover:bg-accent hover:text-accent-foreground',
        'link':        'text-primary underline-offset-4 hover:underline',
    }
    SIZE_CLASSES = {
        'default': 'h-10 px-4 py-2',
        'sm':      'h-9 rounded-md px-3',
        'lg':      'h-11 rounded-md px-8',
        'icon':    'h-10 w-10',
    }
    BASE = ('inline-flex items-center justify-center whitespace-nowrap rounded-md '
            'text-sm font-medium ring-offset-background transition-colors '
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring '
            'focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50')

    def __init__(self, *children, variant: str = 'default', size: str = 'default',
                 full_width: bool = False, **kwargs):
        super().__init__(*children, **kwargs)
        self.variant = variant
        self.size = size
        self.full_width = full_width

    def _get_classes(self) -> List[str]:
        classes = [self.BASE,
                   self.VARIANT_CLASSES.get(self.variant, self.VARIANT_CLASSES['default']),
                   self.SIZE_CLASSES.get(self.size, self.SIZE_CLASSES['default'])]
        if self.full_width:
            classes.append('w-full')
        return classes


class ShadCard(Component):
    """shadcn/ui Card container."""
    tag = 'div'

    def _get_classes(self) -> List[str]:
        return ['rounded-lg border bg-card text-card-foreground shadow-sm']


class ShadCardHeader(Component):
    tag = 'div'
    def _get_classes(self): return ['flex flex-col space-y-1.5 p-6']


class ShadCardTitle(Component):
    tag = 'h3'
    def _get_classes(self): return ['font-semibold leading-none tracking-tight']


class ShadCardDescription(Component):
    tag = 'p'
    def _get_classes(self): return ['text-sm text-muted-foreground']


class ShadCardContent(Component):
    tag = 'div'
    def _get_classes(self): return ['p-6 pt-0']


class ShadCardFooter(Component):
    tag = 'div'
    def _get_classes(self): return ['flex items-center p-6 pt-0']


class ShadInput(Component):
    """shadcn/ui Input."""
    tag = 'input'

    def __init__(self, *args, type='text', placeholder='', value=None, name=None, bind=None, required=False, disabled=False, readonly=False, **props):
        if bind is None:
            bind = props.pop('bind', None)
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    name = self.bind.field_name
                if value is None:
                    value = self.bind
        if args and name is None:
            name = str(args[0]).lower().strip().replace(' ', '_')
        super().__init__(**props)
        self.props['type'] = type
        self.props['placeholder'] = placeholder
        if value is not None: self.props['value'] = value
        if name is not None: self.props['name'] = name
        if required: self.props['required'] = 'required'
        if disabled: self.props['disabled'] = 'disabled'
        if readonly: self.props['readonly'] = 'readonly'

    def _get_classes(self) -> List[str]:
        return [('flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm '
                 'ring-offset-background placeholder:text-muted-foreground '
                 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring '
                 'focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50')]


class ShadBadge(Component):
    """shadcn/ui Badge."""
    tag = 'div'

    VARIANT_CLASSES = {
        'default':     'border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80',
        'secondary':   'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
        'destructive': 'border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80',
        'outline':     'text-foreground',
    }
    BASE = 'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors'

    def __init__(self, *children, variant: str = 'default', **kwargs):
        super().__init__(*children, **kwargs)
        self.variant = variant

    def _get_classes(self) -> List[str]:
        return [self.BASE, self.VARIANT_CLASSES.get(self.variant, self.VARIANT_CLASSES['default'])]


class ShadAlert(Component):
    """shadcn/ui Alert."""
    tag = 'div'

    VARIANT_CLASSES = {
        'default':     'bg-background text-foreground',
        'destructive': 'border-destructive/50 text-destructive dark:border-destructive',
    }

    def __init__(self, *children, variant: str = 'default', **kwargs):
        super().__init__(*children, **kwargs)
        self.variant = variant
        self.props['role'] = 'alert'

    def _get_classes(self) -> List[str]:
        return ['relative w-full rounded-lg border p-4',
                self.VARIANT_CLASSES.get(self.variant, self.VARIANT_CLASSES['default'])]


class ShadSeparator(Component):
    """shadcn/ui Separator."""
    tag = 'div'

    def __init__(self, orientation: str = 'horizontal', **kwargs):
        super().__init__(**kwargs)
        self.orientation = orientation

    def _get_classes(self) -> List[str]:
        size = 'h-[1px] w-full' if self.orientation == 'horizontal' else 'h-full w-[1px]'
        return ['shrink-0 bg-border', size]


class ShadProgress(Component):
    """shadcn/ui Progress bar."""
    tag = 'div'

    def __init__(self, value: int = 0, max_val: int = 100, **kwargs):
        super().__init__(**kwargs)
        self.value = value
        self.max_val = max_val

    def render(self, state_snapshot=None) -> str:
        pct = 0 if self.max_val == 0 else (self.value / self.max_val) * 100
        uid = self.id
        return (f'<div id="{uid}" class="relative h-4 w-full overflow-hidden rounded-full bg-secondary" '
                f'role="progressbar" aria-valuemin="0" aria-valuemax="{self.max_val}" aria-valuenow="{self.value}">'
                f'<div class="h-full w-full flex-1 bg-primary transition-all" '
                f'style="transform: translateX(-{100 - pct:.1f}%)"></div>'
                f'</div>')


class ShadSkeleton(Component):
    """shadcn/ui Skeleton loading placeholder."""
    tag = 'div'
    def _get_classes(self): return ['animate-pulse rounded-md bg-muted']


class ShadSwitch(Component):
    """shadcn/ui Toggle Switch."""
    tag = 'div'

    def __init__(self, checked: bool = False, name: Optional[str] = None, bind: Optional[Any] = None, on_change: Optional[Any] = None, disabled: bool = False, label: Optional[str] = None, **kwargs):
        if bind is None:
            bind = kwargs.pop('bind', None)
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    name = self.bind.field_name
                checked = self.bind
        if name is None and label:
            name = str(label).lower().strip().replace(' ', '_')
        super().__init__(**kwargs)
        self.checked = checked
        self.name = name
        self.on_change = on_change
        self.disabled = disabled
        self.label = label

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        is_chk = bool(self._resolve_value(self.checked, snap))
        bg = 'bg-primary' if is_chk else 'bg-input'
        tx = 'translate-x-5' if is_chk else 'translate-x-0'
        state = 'checked' if is_chk else 'unchecked'
        
        btn_attrs = []
        if self.disabled:
            btn_attrs.append('disabled="disabled"')
        if self.on_change:
            htmx = self._get_event_htmx_attrs('on_click', self.on_change)
            for k, v in htmx.items():
                btn_attrs.append(f'{k}="{escape_html(str(v))}"')

        hidden_inp = ""
        if self.name:
            v_val = "true" if is_chk else "false"
            hidden_inp = f'<input type="hidden" name="{escape_html(self.name)}" value="{v_val}" />'

        lbl_html = f'<span class="text-sm font-medium leading-none">{escape_html(self.label)}</span>' if self.label else ""
        
        return (
            f'<div id="{self.id}" class="inline-flex items-center gap-2">'
            f'{hidden_inp}'
            f'<button type="button" role="switch" aria-checked="{str(is_chk).lower()}" data-state="{state}" '
            f'class="peer inline-flex h-[24px] w-[44px] shrink-0 cursor-pointer items-center '
            f'rounded-full border-2 border-transparent transition-colors '
            f'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring '
            f'focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 {bg}" '
            f'{" ".join(btn_attrs)}>'
            f'<span data-state="{state}" class="pointer-events-none block h-5 w-5 rounded-full '
            f'bg-background shadow-lg ring-0 transition-transform {tx}"></span>'
            f'</button>'
            f'{lbl_html}'
            f'</div>'
        )


class ShadCheckbox(Component):
    """shadcn/ui Checkbox component."""
    tag = 'label'

    def __init__(self, label: str = '', checked: bool = False, name: Optional[str] = None, bind: Optional[Any] = None, disabled: bool = False, on_change: Optional[Any] = None, **kwargs):
        if bind is None:
            bind = kwargs.pop('bind', None)
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    name = self.bind.field_name
                checked = self.bind
        if name is None and label:
            name = str(label).lower().strip().replace(' ', '_')
        super().__init__(**kwargs)
        self.label = label
        self.checked = checked
        self.name = name
        self.disabled = disabled
        self.on_change = on_change

    def _get_classes(self) -> List[str]:
        return ['inline-flex items-center gap-2 cursor-pointer select-none']

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        is_chk = bool(self._resolve_value(self.checked, snap))
        attrs = self._build_attrs(snap)
        
        inp_attrs = [
            'type="checkbox"',
            'class="peer h-4 w-4 shrink-0 rounded-sm border border-primary ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-primary accent-primary"'
        ]
        if self.name:
            inp_attrs.append(f'name="{escape_html(self.name)}"')
        if is_chk:
            inp_attrs.append('checked="checked"')
        if self.disabled:
            inp_attrs.append('disabled="disabled"')
        if self.on_change:
            inp_attrs.append('hx-trigger="change"')
            inp_attrs.append('hx-include="this"')
            htmx = self._get_event_htmx_attrs('on_change', self.on_change)
            for k, v in htmx.items():
                inp_attrs.append(f'{k}="{escape_html(str(v))}"')

        lbl_html = f'<span class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">{escape_html(self.label)}</span>' if self.label else ""
        return f'<{self.tag} {attrs}><input {" ".join(inp_attrs)}/>{lbl_html}</{self.tag}>'


class ShadTable(Component):
    """shadcn/ui Table wrapper."""
    tag = 'div'

    def _get_classes(self): return ['relative w-full overflow-auto']

    def render(self, state_snapshot=None) -> str:
        children_html = self._render_children(state_snapshot or {})
        return (f'<div id="{self.id}" class="relative w-full overflow-auto">'
                f'<table class="w-full caption-bottom text-sm">{children_html}</table>'
                f'</div>')


class ShadSelect(Component):
    """shadcn/ui Select (native styled select)."""
    tag = 'select'

    def __init__(self, *args, options=None, value=None, placeholder='Select an option...', name=None, bind=None, required=False, disabled=False, on_change=None, **kwargs):
        if bind is None:
            bind = kwargs.pop('bind', None)
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    name = self.bind.field_name
                if value is None:
                    value = self.bind
        if args and name is None:
            name = str(args[0]).lower().strip().replace(' ', '_')
        super().__init__(**kwargs)
        self.options = options or []
        self.value = value
        self.placeholder = placeholder
        if name: self.props['name'] = name
        if required: self.props['required'] = 'required'
        if disabled: self.props['disabled'] = 'disabled'
        if on_change:
            self._event_props['on_change'] = on_change
            self.props['hx-trigger'] = 'change'
            self.props['hx-include'] = 'this'

    def _get_classes(self) -> List[str]:
        return [('flex h-10 w-full items-center justify-between rounded-md border border-input '
                 'bg-background px-3 py-2 text-sm ring-offset-background '
                 'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 '
                 'disabled:cursor-not-allowed disabled:opacity-50')]

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        attrs = self._build_attrs(snap)
        selected_val = str(self._resolve_value(self.value, snap)) if self.value is not None else ""
        
        opts = []
        if self.placeholder:
            sel = 'selected' if not selected_val else ''
            opts.append(f'<option value="" disabled {sel}>{escape_html(self.placeholder)}</option>')

        for item in self.options:
            if isinstance(item, dict):
                val = str(item.get('value', ''))
                label = str(item.get('label', val))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                val = str(item[0])
                label = str(item[1])
            else:
                val = str(item)
                label = str(item)
            sel = 'selected' if val == selected_val else ''
            opts.append(f'<option value="{escape_html(val)}" {sel}>{escape_html(label)}</option>')

        return f'<{self.tag} {attrs}>{"".join(opts)}</{self.tag}>'


class ShadTextarea(Component):
    """shadcn/ui Textarea."""
    tag = 'textarea'

    def __init__(self, *args, placeholder='', value=None, name=None, bind=None, rows=4, required=False, disabled=False, readonly=False, **props):
        if bind is None:
            bind = props.pop('bind', None)
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    name = self.bind.field_name
                if value is None:
                    value = self.bind
        if args and name is None:
            name = str(args[0]).lower().strip().replace(' ', '_')
        super().__init__(**props)
        self.props['rows'] = rows
        self.props['placeholder'] = placeholder
        if value is not None: self.props['value'] = value
        if name is not None: self.props['name'] = name
        if required: self.props['required'] = 'required'
        if disabled: self.props['disabled'] = 'disabled'
        if readonly: self.props['readonly'] = 'readonly'

    def _get_classes(self) -> List[str]:
        return [('flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 '
                 'text-sm ring-offset-background placeholder:text-muted-foreground '
                 'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring '
                 'focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50')]


class ShadLabel(Component):
    """shadcn/ui Label."""
    tag = 'label'
    def _get_classes(self): return ['text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70']


class ShadDialog(Component):
    """shadcn/ui Dialog / Modal."""
    tag = 'div'

    def __init__(
        self,
        *children,
        open: bool = False,
        title: Optional[Any] = None,
        description: Optional[Any] = None,
        on_close: Optional[Any] = None,
        close_on_overlay: bool = True,
        **kwargs
    ):
        super().__init__(*children, **kwargs)
        self.open = open
        self.title = title
        self.description = description
        self.on_close = on_close
        self.close_on_overlay = close_on_overlay

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        is_open = bool(self._resolve_value(self.open, snap))
        if not is_open:
            return ''

        close_attrs_str = ""
        overlay_close_str = ""
        if self.on_close:
            htmx_close = self._get_event_htmx_attrs('on_click', self.on_close)
            close_attrs_str = " ".join(f'{k}="{v}"' for k, v in htmx_close.items())
            if self.close_on_overlay:
                overlay_close_str = close_attrs_str

        header_html = ""
        if self.title or self.description:
            t_html = f'<h2 class="text-lg font-semibold leading-none tracking-tight">{escape_html(str(self._resolve_value(self.title, snap)))}</h2>' if self.title else ''
            d_html = f'<p class="text-sm text-muted-foreground mt-1.5">{escape_html(str(self._resolve_value(self.description, snap)))}</p>' if self.description else ''
            header_html = f'<div class="flex flex-col space-y-1.5 text-center sm:text-left">{t_html}{d_html}</div>'

        close_btn = ""
        if self.on_close:
            close_btn = (
                f'<button type="button" class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none cursor-pointer" {close_attrs_str}>'
                f'<span class="text-xl leading-none font-bold">&times;</span>'
                f'<span class="sr-only">Close</span>'
                f'</button>'
            )

        children_html = self._render_children(snap)
        return (
            f'<div id="{self.id}" class="pdu-shad-dialog-wrapper fixed inset-0 z-50 flex items-center justify-center p-4">'
            f'<div class="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm transition-opacity" {overlay_close_str}></div>'
            f'<div class="relative z-50 grid w-full max-w-lg gap-4 border bg-background p-6 shadow-lg sm:rounded-lg">'
            f'{close_btn}'
            f'{header_html}'
            f'{children_html}'
            f'</div>'
            f'</div>'
        )


class ShadScrollArea(Component):
    """shadcn/ui ScrollArea."""
    tag = 'div'
    def _get_classes(self): return ['relative overflow-auto']


class ShadTabs(Component):
    """shadcn/ui Tabs list."""
    tag = 'div'
    def _get_classes(self): return ['inline-flex items-center justify-center rounded-md bg-muted p-1 text-muted-foreground']


class ShadToast(Component):
    """shadcn/ui Toast notification."""
    tag = 'div'
    def _get_classes(self): return [
        'group pointer-events-auto relative flex w-full items-center justify-between '
        'space-x-4 overflow-hidden rounded-md border p-6 pr-8 shadow-lg transition-all '
        'bg-background text-foreground'
    ]


class ShadAvatar(Component):
    """shadcn/ui Avatar."""
    tag = 'span'
    def _get_classes(self): return ['relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full']


class ShadHoverCard(Component):
    """shadcn/ui HoverCard."""
    tag = 'div'
    def _get_classes(self): return ['z-50 w-64 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none']


class ShadAccordion(Component):
    """shadcn/ui Accordion item."""
    tag = 'div'
    def _get_classes(self): return ['border-b']


class ShadSheet(Component):
    """shadcn/ui Sheet (side drawer)."""
    tag = 'div'

    SIDE_CLASSES = {
        'top':    'inset-x-0 top-0 border-b',
        'bottom': 'inset-x-0 bottom-0 border-t',
        'left':   'inset-y-0 left-0 h-full w-3/4 border-r sm:max-w-sm',
        'right':  'inset-y-0 right-0 h-full w-3/4 border-l sm:max-w-sm',
    }

    def __init__(
        self,
        *children,
        open: bool = False,
        side: str = 'right',
        title: Optional[Any] = None,
        on_close: Optional[Any] = None,
        close_on_overlay: bool = True,
        **kwargs
    ):
        super().__init__(*children, **kwargs)
        self.open = open
        self.side = side
        self.title = title
        self.on_close = on_close
        self.close_on_overlay = close_on_overlay

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        is_open = bool(self._resolve_value(self.open, snap))
        if not is_open:
            return ''

        close_attrs_str = ""
        overlay_close_str = ""
        if self.on_close:
            htmx_close = self._get_event_htmx_attrs('on_click', self.on_close)
            close_attrs_str = " ".join(f'{k}="{v}"' for k, v in htmx_close.items())
            if self.close_on_overlay:
                overlay_close_str = close_attrs_str

        close_btn = ""
        if self.on_close:
            close_btn = (
                f'<button type="button" class="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 cursor-pointer" {close_attrs_str}>'
                f'<span class="text-xl leading-none font-bold">&times;</span>'
                f'</button>'
            )

        header_html = ""
        if self.title:
            header_html = f'<div class="flex flex-col space-y-2 text-center sm:text-left mb-4"><h3 class="text-lg font-semibold">{escape_html(str(self._resolve_value(self.title, snap)))}</h3></div>'

        children_html = self._render_children(snap)
        side_cls = self.SIDE_CLASSES.get(self.side, self.SIDE_CLASSES['right'])
        return (
            f'<div id="{self.id}" class="pdu-shad-sheet-wrapper fixed inset-0 z-50">'
            f'<div class="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm" {overlay_close_str}></div>'
            f'<div class="fixed z-50 gap-4 bg-background p-6 shadow-lg transition ease-in-out {side_cls}">'
            f'{close_btn}'
            f'{header_html}'
            f'{children_html}'
            f'</div>'
            f'</div>'
        )


# ============================================================================
# Lucide Icons & SVG Rendering Helper
# ============================================================================

LUCIDE_ICONS: Dict[str, str] = {
    'layout-dashboard': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    'dashboard': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/></svg>',
    'box': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    'package': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>',
    'sparkles': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/></svg>',
    'activity': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>',
    'shield-check': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/></svg>',
    'cpu': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/><path d="M15 2v2"/><path d="M15 20v2"/><path d="M2 15h2"/><path d="M2 9h2"/><path d="M20 15h2"/><path d="M20 9h2"/><path d="M9 2v2"/><path d="M9 20v2"/></svg>',
    'database': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>',
    'terminal': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 17 10 11 4 5"/><line x1="12" x2="20" y1="19" y2="19"/></svg>',
    'settings': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>',
    'user': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>',
    'users': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>',
    'bell': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>',
    'search': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    'chevron-down': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m6 9 6 6 6-6"/></svg>',
    'chevron-right': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m9 18 6-6-6-6"/></svg>',
    'chevron-left': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>',
    'chevron-up': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m18 15-6-6-6 6"/></svg>',
    'menu': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>',
    'check': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    'x': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>',
    'panel-left': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M9 3v18"/></svg>',
    'external-link': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></svg>',
    'sliders': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="4" y1="21" y2="14"/><line x1="4" x2="4" y1="10" y2="3"/><line x1="12" x2="12" y1="21" y2="12"/><line x1="12" x2="12" y1="8" y2="3"/><line x1="20" x2="20" y1="21" y2="16"/><line x1="20" x2="20" y1="12" y2="3"/><line x1="1" x2="7" y1="14" y2="14"/><line x1="9" x2="15" y1="8" y2="8"/><line x1="17" x2="23" y1="16" y2="16"/></svg>',
    'calendar': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 2v4"/><path d="M16 2v4"/><rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg>',
}


def _render_icon(icon: Any, size: int = 16, class_name: str = "") -> str:
    """Renders a Lucide icon SVG, an Icon component, an inline SVG, or an emoji."""
    if not icon:
        return ""
    if isinstance(icon, Component):
        return icon.render({})
    s_icon = str(icon).strip()
    if s_icon.startswith("<svg"):
        return s_icon
    svg = LUCIDE_ICONS.get(s_icon.lower())
    if svg:
        if size != 16:
            svg = svg.replace('width="16"', f'width="{size}"').replace('height="16"', f'height="{size}"')
        if class_name:
            svg = svg.replace('<svg ', f'<svg class="{class_name}" ')
        return svg
    cls_attr = f' class="{class_name}"' if class_name else ''
    return f'<span{cls_attr}>{escape_html(s_icon)}</span>'


# ============================================================================
# Phase 1: Modern Sidebar System & Responsive Dashboard Shell
# ============================================================================

class ShadSidebarProvider(Component):
    """
    Context provider managing open, collapsed, and mobile drawer state for ShadSidebar.
    Supports keyboard shortcuts (Cmd+B / Ctrl+B) and localStorage state retention.
    """
    tag = 'div'

    def __init__(self, *children, default_open: bool = True, collapsible: str = 'icon', **kwargs):
        super().__init__(*children, **kwargs)
        self.default_open = default_open
        self.collapsible = collapsible

    def _get_classes(self) -> List[str]:
        return ['pdu-sidebar-provider', 'min-h-screen', 'w-full', 'flex', 'bg-background', 'text-foreground']

    def render(self, state_snapshot=None) -> str:
        state_str = 'expanded' if self.default_open else 'collapsed'
        self.props['data-sidebar-provider'] = 'true'
        self.props['data-state'] = state_str
        self.props['data-collapsible'] = self.collapsible
        return super().render(state_snapshot)


class ShadSidebar(Component):
    """
    shadcn/ui Sidebar shell (<aside>) with collapsible icon/offcanvas modes
    and responsive slide-over sheet behavior on mobile devices.
    """
    tag = 'aside'

    def __init__(self, *children, collapsible: str = 'icon', side: str = 'left', **kwargs):
        super().__init__(*children, **kwargs)
        self.collapsible = collapsible
        self.side = side

    def _get_classes(self) -> List[str]:
        return [
            'pdu-sidebar', 'group/sidebar', 'relative', 'flex', 'flex-col',
            'border-r', 'bg-card', 'border-border', 'text-foreground',
            'transition-all', 'duration-300', 'ease-in-out',
            'md:relative', 'fixed', 'inset-y-0', 'left-0', 'z-40',
            '-translate-x-full', 'md:translate-x-0',
            'w-64', 'data-[state=collapsed]:w-16',
            'data-[mobile-open=true]:translate-x-0',
            'data-[mobile-open=true]:shadow-2xl'
        ]

    def render(self, state_snapshot=None) -> str:
        self.props['data-collapsible'] = self.collapsible
        self.props['data-side'] = self.side
        aside_html = super().render(state_snapshot)
        # Mobile backdrop overlay
        backdrop = (
            '<div class="pdu-sidebar-backdrop fixed inset-0 z-30 bg-background/80 backdrop-blur-sm hidden md:hidden" '
            'data-pdu-sidebar-backdrop="true"></div>'
        )
        return f'{aside_html}\n{backdrop}'


class ShadSidebarHeader(Component):
    """Top header section of ShadSidebar, typically housing organization branding or team switcher."""
    tag = 'div'

    def _get_classes(self) -> List[str]:
        return ['flex', 'h-14', 'items-center', 'gap-2', 'border-b', 'border-border', 'px-4', 'font-semibold', 'shrink-0']


class ShadSidebarContent(Component):
    """Scrollable main body of ShadSidebar containing navigation groups and menu items."""
    tag = 'div'

    def _get_classes(self) -> List[str]:
        return ['flex-1', 'overflow-y-auto', 'px-3', 'py-3', 'space-y-4']


class ShadSidebarGroup(Component):
    """Container grouping related navigation links with an optional section label."""
    tag = 'div'

    def _get_classes(self) -> List[str]:
        return ['relative', 'flex', 'flex-col', 'gap-1']


class ShadSidebarGroupLabel(Component):
    """Header / title for a ShadSidebarGroup."""
    tag = 'div'

    def _get_classes(self) -> List[str]:
        return [
            'px-2', 'py-1.5', 'text-xs', 'font-semibold', 'text-muted-foreground',
            'uppercase', 'tracking-wider', 'group-data-[state=collapsed]/sidebar:hidden'
        ]


class ShadSidebarMenu(Component):
    """Navigation list container (<ul>) for menu items."""
    tag = 'ul'

    def _get_classes(self) -> List[str]:
        return ['flex', 'flex-col', 'gap-1', 'list-none', 'p-0', 'm-0']


class ShadSidebarMenuItem(Component):
    """Individual item wrapper (<li>) within a ShadSidebarMenu."""
    tag = 'li'

    def _get_classes(self) -> List[str]:
        return ['group/item', 'relative', 'list-none']


class ShadSidebarMenuButton(Component):
    """
    Interactive navigation link or button with Lucide icon, label, and active highlight.
    In icon-collapsed mode, label and badge hide smoothly while icon remains centered.
    """
    def __init__(self, *children, icon: Any = None, active: bool = False,
                 badge: Optional[str] = None, href: Optional[str] = None, **kwargs):
        super().__init__(*children, **kwargs)
        self.icon = icon
        self.active = active
        self.badge = badge
        self.href = href
        self.tag = 'a' if href else 'button'
        if href:
            self.props['href'] = href
        else:
            self.props.setdefault('type', 'button')

    def _get_classes(self) -> List[str]:
        classes = [
            'flex', 'w-full', 'items-center', 'gap-3', 'rounded-md', 'px-3', 'py-2',
            'text-sm', 'font-medium', 'transition-colors',
            'hover:bg-accent', 'hover:text-accent-foreground', 'disabled:opacity-50',
            'group-data-[state=collapsed]/sidebar:justify-center'
        ]
        if self.active:
            classes.extend(['bg-accent', 'text-accent-foreground', 'font-semibold'])
        else:
            classes.append('text-muted-foreground')
        return classes

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        icon_html = _render_icon(self.icon, size=18, class_name="shrink-0") if self.icon else ""
        children_html = self._render_children(snap)
        label_html = f'<span class="truncate group-data-[state=collapsed]/sidebar:hidden">{children_html}</span>'
        badge_html = ""
        if self.badge:
            badge_html = (
                f'<span class="ml-auto text-xs font-semibold px-2 py-0.5 rounded-full bg-muted text-muted-foreground '
                f'group-data-[state=collapsed]/sidebar:hidden">{escape_html(str(self.badge))}</span>'
            )
        attrs = self._build_attrs(snap)
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{icon_html}{label_html}{badge_html}</{self.tag}>'


class ShadSidebarFooter(Component):
    """Bottom footer section of ShadSidebar for user profile snippets, plans, or settings."""
    tag = 'div'

    def _get_classes(self) -> List[str]:
        return ['mt-auto', 'border-t', 'border-border', 'p-3', 'shrink-0']


class ShadSidebarRail(Component):
    """Subtle edge rail handle allowing mouse drag or hover expansion of the sidebar."""
    tag = 'button'

    def __init__(self, **kwargs):
        kwargs.setdefault('aria_label', 'Toggle Sidebar')
        super().__init__(**kwargs)
        self.props['data-pdu-sidebar-rail'] = 'true'
        self.props['type'] = 'button'

    def _get_classes(self) -> List[str]:
        return [
            'absolute', 'inset-y-0', '-right-2', 'z-20', 'hidden', 'w-4',
            '-translate-x-1/2', 'transition-all', 'ease-linear',
            'after:absolute', 'after:inset-y-0', 'after:left-1/2', 'after:w-[2px]',
            'hover:after:bg-border', 'md:block', 'cursor-ew-resize',
            'opacity-0', 'hover:opacity-100'
        ]


class ShadSidebarTrigger(Component):
    """Button (panel-left icon) that toggles the sidebar expanded/collapsed state and mobile drawer."""
    tag = 'button'

    def __init__(self, *children, **kwargs):
        kwargs.setdefault('aria_label', 'Toggle Sidebar')
        kwargs.setdefault('type', 'button')
        super().__init__(*children, **kwargs)
        self.props['data-pdu-sidebar-trigger'] = 'true'

    def _get_classes(self) -> List[str]:
        return [
            'inline-flex', 'h-8', 'w-8', 'items-center', 'justify-center', 'rounded-md',
            'border', 'border-input', 'bg-background', 'hover:bg-accent', 'hover:text-accent-foreground',
            'text-sm', 'font-medium', 'transition-colors', 'cursor-pointer'
        ]

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        if not self.children:
            icon_svg = _render_icon('panel-left', size=16)
            attrs = self._build_attrs(snap)
            attrs_str = f' {attrs}' if attrs else ''
            return f'<{self.tag}{attrs_str}>{icon_svg}</{self.tag}>'
        return super().render(snap)


# ============================================================================
# High-Level Composable Dashboard Helpers (Data/AI Friendly)
# ============================================================================

class NavItem:
    """Declarative specification for an individual navigation item."""
    def __init__(self, label: str, icon: Any = None, href: str = "/",
                 active: bool = False, badge: Optional[str] = None, on_click: Any = None):
        self.label = label
        self.icon = icon
        self.href = href
        self.active = active
        self.badge = badge
        self.on_click = on_click

    def to_component(self) -> ShadSidebarMenuItem:
        props = {}
        if self.on_click:
            props['on_click'] = self.on_click
        return ShadSidebarMenuItem(
            ShadSidebarMenuButton(
                self.label,
                icon=self.icon,
                href=self.href,
                active=self.active,
                badge=self.badge,
                **props
            )
        )


class NavGroup:
    """Declarative specification for a group of NavItems with a group title."""
    def __init__(self, title: str, items: List[NavItem]):
        self.title = title
        self.items = items

    def to_component(self) -> ShadSidebarGroup:
        menu_items = [it.to_component() for it in self.items]
        return ShadSidebarGroup(
            ShadSidebarGroupLabel(self.title),
            ShadSidebarMenu(*menu_items)
        )


def Sidebar(brand: Optional[Dict[str, Any]] = None,
            groups: Optional[List[NavGroup]] = None,
            footer: Optional[Dict[str, Any]] = None,
            collapsible: str = "icon",
            **kwargs) -> ShadSidebar:
    """
    High-level declarative constructor for a complete shadcn Sidebar.
    Accepts pure Python dictionaries and NavGroups — zero HTML or JS required.
    """
    children = []

    # 1. Brand Header
    if brand:
        logo_icon = _render_icon(brand.get('logo', 'cpu'), size=20, class_name="text-primary")
        brand_name = escape_html(brand.get('name', 'PyDataUI App'))
        plan_badge = brand.get('plan')
        badge_html = (
            f'<span class="ml-auto text-[10px] font-semibold uppercase px-1.5 py-0.5 rounded bg-primary/10 text-primary '
            f'group-data-[state=collapsed]/sidebar:hidden">{escape_html(str(plan_badge))}</span>'
            if plan_badge else ''
        )
        brand_html = (
            f'<div class="flex items-center gap-2 w-full overflow-hidden">'
            f'<div class="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">{logo_icon}</div>'
            f'<div class="flex flex-col truncate group-data-[state=collapsed]/sidebar:hidden">'
            f'<span class="text-sm font-semibold tracking-tight">{brand_name}</span>'
            f'</div>'
            f'{badge_html}'
            f'</div>'
        )
        children.append(ShadSidebarHeader(brand_html))

    # 2. Content & Nav Groups
    if groups:
        group_comps = [g.to_component() for g in groups]
        children.append(ShadSidebarContent(*group_comps))

    # 3. User Footer
    if footer:
        name = escape_html(footer.get('name', 'User'))
        email = escape_html(footer.get('email', ''))
        avatar_txt = escape_html(footer.get('avatar', name[:2].upper()))
        footer_html = (
            f'<div class="flex items-center gap-3 w-full overflow-hidden">'
            f'<div class="flex h-9 w-9 items-center justify-center rounded-full bg-muted font-semibold text-xs text-muted-foreground shrink-0">{avatar_txt}</div>'
            f'<div class="flex flex-col truncate group-data-[state=collapsed]/sidebar:hidden">'
            f'<span class="text-sm font-medium leading-none">{name}</span>'
            f'<span class="text-xs text-muted-foreground truncate">{email}</span>'
            f'</div>'
            f'</div>'
        )
        children.append(ShadSidebarFooter(footer_html))

    # 4. Rail handle
    children.append(ShadSidebarRail())

    return ShadSidebar(*children, collapsible=collapsible, **kwargs)


class Header(Component):
    """
    Sticky top header bar for dashboards. Includes sidebar trigger, breadcrumbs,
    optional search/Cmd+K spotlight trigger, actions, theme toggle, and user profile.
    """
    tag = 'header'

    def __init__(self, *children, breadcrumbs: Optional[List[Any]] = None,
                 search: bool = True, actions: Optional[List[Any]] = None,
                 user: Optional[Dict[str, Any]] = None, theme_toggle: bool = True,
                 title: Optional[str] = None, **kwargs):
        super().__init__(*children, **kwargs)
        self.breadcrumbs = breadcrumbs or []
        self.search = search
        self.actions = actions or []
        self.user = user
        self.theme_toggle = theme_toggle
        self.header_title = title

    def _get_classes(self) -> List[str]:
        return [
            'sticky', 'top-0', 'z-20', 'flex', 'h-14', 'items-center', 'gap-4',
            'border-b', 'border-border', 'bg-background/95', 'px-6',
            'backdrop-blur', 'supports-[backdrop-filter]:bg-background/60'
        ]

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        # Left Section: Sidebar Trigger & Breadcrumbs
        left_items = [ShadSidebarTrigger().render(snap)]
        left_items.append('<div class="h-4 w-px bg-border"></div>')

        if self.header_title:
            left_items.append(f'<span class="font-semibold text-sm">{escape_html(self.header_title)}</span>')
        elif self.breadcrumbs:
            crumb_items = []
            for idx, crumb in enumerate(self.breadcrumbs):
                is_last = (idx == len(self.breadcrumbs) - 1)
                if isinstance(crumb, (list, tuple)):
                    label, href = crumb[0], crumb[1]
                else:
                    label, href = str(crumb), "#"
                if is_last:
                    crumb_items.append(
                        f'<li class="inline-flex items-center gap-1.5 list-none">'
                        f'<span class="font-medium text-foreground text-sm" aria-current="page">{escape_html(label)}</span>'
                        f'</li>'
                    )
                else:
                    crumb_items.append(
                        f'<li class="inline-flex items-center gap-1.5 list-none">'
                        f'<a href="{escape_html(href)}" class="text-sm text-muted-foreground hover:text-foreground transition-colors">{escape_html(label)}</a>'
                        f'<span class="text-muted-foreground/60 select-none">/</span>'
                        f'</li>'
                    )
            left_items.append(
                f'<nav aria-label="breadcrumb"><ol class="flex items-center gap-1.5 m-0 p-0">{"".join(crumb_items)}</ol></nav>'
            )

        left_html = f'<div class="flex items-center gap-3">{"".join(left_items)}</div>'

        # Right Section: Search / Cmd+K, Actions, Theme Toggle, User
        right_items = []
        if self.search:
            search_icon = _render_icon('search', size=14, class_name="text-muted-foreground")
            right_items.append(
                f'<button type="button" class="hidden sm:inline-flex items-center gap-2 rounded-md border border-input bg-muted/40 px-3 py-1.5 text-xs text-muted-foreground hover:bg-muted transition-colors cursor-pointer" data-pdu-command-trigger="true">'
                f'{search_icon}'
                f'<span>Search documentation & actions...</span>'
                f'<kbd class="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-background px-1.5 font-mono text-[10px] font-medium text-muted-foreground opacity-100">⌘K</kbd>'
                f'</button>'
            )

        for act in self.actions:
            if isinstance(act, Component):
                right_items.append(act.render(snap))
            else:
                right_items.append(str(act))

        if self.theme_toggle:
            right_items.append(
                '<button type="button" class="inline-flex h-8 w-8 items-center justify-center rounded-md border border-input bg-background hover:bg-accent text-sm font-medium transition-colors cursor-pointer" onclick="document.documentElement.classList.toggle(\'dark\')" aria-label="Toggle Theme">'
                '<span class="dark:hidden">🌙</span><span class="hidden dark:inline">☀️</span>'
                '</button>'
            )

        if self.user:
            avatar = escape_html(self.user.get('avatar', 'U'))
            right_items.append(
                f'<div class="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary font-semibold text-xs border border-primary/20">{avatar}</div>'
            )

        # Children
        children_html = self._render_children(snap)
        if children_html:
            right_items.append(children_html)

        right_html = f'<div class="ml-auto flex items-center gap-3">{"".join(right_items)}</div>'
        attrs = self._build_attrs(snap)
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{left_html}{right_html}</{self.tag}>'


class DashboardLayout(Component):
    """
    High-level responsive dashboard shell. Arranges ShadSidebar on the left
    and Header + main content scroll area on the right with full mobile drawer support.
    """
    tag = 'div'

    def __init__(self, *children, sidebar: Optional[Any] = None,
                 header: Optional[Any] = None, content: Optional[List[Any]] = None,
                 collapsible: str = "icon", **kwargs):
        all_children = list(children)
        if content:
            all_children.extend(content)
        super().__init__(*all_children, **kwargs)
        self.sidebar_comp = sidebar
        self.header_comp = header
        self.collapsible = collapsible

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        sidebar_html = self.sidebar_comp.render(snap) if self.sidebar_comp else ""
        header_html = self.header_comp.render(snap) if self.header_comp else ""
        children_html = self._render_children(snap)

        main_html = (
            f'<div class="flex flex-col flex-1 min-w-0 h-screen overflow-hidden">'
            f'{header_html}'
            f'<main class="flex-1 overflow-y-auto p-6 space-y-6">{children_html}</main>'
            f'</div>'
        )

        provider = ShadSidebarProvider(default_open=True, collapsible=self.collapsible)
        provider.children = [Component(children=[sidebar_html, main_html], tag='div', class_name="flex flex-1 w-full")]
        return provider.render(snap)


# ============================================================================
# Phase 2: Overlays, Menus & Dialogs (Zero Node / NPM)
# ============================================================================

class ShadBreadcrumb(Component):
    """Accessible hierarchical breadcrumb navigation wrapper."""
    tag = 'nav'
    def __init__(self, *children, **kwargs):
        kwargs.setdefault('aria_label', 'breadcrumb')
        super().__init__(*children, **kwargs)


class ShadBreadcrumbList(Component):
    tag = 'ol'
    def _get_classes(self):
        return ['flex', 'flex-wrap', 'items-center', 'gap-1.5', 'break-words', 'text-sm', 'text-muted-foreground', 'list-none', 'p-0', 'm-0']


class ShadBreadcrumbItem(Component):
    tag = 'li'
    def _get_classes(self):
        return ['inline-flex', 'items-center', 'gap-1.5', 'list-none']


class ShadBreadcrumbLink(Component):
    tag = 'a'
    def __init__(self, *children, href: str = '#', **kwargs):
        super().__init__(*children, **kwargs)
        self.props['href'] = href
    def _get_classes(self):
        return ['transition-colors', 'hover:text-foreground', 'text-muted-foreground']


class ShadBreadcrumbPage(Component):
    tag = 'span'
    def __init__(self, *children, **kwargs):
        kwargs.setdefault('aria_current', 'page')
        super().__init__(*children, **kwargs)
    def _get_classes(self):
        return ['font-normal', 'text-foreground']


class ShadBreadcrumbSeparator(Component):
    tag = 'span'
    def __init__(self, *children, **kwargs):
        kwargs.setdefault('role', 'presentation')
        kwargs.setdefault('aria_hidden', 'true')
        super().__init__(*children, **kwargs)
    def _get_classes(self):
        return ['text-muted-foreground/60', 'select-none']
    def render(self, state_snapshot=None) -> str:
        if not self.children:
            self.children = ['/']
        return super().render(state_snapshot)


class ShadDropdownMenu(Component):
    """
    shadcn DropdownMenu container. Wraps trigger button and floating menu card.
    Features click-outside auto-dismiss and keyboard Esc dismiss via pdu-bridge.js.
    """
    tag = 'div'

    def __init__(self, *children, trigger: Optional[Any] = None,
                 content: Optional[Any] = None, **kwargs):
        super().__init__(*children, **kwargs)
        self.trigger = trigger
        self.dropdown_content = content
        self.props['data-pdu-dropdown'] = 'true'

    def _get_classes(self) -> List[str]:
        return ['relative', 'inline-block', 'text-left']

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        trig_html = ""
        if self.trigger:
            if isinstance(self.trigger, Component):
                self.trigger.props['data-pdu-dropdown-trigger'] = 'true'
                trig_html = self.trigger.render(snap)
            else:
                trig_html = f'<button type="button" data-pdu-dropdown-trigger="true" class="cursor-pointer">{self.trigger}</button>'

        cont_html = ""
        if self.dropdown_content:
            if isinstance(self.dropdown_content, Component):
                cont_html = self.dropdown_content.render(snap)
            elif isinstance(self.dropdown_content, (list, tuple)):
                items = "".join(it.render(snap) if isinstance(it, Component) else str(it) for it in self.dropdown_content)
                cont_html = f'<div class="pdu-dropdown-content absolute right-0 z-50 mt-2 min-w-[12rem] overflow-hidden rounded-md border border-border bg-popover p-1 text-popover-foreground shadow-md transition-all hidden data-[open=true]:block animate-in fade-in-0 zoom-in-95">{items}</div>'
            else:
                cont_html = str(self.dropdown_content)

        children_html = self._render_children(snap)
        attrs = self._build_attrs(snap)
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{trig_html}{cont_html}{children_html}</{self.tag}>'


class ShadDropdownItem(Component):
    """Interactive item inside a ShadDropdownMenu supporting icon, label, and keyboard shortcut."""
    def __init__(self, *children, icon: Any = None, shortcut: Optional[str] = None,
                 danger: bool = False, href: Optional[str] = None, **kwargs):
        super().__init__(*children, **kwargs)
        self.icon = icon
        self.shortcut = shortcut
        self.danger = danger
        self.href = href
        self.tag = 'a' if href else 'div'
        if href:
            self.props['href'] = href
        else:
            self.props.setdefault('role', 'menuitem')

    def _get_classes(self) -> List[str]:
        classes = [
            'relative', 'flex', 'cursor-pointer', 'select-none', 'items-center', 'gap-2',
            'rounded-sm', 'px-2', 'py-1.5', 'text-sm', 'outline-none', 'transition-colors',
            'hover:bg-accent', 'hover:text-accent-foreground',
            'data-[disabled=true]:pointer-events-none', 'data-[disabled=true]:opacity-50'
        ]
        if self.danger:
            classes.extend(['text-destructive', 'hover:text-destructive', 'hover:bg-destructive/10'])
        return classes

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        icon_html = _render_icon(self.icon, size=14, class_name="shrink-0") if self.icon else ""
        children_html = self._render_children(snap)
        sc_html = f'<span class="ml-auto text-xs tracking-widest text-muted-foreground">{escape_html(self.shortcut)}</span>' if self.shortcut else ''
        attrs = self._build_attrs(snap)
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{icon_html}<span>{children_html}</span>{sc_html}</{self.tag}>'


class ShadDropdownSeparator(Component):
    tag = 'div'
    def _get_classes(self): return ['-mx-1', 'my-1', 'h-px', 'bg-muted']


class ShadDropdownLabel(Component):
    tag = 'div'
    def _get_classes(self): return ['px-2', 'py-1.5', 'text-xs', 'font-semibold', 'text-muted-foreground']


class ShadPopover(Component):
    """Click-triggered floating card anchored to a button with auto-alignment and dismiss."""
    tag = 'div'

    def __init__(self, *children, trigger: Optional[Any] = None,
                 content: Optional[Any] = None, **kwargs):
        super().__init__(*children, **kwargs)
        self.trigger = trigger
        self.popover_content = content
        self.props['data-pdu-popover'] = 'true'

    def _get_classes(self) -> List[str]:
        return ['relative', 'inline-block']

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        trig_html = ""
        if self.trigger:
            if isinstance(self.trigger, Component):
                self.trigger.props['data-pdu-popover-trigger'] = 'true'
                trig_html = self.trigger.render(snap)
            else:
                trig_html = f'<button type="button" data-pdu-popover-trigger="true">{self.trigger}</button>'

        cont_html = ""
        if self.popover_content:
            body = self.popover_content.render(snap) if isinstance(self.popover_content, Component) else str(self.popover_content)
            cont_html = f'<div class="pdu-popover-content absolute z-50 mt-2 w-72 rounded-md border border-border bg-popover p-4 text-popover-foreground shadow-md outline-none hidden data-[open=true]:block animate-in fade-in-0 zoom-in-95">{body}</div>'

        children_html = self._render_children(snap)
        attrs = self._build_attrs(snap)
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{trig_html}{cont_html}{children_html}</{self.tag}>'


class ShadTooltip(Component):
    """
    CSS-driven, accessible micro-tooltip. Renders hover popover above/below target
    element with zero JavaScript overhead.
    """
    tag = 'span'

    def __init__(self, text: str, *children, side: str = "top", **kwargs):
        super().__init__(*children, **kwargs)
        self.text = text
        self.side = side

    def _get_classes(self) -> List[str]:
        return ['group/tooltip', 'relative', 'inline-flex', 'items-center']

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        children_html = self._render_children(snap)
        side_classes = {
            'top':    'bottom-full left-1/2 -translate-x-1/2 mb-2',
            'bottom': 'top-full left-1/2 -translate-x-1/2 mt-2',
            'left':   'right-full top-1/2 -translate-y-1/2 mr-2',
            'right':  'left-full top-1/2 -translate-y-1/2 ml-2',
        }.get(self.side, 'bottom-full left-1/2 -translate-x-1/2 mb-2')

        tooltip_bubble = (
            f'<span role="tooltip" class="pointer-events-none absolute {side_classes} hidden '
            f'group-hover/tooltip:flex items-center rounded-md bg-primary px-2.5 py-1 text-xs '
            f'font-medium text-primary-foreground shadow-md whitespace-nowrap z-50 animate-in fade-in-0 zoom-in-95">'
            f'{escape_html(self.text)}'
            f'</span>'
        )
        attrs = self._build_attrs(snap)
        attrs_str = f' {attrs}' if attrs else ''
        return f'<{self.tag}{attrs_str}>{children_html}{tooltip_bubble}</{self.tag}>'


class ShadAlertDialog(Component):
    """Destructive confirmation dialog modal for operations like deleting clusters or stopping jobs."""
    tag = 'div'

    def __init__(self, *children, title: str = "Are you absolutely sure?",
                 description: str = "This action cannot be undone.",
                 action_text: str = "Continue", cancel_text: str = "Cancel",
                 action_variant: str = "destructive", open: bool = False,
                 on_action: Optional[Any] = None, on_cancel: Optional[Any] = None, **kwargs):
        super().__init__(*children, **kwargs)
        self.title = title
        self.description = description
        self.action_text = action_text
        self.cancel_text = cancel_text
        self.action_variant = action_variant
        self.open = open
        self.on_action = on_action
        self.on_cancel = on_cancel

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        is_open = bool(self._resolve_value(self.open, snap))
        if not is_open:
            return ""

        cancel_attrs = ""
        if self.on_cancel:
            htmx_close = self._get_event_htmx_attrs('on_click', self.on_cancel)
            cancel_attrs = " ".join(f'{k}="{v}"' for k, v in htmx_close.items())

        action_attrs = ""
        if self.on_action:
            htmx_act = self._get_event_htmx_attrs('on_click', self.on_action)
            action_attrs = " ".join(f'{k}="{v}"' for k, v in htmx_act.items())

        act_cls = "bg-destructive text-destructive-foreground hover:bg-destructive/90" if self.action_variant == "destructive" else "bg-primary text-primary-foreground hover:bg-primary/90"

        return (
            f'<div id="{self.id}" class="pdu-alert-dialog-wrapper fixed inset-0 z-50 flex items-center justify-center p-4">'
            f'<div class="fixed inset-0 bg-background/80 backdrop-blur-sm" {cancel_attrs}></div>'
            f'<div class="relative z-50 w-full max-w-lg rounded-lg border bg-background p-6 shadow-lg animate-in fade-in-0 zoom-in-95">'
            f'<div class="flex flex-col space-y-2 text-center sm:text-left">'
            f'<h2 class="text-lg font-semibold">{escape_html(self.title)}</h2>'
            f'<p class="text-sm text-muted-foreground">{escape_html(self.description)}</p>'
            f'</div>'
            f'<div class="flex flex-col-reverse sm:flex-row sm:justify-end sm:space-x-2 mt-6">'
            f'<button type="button" class="inline-flex items-center justify-center rounded-md border border-input bg-background px-4 py-2 text-sm font-medium hover:bg-accent mt-2 sm:mt-0 cursor-pointer" {cancel_attrs}>{escape_html(self.cancel_text)}</button>'
            f'<button type="button" class="inline-flex items-center justify-center rounded-md px-4 py-2 text-sm font-medium {act_cls} cursor-pointer" {action_attrs}>{escape_html(self.action_text)}</button>'
            f'</div>'
            f'</div>'
            f'</div>'
        )


class ShadCommandPalette(Component):
    """Spotlight search modal triggered via Cmd+K or keyboard shortcuts."""
    tag = 'div'

    def __init__(self, *children, items: Optional[List[Dict[str, str]]] = None,
                 placeholder: str = "Type a command or search...", **kwargs):
        super().__init__(*children, **kwargs)
        self.items = items or []
        self.placeholder = placeholder
        self.props['data-pdu-command-palette'] = 'true'

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        items_html = []
        for it in self.items:
            icon = _render_icon(it.get('icon', 'terminal'), size=16, class_name="text-muted-foreground")
            label = escape_html(it.get('label', ''))
            category = escape_html(it.get('category', 'Actions'))
            shortcut = escape_html(it.get('shortcut', ''))
            sc_badge = f'<kbd class="pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] text-muted-foreground">{shortcut}</kbd>' if shortcut else ''
            items_html.append(
                f'<div class="pdu-command-item relative flex cursor-pointer select-none items-center gap-3 rounded-sm px-3 py-2 text-sm hover:bg-accent hover:text-accent-foreground" data-value="{label.lower()}">'
                f'{icon}<span>{label}</span>'
                f'<span class="ml-auto text-xs text-muted-foreground">{category}</span>{sc_badge}'
                f'</div>'
            )

        rendered_items = "".join(items_html)
        return (
            f'<div id="{self.id}" class="pdu-command-dialog fixed inset-0 z-50 flex items-start justify-center pt-20 p-4 hidden" data-pdu-command-dialog="true" data-pdu-command-palette="true">'
            f'<div class="fixed inset-0 bg-background/80 backdrop-blur-sm" data-pdu-command-close="true"></div>'
            f'<div class="relative z-50 w-full max-w-xl rounded-xl border border-border bg-popover shadow-2xl overflow-hidden animate-in fade-in-0 zoom-in-95">'
            f'<div class="flex items-center border-b px-3">'
            f'{_render_icon("search", size=16, class_name="mr-2 text-muted-foreground shrink-0")}'
            f'<input type="text" class="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50" placeholder="{escape_html(self.placeholder)}" data-pdu-command-input="true" autofocus>'
            f'<kbd class="rounded border bg-muted px-1.5 py-0.5 text-[10px] text-muted-foreground" data-pdu-command-close="true">ESC</kbd>'
            f'</div>'
            f'<div class="max-h-72 overflow-y-auto p-2 space-y-1" data-pdu-command-list="true">{rendered_items}</div>'
            f'</div>'
            f'</div>'
        )


# ============================================================================
# Phase 3: AI & Precision ML Controls (Sliders, RadioGroups, DatePickers)
# ============================================================================

class ShadSlider(Component):
    """
    Styled numeric range slider for machine learning hyperparameters
    (temperature, top_p, learning rate, epoch counts). Features a live value bubble.
    """
    tag = 'div'

    def __init__(self, *args, min_val: float = 0.0, max_val: float = 1.0,
                 step: float = 0.01, value: Optional[float] = None, label: Optional[str] = None,
                 name: Optional[str] = None, bind: Optional[Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.value = value if value is not None else min_val
        self.label = label
        self.name = name
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if self.name is None:
                    self.name = self.bind.field_name
                if value is None:
                    self.value = self.bind

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        val = self._resolve_value(self.value, snap)
        name_attr = f'name="{escape_html(self.name)}"' if self.name else ''
        label_html = ""
        if self.label:
            label_html = (
                f'<div class="flex justify-between items-center text-sm font-medium mb-1.5">'
                f'<span>{escape_html(self.label)}</span>'
                f'<span class="pdu-slider-value font-mono text-xs text-muted-foreground bg-muted px-2 py-0.5 rounded">{val}</span>'
                f'</div>'
            )
        slider_input = (
            f'<input type="range" min="{self.min_val}" max="{self.max_val}" step="{self.step}" '
            f'value="{val}" {name_attr} class="w-full h-2 bg-secondary rounded-lg appearance-none cursor-pointer accent-primary" '
            f'data-pdu-slider="true">'
        )
        return f'<div id="{self.id}" class="w-full space-y-1">{label_html}{slider_input}</div>'


class ShadRadioGroup(Component):
    """Accessible group of mutually exclusive options with card-style descriptions."""
    tag = 'div'

    def __init__(self, *children, options: Optional[List[Dict[str, Any]]] = None,
                 value: Optional[str] = None, name: Optional[str] = None,
                 bind: Optional[Any] = None, **kwargs):
        super().__init__(*children, **kwargs)
        self.options = options or []
        self.value = value
        self.name = name or generate_id()
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if name is None:
                    self.name = self.bind.field_name
                if value is None:
                    self.value = self.bind

    def _get_classes(self) -> List[str]:
        return ['grid', 'gap-2.5', 'w-full']

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        curr_val = str(self._resolve_value(self.value, snap)) if self.value is not None else ""
        cards_html = []
        for opt in self.options:
            val = str(opt.get('value', ''))
            lbl = escape_html(opt.get('label', val))
            desc = escape_html(opt.get('description', ''))
            badge = escape_html(opt.get('badge', ''))
            checked = 'checked' if val == curr_val else ''
            badge_html = f'<span class="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-primary/10 text-primary border border-primary/20">{badge}</span>' if badge else ''
            desc_html = f'<p class="text-xs text-muted-foreground mt-0.5">{desc}</p>' if desc else ''

            cards_html.append(
                f'<label class="relative flex items-start gap-3 rounded-lg border border-input p-3 hover:bg-accent/50 cursor-pointer transition-colors has-[:checked]:border-primary has-[:checked]:bg-primary/5">'
                f'<input type="radio" name="{escape_html(self.name)}" value="{escape_html(val)}" {checked} class="mt-1 h-4 w-4 text-primary accent-primary cursor-pointer">'
                f'<div class="flex flex-col flex-1">'
                f'<div class="flex items-center justify-between"><span class="text-sm font-medium leading-none">{lbl}</span>{badge_html}</div>'
                f'{desc_html}'
                f'</div>'
                f'</label>'
            )

        rendered_options = "".join(cards_html)
        children_html = self._render_children(snap)
        attrs = self._build_attrs(snap)
        attrs_str = f' {attrs}' if attrs else ''
        return f'<div role="radiogroup"{attrs_str}>{rendered_options}{children_html}</div>'


class ShadDatePicker(Component):
    """Accessible HTML5 date input with shadcn styling and calendar icon."""
    tag = 'div'

    def __init__(self, *args, label: Optional[str] = None, value: Optional[str] = None,
                 name: Optional[str] = None, bind: Optional[Any] = None, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.value = value
        self.name = name
        self.bind = bind
        if self.bind is not None:
            from ..state import StateVarRef
            if isinstance(self.bind, StateVarRef):
                if self.name is None:
                    self.name = self.bind.field_name
                if value is None:
                    self.value = self.bind

    def render(self, state_snapshot=None) -> str:
        snap = state_snapshot or {}
        val = self._resolve_value(self.value, snap) or ""
        val_attr = f'value="{escape_html(str(val))}"' if val else ''
        name_attr = f'name="{escape_html(self.name)}"' if self.name else ''
        label_html = f'<label class="text-sm font-medium mb-1.5 block">{escape_html(self.label)}</label>' if self.label else ''

        input_html = (
            f'<div class="relative flex items-center">'
            f'<input type="date" {name_attr} {val_attr} class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">'
            f'</div>'
        )
        return f'<div id="{self.id}" class="w-full">{label_html}{input_html}</div>'


class ShadPagination(Component):
    """Pagination navigation bar for large data tables and analytics queries."""
    tag = 'nav'

    def __init__(self, *children, total_pages: int = 1, current_page: int = 1,
                 page_url_pattern: str = "?page={page}", **kwargs):
        kwargs.setdefault('aria_label', 'pagination')
        super().__init__(*children, **kwargs)
        self.total_pages = total_pages
        self.current_page = current_page
        self.page_url_pattern = page_url_pattern

    def _get_classes(self) -> List[str]:
        return ['mx-auto', 'flex', 'w-full', 'justify-center']

    def render(self, state_snapshot=None) -> str:
        pages = []
        # Previous button
        prev_page = max(1, self.current_page - 1)
        prev_href = self.page_url_pattern.replace("{page}", str(prev_page))
        prev_disabled = "opacity-50 pointer-events-none" if self.current_page <= 1 else ""
        pages.append(
            f'<li class="list-none"><a href="{prev_href}" class="inline-flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-md hover:bg-accent {prev_disabled}">'
            f'{_render_icon("chevron-left", size=14)}<span>Previous</span></a></li>'
        )

        for p in range(1, self.total_pages + 1):
            href = self.page_url_pattern.replace("{page}", str(p))
            if p == self.current_page:
                pages.append(f'<li class="list-none"><span class="inline-flex items-center justify-center h-9 w-9 text-sm font-semibold rounded-md bg-primary text-primary-foreground" aria-current="page">{p}</span></li>')
            else:
                pages.append(f'<li class="list-none"><a href="{href}" class="inline-flex items-center justify-center h-9 w-9 text-sm font-medium rounded-md hover:bg-accent text-muted-foreground hover:text-foreground">{p}</a></li>')

        # Next button
        next_page = min(self.total_pages, self.current_page + 1)
        next_href = self.page_url_pattern.replace("{page}", str(next_page))
        next_disabled = "opacity-50 pointer-events-none" if self.current_page >= self.total_pages else ""
        pages.append(
            f'<li class="list-none"><a href="{next_href}" class="inline-flex items-center gap-1 px-3 py-2 text-sm font-medium rounded-md hover:bg-accent {next_disabled}">'
            f'<span>Next</span>{_render_icon("chevron-right", size=14)}</a></li>'
        )

        content = "".join(pages)
        return f'<nav aria-label="pagination" class="mx-auto flex w-full justify-center"><ul class="flex items-center gap-1 list-none p-0 m-0">{content}</ul></nav>'


# ============================================================================
# Phase 4: Zero-JS Declarative Component Factory
# ============================================================================

def create_shadcn_component(
    tag: str = "div",
    base_classes: str = "",
    variants: Optional[Dict[str, str]] = None,
    default_variant: Optional[str] = None,
    name: str = "CustomShadComponent",
    **default_attrs
) -> type:
    """
    Pure-Python declarative factory to define any new shadcn/ui component or variant in 5 lines.
    Allows data and AI engineers to use upcoming components without writing frontend JavaScript.
    """
    var_map = variants or {}

    class DynamicShadComponent(Component):
        def __init__(self, *children, variant: Optional[str] = None, **kwargs):
            super().__init__(*children, **kwargs)
            self.tag = tag
            self.variant = variant or default_variant
            for k, v in default_attrs.items():
                self.props.setdefault(k, v)

        def _get_classes(self) -> List[str]:
            classes = [base_classes] if base_classes else []
            if self.variant and self.variant in var_map:
                classes.append(var_map[self.variant])
            return classes

    DynamicShadComponent.__name__ = name
    DynamicShadComponent.__doc__ = f"Dynamically generated shadcn component: <{tag}> with {len(var_map)} variants."
    return DynamicShadComponent
