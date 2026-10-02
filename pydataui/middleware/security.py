import secrets
from typing import Any

class CSRFMiddleware:
    """CSRF protection for state-mutating requests."""
    def __init__(self, exempt_prefixes: list = None):
        self.exempt_prefixes = exempt_prefixes or ['/_pdu/', '/api/']
        
    def __call__(self, request: Any, handler: Any) -> Any:
        path = request.path if hasattr(request, 'path') else ''
        method = request.method if hasattr(request, 'method') else 'GET'
        
        is_exempt = any(path.startswith(prefix) for prefix in self.exempt_prefixes)
        
        if method in ('POST', 'PUT', 'DELETE') and not is_exempt:
            csrf_token = request.headers.get('x-csrf-token')
            expected_token = getattr(request, 'session', {}).get('csrf_token')
            
            if not csrf_token or not expected_token or csrf_token != expected_token:
                return {"error": "CSRF validation failed"}, 403
                
        # Generate token if missing
        if hasattr(request, 'session') and 'csrf_token' not in request.session.data:
            request.session.data['csrf_token'] = secrets.token_hex(32)
            
        return handler(request)
