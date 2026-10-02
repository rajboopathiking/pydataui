import os
from typing import Callable, Optional, Dict, Any
from rustapi import FastAPI as RustAPIApp
from rustapi.responses import HTMLResponse, Response, RedirectResponse, PlainTextResponse

from .config import AppConfig
from .page import PageRouter
from .compiler.renderer import Renderer
from .session import SessionManager, Session
from .api import APIGenerator
from .state import StateMeta
from .components.base import Component

class App:
    """PyDataUI Application."""
    
    def __init__(self, title: str = 'PyDataUI App', description: str = '', version: str = '0.1.0', debug: bool = False, **kwargs):
        self.config = AppConfig(title=title, description=description, version=version, debug=debug, **kwargs)
        docs_url = f"{self.config.api_prefix}/docs"
        openapi_url = f"{self.config.api_prefix}/openapi.json"
        self._engine = RustAPIApp(
            title=title,
            description=description,
            version=version,
            docs_url=docs_url,
            openapi_url=openapi_url,
        )
        self._page_router = PageRouter()
        self._renderer = Renderer(self.config)
        self._session_manager = SessionManager(secret=self.config.session_secret, max_age=self.config.session_max_age)
        self._api_generator = APIGenerator(self.config)
        self._custom_api_routes = []
        self._setup_internal_routes()
        
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

    def page(self, path: str, title: Optional[str] = None, layout: Optional[Callable] = None):
        """Decorator to register a page route."""
        def decorator(func: Callable):
            self._page_router.add_page(path, func, title=title, layout=layout)
            self._register_page_route(path)
            return func
        return decorator
        
    def api(self, path: str, method: str = 'GET', **kwargs):
        """Decorator to register a custom API endpoint."""
        def decorator(func: Callable):
            route_method = getattr(self._engine, method.lower())
            route_method(path, **kwargs)(func)
            self._custom_api_routes.append((method, path, func))
            return func
        return decorator
        
    def _get_session(self, request: Any) -> Session:
        headers = getattr(request, 'headers', {})
        cookies_header = headers.get('cookie') or headers.get('Cookie') or ''
        session = None
        for cookie in cookies_header.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('pdu-session='):
                cookie_val = cookie.split('=', 1)[1]
                session = self._session_manager.parse_session_cookie(cookie_val)
                if session:
                    break
        if not session:
            session = self._session_manager.create_session()
        return session
        
    def _build_state_snapshot(self, session: Session) -> Dict[str, Dict[str, Any]]:
        snapshot = {}
        for state_name, state_cls in StateMeta._registry.items():
            if state_name not in session.state_instances:
                session.state_instances[state_name] = state_cls()
            snapshot[state_name] = session.state_instances[state_name].to_dict()
        return snapshot
        
    def _setup_internal_routes(self):
        """Register internal framework routes."""
        # Ensure /docs and /openapi.json redirect to /api/docs and /api/openapi.json
        @self._engine.get('/docs')
        def docs_redirect(request):
            return RedirectResponse(url=f'{self.config.api_prefix}/docs')

        @self._engine.get('/openapi.json')
        def openapi_redirect(request):
            return RedirectResponse(url=f'{self.config.api_prefix}/openapi.json')

        @self._engine.post(f'{self.config.internal_prefix}/event/{{state_name}}/{{method_name}}')
        def event_handler(request, state_name: str, method_name: str):
            return self._handle_event(request, state_name, method_name)
            
        @self._engine.get(f'{self.config.internal_prefix}/static/{{filename}}')
        def static_handler(request, filename: str):
            if filename == 'pydataui.css':
                css_path = os.path.join(
                    os.path.dirname(__file__), 'styling', 'css', 'pydataui.css'
                )
                try:
                    with open(css_path, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    return Response(content=css_content, status_code=200, headers={"Content-Type": "text/css; charset=utf-8"})
                except FileNotFoundError:
                    return Response(content="/* PyDataUI CSS not found */", status_code=200, headers={"Content-Type": "text/css; charset=utf-8"})
            return PlainTextResponse("Not found", status_code=404)
            
        @self._engine.get(f'{self.config.internal_prefix}/health')
        def internal_health(request):
            return {"status": "ok"}
            
    def _register_page_route(self, path: str):
        """Register a page route on the pyrustapi engine."""
        page = self._page_router.get_page(path)
        
        @self._engine.get(path)
        def page_handler(request):
            session = self._get_session(request)
            session.current_page = path
            
            snapshot = self._build_state_snapshot(session)
            
            headers_req = getattr(request, 'headers', {})
            hx_header = headers_req.get('hx-request') or headers_req.get('HX-Request') or ''
            is_htmx = str(hx_header).lower() == 'true'
            if is_htmx:
                content = self._renderer.render_fragment(page.handler, snapshot)
            else:
                title = page.title or self.config.title
                content = self._renderer.render_page(page.handler, snapshot, title=title)
                
            cookie_val = self._session_manager.get_session_cookie_value(session)
            resp_headers = {"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
            return HTMLResponse(content=content, status_code=200, headers=resp_headers)
            
    def _handle_event(self, request: Any, state_name: str, method_name: str) -> Any:
        """Handle an event from HTMX."""
        session = self._get_session(request)
        
        if state_name not in session.state_instances:
            if state_name in StateMeta._registry:
                session.state_instances[state_name] = StateMeta._registry[state_name]()
            else:
                return PlainTextResponse("State not found", status_code=404)
                
        state_instance = session.state_instances[state_name]
        
        if hasattr(state_instance, method_name):
            func = getattr(state_instance, method_name)
            # Basic parsing of kwargs from body if any
            kwargs = {}
            if hasattr(request, 'headers') and request.headers.get('content-type', '').startswith('application/json') and hasattr(request, 'json'):
                kwargs = request.json() or {}
            elif hasattr(request, 'form') and callable(request.form):
                kwargs = request.form() or {}
                
            if isinstance(kwargs, dict):
                func(**kwargs)
            else:
                func()
        
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
            
        snapshot = self._build_state_snapshot(session)
        content = self._renderer.render_fragment(page.handler, snapshot)
        
        cookie_val = self._session_manager.get_session_cookie_value(session)
        resp_headers = {"Set-Cookie": f"pdu-session={cookie_val}; Path=/; HttpOnly"}
        return HTMLResponse(content=content, status_code=200, headers=resp_headers)
        
    def run(self, host: Optional[str] = None, port: Optional[int] = None, reload: bool = False, workers: int = 1):
        """Run the application."""
        self._api_generator.generate_state_endpoints(self._engine, self._session_manager)
        
        h = host or self.config.host
        p = port or self.config.port
        print(f'\n  PyDataUI v{self.config.version}')
        print(f'  Running on http://{h}:{p}')
        print(f'  API docs at http://{h}:{p}{self.config.api_prefix}/docs (or /docs)\n')
        self._engine.run(host=h, port=p, reload=reload, workers=workers)
