from typing import Any
from rustapi.responses import JSONResponse
from .config import AppConfig
from .session import SessionManager, Session
from .state import StateMeta

class APIGenerator:
    """Generates REST API endpoints for all registered State classes."""
    def __init__(self, config: AppConfig):
        self.config = config
        
    def _get_session_from_request(self, request: Any, session_manager: SessionManager) -> Session:
        """Extract session from request cookies."""
        cookies_header = request.headers.get('cookie', '')
        session_cookie = None
        for cookie in cookies_header.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('pdu-session='):
                session_cookie = cookie.split('=', 1)[1]
                break
        return session_manager.get_or_create_session(session_cookie)
        
    def generate_state_endpoints(self, engine: Any, session_manager: SessionManager) -> None:
        """Register API routes on the pyrustapi engine for all State classes."""
        
        @engine.get(f'{self.config.api_prefix}/health')
        def health_check(request):
            return {"status": "ok", "version": self.config.version}
            
        @engine.get(f'{self.config.api_prefix}/pages')
        def list_pages(request):
            # Assumes router is accessible somewhere, but we'll return a simple response
            return {"status": "ok", "message": "Pages API"}

        # Dynamic state endpoints
        for state_name, state_cls in StateMeta._registry.items():
            base_url = f'{self.config.api_prefix}/state/{state_name}'
            
            @engine.get(base_url)
            def get_state(request, state_name=state_name, state_cls=state_cls):
                session = self._get_session_from_request(request, session_manager)
                if state_name not in session.state_instances:
                    session.state_instances[state_name] = state_cls()
                return session.state_instances[state_name].to_dict()
                
            @engine.get(f'{base_url}/{{field}}')
            def get_state_field(request, field: str, state_name=state_name, state_cls=state_cls):
                session = self._get_session_from_request(request, session_manager)
                if state_name not in session.state_instances:
                    session.state_instances[state_name] = state_cls()
                state_instance = session.state_instances[state_name]
                if hasattr(state_instance, field):
                    return {field: getattr(state_instance, field)}
                return JSONResponse({"error": "Field not found"}, status_code=404)
                
            @engine.put(base_url)
            def update_state(request, state_name=state_name, state_cls=state_cls):
                session = self._get_session_from_request(request, session_manager)
                if state_name not in session.state_instances:
                    session.state_instances[state_name] = state_cls()
                state_instance = session.state_instances[state_name]
                data = request.json() if hasattr(request, 'json') else {}
                state_instance.from_dict(data)
                return state_instance.to_dict()
                
            @engine.delete(base_url)
            def reset_state(request, state_name=state_name, state_cls=state_cls):
                session = self._get_session_from_request(request, session_manager)
                if state_name not in session.state_instances:
                    session.state_instances[state_name] = state_cls()
                session.state_instances[state_name].reset()
                return {"status": "reset"}
                
            @engine.post(f'{base_url}/{{method}}')
            def call_state_method(request, method: str, state_name=state_name, state_cls=state_cls):
                session = self._get_session_from_request(request, session_manager)
                if state_name not in session.state_instances:
                    session.state_instances[state_name] = state_cls()
                state_instance = session.state_instances[state_name]
                if hasattr(state_instance, method) and callable(getattr(state_instance, method)):
                    func = getattr(state_instance, method)
                    # Attempt to pass json body as kwargs if present
                    kwargs = request.json() if hasattr(request, 'json') and request.body else {}
                    if isinstance(kwargs, dict):
                        func(**kwargs)
                    else:
                        func()
                    return state_instance.to_dict()
                return JSONResponse({"error": "Method not found"}, status_code=404)
