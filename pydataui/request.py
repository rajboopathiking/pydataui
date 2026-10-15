"""Python-owned request context normalizing FastAPI/Starlette and PyRustAPI requests."""
from __future__ import annotations
from collections.abc import Mapping
import inspect
import json
from typing import Any, Dict, Optional
from urllib.parse import parse_qs


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
