import pytest
import anyio
from pydataui import App
from pydataui.auth import (
    AuthManager, User, Role, APIKey,
    require_auth, require_role, require_api_key,
    LoginState, current_user,
    LoginPage, UserMenu, APIKeyManager, AuthGuard
)

SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes-long!"

def test_auth_manager_user_crud():
    mgr = AuthManager(secret_key=SECRET_KEY)
    user = mgr.add_user("alice", "password123", email="alice@test.com", roles=[Role.ADMIN, Role.DATA_ENGINEER])
    assert user.username == "alice"
    assert Role.ADMIN in user.roles
    assert Role.DATA_ENGINEER in user.roles
    assert user.is_active is True

    # Duplicate username raises ValueError
    with pytest.raises(ValueError):
        mgr.add_user("alice", "otherpass")

def test_auth_authentication():
    mgr = AuthManager(secret_key=SECRET_KEY)
    mgr.add_user("bob", "secret_pass")
    
    # Successful login
    token = mgr.authenticate("bob", "secret_pass")
    assert token is not None
    assert isinstance(token, str)

    # Failed login with wrong password
    assert mgr.authenticate("bob", "wrong_pass") is None

    # Failed login with nonexistent user
    assert mgr.authenticate("charlie", "any") is None

    # Token verification
    verified = mgr.verify_token(token)
    assert verified is not None
    assert verified.username == "bob"

def test_api_key_lifecycle():
    mgr = AuthManager(secret_key=SECRET_KEY)
    user = mgr.add_user("engineer", "pass123")
    
    # Create key
    key = mgr.create_api_key("ETL Job Key", user.id, scopes=["read", "write"])
    assert key.key.startswith("pdu_live_")
    assert key.name == "ETL Job Key"
    assert "read" in key.scopes
    assert key.usage_count == 0

    # Verify key
    verified = mgr.verify_api_key(key.key)
    assert verified is not None
    assert verified.key_id == key.key_id
    assert verified.usage_count == 1
    assert verified.last_used is not None

    # List keys
    keys = mgr.list_api_keys(user.id)
    assert len(keys) == 1
    assert keys[0].key_id == key.key_id

    # Revoke key
    mgr.revoke_api_key(key.key_id)
    assert mgr.verify_api_key(key.key) is None
    assert len(mgr.list_api_keys(user.id)) == 0

def test_login_state():
    mgr = AuthManager(secret_key=SECRET_KEY)
    mgr.add_user("data_analyst", "mypassword")

    state = LoginState()
    state.username = "data_analyst"
    state.password = "wrong"
    state.login()
    assert state.is_authenticated is False
    assert "Invalid" in state.error

    state.password = "mypassword"
    state.login()
    assert state.is_authenticated is True
    assert state.current_user_name == "data_analyst"
    assert state.token != ""
    assert state.error == ""

    state.logout()
    assert state.is_authenticated is False
    assert state.token == ""

def test_auth_components_render():
    lp = LoginPage(title="Team Portal")
    html = lp.render({})
    assert "Team Portal" in html
    assert 'name="username"' in html
    assert 'name="password"' in html

    user = User("1", "lead_dev", "lead@test.com", "hash", [Role.ADMIN], True, "now", None, {})
    um = UserMenu(user)
    html_um = um.render({})
    assert "lead_dev" in html_um
    assert "Logout" in html_um

    akm = APIKeyManager()
    html_akm = akm.render({})
    assert "API Key Management" in html_akm

    ag = AuthGuard(lp)
    unauth = ag.render({})
    assert "Authentication required" in unauth
    auth = ag.render({"LoginState": {"is_authenticated": True}})
    assert "Team Portal" in auth

@pytest.mark.anyio
async def test_auth_api_endpoints_via_app():
    app = App(title="Auth Test App")
    mgr = AuthManager(secret_key=SECRET_KEY)
    user = mgr.add_user("dev", "devpass", roles=[Role.USER])
    app.setup_auth(mgr)

    # 1. Login endpoint
    s, b, h = await app._engine.dispatch_request(
        "POST", "/api/auth/login", "",
        {"content-type": "application/json"},
        '{"username": "dev", "password": "devpass"}'
    )
    assert s == 200
    import json
    data = json.loads(b)
    assert "token" in data
    jwt_token = data["token"]

    # 2. Get current user info with JWT
    s, b, h = await app._engine.dispatch_request(
        "GET", "/api/auth/me", "",
        {"authorization": f"Bearer {jwt_token}"},
        ""
    )
    assert s == 200
    me_data = json.loads(b)
    assert me_data["user"]["username"] == "dev"

    # 3. Unauthorized access without token
    s, b, h = await app._engine.dispatch_request("GET", "/api/auth/me", "", {}, "")
    assert s == 401
