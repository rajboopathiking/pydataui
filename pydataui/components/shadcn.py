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
            inp_attrs.append('hx-include="#pdu-root"')
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
            self.props['hx-include'] = '#pdu-root'

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
