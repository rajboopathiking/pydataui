import html
import uuid
import re
from typing import Any, Dict

def generate_id(prefix: str = 'pdu') -> str:
    """Generate a unique component ID."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def escape_html(text: str) -> str:
    """Escape HTML characters in a string."""
    return html.escape(str(text), quote=True)

def to_css_value(value: Any) -> str:
    """Convert Python values to CSS value strings."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value}px"
    return str(value)

def to_css_class(*classes: str) -> str:
    """Join multiple CSS classes into a single string."""
    return " ".join(filter(None, classes))

def snake_to_kebab(name: str) -> str:
    """Convert snake_case to kebab-case."""
    return name.replace('_', '-')

def snake_to_camel(name: str) -> str:
    """Convert snake_case to camelCase."""
    parts = name.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result

def sanitize_attr(value: str) -> str:
    """Sanitize HTML attribute values."""
    return re.sub(r'[\x00-\x1F\x7F"\']', '', str(value))

def to_json_compatible(obj: Any) -> Any:
    """Recursively convert arbitrary Python objects (Pydantic models, dataclasses,
    datetimes, sets, numpy types) into standard JSON-serializable primitives."""
    if obj is None or isinstance(obj, (int, float, str, bool)):
        return obj
    if hasattr(obj, 'model_dump') and callable(obj.model_dump):
        return to_json_compatible(obj.model_dump())
    if hasattr(obj, 'dict') and callable(obj.dict):
        return to_json_compatible(obj.dict())
    from dataclasses import is_dataclass, asdict
    if is_dataclass(obj):
        return to_json_compatible(asdict(obj))
    from datetime import datetime, date
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {str(k): to_json_compatible(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [to_json_compatible(v) for v in obj]
    if hasattr(obj, 'to_dict') and callable(obj.to_dict):
        return to_json_compatible(obj.to_dict())
    return str(obj)
