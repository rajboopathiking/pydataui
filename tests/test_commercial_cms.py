import os
import tempfile
import pytest
from pydataui import App
from pydataui.auth import (
    AuthManager, Role, User, current_user
)
from pydataui.auth.manager import _current_user_var
from pydataui.storage import SQLiteAuthStore
from examples.commercial_saas_app import (
    AdminUserState, admin_users_view, auth as app_auth
)

SECRET_KEY = "test-secret-key-that-is-at-least-32-bytes-long!"


@pytest.fixture(autouse=True)
def reset_current_user():
    yield
    _current_user_var.set(None)


def test_auth_manager_password_reset_and_delete():
    mgr = AuthManager(secret_key=SECRET_KEY)
    u = mgr.add_user("testuser", "initial_pass123", email="test@domain.com", roles=[Role.USER])
    assert u.username == "testuser"

    # Authenticate with initial password
    assert mgr.authenticate("testuser", "initial_pass123") is not None
    assert mgr.authenticate("testuser", "wrong_pass") is None

    # Reset password
    success = mgr.set_user_password(u.id, "new_secret_456")
    assert success is True

    # Old password must fail, new password must succeed
    assert mgr.authenticate("testuser", "initial_pass123") is None
    token = mgr.authenticate("testuser", "new_secret_456")
    assert token is not None
    verified = mgr.verify_token(token)
    assert verified.id == u.id

    # Test delete_user
    del_ok = mgr.delete_user(u.id)
    assert del_ok is True
    assert mgr.users.get(u.id) is None
    assert mgr.authenticate("testuser", "new_secret_456") is None

    # Test del mgr.users[id]
    u2 = mgr.add_user("testuser2", "pass123")
    assert u2.id in mgr.users
    del mgr.users[u2.id]
    assert u2.id not in mgr.users


def test_sqlite_auth_store_password_and_delete():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_auth.db")
        store = SQLiteAuthStore(f"sqlite:///{db_path}")

        user = User(
            id="usr_123",
            username="sql_user",
            email="sql@test.com",
            password_hash="hash_placeholder",
            roles=[Role.USER],
            is_active=True,
            created_at="2026-10-01T00:00:00Z",
            last_login=None,
            metadata={}
        )
        store.save_user(user)
        assert store.get_user("usr_123") is not None
        assert store.get_user_by_username("sql_user") is not None

        # Delete user
        assert store.delete_user("usr_123") is True
        assert store.get_user("usr_123") is None
        assert store.get_user_by_username("sql_user") is None
        assert store.delete_user("nonexistent") is False


def test_admin_user_state_cms_lifecycle():
    # Setup admin and regular user in app_auth
    admin = app_auth.get_or_create_user("cms_admin", "adminpass123", email="admin@cms.com", roles=[Role.ADMIN])
    
    state = AdminUserState()

    # 1. Unauthenticated / Non-admin mutation attempt must be blocked
    _current_user_var.set(None)
    state.open_create_modal()
    state.save_user(username="hacker", email="hacker@bad.com", password="pwd", role=Role.ADMIN)
    assert "Unauthorized" in state.feedback_msg
    assert state.feedback_type == "error"
    assert app_auth.users_by_username.get("hacker") is None

    # 2. Authenticated as Admin
    _current_user_var.set(admin)

    # 2a. Provision New User
    state.open_create_modal()
    assert state.modal_open is True
    assert state.modal_mode == "create"

    state.save_user(
        username="carol_engineer",
        email="carol@enterprise.com",
        password="carol_initial_password",
        role=Role.DATA_ENGINEER,
        is_active=True
    )
    assert state.modal_open is False
    assert state.feedback_type == "success"
    assert "provisioned successfully" in state.feedback_msg

    carol_id = app_auth.users_by_username.get("carol_engineer")
    assert carol_id is not None
    carol = app_auth.users.get(carol_id)
    assert carol.email == "carol@enterprise.com"
    assert Role.DATA_ENGINEER in carol.roles
    assert carol.is_active is True

    # Carol can log in with provisioned password
    assert app_auth.authenticate("carol_engineer", "carol_initial_password") is not None

    # 2b. Edit User
    state.open_edit_modal(carol_id)
    assert state.modal_open is True
    assert state.modal_mode == "edit"
    assert state.input_username == "carol_engineer"
    assert state.input_email == "carol@enterprise.com"

    state.save_user(
        username="carol_lead",
        email="carol.lead@enterprise.com",
        password="",
        role=Role.ADMIN,
        is_active=True
    )
    assert state.modal_open is False
    assert state.feedback_type == "success"

    carol_updated = app_auth.users.get(carol_id)
    assert carol_updated.username == "carol_lead"
    assert carol_updated.email == "carol.lead@enterprise.com"
    assert Role.ADMIN in carol_updated.roles

    # 2c. Reset Password
    state.open_password_modal(carol_id)
    assert state.modal_open is True
    assert state.modal_mode == "password"

    state.save_user(password="carol_new_secure_pwd_2026")
    assert state.modal_open is False
    assert state.feedback_type == "success"

    # Verify password changed
    assert app_auth.authenticate("carol_lead", "carol_initial_password") is None
    assert app_auth.authenticate("carol_lead", "carol_new_secure_pwd_2026") is not None

    # 2d. Toggle Active / Disabled
    state.toggle_active(carol_id)
    carol_toggled = app_auth.users.get(carol_id)
    assert carol_toggled.is_active is False
    assert "deactivated" in state.feedback_msg

    state.toggle_active(carol_id)
    carol_toggled2 = app_auth.users.get(carol_id)
    assert carol_toggled2.is_active is True
    assert "activated" in state.feedback_msg

    # 2e. Guard: Admin cannot deactivate or delete self
    state.toggle_active(admin.id)
    assert "Security restriction" in state.feedback_msg
    assert state.feedback_type == "error"
    assert admin.is_active is True

    state.delete_user_action(admin.id)
    assert "Security restriction" in state.feedback_msg
    assert state.feedback_type == "error"
    assert app_auth.users.get(admin.id) is not None

    # 2f. Delete User
    state.delete_user_action(carol_id)
    assert state.feedback_type == "success"
    assert "deleted permanently" in state.feedback_msg
    assert app_auth.users.get(carol_id) is None


def test_admin_users_view_render():
    admin = app_auth.get_or_create_user("view_admin", "pass123", email="view_admin@test.com", roles=[Role.ADMIN])
    regular = app_auth.get_or_create_user("view_user", "pass123", email="view_user@test.com", roles=[Role.USER])

    # Unauthenticated / non-admin access
    _current_user_var.set(regular)
    comp_unauth = admin_users_view()
    html_unauth = comp_unauth.render({})
    assert "ACCESS RESTRICTED" in html_unauth
    assert "Enterprise Administrator Clearance Required" in html_unauth

    # Admin access
    _current_user_var.set(admin)
    comp_admin = admin_users_view()
    html_admin = comp_admin.render({})
    assert "User Identity" in html_admin
    assert "Total Accounts" in html_admin
    assert "Central Identity Directory" in html_admin
    assert "view_admin" in html_admin
    assert "Provision New User" in html_admin
