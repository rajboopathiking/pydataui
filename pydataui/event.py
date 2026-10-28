from typing import List, Dict, Any, Optional
from .state import EventHandler

EVENT_TRIGGERS = {
    'on_click': 'click',
    'on_change': 'change', 
    'on_submit': 'submit',
    'on_input': 'input',
    'on_blur': 'blur',
    'on_focus': 'focus',
    'on_keydown': 'keydown',
    'on_keyup': 'keyup',
    'on_mouse_enter': 'mouseenter',
    'on_mouse_leave': 'mouseleave',
    'on_scroll': 'scroll',
    'on_load': 'load',
}

class EventChain:
    """Chain multiple event handlers together."""
    def __init__(self, initial_handler: Optional[EventHandler] = None):
        self.handlers: List[EventHandler] = []
        if initial_handler:
            self.handlers.append(initial_handler)
            
    def then(self, handler: EventHandler) -> 'EventChain':
        self.handlers.append(handler)
        return self

class EventSpec:
    """Full event specification with arguments and options."""
    def __init__(
        self, 
        handler: EventHandler, 
        args: Optional[Dict[str, Any]] = None,
        debounce: Optional[int] = None,
        throttle: Optional[int] = None,
        prevent_default: bool = False,
        stop_propagation: bool = False,
        confirm: Optional[str] = None,
        target: Optional[str] = None,
        swap: Optional[str] = None,
    ):
        self.handler = handler
        self.args = args or {}
        self.debounce = debounce
        self.throttle = throttle
        self.prevent_default = prevent_default
        self.stop_propagation = stop_propagation
        self.confirm = confirm
        self.target = target or getattr(handler, 'target', '#pdu-root')
        self.swap = swap or getattr(handler, 'swap', 'innerHTML')

    def target_to(self, target: str, swap: Optional[str] = None) -> 'EventSpec':
        """Fluent helper to target a specific DOM element ID for minimal updates."""
        self.target = target
        if swap:
            self.swap = swap
        return self
        
    def get_htmx_attrs(self, trigger: str = 'click') -> Dict[str, str]:
        attrs = self.handler.get_htmx_attrs(trigger=trigger, target=self.target, swap=self.swap)
        
        trigger_val = attrs.get('hx-trigger', trigger)
        
        modifiers = []
        if self.debounce:
            modifiers.append(f'delay:{self.debounce}ms')
        if self.throttle:
            modifiers.append(f'throttle:{self.throttle}ms')
        if self.prevent_default:
            modifiers.append('consume') # HTMX idiom for prevent/consume
        
        if modifiers:
            attrs['hx-trigger'] = f"{trigger_val} {' '.join(modifiers)}"
            
        if self.confirm:
            attrs['hx-confirm'] = self.confirm

        if self.target:
            attrs['hx-target'] = self.target
        if self.swap:
            attrs['hx-swap'] = self.swap
            
        if self.args:
            import json
            attrs['hx-vals'] = json.dumps(self.args)
            
        return attrs

def create_event_spec(handler: EventHandler, **kwargs: Any) -> EventSpec:
    """Create an EventSpec from an EventHandler with options."""
    return EventSpec(handler, **kwargs)
