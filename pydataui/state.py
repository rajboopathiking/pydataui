from typing import Any, Dict, Callable, Type, Optional
from .types import StateSnapshot

class StateVarRef:
    """A reference to a state variable, used in components for reactive rendering."""
    def __init__(self, state_cls_name: str, field_name: str, default: Any = None):
        self.state_cls_name = state_cls_name
        self.field_name = field_name
        self.default = default
        
    def resolve(self, state_snapshot: StateSnapshot) -> Any:
        state_dict = state_snapshot.get(self.state_cls_name, {})
        return state_dict.get(self.field_name, self.default)
        
    def __str__(self) -> str:
        return f'{{{{state.{self.state_cls_name}.{self.field_name}}}}}'
        
    def __format__(self, format_spec) -> str:
        return str(self)

class StateVar:
    """Descriptor representing a reactive state variable reference."""
    def __init__(self, default: Any = None, field_name: str = ''):
        self.default = default
        self.field_name = field_name
        self._name = field_name
        
    def __set_name__(self, owner: Type, name: str):
        self._name = name
        if not self.field_name:
            self.field_name = name
            
    def __get__(self, obj: Any, objtype: Type = None) -> Any:
        if obj is None:
            return StateVarRef(objtype.__name__, self._name, self.default)
        return obj.__dict__.get(self._name, self.default)
        
    def __set__(self, obj: Any, value: Any):
        obj.__dict__[self._name] = value

class EventHandler:
    """Reference to a state method, used for event binding in components.
    
    When a user writes ``Button('Click', on_click=MyState.increment)``,
    ``MyState.increment`` returns an ``EventHandler`` instance (via the
    ``StateMeta`` metaclass).  The component system inspects this object
    to produce the correct HTMX attributes so the browser POSTs to the
    right server endpoint.
    """

    def __init__(self, state_cls_name: str, method_name: str) -> None:
        self.state_cls_name = state_cls_name
        self.method_name = method_name

    def get_endpoint(self) -> str:
        """Return the internal PyDataUI event endpoint path."""
        return f'/_pdu/event/{self.state_cls_name}/{self.method_name}'

    def get_htmx_attrs(
        self,
        trigger: str = 'click',
        target: str = '#pdu-root',
        swap: str = 'innerHTML',
    ) -> Dict[str, str]:
        """Return HTMX attributes dict for embedding in HTML elements."""
        return {
            'hx-post': self.get_endpoint(),
            'hx-target': target,
            'hx-swap': swap,
            'hx-trigger': trigger,
        }

    def __repr__(self) -> str:
        return f'EventHandler({self.state_cls_name}.{self.method_name})'

    def __hash__(self) -> int:
        return hash((self.state_cls_name, self.method_name))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, EventHandler):
            return (self.state_cls_name == other.state_cls_name
                    and self.method_name == other.method_name)
        return NotImplemented


# ---------------------------------------------------------------------------
# Names that belong to Python / the metaclass and must never be wrapped.
# ---------------------------------------------------------------------------
_META_PASSTHROUGH = frozenset({
    '__class__', '__dict__', '__bases__', '__mro__', '__subclasses__',
    '__name__', '__qualname__', '__module__', '__doc__',
    '__new__', '__init__', '__init_subclass__', '__instancecheck__',
    '__subclasscheck__', '__prepare__', '__set_name__',
    '__abstractmethods__', '__flags__',
    # Our own helpers that must stay accessible:
    '_registry', 'get_state_vars', 'get_event_handlers',
    'to_dict', 'from_dict', 'reset',
})


class StateMeta(type):
    """Metaclass for State that registers states and processes annotated
    fields as ``StateVar`` descriptors.

    **Class-level attribute access semantics** (the key magic):

    * Accessing a *state variable* on the **class** returns a
      ``StateVarRef`` (handled by the ``StateVar`` descriptor).
    * Accessing a *method* on the **class** returns an ``EventHandler``
      instead of the raw function.  This is what makes
      ``on_click=MyState.increment`` work.
    * Accessing anything on an **instance** works normally.
    """

    _registry: Dict[str, Type['State']] = {}

    # ---- class creation ----------------------------------------------------
    def __new__(mcs, name: str, bases: tuple, namespace: dict, **kwargs: Any):
        annotations = namespace.get('__annotations__', {})

        # Wrap annotated fields as StateVar descriptors
        for field, ann in annotations.items():
            if field.startswith('_'):
                continue
            default = namespace.get(field, None)
            if (not isinstance(default, StateVar)
                    and not callable(default)
                    and not isinstance(default, (classmethod, staticmethod, property))):
                namespace[field] = StateVar(default=default, field_name=field)

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if name != 'State':
            mcs._registry[name] = cls
        return cls

    # ---- intercept class-level attribute access ----------------------------
    def __getattribute__(cls, name: str) -> Any:
        """Override on the *metaclass* so that ``MyState.some_method``
        returns an ``EventHandler`` instead of the raw function when
        accessed on the **class** (not on an instance).

        ``StateVar`` fields are already handled by the descriptor
        protocol (``StateVar.__get__`` with ``obj is None``).
        """
        # Always let internal / dunder names through normally.
        if name.startswith('__') or name in _META_PASSTHROUGH:
            return super().__getattribute__(name)

        # If the attribute lives in the class dict and is a plain function
        # (i.e. a user-defined event handler), wrap it.
        raw = None
        for klass in cls.__mro__:
            if name in klass.__dict__:
                raw = klass.__dict__[name]
                break

        if raw is not None:
            # StateVar descriptors handle themselves — delegate.
            if isinstance(raw, StateVar):
                return super().__getattribute__(name)
            # Wrap plain callables (user methods) as EventHandler.
            if callable(raw) and not isinstance(
                raw, (classmethod, staticmethod, property, type)
            ):
                return EventHandler(cls.__name__, name)

        # Fallback to normal lookup (classmethods, properties, etc.)
        return super().__getattribute__(name)


class State(metaclass=StateMeta):
    """Base class for application state.

    Subclass and declare typed class attributes to create reactive state::

        class CounterState(State):
            count: int = 0
            name: str = 'World'

            def increment(self):
                self.count += 1

    * Accessing ``CounterState.count`` on the **class** returns a
      ``StateVarRef`` (for component binding).
    * Accessing ``CounterState.increment`` on the **class** returns an
      ``EventHandler`` (for event binding).
    * On an **instance**, everything behaves normally.
    """

    def __init__(self) -> None:
        for name, var in self.get_state_vars().items():
            # Use object.__setattr__ to bypass descriptors during init
            self.__dict__[name] = var.default

    def to_dict(self) -> Dict[str, Any]:
        """Serialize current state to a plain dictionary."""
        return {name: getattr(self, name) for name in self.get_state_vars()}

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Bulk-update state from a dictionary."""
        vars_dict = self.get_state_vars()
        for k, v in data.items():
            if k in vars_dict:
                setattr(self, k, v)

    def reset(self) -> None:
        """Reset all state variables to their declared defaults."""
        for name, var in self.get_state_vars().items():
            setattr(self, name, var.default)

    @classmethod
    def get_event_handlers(cls) -> Dict[str, Callable]:
        """Return a dict of {name: function} for all public methods."""
        handlers: Dict[str, Callable] = {}
        for name in list(cls.__dict__):
            if name.startswith('_'):
                continue
            attr = cls.__dict__[name]
            if callable(attr) and not isinstance(
                attr, (classmethod, staticmethod, type, StateVar)
            ):
                handlers[name] = attr
        return handlers

    @classmethod
    def get_state_vars(cls) -> Dict[str, StateVar]:
        """Return a dict of {name: StateVar} for all declared state fields."""
        result: Dict[str, StateVar] = {}
        for klass in reversed(cls.__mro__):
            for name, attr in klass.__dict__.items():
                if isinstance(attr, StateVar):
                    result[name] = attr
        return result
