"""Optional Chromium test: install .[dev,browser], then playwright install chromium."""
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from urllib.request import build_opener, ProxyHandler

import pytest

playwright = pytest.importorskip('playwright.sync_api')

APP = '''from pydataui import App, State, AuthManager
from pydataui.components import Container, Heading, Button
from pydataui.auth import LoginPage, current_user, UserMenu
class BrowserCounter(State):
    count: int = 0
    def increment(self): self.count += 1
app = App()
auth = AuthManager()
auth.add_user('alice', 'browser-test-password')
app.setup_auth(auth)
@app.page('/login')
def login(): return LoginPage()
@app.page('/')
def home():
    return Container(Heading(BrowserCounter.count), Button('Increment', on_click=BrowserCounter.increment), UserMenu(current_user.get()))
app.run(port=int(__import__('os').environ['PYDATAUI_TEST_PORT']))
'''


def test_real_browser_login_click_isolation_and_logout(tmp_path):
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    script = tmp_path / 'browser_app.py'
    script.write_text(APP)
    project = Path(__file__).resolve().parents[1]
    env = dict(os.environ, PYTHONPATH=str(project), PYDATAUI_TEST_PORT=str(port))
    log = (tmp_path / 'server.log').open('w')
    process = subprocess.Popen([sys.executable, str(script)], env=env, stdout=log, stderr=log)
    base = f'http://127.0.0.1:{port}'
    opener = build_opener(ProxyHandler({}))
    try:
        for _ in range(100):
            if process.poll() is not None:
                pytest.fail('Browser fixture failed: '+(tmp_path / 'server.log').read_text())
            try:
                opener.open(base+'/_pdu/health', timeout=.2).close()
                break
            except OSError:
                time.sleep(.1)
        else:
            pytest.fail('Server did not become ready')
        with playwright.sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except playwright.Error as exc:
                if "Executable doesn't exist" in str(exc):
                    if os.environ.get('PYDATAUI_REQUIRE_BROWSER') == '1':
                        raise
                    pytest.skip('Install Chromium using python -m playwright install chromium')
                raise
            # Tailwind CDN is unrelated to functional checks; keep the test offline.
            first = browser.new_context()
            second = browser.new_context()
            first.route('https://**', lambda route: route.abort())
            second.route('https://**', lambda route: route.abort())
            try:
                pages = [first.new_page(), second.new_page()]
                errors = []
                for page in pages:
                    page.on('pageerror', lambda exc: errors.append(str(exc)))
                    page.goto(base+'/login')
                    page.fill('input[name=username]', 'alice')
                    page.fill('input[name=password]', 'browser-test-password')
                    page.get_by_role('button', name='Sign In', exact=True).click()
                    page.wait_for_url(base+'/')
                    playwright.expect(page.get_by_role('heading')).to_have_text('0')
                for value in range(1, 4):
                    pages[0].get_by_role('button', name='Increment', exact=True).click()
                    playwright.expect(pages[0].get_by_role('heading')).to_have_text(str(value))
                pages[0].reload()
                playwright.expect(pages[0].get_by_role('heading')).to_have_text('3')
                pages[1].reload()
                playwright.expect(pages[1].get_by_role('heading')).to_have_text('0')
                pages[0].get_by_role('button', name='Logout', exact=True).click()
                pages[0].wait_for_url(base+'/login')
                response = first.request.get(base+'/api/BrowserCounter')
                assert response.status == 401
                assert errors == []
            finally:
                first.close()
                second.close()
                browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        log.close()
