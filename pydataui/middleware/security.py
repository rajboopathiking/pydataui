"""CSRF helpers for framework routes and custom middleware."""
import secrets
from urllib.parse import urlsplit


def headers_of(request):
    return {str(k).lower(): v for k, v in getattr(request, 'headers', {}).items()}


def csrf_token(session):
    return session.data.setdefault('csrf_token', secrets.token_hex(32))


def validate_csrf(request, session, *, force=False):
    headers = headers_of(request)
    # Explicit bearer credentials are not ambient browser cookies.
    if headers.get('authorization', '').lower().startswith('bearer '):
        return True
    origin = headers.get('origin')
    if origin:
        try:
            if urlsplit(origin).netloc != headers.get('host', ''):
                return False
        except ValueError:
            return False
    cookies = headers.get('cookie', '')
    has_credentials = any(c.strip().startswith(('pdu-session=', 'pdu-auth='))
                          for c in cookies.split(';'))
    if not force and not has_credentials:
        return True
    supplied = headers.get('x-csrf-token', '')
    expected = session.data.get('csrf_token', '')
    return bool(supplied and expected and secrets.compare_digest(supplied, expected))


class CSRFMiddleware:
    def __init__(self, exempt_prefixes=None):
        self.exempt_prefixes = [] if exempt_prefixes is None else exempt_prefixes

    def __call__(self, request, handler):
        path = getattr(request, 'path', '')
        session = getattr(request, 'session', None)
        if session is None:
            return {'error': 'Session middleware required'}, 403
        csrf_token(session)
        if getattr(request, 'method', 'GET') in ('POST', 'PUT', 'PATCH', 'DELETE'):
            if not any(path.startswith(p) for p in self.exempt_prefixes):
                if not validate_csrf(request, session, force=True):
                    return {'error': 'CSRF validation failed'}, 403
        return handler(request)
