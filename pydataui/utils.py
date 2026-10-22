import html
import uuid
import re
from html.parser import HTMLParser
from typing import Any, Dict, Optional
from urllib.parse import urlsplit

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


# ---------------------------------------------------------------------------
# HTML sanitization for user/Markdown-authored content.
# ---------------------------------------------------------------------------
_ALLOWED_TAGS = frozenset({
    'a', 'abbr', 'b', 'blockquote', 'br', 'code', 'dd', 'del', 'div', 'dl',
    'dt', 'em', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'hr', 'i', 'img', 'ins',
    'kbd', 'li', 'ol', 'p', 'pre', 'q', 's', 'span', 'strong', 'sub', 'sup',
    'table', 'tbody', 'td', 'tfoot', 'th', 'thead', 'tr', 'u', 'ul',
})
_VOID_TAGS = frozenset({'br', 'hr', 'img'})
# Tags whose text content can execute or alter the document; drop them entirely.
_DROP_CONTENT_TAGS = frozenset({
    'applet', 'audio', 'base', 'button', 'canvas', 'embed', 'form', 'frame',
    'frameset', 'iframe', 'input', 'link', 'math', 'meta', 'noscript', 'object',
    'option', 'script', 'select', 'style', 'svg', 'template', 'textarea',
    'video',
})
# Dropped tags that never have a closing tag and therefore must not change depth.
_DROP_VOID_TAGS = frozenset({'base', 'embed', 'input', 'link', 'meta'})
_ALLOWED_ATTRS = {
    'a': frozenset({'href', 'title'}),
    'img': frozenset({'src', 'alt', 'title', 'width', 'height'}),
    'code': frozenset({'class'}),
    'pre': frozenset({'class'}),
    'span': frozenset({'class'}),
    'div': frozenset({'class'}),
}
_GLOBAL_ATTRS = frozenset()
_URL_ATTRS = frozenset({'href', 'src'})
_URL_SCHEMES = {
    'a': frozenset({'http', 'https', 'mailto'}),
    'img': frozenset({'http', 'https'}),
}


def _is_safe_url(value: str, tag: str) -> bool:
    """Reject script-bearing URLs, including obfuscated control/space variants."""
    candidate = re.sub(r'[\x00-\x20\x7f]+', '', str(value))
    if not candidate:
        return False
    try:
        parsed = urlsplit(candidate)
    except ValueError:
        return False
    scheme = parsed.scheme.lower()
    if not scheme:
        return True
    allowed = _URL_SCHEMES.get(tag, frozenset({'http', 'https'}))
    return scheme in allowed


class _SanitizingHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts = []
        self._drop_depth = 0

    def _filtered_attrs(self, tag: str, attrs) -> str:
        allowed = _ALLOWED_ATTRS.get(tag, frozenset()) | _GLOBAL_ATTRS
        rendered = []
        for name, value in attrs:
            name = (name or '').lower()
            if name.startswith('on') or name in ('style', 'srcdoc', 'formaction'):
                continue
            if name not in allowed:
                continue
            if value is None:
                value = ''
            if name in _URL_ATTRS and not _is_safe_url(value, tag):
                continue
            rendered.append(f'{name}="{html.escape(str(value), quote=True)}"')
        return (' ' + ' '.join(rendered)) if rendered else ''

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in _DROP_CONTENT_TAGS:
            if tag not in _DROP_VOID_TAGS:
                self._drop_depth += 1
            return
        if self._drop_depth or tag not in _ALLOWED_TAGS:
            return
        filtered = self._filtered_attrs(tag, attrs)
        if tag == 'img' and ' src=' not in filtered:
            return
        self.parts.append(f'<{tag}{filtered}>')

    def handle_startendtag(self, tag, attrs):
        tag = tag.lower()
        if self._drop_depth or tag not in _ALLOWED_TAGS or tag in _DROP_CONTENT_TAGS:
            return
        filtered = self._filtered_attrs(tag, attrs)
        if tag == 'img' and ' src=' not in filtered:
            return
        self.parts.append(f'<{tag}{filtered}/>')

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in _DROP_CONTENT_TAGS:
            if tag not in _DROP_VOID_TAGS and self._drop_depth:
                self._drop_depth -= 1
            return
        if self._drop_depth or tag not in _ALLOWED_TAGS or tag in _VOID_TAGS:
            return
        self.parts.append(f'</{tag}>')

    def handle_data(self, data):
        if not self._drop_depth:
            self.parts.append(html.escape(data))

    def handle_comment(self, data):
        return

    def handle_decl(self, decl):
        return

    def handle_pi(self, data):
        return

    def unknown_decl(self, data):
        return


def sanitize_html(content: str) -> str:
    """Sanitize untrusted HTML to a conservative formatting allowlist."""
    parser = _SanitizingHTMLParser()
    parser.feed(str(content))
    parser.close()
    return ''.join(parser.parts)
