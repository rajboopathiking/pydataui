from typing import Any
from ..session import SessionManager

class SessionMiddleware:
    """Middleware that attaches session to each request."""
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        
    def __call__(self, request: Any, handler: Any) -> Any:
        cookies = request.headers.get('cookie', '')
        session_id = None
        for cookie in cookies.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('pdu-session='):
                session_id = cookie.split('=', 1)[1]
                break
                
        session = self.session_manager.get_or_create_session(session_id)
        request.session = session
        
        response = handler(request)
        
        # Inject cookie header in response (simplified for illustrative purposes)
        # Assuming response has a headers dict or similar mechanism
        if hasattr(response, 'headers'):
            cookie_val = self.session_manager.get_session_cookie_value(session)
            response.headers['Set-Cookie'] = f"pdu-session={cookie_val}; Path=/; HttpOnly"
            
        return response
