import inspect
from typing import Any, Dict, Set
from rustapi.responses import JSONResponse
from .request import request_context
from .config import AppConfig
from .session import SessionManager, Session
from .state import StateMeta
from .utils import to_json_compatible

class APIGenerator:
    """Generates REST API endpoints for all registered State classes."""
    def __init__(self, config: AppConfig, app):
        self.config = config
        self.app = app
        self._registered_states: Set[str] = set()
        self._root_registered = False

    def _get_session_and_stateless(self, request, session_manager):
        # A request-local context reuses exactly one verified session.
        return self.app._get_session(request), False

    def _extract_kwargs(self, request: Any) -> Dict[str, Any]:
        kwargs: Dict[str, Any] = {}
        if hasattr(request, 'query_params'):
            try:
                qp = request.query_params() if callable(request.query_params) else request.query_params
                if isinstance(qp, dict):
                    kwargs.update(qp)
            except Exception:
                pass
        if hasattr(request, 'form'):
            try:
                f = request.form() if callable(request.form) else request.form
                if isinstance(f, dict):
                    kwargs.update(f)
            except Exception:
                pass
        if hasattr(request, 'json'):
            try:
                j = request.json() if callable(request.json) else request.json
                if isinstance(j, dict):
                    kwargs.update(j)
            except Exception:
                pass
        if hasattr(request, 'body'):
            try:
                b = request.body() if callable(request.body) else request.body
                if isinstance(b, (bytes, str)) and b:
                    b_str = b.decode('utf-8', errors='ignore') if isinstance(b, bytes) else b
                    b_str_s = b_str.strip()
                    if b_str_s and not b_str_s.startswith('{') and '=' in b_str_s:
                        from urllib.parse import parse_qs
                        parsed = parse_qs(b_str_s)
                        for k, v in parsed.items():
                            if k not in kwargs:
                                kwargs[k] = v[0] if len(v) == 1 else v
            except Exception:
                pass
        return kwargs

    def _ensure_instance(self, session, state_name, state_cls):
        if state_name not in session.state_instances:
            session.state_instances[state_name] = state_cls()
        return session.state_instances[state_name]

    def _protected(self, scope, state_cls=None):
        from functools import wraps
        def decorate(func):
            @wraps(func)
            def wrapped(request, *args, **kwargs):
                request = request_context(request, self.app)
                session = self.app._get_session(request)
                with session.lock:
                    denied = self.app._guard_request(request, session, scope=scope,
                                                     roles=getattr(state_cls, '__roles__', ()))
                    if denied is not None:
                        return denied
                    with self.app._request_context(request):
                        return func(request, *args, **kwargs)
            return wrapped
        return decorate

    def generate_state_endpoints(self, engine: Any, session_manager: SessionManager) -> None:
        """Register API routes on the pyrustapi engine for all State classes."""
        prefix = self.config.api_prefix

        if not self._root_registered:
            self._root_registered = True

            @engine.get(f'{prefix}')
            @engine.get(f'{prefix}/')
            @self._protected("read")
            def api_catalog(request):
                states_info = {}
                for s_name, s_cls in StateMeta._registry.items():
                    if not self.config.auto_api or not s_cls.__api__:
                        continue
                    methods = list(s_cls.get_event_handlers())
                    vars_dict = {f: var.default for f, var in s_cls.get_public_state_vars().items()}
                    states_info[s_name] = {
                        "endpoint": f"{prefix}/{s_name}",
                        "state_endpoint": f"{prefix}/state/{s_name}",
                        "methods": methods,
                        "fields": list(vars_dict.keys()),
                        "defaults": vars_dict,
                    }
                return {
                    "framework": "PyDataUI",
                    "title": self.config.title,
                    "version": self.config.version,
                    "description": self.config.description or "PyDataUI Full-Stack API",
                    "docs": f"{prefix}/docs",
                    "swagger_ui": "/docs",
                    "openapi": "/openapi.json",
                    "health": f"{prefix}/health",
                    "states": states_info,
                    "routes": [
                        {"method": "GET", "path": f"{prefix}", "desc": "API catalog"},
                        {"method": "GET", "path": f"{prefix}/health", "desc": "Health check"},
                        {"method": "GET", "path": f"{prefix}/docs", "desc": "Swagger UI documentation"},
                        {"method": "GET", "path": f"{prefix}/{{state}}", "desc": "Get state JSON"},
                        {"method": "GET", "path": f"{prefix}/{{state}}/{{field}}", "desc": "Get specific state field"},
                        {"method": "PUT", "path": f"{prefix}/{{state}}", "desc": "Update state values"},
                        {"method": "POST", "path": f"{prefix}/{{state}}/{{method}}", "desc": "Execute state action"},
                        {"method": "DELETE", "path": f"{prefix}/{{state}}", "desc": "Reset state to defaults"},
                    ]
                }

            @engine.get(f'{prefix}/health')
            def health_check(request):
                return {"status": "ok", "version": self.config.version}

            @engine.get(f'{prefix}/pages')
            def list_pages(request):
                return {"status": "ok", "message": "Pages API"}

        # Dynamic state endpoints
        for state_name, state_cls in StateMeta._registry.items():
            if not state_cls.__api__ or not self.config.auto_api:
                continue
            if state_name in self._registered_states:
                continue
            self._registered_states.add(state_name)

            urls = [
                f'{prefix}/{state_name}',
                f'{prefix}/state/{state_name}',
            ]

            for base_url in urls:
                self._register_single_state_routes(engine, session_manager, base_url, state_name, state_cls)

    def _register_single_state_routes(
        self, engine: Any, session_manager: SessionManager, base_url: str, state_name: str, state_cls: Any
    ):
        @engine.get(base_url)
        @self._protected("read", state_cls)
        def get_state(request):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            return JSONResponse(
                content=to_json_compatible(inst.to_dict()),
                status_code=200,
                headers={"Set-Cookie": self.app._session_cookie(session), "Cache-Control": "no-store"}
            )

        @engine.get(f'{base_url}/{{field}}')
        @self._protected('read', state_cls)
        def get_state_field(request, field: str):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            if hasattr(inst, field) and field in state_cls.get_public_state_vars():
                return JSONResponse(
                    content=to_json_compatible({field: getattr(inst, field)}),
                    status_code=200,
                    headers={"Set-Cookie": self.app._session_cookie(session), "Cache-Control": "no-store"}
                )
            return JSONResponse(content={"error": f"Field '{field}' not found"}, status_code=404)

        @engine.put(base_url)
        @self._protected("write", state_cls)
        def update_state(request):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            data = self._extract_kwargs(request)
            try:
                inst.from_dict(data)
            except ValueError:
                return JSONResponse(content={"error": "Invalid state input"}, status_code=422)
            return JSONResponse(
                content=to_json_compatible(inst.to_dict()),
                status_code=200,
                headers={"Set-Cookie": self.app._session_cookie(session), "Cache-Control": "no-store"}
            )

        @engine.delete(base_url)
        @self._protected("write", state_cls)
        def reset_state(request):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            inst.reset()
            return JSONResponse(
                content=to_json_compatible({"status": "reset", "state": inst.to_dict()}),
                status_code=200,
                headers={"Set-Cookie": self.app._session_cookie(session), "Cache-Control": "no-store"}
            )

        @engine.post(f'{base_url}/{{method}}')
        @self._protected("write", state_cls)
        def call_state_method(request, method: str):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            if method in state_cls.get_event_handlers():
                func = getattr(inst, method)
                kwargs = self._extract_kwargs(request)
                sig = inspect.signature(func)
                has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                if has_var_keyword:
                    call_kwargs = kwargs
                else:
                    accepted_param_names = [p.name for p in sig.parameters.values() if p.name not in ('self', 'cls')]
                    call_kwargs = {k: v for k, v in kwargs.items() if k in accepted_param_names}
                    if len(accepted_param_names) == 1 and len(kwargs) == 1 and not call_kwargs:
                        call_kwargs = {accepted_param_names[0]: next(iter(kwargs.values()))}

                try:
                    result = func(**call_kwargs)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return JSONResponse(
                        content={"error": str(e) if self.config.debug else "Action failed"},
                        status_code=400,
                        headers={"Set-Cookie": self.app._session_cookie(session), "Cache-Control": "no-store"}
                    )


                if result is not None:
                    resp_data = {"result": result, "state": inst.to_dict()}
                else:
                    resp_data = inst.to_dict()
                return JSONResponse(
                    content=to_json_compatible(resp_data),
                    status_code=200,
                    headers={"Set-Cookie": self.app._session_cookie(session), "Cache-Control": "no-store"}
                )
            return JSONResponse(content={"error": f"Method '{method}' not found"}, status_code=404)
