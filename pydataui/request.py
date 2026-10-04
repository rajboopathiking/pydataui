"""Python-owned request context around the Rust engine's immutable request."""
class RequestContext:
    def __init__(self, request, app=None):
        self._request = request
        self.app = app or getattr(request, 'app', None)

    def __getattr__(self, name):
        return getattr(self._request, name)


def request_context(request, app=None):
    return request if isinstance(request, RequestContext) else RequestContext(request, app)
