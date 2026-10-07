import os
from contextlib import contextmanager
import secrets
import inspect
from typing import Callable, Optional, Dict, Any, List, Union
from rustapi import FastAPI as RustAPIApp
from rustapi.responses import JSONResponse, HTMLResponse, Response, RedirectResponse, PlainTextResponse, StreamingResponse

from .request import request_context
from .config import AppConfig
from .page import PageRouter
from .compiler.renderer import Renderer
from .session import SessionManager, Session
from .api import APIGenerator
from .state import StateMeta, _current_session, _current_snapshot
from .components.base import Component
from .exceptions import AuthenticationThrottledError

class App:
    """PyDataUI Application."""
    
    def __init__(
        self,
        title: str = 'PyDataUI App',
        description: str = '',
        version: str = '0.2.1',
        debug: bool = False,
        theme: str = 'light',
        palette: str = 'zinc',
        tailwind_config: Optional[Dict[str, Any]] = None,
        custom_css: Optional[str] = None,
        stylesheets: Optional[List[str]] = None,
        scripts: Optional[List[str]] = None,
        head: Optional[Union[str, List[str]]] = None,
        storage: Optional[str] = None,
        **kwargs
    ):
        self.config = AppConfig(
            title=title,
            description=description,
            version=version,
            debug=debug,
            theme=theme,
            palette=palette,
            tailwind_config=tailwind_config,
            custom_css=custom_css,
            stylesheets=stylesheets,
            scripts=scripts,
            head=head,
            storage=storage,
            **kwargs
        )
        if storage is not None:
            self.config.storage = storage

        docs_url = f"{self.config.api_prefix}/docs"
        openapi_url = f"{self.config.api_prefix}/openapi.json"
        self._engine = RustAPIApp(
            title=title,
            description=description,
            version=version,
            docs_url=docs_url,
            openapi_url=openapi_url,
        )
        self.auth = None
        self._page_security = {}
        self._page_router = PageRouter()
        self._renderer = Renderer(self.config)

        from .storage import parse_storage_backend, create_session_store
        backend_type, target = parse_storage_backend(self.config.storage)
        session_store = create_session_store(self.config.storage)
        if backend_type in ("sqlite", "postgres"):
            # Ensure multi-worker cluster secret continuity:
            # If PYDATAUI_SESSION_SECRET is not in env and session_secret was not explicitly
            # passed in kwargs, load or initialize the shared cluster secret from persistent metadata.
            if "session_secret" not in kwargs and "PYDATAUI_SESSION_SECRET" not in os.environ:
                if hasattr(session_store, "get_or_create_cluster_secret"):
                    shared_secret = session_store.get_or_create_cluster_secret()
                    self.config.session_secret = shared_secret

        self._session_manager = SessionManager(secret=self.config.session_secret, max_age=self.config.session_max_age, store=session_store)
        self._api_generator = APIGenerator(self.config, self)
        self._custom_api_routes = []
        self._setup_internal_routes()
        self._register_api_endpoints()
        
    @property
    def title(self) -> str:
        """Application title."""
        return self.config.title

    @property
    def routes(self) -> Dict[str, Callable]:
        """Dictionary of registered page path to handler."""
        return {path: route.handler for path, route in self._page_router._routes.items()}

    @property
    def api_routes(self) -> Dict[str, Dict[str, Any]]:
        """Dictionary of registered custom API endpoints."""
        return {path: {'method': method, 'handler': func} for method, path, func in self._custom_api_routes}

    def page(self, path: str, title: Optional[str] = None, layout: Optional[Callable] = None, *, public: bool = False, roles=()):
        """Decorator to register a page route."""
        def decorator(func: Callable):
            self._page_security[path] = (public or path == "/login", tuple(roles))
            self._page_router.add_page(path, func, title=title, layout=layout)
            self._register_page_route(path)
            return func
        return decorator
        
    def api(self, path: str, method: str = 'GET', *, public=False, roles=(), **kwargs):
        """Custom routes inherit authentication; opt into public access explicitly."""
        import inspect
        from functools import wraps
        def decorator(func):
            signature = inspect.signature(func)
            accepts_request = 'request' in signature.parameters
            scope = 'read' if method.upper() in ('GET', 'HEAD', 'OPTIONS') else 'write'
            if inspect.iscoroutinefunction(func):
                @wraps(func)
                async def endpoint(request, *args, **params):
                    import asyncio
                    request = request_context(request, self)

                    def authorize():
                        session = self._get_session(request)
                        with session.lock:
                            return self._guard_request(
                                request, session, scope=scope, roles=roles, public=public)

                    # Session locks are threading locks: never hold one over await
                    # or block the event loop waiting for a synchronous handler.
                    denied = await asyncio.to_thread(authorize)
                    if denied is not None:
                        return denied
                    with self._request_context(request):
                        if accepts_request:
                            return await func(request, *args, **params)
                        return await func(*args, **params)
            else:
                @wraps(func)
                def endpoint(request, *args, **params):
                    request = request_context(request, self)
                    session = self._get_session(request)
                    with session.lock:
                        denied = self._guard_request(request, session, scope=scope, roles=roles, public=public)
                        if denied is not None:
                            return denied
                        with self._request_context(request):
                            if accepts_request:
                                return func(request, *args, **params)
                            return func(*args, **params)
            if not accepts_request:
                endpoint.__signature__ = signature.replace(parameters=[
                    inspect.Parameter('request', inspect.Parameter.POSITIONAL_OR_KEYWORD),
                    *signature.parameters.values()])
            getattr(self._engine, method.lower())(path, **kwargs)(endpoint)
            self._custom_api_routes.append((method, path, func))
            return func
        return decorator

    def _get_session(self, request: Any) -> Session:
        cached = getattr(request, "_pdu_session", None)
        if cached is not None:
            return cached
        session = None
        if hasattr(request, 'cookies') and isinstance(request.cookies, dict):
            cookie_val = request.cookies.get('pdu-session')
            if cookie_val:
                session = self._session_manager.parse_session_cookie(cookie_val)
                
        if not session:
            headers = getattr(request, 'headers', {})
            cookies_header = headers.get('cookie') or headers.get('Cookie') or ''
            for cookie in cookies_header.split(';'):
                cookie = cookie.strip()
                if cookie.startswith('pdu-session='):
                    cookie_val = cookie.split('=', 1)[1]
                    session = self._session_manager.parse_session_cookie(cookie_val)
                    if session:
                        break
        if not session:
            session = self._session_manager.create_session()
        request._pdu_session = session
        return session
        
    def _build_state_snapshot(self, session: Session) -> Dict[str, Dict[str, Any]]:
        from .auth.manager import current_user
        user = current_user.get()
        if 'LoginState' in StateMeta._registry:
            login = session.state_instances.setdefault('LoginState', StateMeta._registry['LoginState']())
            login.is_authenticated = bool(user)
            login.current_user_name = user.username if user else ''
        snapshot = {}
        for state_name, state_cls in StateMeta._registry.items():
            if state_name not in session.state_instances:
                session.state_instances[state_name] = state_cls()
            snapshot[state_name] = session.state_instances[state_name].to_dict()
        return snapshot
        
    def _session_cookie(self, session):
        self._session_manager.save_session(session)
        cookie = f"pdu-session={self._session_manager.get_session_cookie_value(session)}; Path=/; HttpOnly; SameSite=Lax"
        if self.config.cookie_secure:
            cookie += "; Secure"
        return cookie

    def _guard_request(self, request, session, *, scope='read', roles=(), public=False,
                       force_csrf=False):
        from .middleware.security import validate_csrf
        if scope == 'write' and not validate_csrf(request, session, force=force_csrf):
            return JSONResponse({'error': 'CSRF validation failed'}, status_code=403)
        if roles and not self.auth:
            return JSONResponse({'error': 'Authentication not configured'}, status_code=401)
        if self.auth and (not public or roles):
            token = self.auth.request_token(request) or session.data.get('auth_token', '')
            if token.startswith('pdu_live_'):
                key = self.auth.verify_api_key(token)
                user = self.auth.users.get(key.user_id) if key else None
                if key and scope not in key.scopes:
                    return JSONResponse({'error': 'Insufficient API key scope'}, status_code=403)
            else:
                user = self.auth.verify_token(token) if token else None
            if not user:
                return JSONResponse({'error': 'Authentication required'}, status_code=401)
            if roles and not any(r in user.roles for r in roles):
                return JSONResponse({'error': 'Forbidden'}, status_code=403)
            owner = session.data.get('auth_user_id')
            if owner and owner != user.id:
                return JSONResponse({'error': 'Session belongs to a different user'}, status_code=403)
            session.data['auth_user_id'] = user.id
        return None

    @contextmanager
    def _request_context(self, request):
        from .auth.manager import _current_auth_var, _current_user_var
        auth_token = _current_auth_var.set(self.auth)
        user_token = _current_user_var.set(self.auth.require_auth_middleware(request) if self.auth else None)
        try:
            yield
        finally:
            _current_user_var.reset(user_token)
            _current_auth_var.reset(auth_token)

    def _setup_internal_routes(self):
        """Register internal framework routes."""
        @self._engine.get(f'{self.config.internal_prefix}/csrf')
        def csrf_handler(request):
            request = request_context(request, self)
            from .middleware.security import csrf_token
            session = self._get_session(request)
            return JSONResponse({'csrf_token': csrf_token(session)},
                                headers={'Set-Cookie': self._session_cookie(session),
                                         'Cache-Control': 'no-store'})

        @self._engine.get('/docs')
        def docs_handler(request):
            return HTMLResponse(content=self._engine._get_swagger_ui_html(), status_code=200)

        @self._engine.get(f'{self.config.api_prefix}/docs')
        def api_docs_handler(request):
            return HTMLResponse(content=self._engine._get_swagger_ui_html(), status_code=200)

        @self._engine.get('/openapi.json')
        def openapi_handler(request):
            return self._engine.openapi()

        @self._engine.get(f'{self.config.api_prefix}/openapi.json')
        def api_openapi_handler(request):
            return self._engine.openapi()

        @self._engine.post(f'{self.config.internal_prefix}/event/{{state_name}}/{{method_name}}')
        def event_handler(request, state_name: str, method_name: str):
            return self._handle_event(request, state_name, method_name)
            
        MIME_TYPES = {
            '.css': 'text/css; charset=utf-8',
            '.js': 'application/javascript; charset=utf-8',
            '.mjs': 'application/javascript; charset=utf-8',
            '.json': 'application/json; charset=utf-8',
            '.map': 'application/json; charset=utf-8',
            '.svg': 'image/svg+xml',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.ico': 'image/x-icon',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.otf': 'font/otf',
            '.txt': 'text/plain; charset=utf-8',
            '.html': 'text/html; charset=utf-8',
        }

        def serve_file(target_path: str, ext: str):
            media_type = MIME_TYPES.get(ext) or 'application/octet-stream'
            try:
                with open(target_path, 'rb') as f:
                    content = f.read()
                return StreamingResponse(
                    iter([content]),
                    status_code=200,
                    media_type=media_type,
                    headers={"Cache-Control": "public, max-age=3600"}
                )
            except FileNotFoundError:
                return PlainTextResponse("Not found", status_code=404)

        @self._engine.get(f'{self.config.internal_prefix}/static/{{filename}}')
        def static_handler(request, filename: str):
            if '..' in filename or filename.startswith('/'):
                return PlainTextResponse("Forbidden", status_code=403)
            
            # 1. Check custom static_dir if configured
            if self.config.static_dir and os.path.isdir(self.config.static_dir):
                candidate = os.path.join(self.config.static_dir, filename)
                if os.path.isfile(candidate):
                    ext = os.path.splitext(filename)[1].lower()
                    return serve_file(candidate, ext)

            # 2. Check pydataui/styling directory
            static_base = os.path.join(os.path.dirname(__file__), 'styling')
            ext = os.path.splitext(filename)[1].lower()
            if ext == '.css':
                candidate = os.path.join(static_base, 'css', filename)
            elif ext == '.js':
                candidate = os.path.join(static_base, 'js', filename)
            else:
                candidate = os.path.join(static_base, filename)

            if os.path.isfile(candidate):
                return serve_file(candidate, ext)
            return PlainTextResponse(f"{filename} not found", status_code=404)

        @self._engine.get(f'{self.config.internal_prefix}/static/{{subfolder}}/{{filename}}')
        def static_subfolder_handler(request, subfolder: str, filename: str):
            if '..' in subfolder or '..' in filename:
                return PlainTextResponse("Forbidden", status_code=403)

            # 1. Check custom static_dir
            if self.config.static_dir and os.path.isdir(self.config.static_dir):
                candidate = os.path.join(self.config.static_dir, subfolder, filename)
                if os.path.isfile(candidate):
                    ext = os.path.splitext(filename)[1].lower()
                    return serve_file(candidate, ext)

            # 2. Check pydataui/styling
            static_base = os.path.join(os.path.dirname(__file__), 'styling')
            candidate = os.path.join(static_base, subfolder, filename)
            ext = os.path.splitext(filename)[1].lower()
            if os.path.isfile(candidate):
                return serve_file(candidate, ext)
            return PlainTextResponse(f"{subfolder}/{filename} not found", status_code=404)

        @self._engine.get(f'{self.config.internal_prefix}/health')
        def internal_health(request):
            return {"status": "ok"}
            
    def _register_page_route(self, path: str):
        """Register a page route on the pyrustapi engine."""
        page = self._page_router.get_page(path)
        
        @self._engine.get(path)
        def page_handler(request):
            request = request_context(request, self)
            session = self._get_session(request)
            public, roles = self._page_security[path]
            with session.lock:
                denied = self._guard_request(request, session, roles=roles, public=public)
                if denied is not None:
                    headers_req = getattr(request, 'headers', {}) or {}
                    accept = headers_req.get('accept') or headers_req.get('Accept') or headers_req.get('sec-fetch-dest') or ''
                    if (getattr(denied, 'status_code', None) == 401
                            and ('text/html' in str(accept).lower() or accept == 'document')
                            and self._page_router.get_page('/login')
                            and path != '/login'):
                        from rustapi.responses import RedirectResponse
                        cookie_header = self._session_cookie(session)
                        return RedirectResponse(f'/login?next={path}', status_code=303,
                                                headers={'Set-Cookie': cookie_header})
                    return denied
                with self._request_context(request):
                    return render_page(request, session)

        def render_page(request, session):
            session.current_page = path
            
            snapshot = self._build_state_snapshot(session)
            token_sess = _current_session.set(session)
            token_snap = _current_snapshot.set(snapshot)
            headers_req = getattr(request, 'headers', {})
            hx_header = headers_req.get('hx-request') or headers_req.get('HX-Request') or ''
            is_htmx = str(hx_header).lower() == 'true'
            import html
            render_failed = False
            try:
                component = (page.handler(request=request) if 'request' in inspect.signature(page.handler).parameters
                             else page.handler())
                if isinstance(component, (Response, HTMLResponse, PlainTextResponse,
                                          RedirectResponse, JSONResponse, StreamingResponse)):
                    return component
                render_handler = lambda: component
                if is_htmx:
                    content = self._renderer.render_fragment(render_handler, snapshot)
                else:
                    title = page.title or self.config.title
                    content = self._renderer.render_page(render_handler, snapshot, title=title)
            except Exception as e:
                render_failed = True
                import traceback
                print(f"\n[PyDataUI Render Error] In page handler for '{path}': {e}")
                traceback.print_exc()
                tb_str = traceback.format_exc() if self.config.debug else ''
                error_body = (
                    f'<div class="pdu-error-boundary p-6 bg-red-50 border border-red-200 rounded-lg text-red-900 m-8 shadow-md max-w-4xl mx-auto font-sans">'
                    f'<h2 class="font-bold text-xl text-red-700 flex items-center gap-2">⚠️ PyDataUI Application Error</h2>'
                    f'<p class="mt-2 text-sm text-red-600 font-medium">An error occurred while rendering <code>{html.escape(path)}</code>:</p>'
                    f'<div class="mt-2 font-bold text-red-800 text-sm bg-red-100 p-2 rounded">{html.escape(type(e).__name__ if self.config.debug else "Error")}: {html.escape(str(e) if self.config.debug else "An internal error occurred")}</div>'
                    f'<pre class="mt-3 p-4 bg-red-100/60 rounded text-xs overflow-auto font-mono text-red-900 max-h-96">{html.escape(tb_str)}</pre>'
                    f'<button class="mt-4 px-4 py-2 bg-red-600 text-white rounded text-sm font-medium hover:bg-red-700 transition" onclick="window.location.reload()">Reload Page</button>'
                    f'</div>'
                )
                if is_htmx:
                    content = error_body
                else:
                    css_url = f'{self.config.internal_prefix}/static/pydataui.css'
                    from .compiler.templates import get_base_html
                    content = get_base_html(
                        title="Error - " + self.config.title,
                        content=error_body,
                        css_url=css_url,
                        theme=getattr(self.config, 'theme', 'light'),
                        palette=getattr(self.config, 'palette', 'zinc')
                    )
            finally:
                _current_session.reset(token_sess)
                _current_snapshot.reset(token_snap)
                
            cookie_val = self._session_manager.get_session_cookie_value(session)
            resp_headers = {"Set-Cookie": self._session_cookie(session), "Cache-Control": "no-store"}
            return HTMLResponse(content=content, status_code=500 if render_failed else 200, headers=resp_headers)
            
    def _handle_event(self, request: Any, state_name: str, method_name: str) -> Any:
        request = request_context(request, self)
        session = self._get_session(request)
        cls = StateMeta._registry.get(state_name)
        if not cls or method_name not in cls.get_event_handlers():
            return PlainTextResponse('Action not found', status_code=404)
        if state_name == 'LoginState' and not self.auth:
            return PlainTextResponse('Authentication not configured', status_code=401)
        public = state_name == 'LoginState' and method_name == 'login'
        with session.lock:
            denied = self._guard_request(request, session, scope='write', roles=cls.__roles__,
                                         public=public, force_csrf=True)
            if denied is not None:
                return denied
            with self._request_context(request):
                return self._render_event(request, state_name, method_name)

    def _render_event(self, request: Any, state_name: str, method_name: str) -> Any:
        """Handle an event from HTMX with full error boundary and graceful degradation."""
        import html
        session = self._get_session(request)
        token_sess = _current_session.set(session)
        try:
            if state_name not in session.state_instances:
                if state_name in StateMeta._registry:
                    session.state_instances[state_name] = StateMeta._registry[state_name]()
                else:
                    return PlainTextResponse("State not found", status_code=404)
                    
            state_instance = session.state_instances[state_name]
            
            # Robust parsing of kwargs from query, form, and json body
            kwargs: Dict[str, Any] = {}
            if hasattr(request, 'query_params'):
                qp = request.query_params() if callable(request.query_params) else request.query_params
                if isinstance(qp, dict):
                    kwargs.update(qp)
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

            # Only the targeted state receives declared client-editable fields.
            inputs = {k: v for k, v in kwargs.items()
                      if k in state_instance.get_input_fields()}
            forbidden = set(kwargs) & (set(state_instance.get_state_vars()) -
                                       state_instance.get_input_fields())
            if forbidden:
                return JSONResponse({'error': 'Read-only input field'}, status_code=422)
            try:
                state_instance.from_dict(inputs)
            except ValueError:
                return JSONResponse({'error': 'Invalid state input'}, status_code=422)

            handler_error = None
            if hasattr(state_instance, method_name):
                func = getattr(state_instance, method_name)
                import inspect
                sig = inspect.signature(func)
                has_var_keyword = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
                if has_var_keyword:
                    call_kwargs = kwargs
                else:
                    accepted_param_names = [p.name for p in sig.parameters.values() if p.name not in ('self', 'cls')]
                    call_kwargs = {k: v for k, v in kwargs.items() if k in accepted_param_names}
                    # Fallback for single argument with mismatched name (e.g. id -> item_id)
                    if len(accepted_param_names) == 1 and len(kwargs) == 1 and not call_kwargs:
                        call_kwargs = {accepted_param_names[0]: next(iter(kwargs.values()))}
                try:
                    func(**call_kwargs)
                except Exception as e:
                    import traceback
                    handler_error = f"{type(e).__name__}: {e}" if self.config.debug else "Action failed"
                    print(f"\n[PyDataUI Event Error] In {state_name}.{method_name}(): {e}")
                    traceback.print_exc()
            
            if state_name == 'LoginState' and self.auth:
                if method_name == 'login' and state_instance.token:
                    old = session
                    self._session_manager.delete_session(old.session_id)
                    session = self._session_manager.create_session()
                    request._pdu_session = session
                    session.data['auth_token'] = state_instance.token
                    user = self.auth.verify_token(state_instance.token)
                    session.data['auth_user_id'] = user.id
                    return HTMLResponse('', headers={'Set-Cookie': self._session_cookie(session),
                                                      'HX-Redirect': '/', 'Cache-Control': 'no-store'})
                if method_name == 'logout':
                    self.auth.revoke_token(session.data.get('auth_token', ''))
                    self._session_manager.delete_session(session.session_id)
                    return HTMLResponse('', headers={'Set-Cookie': 'pdu-session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0',
                                                      'HX-Redirect': '/login', 'Cache-Control': 'no-store'})

            # Re-render the current page fragment
            headers_req = getattr(request, 'headers', {})
            current_url = headers_req.get('hx-current-url') or headers_req.get('HX-Current-URL') or headers_req.get('referer') or headers_req.get('Referer') or ''
            if current_url:
                from urllib.parse import urlparse
                path = urlparse(current_url).path
                if path and self._page_router.get_page(path):
                    session.current_page = path

            page_path = session.current_page or '/'
            page = self._page_router.get_page(page_path)
            if not page:
                all_pages = self._page_router.get_all_pages()
                page = all_pages[0] if all_pages else None
            if not page:
                return HTMLResponse("", status_code=200)
                
            public, roles = self._page_security.get(page.path if hasattr(page, 'path') else page_path, (False, ()))
            denied = self._guard_request(request, session, roles=roles, public=public)
            if denied is not None:
                return denied
            snapshot = self._build_state_snapshot(session)
            token_snap = _current_snapshot.set(snapshot)
            try:
                component = (page.handler(request=request) if 'request' in inspect.signature(page.handler).parameters
                             else page.handler())
                if isinstance(component, (Response, HTMLResponse, PlainTextResponse,
                                          RedirectResponse, JSONResponse, StreamingResponse)):
                    return component
                content = self._renderer.render_fragment(lambda: component, snapshot)
            except Exception as e:
                import traceback
                print(f"\n[PyDataUI Render Error] While re-rendering page fragment '{page_path}': {e}")
                traceback.print_exc()
                tb_str = traceback.format_exc() if self.config.debug else ''
                content = (
                    f'<div class="pdu-error-boundary p-6 bg-red-50 border border-red-200 rounded-lg text-red-900 m-4 shadow-md font-sans">'
                    f'<h3 class="font-bold text-lg text-red-700 flex items-center gap-2">⚠️ Page Re-render Error</h3>'
                    f'<p class="mt-2 text-sm text-red-600 font-semibold">{html.escape(str(e) if self.config.debug else "An internal error occurred")}</p>'
                    f'<pre class="mt-3 p-3 bg-red-100 rounded text-xs overflow-auto font-mono text-red-800 max-h-60">{html.escape(tb_str)}</pre>'
                    f'<button class="mt-4 px-4 py-2 bg-red-600 text-white rounded text-sm font-medium hover:bg-red-700 transition" onclick="window.location.reload()">Reload Page</button>'
                    f'</div>'
                )
            finally:
                _current_snapshot.reset(token_snap)
            
            # Prepend toast/alert banner if handler raised an exception
            if handler_error:
                error_toast = (
                    f'<div id="pdu-action-error" class="fixed top-4 right-4 z-[9999] max-w-md bg-red-600 text-white p-4 rounded-lg shadow-2xl border border-red-400 flex items-start gap-3" style="position:fixed;top:1rem;right:1rem;z-index:9999;max-width:28rem;background:#dc2626;color:#ffffff;padding:1rem;border-radius:0.5rem;box-shadow:0 20px 25px -5px rgba(0,0,0,0.3);">'
                    f'<div style="flex:1;">'
                    f'<div style="font-weight:bold;font-size:0.875rem;">Action Failed ({state_name}.{method_name})</div>'
                    f'<div style="font-size:0.75rem;margin-top:0.25rem;color:#fee2e2;">{html.escape(handler_error)}</div>'
                    f'</div>'
                    f'<button type="button" style="background:none;border:none;color:#ffffff;font-weight:bold;font-size:1.25rem;line-height:1;cursor:pointer;padding:0;margin-left:0.5rem;" onclick="this.closest(\'#pdu-action-error\').remove()">&times;</button>'
                    f'</div>'
                )
                content = error_toast + content

            cookie_val = self._session_manager.get_session_cookie_value(session)
            resp_headers = {"Set-Cookie": self._session_cookie(session), "Cache-Control": "no-store"}
            return HTMLResponse(content=content, status_code=200, headers=resp_headers)
        finally:
            _current_session.reset(token_sess)
    def _register_api_endpoints(self):
        """Ensure state and REST API endpoints are registered on the engine."""
        self._api_generator.generate_state_endpoints(self._engine, self._session_manager)

    def setup_auth(self, auth_manager, *, allow_registration=False):
        if self.auth is not None:
            raise ValueError('Authentication is already configured')
        self.auth = auth_manager
        self._engine.auth = auth_manager

        from .storage import parse_storage_backend, create_auth_store, MemoryAuthStore
        from .auth.manager import _UsersDictProxy, _ApiKeysDictProxy, _UsersByUsernameProxy
        backend_type, target = parse_storage_backend(self.config.storage)
        if backend_type in ("sqlite", "postgres") and hasattr(auth_manager, '_store') and isinstance(auth_manager._store, MemoryAuthStore):
            persistent_auth = create_auth_store(self.config.storage)
            for u in auth_manager._store.get_all_users().values():
                persistent_auth.save_user(u)
            for d, k in auth_manager._store.get_all_api_keys().items():
                persistent_auth.save_api_key(d, k)
            auth_manager._store = persistent_auth
            auth_manager.users = _UsersDictProxy(persistent_auth)
            auth_manager.api_keys = _ApiKeysDictProxy(persistent_auth)
            auth_manager.users_by_username = _UsersByUsernameProxy(persistent_auth)

        def body_of(request):
            try:
                value = request.json() if callable(getattr(request, 'json', None)) else {}
                return value if isinstance(value, dict) else {}
            except (ValueError, TypeError):
                return {}

        def guard(request, scope='read', public=False):
            session = self._get_session(request)
            if not public and self.auth.request_token(request).startswith('pdu_live_'):
                return JSONResponse({'error': 'User sign-in required for key management'}, status_code=403)
            return self._guard_request(request, session, scope=scope, public=public)

        @self._engine.post('/api/auth/login')
        def login_handler(request):
            request = request_context(request, self)
            denied = guard(request, 'write', public=True)
            if denied is not None:
                return denied
            body = body_of(request)
            client_ip = None
            client = getattr(request, 'client', None)
            if client and hasattr(client, 'host'):
                client_ip = client.host
            elif isinstance(client, str):
                client_ip = client
            else:
                client_ip = getattr(request, 'remote_addr', None)

            try:
                token = self.auth.authenticate(body.get('username'), body.get('password'), client_ip=client_ip)
            except AuthenticationThrottledError as throttled:
                return JSONResponse({'error': str(throttled)}, status_code=429)

            if not token:
                return PlainTextResponse('Invalid credentials', status_code=401)
            old = self._get_session(request)
            self.auth.revoke_token(old.data.get('auth_token', ''))
            self._session_manager.delete_session(old.session_id)
            session = self._session_manager.create_session()
            user = self.auth.verify_token(token)
            session.data.update(auth_token=token, auth_user_id=user.id)
            request._pdu_session = session
            return JSONResponse({'token': token}, headers={'Set-Cookie': self._session_cookie(session),
                                                          'Cache-Control': 'no-store'})

        @self._engine.post('/api/auth/logout')
        def logout_handler(request):
            request = request_context(request, self)
            denied = guard(request, 'write')
            if denied is not None:
                return denied
            session = self._get_session(request)
            self.auth.revoke_token(self.auth.request_token(request))
            self.auth.revoke_token(session.data.get('auth_token', ''))
            self._session_manager.delete_session(session.session_id)
            return JSONResponse({'status': 'ok'}, headers={'Set-Cookie': 'pdu-session=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0'})

        @self._engine.get('/api/auth/me')
        def me_handler(request):
            request = request_context(request, self)
            denied = self._guard_request(request, self._get_session(request))
            if denied is not None:
                return denied
            return {'user': self.auth.require_auth_middleware(request).public_dict()}

        @self._engine.post('/api/auth/register')
        def register_handler(request):
            request = request_context(request, self)
            if not allow_registration:
                return PlainTextResponse('Registration disabled', status_code=403)
            denied = guard(request, 'write', public=True)
            if denied is not None:
                return denied
            body = body_of(request)
            if 'roles' in body:
                return PlainTextResponse('Roles are assigned by administrators', status_code=400)
            try:
                user = self.auth.add_user(body.get('username'), body.get('password'), body.get('email', ''))
                return {'user': user.public_dict()}
            except ValueError as exc:
                return PlainTextResponse(str(exc), status_code=400)

        @self._engine.get('/api/auth/keys')
        def get_keys_handler(request):
            request = request_context(request, self)
            denied = guard(request)
            if denied is not None:
                return denied
            user = self.auth.require_auth_middleware(request)
            return {'keys': [k.public_dict() for k in self.auth.list_api_keys(user.id)]}

        @self._engine.post('/api/auth/keys')
        def create_key_handler(request):
            request = request_context(request, self)
            denied = guard(request, 'write')
            if denied is not None:
                return denied
            user = self.auth.require_auth_middleware(request)
            body = body_of(request)
            try:
                key = self.auth.create_api_key(body.get('name', 'Key'), user.id,
                                               body.get('scopes', ['read']), body.get('expires_days'))
                return {'key': {**key.public_dict(), 'key': key.key}}
            except ValueError as exc:
                return PlainTextResponse(str(exc), status_code=400)

        @self._engine.delete('/api/auth/keys/{key_id}')
        def delete_key_handler(request, key_id: str):
            request = request_context(request, self)
            denied = guard(request, 'write')
            if denied is not None:
                return denied
            user = self.auth.require_auth_middleware(request)
            if not self.auth.revoke_api_key(key_id, user_id=user.id):
                return PlainTextResponse('Key not found', status_code=404)
            return {'status': 'ok'}

    def run(self, host: Optional[str] = None, port: Optional[int] = None, reload: bool = False, workers: int = 1, share: bool = False, auth: Optional[Any] = None):
        """Run the application."""
        if auth:
            self.setup_auth(auth)
            
        self._register_api_endpoints()

        # Auto-upgrade to SQLite WAL storage if running multiple workers without persistent store
        if workers > 1:
            from .storage import MemorySessionStore, SQLiteSessionStore, SQLiteAuthStore
            if isinstance(self._session_manager._store, MemorySessionStore):
                default_db = ".pydataui_storage.db"
                sqlite_session = SQLiteSessionStore(default_db)
                if "PYDATAUI_SESSION_SECRET" not in os.environ:
                    shared_secret = sqlite_session.get_or_create_cluster_secret()
                    self.config.session_secret = shared_secret
                    self._session_manager._secret = shared_secret.encode('utf-8')
                for sid, s in list(self._session_manager._active_sessions.items()):
                    sqlite_session.save(sid, s.to_dict(), s.last_accessed)
                self._session_manager._store = sqlite_session

                if self.auth and hasattr(self.auth, '_store'):
                    from .storage import MemoryAuthStore
                    from .auth.manager import _UsersDictProxy, _ApiKeysDictProxy, _UsersByUsernameProxy
                    if isinstance(self.auth._store, MemoryAuthStore):
                        sqlite_auth = SQLiteAuthStore(default_db)
                        for u in self.auth._store.get_all_users().values():
                            sqlite_auth.save_user(u)
                        for d, k in self.auth._store.get_all_api_keys().items():
                            sqlite_auth.save_api_key(d, k)
                        self.auth._store = sqlite_auth
                        self.auth.users = _UsersDictProxy(sqlite_auth)
                        self.auth.api_keys = _ApiKeysDictProxy(sqlite_auth)
                        self.auth.users_by_username = _UsersByUsernameProxy(sqlite_auth)
                print(f'  [Storage] Multi-worker mode enabled ({workers} workers). Auto-configured SQLite WAL storage at {default_db}', flush=True)

        h = host or self.config.host
        p = port or self.config.port
        print(f'\n  PyDataUI v{self.config.version}', flush=True)
        print(f'  Running on http://{h}:{p}', flush=True)
        if share:
            from .tunnel import TunnelManager
            self._tunnel = TunnelManager(port=p)
            url = self._tunnel.create_tunnel(p)
            if url:
                print(f'  Public URL: {url}', flush=True)
            else:
                print(f'  [Warning] Could not establish public tunnel. Falling back to local URL.', flush=True)
                
        print(f'  API docs at http://{h}:{p}/docs and http://{h}:{p}{self.config.api_prefix}/docs', flush=True)
        print(f'  REST API root at http://{h}:{p}{self.config.api_prefix}\n', flush=True)
        self._engine.run(host=h, port=p, reload=reload, workers=workers)
