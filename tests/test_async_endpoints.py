"""Async custom routes through the real Rust dispatcher and wrapper lifecycle."""
import asyncio
import inspect
import json
from types import SimpleNamespace
from unittest.mock import patch

from pydataui import App, AuthManager
from pydataui.auth import current_user

async def call(app, path, headers=None):
    status, body, _ = await app._engine.dispatch_request('GET', path, '', headers or {}, '')
    return status, json.loads(body)

def test_sync_and_async_dispatch():
    async def run():
        app = App()
        @app.api('/async/{value}', public=True)
        async def route(request, value: int):
            await asyncio.sleep(0)
            assert request.app is app
            return {'value':value}
        @app.api('/sync', public=True)
        def sync():
            return {'sync':True}
        assert await call(app,'/async/7') == (200, {'value':7})
        assert await call(app,'/sync') == (200, {'sync':True})
    asyncio.run(run())

def test_auth_and_context_isolation():
    async def run():
        app=App()
        auth=AuthManager()
        alice=auth.add_user('async-alice','test-password')
        bob=auth.add_user('async-bob','test-password')
        app.setup_auth(auth)
        @app.api('/who')
        async def who():
            before=current_user.get().id
            await asyncio.sleep(.01)
            assert current_user.get().id == before
            return {'id':before}
        assert (await call(app,'/who'))[0] == 401
        tokens=[auth.authenticate(u.username, 'test-password') for u in [alice,bob]]
        results=await asyncio.gather(*(call(app,'/who',{'authorization':'Bearer '+t}) for t in tokens))
        assert results == [(200,{'id':alice.id}),(200,{'id':bob.id})]
        assert current_user.get() is None
    asyncio.run(run())

def test_wrapper_concurrency_cancellation_and_exception_cleanup():
    async def run():
        app=App()
        auth=AuthManager()
        user=auth.add_user('async-cancel','test-password')
        app.setup_auth(auth)
        handlers={}
        def register(path, **kwargs):
            def decorate(fn):
                handlers[path]=fn
                return fn
            return decorate
        gate=asyncio.Event()
        count=0
        with patch.object(app._engine,'get',side_effect=register):
            @app.api('/wait')
            async def wait(request):
                nonlocal count
                assert current_user.get().id == user.id
                count+=1
                if count==2: gate.set()
                await gate.wait()
                return count
            @app.api('/cancel')
            async def cancel(request):
                try:
                    await asyncio.Event().wait()
                finally:
                    assert current_user.get().id == user.id
            @app.api('/fail')
            async def fail(request):
                raise ValueError('expected')
        def req():
            return SimpleNamespace(headers={'authorization':'Bearer '+auth.authenticate(user.username, 'test-password')}, cookies={})
        assert inspect.iscoroutinefunction(handlers['/wait'])
        await asyncio.wait_for(asyncio.gather(handlers['/wait'](req()),handlers['/wait'](req())),1)
        task=asyncio.create_task(handlers['/cancel'](req()))
        await asyncio.sleep(.05)
        task.cancel()
        try: await task
        except asyncio.CancelledError: pass
        else: raise AssertionError('Cancellation swallowed')
        try: await handlers['/fail'](req())
        except ValueError: pass
        else: raise AssertionError('Exception swallowed')
        assert current_user.get() is None
    asyncio.run(run())

def test_async_write_requires_csrf_for_cookie_session():
    async def run():
        app=App()
        called=[]
        @app.api('/write', method='POST', public=True)
        async def write():
            called.append(True)
            return {'ok':True}
        status, body, headers=await app._engine.dispatch_request('GET',app.config.internal_prefix+'/csrf','',{},'')
        assert status==200
        token=json.loads(body)['csrf_token']
        cookie=headers.get('Set-Cookie', headers.get('set-cookie')).split(';',1)[0]
        status, _, _=await app._engine.dispatch_request('POST','/write','',{'cookie':cookie},'')
        assert status==403 and not called
        status, body, _=await app._engine.dispatch_request('POST','/write','',{'cookie':cookie,'x-csrf-token':token},'')
        assert status==200 and json.loads(body)=={'ok':True} and called==[True]
    asyncio.run(run())


def test_native_http_async_and_sync_execution(tmp_path):
    import os
    import socket
    import subprocess
    import sys
    import time
    from pathlib import Path
    from urllib.error import HTTPError
    from urllib.request import build_opener, ProxyHandler, Request

    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    script = tmp_path / 'async_app.py'
    script.write_text('''import asyncio
from pydataui import App
from pydataui.components import Container, Heading

app = App()

@app.api('/sync', method='GET', public=True)
def sync_test():
    return {'message': 'sync works'}

@app.api('/async', method='GET', public=True)
async def async_test():
    await asyncio.sleep(0.05)
    return {'message': 'async works'}

@app.page('/async_page', public=True)
async def async_page():
    await asyncio.sleep(0.02)
    return Container(Heading('Async Page Loaded'))

app.run(port=int(__import__('os').environ['PYDATAUI_TEST_PORT']))
''')
    log_file = tmp_path / 'server.log'
    log = log_file.open('w')
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]),
               PYDATAUI_TEST_PORT=str(port))
    server = subprocess.Popen([sys.executable, str(script)], env=env, stdout=log, stderr=log)
    opener = build_opener(ProxyHandler({}))
    base = f'http://127.0.0.1:{port}'

    def call(path, headers=None):
        req = Request(base + path, headers=headers or {})
        try:
            response = opener.open(req, timeout=5)
        except HTTPError as exc:
            response = exc
        with response:
            return response.status, response.read().decode()

    try:
        for _ in range(100):
            if server.poll() is not None:
                raise AssertionError(log_file.read_text())
            try:
                if call('/_pdu/health')[0] == 200:
                    break
            except OSError:
                time.sleep(0.1)
        else:
            raise AssertionError('Server did not become ready')

        # Test sync endpoint
        status, body = call('/sync')
        assert status == 200
        assert json.loads(body) == {'message': 'sync works'}

        # Test async endpoint
        status, body = call('/async')
        assert status == 200
        assert json.loads(body) == {'message': 'async works'}

        # Test async page
        status, html = call('/async_page')
        assert status == 200
        assert 'Async Page Loaded' in html
    finally:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        log.close()

    server_output = log_file.read_text()
    assert 'RuntimeWarning: coroutine' not in server_output
    assert 'was never awaited' not in server_output

