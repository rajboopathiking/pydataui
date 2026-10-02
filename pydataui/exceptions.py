class PyDataUIError(Exception):
    """Base exception for PyDataUI framework."""
    pass

class StateError(PyDataUIError):
    """Raised when there is an issue with application state."""
    pass

class ComponentError(PyDataUIError):
    """Raised when there is an issue with component rendering or lifecycle."""
    pass

class SessionError(PyDataUIError):
    """Raised when there is an issue with user sessions."""
    pass

class EventError(PyDataUIError):
    """Raised when there is an issue with event handling."""
    pass

class ConfigError(PyDataUIError):
    """Raised when there is a configuration error."""
    pass

class RenderError(PyDataUIError):
    """Raised when a rendering failure occurs."""
    pass

class APIError(PyDataUIError):
    """Raised when there is an issue with API generation or routing."""
    pass
