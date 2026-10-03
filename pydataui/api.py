import copy
import inspect
from typing import Any, Dict, Set
from rustapi.responses import JSONResponse
from .config import AppConfig
from .session import SessionManager, Session
from .state import StateMeta
from .utils import to_json_compatible

class APIGenerator:
    """Generates REST API endpoints for all registered State classes."""
    def __init__(self, config: AppConfig):
        self.config = config
        self._registered_states: Set[str] = set()
        self._root_registered = False

    def _get_session_and_stateless(self, request: Any, session_manager: SessionManager):
        headers = getattr(request, 'headers', {})
        cookies_header = headers.get('cookie') or headers.get('Cookie') or ''
        session = None
        has_cookie = False
        for cookie in cookies_header.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('pdu-session='):
                cookie_val = cookie.split('=', 1)[1]
                session = session_manager.parse_session_cookie(cookie_val)
                if session:
                    has_cookie = True
                    break
        if not session:
            session = session_manager.create_session()
        return session, not has_cookie

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

    def _ensure_instance(self, session: Session, state_name: str, state_cls: Any) -> Any:
        if state_name not in session.state_instances:
            inst = state_cls()
            if hasattr(state_cls, '_class_store'):
                for k, v in state_cls._class_store.items():
                    if hasattr(inst, k):
                        setattr(inst, k, copy.deepcopy(v) if isinstance(v, (list, dict, set)) else v)
            session.state_instances[state_name] = inst
        return session.state_instances[state_name]

    def _sync_to_class_store(self, state_cls: Any, state_instance: Any):
        if hasattr(state_cls, '_class_store'):
            for k, v in state_instance.to_dict().items():
                state_cls._class_store[k] = copy.deepcopy(v) if isinstance(v, (list, dict, set)) else v

    def generate_state_endpoints(self, engine: Any, session_manager: SessionManager) -> None:
        """Register API routes on the pyrustapi engine for all State classes."""
        prefix = self.config.api_prefix

        if not self._root_registered:
            self._root_registered = True

            @engine.get(f'{prefix}')
            @engine.get(f'{prefix}/')
            def api_catalog(request):
                states_info = {}
                for s_name, s_cls in StateMeta._registry.items():
                    methods = [
                        m for m in dir(s_cls)
                        if callable(getattr(s_cls, m)) and not m.startswith('_') and m not in (
                            'to_dict', 'from_dict', 'reset', 'get_state_vars', 'get_event_handlers'
                        )
                    ]
                    vars_dict = {f: var.default for f, var in s_cls.get_state_vars().items()}
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
        def get_state(request, state_name=state_name, state_cls=state_cls):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            cookie_val = session_manager.get_session_cookie_value(session)
            return JSONResponse(
                content=to_json_compatible(inst.to_dict()),
                status_code=200,
                headers={"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
            )

        @engine.get(f'{base_url}/{{field}}')
        def get_state_field(request, field: str, state_name=state_name, state_cls=state_cls):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            cookie_val = session_manager.get_session_cookie_value(session)
            if hasattr(inst, field) and field in state_cls.get_state_vars():
                return JSONResponse(
                    content=to_json_compatible({field: getattr(inst, field)}),
                    status_code=200,
                    headers={"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
                )
            return JSONResponse(content={"error": f"Field '{field}' not found"}, status_code=404)

        @engine.put(base_url)
        def update_state(request, state_name=state_name, state_cls=state_cls):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            data = self._extract_kwargs(request)
            inst.from_dict(data)
            if stateless:
                self._sync_to_class_store(state_cls, inst)
            cookie_val = session_manager.get_session_cookie_value(session)
            return JSONResponse(
                content=to_json_compatible(inst.to_dict()),
                status_code=200,
                headers={"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
            )

        @engine.delete(base_url)
        def reset_state(request, state_name=state_name, state_cls=state_cls):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            inst.reset()
            if stateless:
                self._sync_to_class_store(state_cls, inst)
            cookie_val = session_manager.get_session_cookie_value(session)
            return JSONResponse(
                content=to_json_compatible({"status": "reset", "state": inst.to_dict()}),
                status_code=200,
                headers={"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
            )

        @engine.post(f'{base_url}/{{method}}')
        def call_state_method(request, method: str, state_name=state_name, state_cls=state_cls):
            session, stateless = self._get_session_and_stateless(request, session_manager)
            inst = self._ensure_instance(session, state_name, state_cls)
            if hasattr(inst, method) and callable(getattr(inst, method)):
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

                cookie_val = session_manager.get_session_cookie_value(session)
                try:
                    result = func(**call_kwargs)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return JSONResponse(
                        content={"error": str(e), "type": type(e).__name__},
                        status_code=400,
                        headers={"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
                    )

                if stateless:
                    self._sync_to_class_store(state_cls, inst)

                if result is not None:
                    resp_data = {"result": result, "state": inst.to_dict()}
                else:
                    resp_data = inst.to_dict()
                return JSONResponse(
                    content=to_json_compatible(resp_data),
                    status_code=200,
                    headers={"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
                )
            return JSONResponse(content={"error": f"Method '{method}' not found"}, status_code=404)
