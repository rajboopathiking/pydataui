"""Exercise the native HTTP server, not just the internal dispatcher."""
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
from urllib.error import HTTPError
from urllib.request import build_opener, ProxyHandler, Request


def test_native_http_login_event_and_logout(tmp_path):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    script = tmp_path / 'socket_app.py'
    script.write_text('''from pydataui import App, State, AuthManager
from pydataui.auth import LoginPage
from pydataui.components import Container, Heading, Button
class SocketCounter(State):
    count: int = 0
    def increment(self): self.count += 1
app = App()
auth = AuthManager()
auth.add_user('alice','socket-test-password')
app.setup_auth(auth)
@app.page('/login')
def login(): return LoginPage()
@app.page('/')
def home(): return Container(Heading(SocketCounter.count), Button('Increment', on_click=SocketCounter.increment))
app.run(port=int(__import__('os').environ['PYDATAUI_TEST_PORT']))
''')
    log = (tmp_path / 'server.log').open('w')
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]),
               PYDATAUI_TEST_PORT=str(port))
    server = subprocess.Popen([sys.executable, str(script)], env=env, stdout=log, stderr=log)
    opener = build_opener(ProxyHandler({}))
    base = f'http://127.0.0.1:{port}'

    def call(path, data=None, headers=None):
        req = Request(base+path, data=json.dumps(data).encode() if data is not None else None,
                      headers=headers or {})
        try:
            response = opener.open(req, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.status, response.read().decode(), response.headers

    try:
        for _ in range(100):
            if server.poll() is not None:
                raise AssertionError((tmp_path / 'server.log').read_text())
            try:
                if call('/_pdu/health')[0] == 200:
                    break
            except OSError:
                time.sleep(.1)
        else:
            raise AssertionError('Server did not become ready')
        status, html, headers = call('/login')
        assert status == 200
        old_cookie = headers['Set-Cookie'].split(';')[0]
        token = re.search(r'name="pdu-csrf-token" content="([^"]+)"', html).group(1)
        status, _, headers = call('/_pdu/event/LoginState/login',
                                   {'username':'alice','password':'socket-test-password'},
                                   {'Cookie':old_cookie,'X-CSRF-Token':token,'Content-Type':'application/json'})
        assert status == 200 and headers['HX-Redirect'] == '/'
        cookie = headers['Set-Cookie'].split(';')[0]
        assert cookie != old_cookie
        status, html, _ = call('/', headers={'Cookie':cookie})
        assert status == 200
        token = re.search(r'name="pdu-csrf-token" content="([^"]+)"', html).group(1)
        browser = {'Cookie':cookie,'X-CSRF-Token':token,'Content-Type':'application/json'}
        for expected in range(1, 4):
            status, fragment, _ = call('/_pdu/event/SocketCounter/increment', {}, browser)
            assert status == 200 and f'>{expected}</h' in fragment
        status, body, _ = call('/api/SocketCounter', headers={'Cookie':cookie})
        assert status == 200 and json.loads(body)['count'] == 3
        assert call('/api/SocketCounter')[0] == 401
        status, _, _ = call('/_pdu/event/LoginState/logout', {}, browser)
        assert status == 200
        assert call('/api/SocketCounter', headers={'Cookie':cookie})[0] == 401
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        log.close()
