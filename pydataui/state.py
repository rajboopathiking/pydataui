import copy
import contextvars
from typing import Any, Dict, Callable, Type, Optional
from .types import StateSnapshot

_current_snapshot: contextvars.ContextVar[Optional[Dict[str, Dict[str, Any]]]] = contextvars.ContextVar(
    'current_snapshot', default=None
)
_current_session: contextvars.ContextVar[Optional[Any]] = contextvars.ContextVar(
    'current_session', default=None
)

class StateVarRef:
    """A reference to a state variable, used in components for reactive rendering.
    Acts as a transparent proxy to the underlying value during request execution."""
    def __init__(self, state_cls_name: str, field_name: str, default: Any = None):
        self.state_cls_name = state_cls_name
        self.field_name = field_name
        self.default = default
        
    def _get_val(self) -> Any:
        # 1. Active request snapshot context
        snapshot = _current_snapshot.get()
        if snapshot is not None and self.state_cls_name in snapshot:
            state_dict = snapshot[self.state_cls_name]
            if self.field_name in state_dict:
                return state_dict[self.field_name]

        # 2. Active request session context
        session = _current_session.get()
        if session is not None and hasattr(session, 'state_instances') and self.state_cls_name in session.state_instances:
            inst = session.state_instances[self.state_cls_name]
            if hasattr(inst, self.field_name):
                return getattr(inst, self.field_name)

        # 3. Class store
        cls = StateMeta._registry.get(self.state_cls_name)
        if cls and hasattr(cls, '_class_store') and self.field_name in cls._class_store:
            return cls._class_store[self.field_name]
            
        return self.default

    def resolve(self, state_snapshot: StateSnapshot) -> Any:
        state_dict = state_snapshot.get(self.state_cls_name, {})
        return state_dict.get(self.field_name, self.default)

    def __iter__(self):
        val = self._get_val()
        if val is None:
            return iter(())
        try:
            return iter(val)
        except TypeError:
            return iter([val])

    def __len__(self) -> int:
        val = self._get_val()
        if val is None:
            return 0
        try:
            return len(val)
        except TypeError:
            return 1

    def __getitem__(self, key: Any) -> Any:
        val = self._get_val()
        if val is None:
            raise KeyError(key)
        return val[key]

    def __contains__(self, item: Any) -> bool:
        val = self._get_val()
        if val is None:
            return False
        return item in val

    def __bool__(self) -> bool:
        return bool(self._get_val())

    def __getattr__(self, name: str) -> Any:
        val = self._get_val()
        if hasattr(val, name):
            return getattr(val, name)
        raise AttributeError(f"'{self.state_cls_name}.{self.field_name}' object has no attribute '{name}'")

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, StateVarRef):
            return self.state_cls_name == other.state_cls_name and self.field_name == other.field_name
        return self._get_val() == other

    def __ne__(self, other: Any) -> bool:
        return not (self == other)

    def __lt__(self, other: Any) -> bool:
        return self._get_val() < other

    def __le__(self, other: Any) -> bool:
        return self._get_val() <= other

    def __gt__(self, other: Any) -> bool:
        return self._get_val() > other

    def __ge__(self, other: Any) -> bool:
        return self._get_val() >= other

    def __int__(self) -> int:
        return int(self._get_val())

    def __float__(self) -> float:
        return float(self._get_val())

    def __add__(self, other: Any) -> Any:
        return self._get_val() + other

    def __radd__(self, other: Any) -> Any:
        return other + self._get_val()

    def __sub__(self, other: Any) -> Any:
        return self._get_val() - other

    def __rsub__(self, other: Any) -> Any:
        return other - self._get_val()

    def __mul__(self, other: Any) -> Any:
        return self._get_val() * other

    def __rmul__(self, other: Any) -> Any:
        return other * self._get_val()

    def __truediv__(self, other: Any) -> Any:
        return self._get_val() / other

    def __rtruediv__(self, other: Any) -> Any:
        return other / self._get_val()

    def __floordiv__(self, other: Any) -> Any:
        return self._get_val() // other

    def __rfloordiv__(self, other: Any) -> Any:
        return other // self._get_val()

    def __mod__(self, other: Any) -> Any:
        return self._get_val() % other

    def __rmod__(self, other: Any) -> Any:
        return other % self._get_val()

    def __pow__(self, other: Any) -> Any:
        return self._get_val() ** other

    def __rpow__(self, other: Any) -> Any:
        return other ** self._get_val()

    def __neg__(self) -> Any:
        return -self._get_val()

    def __pos__(self) -> Any:
        return +self._get_val()

    def __abs__(self) -> Any:
        return abs(self._get_val())

    def __str__(self) -> str:
        val = self._get_val()
        return str(val) if val is not None else ''

    def __repr__(self) -> str:
        return f"StateVarRef({self.state_cls_name}.{self.field_name}, val={repr(self._get_val())})"

    def __format__(self, format_spec: str) -> str:
        return format(self._get_val(), format_spec)

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

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """Allow calling event handlers directly on the class for convenience."""
        cls = StateMeta._registry.get(self.state_cls_name)
        if cls:
            for klass in cls.__mro__:
                if self.method_name in klass.__dict__:
                    attr = klass.__dict__[self.method_name]
                    if isinstance(attr, hybridmethod):
                        return attr.__get__(None, cls)(*args, **kwargs)
                    if callable(attr):
                        return attr(cls, *args, **kwargs)
        return None

    def with_args(self, **kwargs: Any) -> Any:
        from .event import EventSpec
        return EventSpec(self, args=kwargs)


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
    'to_dict', '_class_store',
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

        field_names = set(annotations.keys())
        for key, val in namespace.items():
            if key.startswith('_') or key in _META_PASSTHROUGH or key in ('reset', 'to_dict'):
                continue
            if isinstance(val, StateVar):
                field_names.add(key)
            elif callable(val) or isinstance(val, (classmethod, staticmethod, property, type, hybridmethod)):
                continue
            else:
                field_names.add(key)

        # Wrap state fields as StateVar descriptors
        for field in field_names:
            if field.startswith('_'):
                continue
            default = namespace.get(field, None)
            if (not isinstance(default, StateVar)
                    and not callable(default)
                    and not isinstance(default, (classmethod, staticmethod, property, hybridmethod))):
                namespace[field] = StateVar(default=default, field_name=field)

        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        cls._class_store = {}
        for f, var in cls.get_state_vars().items():
            cls._class_store[f] = copy.deepcopy(var.default) if isinstance(var.default, (list, dict, set)) else var.default
        if name != 'State':
            mcs._registry[name] = cls
        return cls

    def __setattr__(cls, name: str, value: Any) -> None:
        if hasattr(cls, '_class_store') and name in cls.get_state_vars():
            cls._class_store[name] = value
            return
        super().__setattr__(name, value)

    def to_dict(cls) -> Dict[str, Any]:
        return {name: cls._class_store.get(name, var.default) for name, var in cls.get_state_vars().items()}

    def reset(cls) -> None:
        for name, var in cls.get_state_vars().items():
            cls._class_store[name] = copy.deepcopy(var.default) if isinstance(var.default, (list, dict, set)) else var.default

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

        if name == 'reset':
            if 'reset' in cls.__dict__ and callable(cls.__dict__['reset']) and not isinstance(cls.__dict__['reset'], hybridmethod):
                return EventHandler(cls.__name__, 'reset')
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


class hybridmethod:
    """Descriptor that acts as a classmethod when accessed on a class,
    and an instancemethod when accessed on an instance."""
    def __init__(self, func: Callable):
        self.func = func
    def __get__(self, obj: Any, objtype: Optional[Type] = None) -> Callable:
        target = obj if obj is not None else objtype
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return self.func(target, *args, **kwargs)
        return wrapper


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
            self.__dict__[name] = copy.deepcopy(var.default) if isinstance(var.default, (list, dict, set)) else var.default

    @hybridmethod
    def to_dict(self_or_cls: Any) -> Dict[str, Any]:
        """Serialize current state to a plain dictionary (works on class or instance)."""
        if isinstance(self_or_cls, type):
            store = getattr(self_or_cls, '_class_store', {})
            return {name: store.get(name, var.default) for name, var in self_or_cls.get_state_vars().items()}
        return {name: getattr(self_or_cls, name) for name in self_or_cls.get_state_vars()}

    def from_dict(self, data: Dict[str, Any]) -> None:
        """Bulk-update state from a dictionary."""
        vars_dict = self.get_state_vars()
        for k, v in data.items():
            if k in vars_dict:
                setattr(self, k, v)

    @hybridmethod
    def reset(self_or_cls: Any) -> None:
        """Reset state variables to their declared defaults (works on class or instance)."""
        if isinstance(self_or_cls, type):
            if hasattr(self_or_cls, '_class_store'):
                for name, var in self_or_cls.get_state_vars().items():
                    self_or_cls._class_store[name] = copy.deepcopy(var.default) if isinstance(var.default, (list, dict, set)) else var.default
            return
        for name, var in self_or_cls.get_state_vars().items():
            setattr(self_or_cls, name, copy.deepcopy(var.default) if isinstance(var.default, (list, dict, set)) else var.default)

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
