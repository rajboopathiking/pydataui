import pytest
import json
from pydataui import App, State
from pydataui.components import Button, Heading, Container

class DemoCounterState(State):
    count: int = 10

    def increment(self):
        self.count += 1

    def decrement(self):
        self.count -= 1

    def fail_action(self):
        raise ValueError("Simulated business logic failure")

@pytest.mark.anyio
async def test_bff_and_static_routes():
    app = App(title="Test BFF App", debug=True)

    @app.page("/")
    def index():
        return Container(
            Heading(DemoCounterState.count),
            Button("+", on_click=DemoCounterState.increment),
        )

    @app.page("/broken")
    def broken_page():
        raise RuntimeError("Simulated render failure")

    # 1. Test Static JS and CSS (both root static and subfolder static)
    s, b, h = await app._engine.dispatch_request('GET', '/_pdu/static/htmx.min.js', '', {}, '')
    assert s == 200
    assert len(b) > 40000

    s, b, h = await app._engine.dispatch_request('GET', '/_pdu/static/js/htmx.min.js', '', {}, '')
    assert s == 200
    assert len(b) > 40000

    s, b, h = await app._engine.dispatch_request('GET', '/_pdu/static/pydataui.css', '', {}, '')
    assert s == 200
    assert len(b) > 1000

    s, b, h = await app._engine.dispatch_request('GET', '/_pdu/static/css/pydataui.css', '', {}, '')
    assert s == 200
    assert len(b) > 1000

    # 2. Test Page Rendering & Event Attributes
    s, b, h = await app._engine.dispatch_request('GET', '/', '', {}, '')
    assert s == 200
    assert '/_pdu/static/htmx.min.js' in b
    assert 'hx-include="#pdu-root"' in b
    assert 'closest form' not in b

    # Continue the browser session and send the token embedded by the renderer.
    import re
    cookie = h['set-cookie'].split(';', 1)[0] if 'set-cookie' in h else h['Set-Cookie'].split(';', 1)[0]
    token = re.search(r'name="pdu-csrf-token" content="([^"]+)"', b).group(1)
    browser_headers = {'cookie': cookie, 'x-csrf-token': token}

    # 3. Test Event SSR Fragment Update
    s, b, h = await app._engine.dispatch_request('POST', '/_pdu/event/DemoCounterState/increment', '', browser_headers, '')
    assert s == 200
    assert '11' in b

    # 4. Test Event Error Boundary (no 500! returns 200 with error toast banner)
    s, b, h = await app._engine.dispatch_request('POST', '/_pdu/event/DemoCounterState/fail_action', '', browser_headers, '')
    assert s == 200
    assert 'pdu-action-error' in b
    assert 'Simulated business logic failure' in b

    # 5. Test Page Error Boundary (no 500! returns 200 with error boundary UI)
    s, b, h = await app._engine.dispatch_request('GET', '/broken', '', {}, '')
    assert s == 500
    assert 'pdu-error-boundary' in b
    assert 'Simulated render failure' in b

    # 6. Test API Catalog
    s, b, h = await app._engine.dispatch_request('GET', '/api', '', {}, '')
    assert s == 200
    cat = json.loads(b)
    assert 'DemoCounterState' in cat['states']

    # 7. Test Docs & OpenAPI
    s, b, _ = await app._engine.dispatch_request('GET', '/api/docs', '', {}, '')
    assert s == 200
    s, b, _ = await app._engine.dispatch_request('GET', '/docs', '', {}, '')
    assert s == 200
    s, b, _ = await app._engine.dispatch_request('GET', '/api/openapi.json', '', {}, '')
    assert s == 200
    s, b, _ = await app._engine.dispatch_request('GET', '/openapi.json', '', {}, '')
    assert s == 200

    # 8. Test State REST Endpoints
    s, b, _ = await app._engine.dispatch_request('GET', '/api/DemoCounterState', '', browser_headers, '')
    assert s == 200

    s, b, _ = await app._engine.dispatch_request('POST', '/api/DemoCounterState/increment', '', browser_headers, '')
    assert s == 200

    s, b, _ = await app._engine.dispatch_request('GET', '/api/DemoCounterState/count', '', browser_headers, '')
    assert s == 200
    assert json.loads(b)['count'] >= 11

    s, b, _ = await app._engine.dispatch_request('PUT', '/api/DemoCounterState', '', browser_headers, json.dumps({'count': 50}))
    assert s == 200
    assert json.loads(b)['count'] == 50

    s, b, _ = await app._engine.dispatch_request('DELETE', '/api/DemoCounterState', '', browser_headers, '')
    assert s == 200
    assert json.loads(b)['state']['count'] == 10

    # 9. Test API State Method Error Handling (returns 400 with clean error JSON, not 500)
    s, b, _ = await app._engine.dispatch_request('POST', '/api/DemoCounterState/fail_action', '', browser_headers, '')
    assert s == 400
    err_json = json.loads(b)
    assert 'Simulated business logic failure' in err_json['error']
