"""Python-owned request context normalizing FastAPI/Starlette and PyRustAPI requests."""
from __future__ import annotations
from collections.abc import Mapping
import inspect
import json
from email import policy
from email.parser import BytesParser
from typing import Any, Dict, Optional
from urllib.parse import parse_qs


class UploadedFile:
    """Small synchronous file wrapper for multipart uploads on event routes."""

    def __init__(self, filename: str, content: bytes, content_type: str = ''):
        self.filename = filename
        self.content = content
        self.content_type = content_type
        self.size = len(content)
        self._position = 0

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            data = self.content[self._position:]
            self._position = len(self.content)
            return data
        data = self.content[self._position:self._position + size]
        self._position += len(data)
        return data

    def seek(self, offset: int, whence: int = 0) -> int:
        if whence == 1:
            offset += self._position
        elif whence == 2:
            offset += len(self.content)
        self._position = max(0, min(offset, len(self.content)))
        return self._position

    def close(self) -> None:
        return None


def _parse_multipart(body: bytes, content_type: str) -> Optional[Dict[str, Any]]:
    """Parse a cached multipart body without requiring an async request."""
    if 'boundary=' not in content_type.lower():
        return None
    try:
        message = BytesParser(policy=policy.default).parsebytes(
            b'Content-Type: ' + content_type.encode('latin-1') +
            b'\r\nMIME-Version: 1.0\r\n\r\n' + body
        )
    except Exception:
        return None
    if not message.is_multipart():
        return None
    result: Dict[str, Any] = {}
    for part in message.iter_parts():
        name = part.get_param('name', header='content-disposition')
        if not name:
            continue
        payload = part.get_payload(decode=True) or b''
        filename = part.get_filename()
        if filename is not None:
            result[name] = UploadedFile(filename, payload, part.get_content_type())
        else:
            charset = part.get_content_charset() or 'utf-8'
            result[name] = payload.decode(charset, errors='replace')
    return result


class QueryParamsDict(dict):
    """Dictionary supporting both property access and method call syntax."""
    def __call__(self) -> "QueryParamsDict":
        return self


class RequestContext:
    """Wraps incoming requests to provide uniform access across all backends."""

    def __init__(self, request: Any, app: Optional[Any] = None):
        self._request = request
        self.app = app or getattr(request, "app", None)
        self._cached_body: Optional[bytes] = None
        self._cached_json: Optional[Dict[str, Any]] = None
        self._cached_form: Optional[Dict[str, Any]] = None

    @property
    def query_params(self) -> QueryParamsDict:
        raw_qp = getattr(self._request, "query_params", None)
        if callable(raw_qp):
            try:
                raw_qp = raw_qp()
            except Exception:
                pass
        if isinstance(raw_qp, Mapping):
            return QueryParamsDict(raw_qp)
        elif isinstance(raw_qp, dict):
            return QueryParamsDict(raw_qp)
        return QueryParamsDict()

    def body(self) -> bytes:
        if self._cached_body is not None:
            return self._cached_body
        scope = getattr(self._request, "scope", None)
        if isinstance(scope, dict) and "_cached_body" in scope:
            self._cached_body = scope["_cached_body"]
            return self._cached_body
        if hasattr(self._request, "_body") and self._request._body is not None:
            self._cached_body = self._request._body
            return self._cached_body

        raw_b = getattr(self._request, "body", None)
        if callable(raw_b):
            try:
                res = raw_b()
                if not inspect.isawaitable(res):
                    self._cached_body = res if isinstance(res, bytes) else str(res).encode("utf-8")
                    return self._cached_body
            except Exception:
                pass
        elif isinstance(raw_b, (bytes, str)):
            self._cached_body = raw_b if isinstance(raw_b, bytes) else raw_b.encode("utf-8")
            return self._cached_body
        return b""

    def json(self) -> Dict[str, Any]:
        if self._cached_json is not None:
            return self._cached_json
        scope = getattr(self._request, "scope", None)
        if isinstance(scope, dict) and "_cached_json" in scope and isinstance(scope["_cached_json"], dict):
            self._cached_json = scope["_cached_json"]
            return self._cached_json

        if not hasattr(self._request, "scope"):
            raw_j = getattr(self._request, "json", None)
            if callable(raw_j) and not inspect.iscoroutinefunction(raw_j):
                try:
                    res = raw_j()
                    if not inspect.isawaitable(res) and isinstance(res, dict):
                        self._cached_json = res
                        return self._cached_json
                except Exception:
                    pass

        b = self.body()
        if b:
            try:
                b_str = b.decode("utf-8", errors="ignore").strip()
                if b_str.startswith("{") or b_str.startswith("["):
                    parsed = json.loads(b_str)
                    if isinstance(parsed, dict):
                        self._cached_json = parsed
                        return self._cached_json
            except Exception:
                pass
        return {}

    def form(self) -> Dict[str, Any]:
        if self._cached_form is not None:
            return self._cached_form
        scope = getattr(self._request, "scope", None)
        if isinstance(scope, dict) and "_cached_form" in scope and isinstance(scope["_cached_form"], dict):
            self._cached_form = scope["_cached_form"]
            return self._cached_form

        if not hasattr(self._request, "scope"):
            raw_f = getattr(self._request, "form", None)
            if callable(raw_f) and not inspect.iscoroutinefunction(raw_f):
                try:
                    res = raw_f()
                    if not inspect.isawaitable(res) and isinstance(res, (dict, Mapping)):
                        self._cached_form = dict(res)
                        return self._cached_form
                except Exception:
                    pass

        b = self.body()
        if b:
            headers = getattr(self._request, 'headers', {}) or {}
            content_type = headers.get('content-type') or headers.get('Content-Type') or ''
            if 'multipart/form-data' in str(content_type).lower():
                parsed = _parse_multipart(b, str(content_type))
                if parsed is not None:
                    self._cached_form = parsed
                    return self._cached_form
            try:
                b_str = b.decode("utf-8", errors="ignore").strip()
                if b_str and not b_str.startswith("{") and not b_str.startswith("[") and "=" in b_str:
                    parsed = parse_qs(b_str)
                    self._cached_form = {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                    return self._cached_form
            except Exception:
                pass
        return {}

    def __getattr__(self, name: str) -> Any:
        return getattr(self._request, name)


def request_context(request: Any, app: Optional[Any] = None) -> RequestContext:
    if isinstance(request, RequestContext):
        if app is not None and request.app is None:
            request.app = app
        return request
    return RequestContext(request, app)
