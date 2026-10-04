"""Regression coverage over the real Rust dispatcher; no external services."""
import json
import re
from types import SimpleNamespace

import pytest

from pydataui import App, AuthManager, State
from pydataui.auth import current_user, require_auth
from pydataui.components import Button, Container, Heading
from pydataui.session import SessionManager


class SecureReviewState(State):
    __actions__ = ('increment', 'fail')
    __private_fields__ = ('database_credentials',)
    __readonly_fields__ = ('approved',)
    count: int = 0
    approved: bool = False
    token: str = 'private-token-sentinel'
    database_credentials: str = 'private-database-sentinel'

    def increment(self):
        self.count += 1

    def fail(self):
        raise RuntimeError('SECRET-CONNECTION-STRING')

    def _internal_reset(self):
        self.count = -100

    def helper(self):
        self.count = -200


class HiddenReviewState(State):
    __api__ = False
    value: str = 'hidden'


async def call(app, method, path, data=None, headers=None):
    status, body, response_headers = await app._engine.dispatch_request(
        method, path, '', headers or {}, json.dumps(data) if data is not None else '')
    try:
        payload = json.loads(body)
    except (ValueError, TypeError):
        payload = body
    return status, payload, {k.lower(): v for k, v in response_headers.items()}


async def browser(app, path='/'):
    status, body, headers = await call(app, 'GET', path)
    assert status == 200
    token = re.search(r'name="pdu-csrf-token" content="([^"]+)"', body).group(1)
    return {'cookie': headers['set-cookie'].split(';', 1)[0], 'x-csrf-token': token}


def make_app(auth=False):
    app = App()

    @app.page('/')
    def home():
        return Container(Heading(SecureReviewState.count), Button('+', on_click=SecureReviewState.increment))

    @app.page('/login')
    def login():
        from pydataui.auth import LoginPage
        return LoginPage()

    @app.page('/public', public=True)
    def public():
        return 'public'

    if auth:
        manager = AuthManager()
        manager.add_user('alice', 'test-password')
        manager.add_user('bob', 'test-password')
        app.setup_auth(manager)
    return app


@pytest.mark.anyio
async def test_cookie_less_api_writes_do_not_change_another_session():
    app = make_app()
    status, value, headers = await call(app, 'PUT', '/api/SecureReviewState', {'count': 42})
    assert status == 200 and value['count'] == 42
    assert 'SameSite=Lax' in headers['set-cookie']
    status, fresh, _ = await call(app, 'GET', '/api/SecureReviewState')
    assert status == 200 and fresh['count'] == 0
    status, own, _ = await call(app, 'GET', '/api/SecureReviewState',
                               headers={'cookie': headers['set-cookie'].split(';')[0]})
    assert status == 200 and own['count'] == 42
    assert SecureReviewState.count == 0


@pytest.mark.anyio
async def test_events_require_csrf_and_remain_in_their_session():
    app = make_app()
    a = await browser(app)
    b = await browser(app)
    status, _, _ = await call(app, 'POST', '/_pdu/event/SecureReviewState/increment')
    assert status == 403
    status, _, _ = await call(app, 'POST', '/_pdu/event/SecureReviewState/increment', headers=a)
    assert status == 200
    _, a_state, _ = await call(app, 'GET', '/api/SecureReviewState', headers=a)
    _, b_state, _ = await call(app, 'GET', '/api/SecureReviewState', headers=b)
    assert a_state['count'] == 1 and b_state['count'] == 0
    status, _, _ = await call(app, 'PUT', '/api/SecureReviewState', {'count': 9},
                              {'cookie': a['cookie']})
    assert status == 403
    status, _, _ = await call(app, 'PUT', '/api/SecureReviewState', {'count': 9},
                              {**a, 'x-csrf-token': b['x-csrf-token']})
    assert status == 403


@pytest.mark.anyio
@pytest.mark.parametrize('method', ['_internal_reset', 'helper', 'from_dict', 'to_dict', '__init__'])
async def test_non_actions_cannot_be_called(method):
    app = make_app()
    headers = await browser(app)
    status, _, _ = await call(app, 'POST', f'/api/SecureReviewState/{method}', headers=headers)
    assert status == 404
    status, _, _ = await call(app, 'POST', f'/_pdu/event/SecureReviewState/{method}', headers=headers)
    assert status == 404


@pytest.mark.anyio
async def test_authentication_protects_state_routes_events_and_pages():
    app = make_app(auth=True)
    for method, path in [('GET', '/api'), ('GET', '/api/SecureReviewState'),
                         ('PUT', '/api/SecureReviewState'), ('GET', '/')]:
        status, _, _ = await call(app, method, path, {'count': 99} if method == 'PUT' else None)
        assert status == 401
    status, _, _ = await call(app, 'GET', '/public')
    assert status == 200
    headers = await browser(app, '/login')
    status, _, _ = await call(app, 'POST', '/_pdu/event/SecureReviewState/increment', headers=headers)
    assert status == 401
    assert not current_user


@pytest.mark.anyio
async def test_registration_disabled_or_unprivileged_and_responses_hide_hashes():
    app = App()
    manager = AuthManager()
    app.setup_auth(manager)
    status, _, _ = await call(app, 'POST', '/api/auth/register', {'username':'new','password':'pw'})
    assert status == 403
    app = App()
    manager = AuthManager()
    app.setup_auth(manager, allow_registration=True)
    status, _, _ = await call(app, 'POST', '/api/auth/register',
                              {'username':'new','password':'pw','roles':['admin']})
    assert status == 400 and not manager.users
    status, payload, _ = await call(app, 'POST', '/api/auth/register', {'username':'new','password':'pw'})
    assert status == 200 and payload['user']['roles'] == ['user']
    assert 'password_hash' not in payload['user']


@pytest.mark.anyio
async def test_keys_are_hashed_owner_scoped_and_read_scope_cannot_mutate():
    app = make_app(auth=True)
    auth = app.auth
    alice = auth.users[auth.users_by_username['alice']]
    bob = auth.users[auth.users_by_username['bob']]
    alice_token = auth.authenticate('alice', 'test-password')
    headers = {'authorization': 'Bearer ' + alice_token}
    bob_key = auth.create_api_key('bob key', bob.id)
    status, _, _ = await call(app, 'DELETE', '/api/auth/keys/' + bob_key.key_id, headers=headers)
    assert status == 404 and auth.verify_api_key(bob_key.key) is not None
    status, payload, _ = await call(app, 'POST', '/api/auth/keys', {'name':'alice key'}, headers)
    assert status == 200
    raw = payload['key']['key']
    assert raw not in auth.api_keys and all(k.key == '' for k in auth.api_keys.values())
    status, payload, _ = await call(app, 'GET', '/api/auth/keys', headers=headers)
    assert status == 200 and all('key' not in k for k in payload['keys'])
    read_headers = {'authorization':'Bearer '+raw}
    status, _, _ = await call(app, 'GET', '/api/SecureReviewState', headers=read_headers)
    assert status == 200
    status, _, _ = await call(app, 'PUT', '/api/SecureReviewState', {'count':10}, read_headers)
    assert status == 403
    status, _, _ = await call(app, 'POST', '/api/auth/keys', {'name':'escalation','scopes':['write']}, read_headers)
    assert status == 403
    status, _, _ = await call(app, 'DELETE', '/api/auth/keys/'+payload['keys'][0]['key_id'], headers=headers)
    assert status == 200 and auth.verify_api_key(raw) is None


@pytest.mark.anyio
async def test_login_browser_rotation_and_logout_revoke_tokens():
    app = make_app(auth=True)
    old = await browser(app, '/login')
    status, _, headers = await call(app, 'POST', '/_pdu/event/LoginState/login',
                                    {'username':'alice','password':'test-password'}, old)
    assert status == 200 and headers['hx-redirect'] == '/'
    cookie = headers['set-cookie'].split(';')[0]
    assert cookie != old['cookie']
    status, _, _ = await call(app, 'GET', '/', headers={'cookie':cookie})
    assert status == 200
    status, _, _ = await call(app, 'GET', '/', headers={'cookie':old['cookie']})
    assert status == 401
    _, payload, h = await call(app, 'GET', '/_pdu/csrf', headers={'cookie':cookie})
    new = {'cookie':cookie, 'x-csrf-token':payload['csrf_token']}
    status, _, _ = await call(app, 'POST', '/_pdu/event/LoginState/logout', headers=new)
    assert status == 200
    status, _, _ = await call(app, 'GET', '/', headers={'cookie':cookie})
    assert status == 401
    token = app.auth.authenticate('alice', 'test-password')
    headers = {'authorization':'Bearer '+token}
    status, me, _ = await call(app, 'GET', '/api/auth/me', headers=headers)
    assert status == 200 and 'password_hash' not in me['user']
    status, _, _ = await call(app, 'POST', '/api/auth/logout', headers=headers)
    assert status == 200 and app.auth.verify_token(token) is None
    assert not current_user


@pytest.mark.anyio
async def test_private_fields_hidden_and_inputs_validated_atomically():
    app = make_app()
    headers = await browser(app)
    status, state, _ = await call(app, 'GET', '/api/SecureReviewState', headers=headers)
    assert status == 200 and 'token' not in state and 'database_credentials' not in state
    _, catalog, _ = await call(app, 'GET', '/api')
    assert 'LoginState' not in catalog['states'] and 'HiddenReviewState' not in catalog['states']
    assert 'token' not in catalog['states']['SecureReviewState']['fields']
    for data in ({'count':'not-an-int'}, {'count':4,'approved':True}, {'token':'stolen'}):
        status, _, _ = await call(app, 'PUT', '/api/SecureReviewState', data, headers)
        assert status == 422
    _, state, _ = await call(app, 'GET', '/api/SecureReviewState', headers=headers)
    assert state['count'] == 0 and state['approved'] is False
    status, _, _ = await call(app, 'GET', '/api/SecureReviewState/token', headers=headers)
    assert status == 404
    status, _, _ = await call(app, 'GET', '/api/LoginState')
    assert status == 404


@pytest.mark.anyio
async def test_production_errors_do_not_expose_details():
    app = make_app()

    @app.page('/broken')
    def broken():
        raise RuntimeError('SECRET-CONNECTION-STRING')

    status, body, _ = await call(app, 'GET', '/broken')
    assert status == 500 and 'SECRET-CONNECTION-STRING' not in body and 'Traceback' not in body
    headers = await browser(app)
    status, body, _ = await call(app, 'POST', '/api/SecureReviewState/fail', headers=headers)
    assert status == 400 and body == {'error':'Action failed'}
    status, body, _ = await call(app, 'POST', '/_pdu/event/SecureReviewState/fail', headers=headers)
    assert status == 200 and 'SECRET-CONNECTION-STRING' not in body


def test_passwords_salted_and_inactive_users_rejected():
    auth = AuthManager()
    a = auth.add_user('alice', 'same-password')
    b = auth.add_user('bob', 'same-password')
    assert a.password_hash != b.password_hash
    token = auth.authenticate('alice', 'same-password')
    key = auth.create_api_key('key', a.id)
    a.is_active = False
    assert auth.verify_token(token) is None
    assert auth.verify_api_key(key.key) is None
    with pytest.raises(ValueError):
        AuthManager(secret_key='default_secret')


def test_unsigned_session_cookie_and_unconfigured_auth_fail_closed():
    manager = SessionManager('test-secret')
    original = manager.create_session()
    assert manager.get_or_create_session(original.session_id) is not original
    assert manager.get_or_create_session(manager.sign_session_id(original.session_id)) is original
    @require_auth()
    def endpoint(request):
        pytest.fail('unconfigured authentication passed through')
    response = endpoint(SimpleNamespace(app=None))
    assert response.status_code == 401


@pytest.mark.anyio
async def test_custom_api_and_role_checks():
    app = make_app(auth=True)

    @app.api('/custom')
    def custom():
        return {'user': current_user.username}

    @app.api('/admin', roles=['admin'])
    def admin(request):
        return {'allowed': True}

    @app.page('/admin-page', roles=['admin'])
    def admin_page():
        return 'admin content'

    status, _, _ = await call(app, 'GET', '/custom')
    assert status == 401
    token = app.auth.authenticate('alice', 'test-password')
    headers = {'authorization': 'Bearer '+token}
    status, body, _ = await call(app, 'GET', '/custom', headers=headers)
    assert status == 200 and body['user'] == 'alice'
    for path in ('/admin', '/admin-page'):
        status, _, _ = await call(app, 'GET', path, headers=headers)
        assert status == 403
    assert not current_user


@pytest.mark.anyio
async def test_global_api_disable_and_readonly_login_state():
    app = App(auto_api=False)
    status, _, _ = await call(app, 'GET', '/api/SecureReviewState')
    assert status == 404
    app = make_app(auth=True)
    headers = await browser(app, '/login')
    status, _, _ = await call(app, 'POST', '/_pdu/event/LoginState/login',
                              {'username':'alice','password':'wrong','is_authenticated':True}, headers)
    assert status == 422
    status, _, _ = await call(app, 'GET', '/', headers=headers)
    assert status == 401


@pytest.mark.anyio
async def test_context_uses_each_apps_auth_manager():
    first = make_app(auth=True)
    second = make_app(auth=True)
    # Deliberately give the same username different passwords across applications.
    second.auth.users[second.auth.users_by_username['alice']].password_hash = second.auth._hash_password('different')
    headers = await browser(first, '/login')
    status, _, response = await call(first, 'POST', '/_pdu/event/LoginState/login',
                                     {'username':'alice','password':'test-password'}, headers)
    assert status == 200 and response['hx-redirect'] == '/'
    assert not current_user


@pytest.mark.anyio
async def test_session_cannot_be_reused_by_another_authenticated_user():
    app = make_app(auth=True)
    alice = {'authorization':'Bearer '+app.auth.authenticate('alice','test-password')}
    status, _, response = await call(app, 'GET', '/api/SecureReviewState', headers=alice)
    assert status == 200
    bob = {'authorization':'Bearer '+app.auth.authenticate('bob','test-password'),
           'cookie':response['set-cookie'].split(';')[0]}
    status, _, _ = await call(app, 'GET', '/api/SecureReviewState', headers=bob)
    assert status == 403


def test_auth_components_escape_user_data():
    from pydataui.auth import UserMenu
    auth = AuthManager()
    user = auth.add_user('<img src=x onerror=alert(1)>', 'pw')
    html = UserMenu(user).render({})
    assert '<img' not in html and '&lt;img' in html


@pytest.mark.anyio
async def test_page_auth_decorators_receive_request_and_preserve_denials():
    from pydataui.auth import require_role
    app = make_app(auth=True)
    @app.page('/decorated')
    @require_auth()
    @require_role('admin')
    def decorated(request):
        return Heading('admin only')
    headers = {'authorization':'Bearer '+app.auth.authenticate('alice','test-password')}
    status, body, _ = await call(app, 'GET', '/decorated', headers=headers)
    assert status == 403 and 'admin only' not in body
    app.auth.users[app.auth.users_by_username['alice']].roles.append('admin')
    status, body, _ = await call(app, 'GET', '/decorated', headers=headers)
    assert status == 200 and 'admin only' in body


@pytest.mark.anyio
async def test_role_gates_fail_closed_without_authentication():
    app = App()
    @app.api('/restricted', roles=['admin'])
    def restricted():
        return {'secret': 'not public'}
    status, body, _ = await call(app, 'GET', '/restricted')
    assert status == 401 and 'secret' not in body


@pytest.mark.anyio
async def test_cross_origin_login_without_cookies_is_rejected():
    app = make_app(auth=True)
    status, _, _ = await call(app, 'POST', '/api/auth/login',
                              {'username':'alice','password':'test-password'},
                              {'origin':'https://untrusted.example','host':'localhost'})
    assert status == 403
