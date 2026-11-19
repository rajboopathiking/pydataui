from __future__ import annotations
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

class Alert(Component):
    tag = 'div'
    def __init__(self, *children, variant='info', title=None, closable=False, icon=True, on_close=None, **props):
        super().__init__(*children, **props)
        self.variant = variant
        self.title = title
        self.closable = closable
        self.icon = icon
        if on_close:
            self._event_props['on_close'] = on_close
            
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-alert', f'pdu-alert-{self.variant}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        parts = []
        if self.icon:
            parts.append("<div class='pdu-alert-icon'></div>")
            
        content = []
        if self.title:
            t = self._resolve_value(self.title, state_snapshot)
            content.append(f"<div class='pdu-alert-title'>{escape_html(str(t))}</div>")
        content.append(f"<div class='pdu-alert-body'>{children}</div>")
        
        parts.append(f"<div class='pdu-alert-content'>{''.join(content)}</div>")
        
        if self.closable:
            close_attrs = ""
            if 'on_close' in self._event_props:
                htmx = self._get_event_htmx_attrs('on_close', self._event_props['on_close'])
                close_attrs = " ".join([f"{k}='{v}'" for k,v in htmx.items()])
            parts.append(f"<button class='pdu-alert-close' {close_attrs}>&times;</button>")
            
        return f"<{self.tag} {attrs}>{''.join(parts)}</{self.tag}>"

class Progress(Component):
    tag = 'div'
    def __init__(self, value=0, max=100, size='md', variant='primary', show_label=False, striped=False, animated=False, **props):
        super().__init__(**props)
        self.value = value
        self.max = max
        self.size = size
        self.variant = variant
        self.show_label = show_label
        self.striped = striped
        self.animated = animated
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-progress', f'pdu-progress-{self.size}', f'pdu-progress-{self.variant}']
        if self.striped: classes.append('pdu-progress-striped')
        if self.animated: classes.append('pdu-progress-animated')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        val = float(self._resolve_value(self.value, state_snapshot) or 0)
        m = float(self._resolve_value(self.max, state_snapshot) or 100)
        pct = min(100, max(0, (val / m) * 100 if m > 0 else 0))
        
        bar_html = f"<div class='pdu-progress-bar' style='width: {pct}%' role='progressbar' aria-valuenow='{val}' aria-valuemin='0' aria-valuemax='{m}'></div>"
        
        if self.show_label:
            return f"<div class='pdu-progress-wrapper'><div class='pdu-progress-label'>{pct:.0f}%</div><{self.tag} {attrs}>{bar_html}</{self.tag}></div>"
        return f"<{self.tag} {attrs}>{bar_html}</{self.tag}>"

class Spinner(Component):
    tag = 'div'
    def __init__(self, size='md', variant='primary', label=None, **props):
        super().__init__(**props)
        self.size = size
        self.variant = variant
        self.label = label
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-spinner', f'pdu-spinner-{self.size}', f'pdu-spinner-{self.variant}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        spinner = f"<{self.tag} {attrs} role='status'></{self.tag}>"
        
        if self.label:
            lbl = escape_html(str(self._resolve_value(self.label, state_snapshot)))
            return f"<div class='pdu-spinner-wrapper'>{spinner}<span class='pdu-spinner-label'>{lbl}</span></div>"
        return spinner


class Loader(Component):
    """
    Modern high-performance loading animation component supporting essential visual presets:
    - 'circle': SVG spinning ring with smooth 360° rotation + text (e.g. circle() {text})
    - 'dots': 3 staggered bouncing/pulsing dots (LLM thinking / typing indicator: ... {text} or {text} ...)
    - 'pulse': Glowing radar ping status beacon + text
    - 'bars': Equalizer wave bars + text
    - 'shimmer': Shimmering pulse text
    """
    tag = 'div'
    def __init__(
        self,
        text: Optional[str] = None,
        preset: str = "circle",
        size: str = "md",
        color: Optional[str] = None,
        dots_position: str = "start",
        center: bool = False,
        **props
    ):
        super().__init__(**props)
        self.text = text
        self.preset = preset.lower() if preset else "circle"
        self.size = size
        self.color = color or "primary"
        self.dots_position = dots_position
        self.center = center

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        label_text = self._resolve_value(self.text, snap)
        label_html = f"<span class='font-medium text-foreground/90'>{escape_html(str(label_text))}</span>" if label_text else ""
        
        size_configs = {
            "sm": {"circle": "w-4 h-4", "dot": "w-1.5 h-1.5", "bar": "h-3 w-0.5", "text": "text-xs", "gap": "gap-2"},
            "md": {"circle": "w-5 h-5", "dot": "w-2 h-2", "bar": "h-4 w-1", "text": "text-sm", "gap": "gap-2.5"},
            "lg": {"circle": "w-7 h-7", "dot": "w-2.5 h-2.5", "bar": "h-6 w-1.5", "text": "text-base", "gap": "gap-3"},
            "xl": {"circle": "w-10 h-10", "dot": "w-3.5 h-3.5", "bar": "h-8 w-2", "text": "text-lg", "gap": "gap-4"},
        }
        cfg = size_configs.get(self.size, size_configs["md"])
        center_cls = "justify-center" if self.center else "justify-start"

        if self.preset in ("circle", "spinner", "ring"):
            anim_html = (
                f"<svg class='animate-spin {cfg['circle']} text-primary shrink-0' xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'>"
                f"<circle class='opacity-25' cx='12' cy='12' r='10' stroke='currentColor' stroke-width='3.5'></circle>"
                f"<path class='opacity-85' fill='currentColor' d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'></path>"
                f"</svg>"
            )
            content = f"{anim_html}{label_html}"

        elif self.preset in ("dots", "ellipsis", "bounce", "..."):
            anim_html = (
                f"<span class='inline-flex items-center gap-1 shrink-0' aria-hidden='true'>"
                f"<span class='{cfg['dot']} rounded-full bg-primary animate-bounce [animation-delay:-0.32s]'></span>"
                f"<span class='{cfg['dot']} rounded-full bg-primary animate-bounce [animation-delay:-0.16s]'></span>"
                f"<span class='{cfg['dot']} rounded-full bg-primary animate-bounce'></span>"
                f"</span>"
            )
            if self.dots_position == "end":
                content = f"{label_html}{anim_html}"
            else:
                content = f"{anim_html}{label_html}"

        elif self.preset in ("pulse", "radar", "beacon"):
            anim_html = (
                f"<span class='relative flex {cfg['circle']} items-center justify-center shrink-0'>"
                f"<span class='animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-60'></span>"
                f"<span class='relative inline-flex rounded-full {cfg['dot']} bg-primary'></span>"
                f"</span>"
            )
            content = f"{anim_html}{label_html}"

        elif self.preset in ("bars", "wave", "equalizer", "audio"):
            anim_html = (
                f"<span class='inline-flex items-end gap-1 shrink-0' style='height: 20px;' aria-hidden='true'>"
                f"<span class='{cfg['bar']} bg-primary rounded-full animate-bounce [animation-delay:-0.4s]'></span>"
                f"<span class='{cfg['bar']} bg-primary rounded-full animate-bounce [animation-delay:-0.2s]'></span>"
                f"<span class='{cfg['bar']} bg-primary rounded-full animate-bounce [animation-delay:-0.35s]'></span>"
                f"<span class='{cfg['bar']} bg-primary rounded-full animate-bounce [animation-delay:-0.1s]'></span>"
                f"</span>"
            )
            content = f"{anim_html}{label_html}"

        elif self.preset in ("shimmer", "glow"):
            anim_html = f"<span class='animate-pulse text-primary font-bold tracking-widest text-xs uppercase shrink-0'>●</span>"
            text_shimmer = f"<span class='animate-pulse font-medium text-foreground/90'>{escape_html(str(label_text or 'Loading...'))}</span>"
            content = f"{anim_html}{text_shimmer}"

        else:
            anim_html = (
                f"<svg class='animate-spin {cfg['circle']} text-primary shrink-0' xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24'>"
                f"<circle class='opacity-25' cx='12' cy='12' r='10' stroke='currentColor' stroke-width='3.5'></circle>"
                f"<path class='opacity-85' fill='currentColor' d='M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z'></path>"
                f"</svg>"
            )
            content = f"{anim_html}{label_html}"

        attrs = self._build_attrs(snap)
        return (
            f"<div {attrs} class='pdu-loader inline-flex items-center {cfg['gap']} {cfg['text']} {center_cls} my-2 p-1.5 select-none'>"
            f"{content}"
            f"</div>"
        )


class Skeleton(Component):
    tag = 'div'
    def __init__(self, width=None, height=None, variant='rectangle', lines=1, rounded="xl", **props):
        super().__init__(**props)
        self.width = width
        self.height = height
        self.variant = variant
        self.lines = lines
        self.rounded = rounded
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-skeleton', 'animate-pulse', 'bg-muted/80', f'rounded-{self.rounded}']
        if self.variant == 'circle':
            classes.append('rounded-full')
        return classes
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.width:
            w_val = f"{self.width}px" if isinstance(self.width, (int, float)) or (isinstance(self.width, str) and str(self.width).isdigit()) else str(self.width)
            s += f" width: {w_val};"
        if self.height:
            h_val = f"{self.height}px" if isinstance(self.height, (int, float)) or (isinstance(self.height, str) and str(self.height).isdigit()) else str(self.height)
            s += f" height: {h_val};"
        return s.strip()
        
    def render(self, state_snapshot: Optional[dict] = None) -> str:
        attrs = self._build_attrs(state_snapshot or {})
        if self.lines > 1:
            line_htmls = []
            for i in range(self.lines):
                w_style = "width: 100%;" if i < self.lines - 1 else "width: 70%;"
                line_htmls.append(f"<div class='h-4 bg-muted/80 rounded-md animate-pulse my-1.5' style='{w_style}'></div>")
            return f"<div class='pdu-skeleton-lines w-full my-2'>{''.join(line_htmls)}</div>"
        return f"<{self.tag} {attrs}></{self.tag}>"

class Toast(Component):
    tag = 'div'
    def __init__(self, message='', variant='info', duration=3000, position='top-right', **props):
        super().__init__(**props)
        self.message = message
        self.variant = variant
        self.duration = duration
        self.position = position
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-toast', f'pdu-toast-{self.variant}', f'pdu-toast-{self.position}']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        msg = escape_html(str(self._resolve_value(self.message, state_snapshot)))
        
        # Adding a bit of inline script for duration removal is standard if pure CSS is not used
        script = f"<script>setTimeout(function(){{ document.getElementById('{self.id}').remove(); }}, {self.duration});</script>" if self.duration > 0 else ""
        
        return f"<{self.tag} {attrs}><div class='pdu-toast-message'>{msg}</div><button class='pdu-toast-close' onclick='this.parentElement.remove()'>&times;</button></{self.tag}>{script}"

class Empty(Component):
    tag = 'div'
    def __init__(self, title='No data', description=None, icon=None, *children, **props):
        super().__init__(*children, **props)
        self.title = title
        self.description = description
        self.icon = icon
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-empty']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        children = self._render_children(state_snapshot)
        
        parts = []
        if self.icon:
            parts.append(f"<div class='pdu-empty-icon'>{self.icon}</div>")
            
        if self.title:
            t = escape_html(str(self._resolve_value(self.title, state_snapshot)))
            parts.append(f"<div class='pdu-empty-title'>{t}</div>")
            
        if self.description:
            d = escape_html(str(self._resolve_value(self.description, state_snapshot)))
            parts.append(f"<div class='pdu-empty-description'>{d}</div>")
            
        if children:
            parts.append(f"<div class='pdu-empty-actions'>{children}</div>")
            
        return f"<{self.tag} {attrs}>{''.join(parts)}</{self.tag}>"
