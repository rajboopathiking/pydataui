from functools import wraps
from rustapi.responses import RedirectResponse, PlainTextResponse

def require_auth(redirect_to="/login"):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            # Assumes request has user attached, or we check here
            # For simplicity, assuming request.app.auth exists
            auth_manager = getattr(getattr(request, 'app', None), 'auth', None)
            if not auth_manager:
                return PlainTextResponse("Authentication not configured", status_code=401)
            if auth_manager:
                user = auth_manager.require_auth_middleware(request)
                if not user:
                    return RedirectResponse(redirect_to)
                request.user = user
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
    
def require_role(*roles):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            if not hasattr(request, 'user') or not request.user:
                return PlainTextResponse("Unauthorized", status_code=401)
            if not any(role in request.user.roles for role in roles):
                return PlainTextResponse("Forbidden", status_code=403)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_api_key(scopes=None):
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            auth_manager = getattr(getattr(request, 'app', None), 'auth', None)
            if not auth_manager:
                return PlainTextResponse("Auth not configured", status_code=500)
                
            headers = getattr(request, 'headers', {})
            auth_header = headers.get('authorization', headers.get('Authorization', ''))
            
            if not auth_header.startswith('Bearer pdu_live_'):
                return PlainTextResponse("Unauthorized", status_code=401)
                
            token = auth_header.removeprefix('Bearer ').strip()
            api_key = auth_manager.verify_api_key(token)
            
            if not api_key:
                return PlainTextResponse("Invalid API Key", status_code=401)
                
            if scopes:
                if not all(scope in api_key.scopes for scope in scopes):
                    return PlainTextResponse("Forbidden: Insufficient scopes", status_code=403)
                    
            request.api_key = api_key
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
