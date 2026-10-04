"""
Tests for PyDataUI Pluggable Storage Engine.
Verifies Memory and SQLite WAL storage backends, cross-process simulation,
session serialization, user persistence, API key verification, and token revocation.
"""
import os
import tempfile
import time
import pytest

from pydataui.session import Session, SessionManager
from pydataui.auth.manager import AuthManager
from pydataui.auth.models import User
from pydataui.state import State
from pydataui.storage import (
    MemorySessionStore,
    MemoryAuthStore,
    SQLiteSessionStore,
    SQLiteAuthStore,
    parse_storage_path,
)
from pydataui.app import App


class SampleCounterState(State):
    count: int = 0
    label: str = "initial"

    def increment(self):
        self.count += 1


def test_parse_storage_path():
    assert parse_storage_path(None) is None
    assert parse_storage_path("memory") is None
    assert parse_storage_path(":memory:") is None
    assert parse_storage_path("sqlite") == ".pydataui_storage.db"
    assert parse_storage_path("sqlite:///data/app.db") == "data/app.db"
    assert parse_storage_path("sqlite://data/app.db") == "data/app.db"
    assert parse_storage_path("custom.sqlite3") == "custom.sqlite3"


def test_sqlite_session_store_direct():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test_sessions.db")
        store = SQLiteSessionStore(db_path)

        # Non-existent session
        assert store.get("non-existent") is None

        # Save and get session
        payload = {"data": {"foo": "bar"}, "count": 42}
        now = time.time()
        store.save("sess-1", payload, now)

        retrieved = store.get("sess-1")
        assert retrieved is not None
        assert retrieved["data"]["foo"] == "bar"
        assert retrieved["count"] == 42

        # Update session
        payload["count"] = 43
        store.save("sess-1", payload, now + 1)
        assert store.get("sess-1")["count"] == 43

        # Delete session
        store.delete("sess-1")
        assert store.get("sess-1") is None


def test_cross_process_session_sharing():
    """Simulate two independent worker processes accessing the same SQLite database file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "cluster.db")
        secret = "0123456789abcdef0123456789abcdef"

        # Worker 1 creates a session and mutates state
        worker1_store = SQLiteSessionStore(db_path)
        mgr1 = SessionManager(secret=secret, store=worker1_store)

        session1 = mgr1.create_session()
        session1.data["user_id"] = "user_42"
        counter = SampleCounterState()
        counter.count = 99
        counter.label = "worker1_value"
        session1.state_instances["SampleCounterState"] = counter
        mgr1.save_session(session1)

        sid = session1.session_id
        cookie = mgr1.sign_session_id(sid)

        # Worker 2 (separate process / instance) receives the cookie
        worker2_store = SQLiteSessionStore(db_path)
        mgr2 = SessionManager(secret=secret, store=worker2_store)

        session2 = mgr2.parse_session_cookie(cookie)
        assert session2 is not None
        assert session2.session_id == sid
        assert session2.data["user_id"] == "user_42"
        assert "SampleCounterState" in session2.state_instances
        loaded_counter = session2.state_instances["SampleCounterState"]
        assert loaded_counter.count == 99
        assert loaded_counter.label == "worker1_value"

        # Worker 2 modifies the state and saves
        loaded_counter.increment()
        loaded_counter.label = "worker2_updated"
        session2.data["last_action"] = "incremented"
        mgr2.save_session(session2)

        # Worker 1 reads back the session and sees the updates from Worker 2
        refreshed_session1 = mgr1.get_session(sid)
        assert refreshed_session1.data["last_action"] == "incremented"
        assert refreshed_session1.state_instances["SampleCounterState"].count == 100
        assert refreshed_session1.state_instances["SampleCounterState"].label == "worker2_updated"


def test_sqlite_auth_store_cross_process():
    """Simulate user auth, API keys, and token revocations across worker processes."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "auth_cluster.db")
        secret = "0123456789abcdef0123456789abcdef0123456789abcdef"

        # Worker 1 sets up auth and creates user
        w1_store = SQLiteAuthStore(db_path)
        auth1 = AuthManager(secret_key=secret, store=w1_store)
        user = auth1.add_user("alice", "Password123!", email="alice@test.com", roles=["admin"])
        assert user.username == "alice"

        # Worker 2 authenticates the same user
        w2_store = SQLiteAuthStore(db_path)
        auth2 = AuthManager(secret_key=secret, store=w2_store)
        token = auth2.authenticate("alice", "Password123!")
        assert token is not None

        # Verify token in Worker 1
        verified_user = auth1.verify_token(token)
        assert verified_user is not None
        assert verified_user.id == user.id
        assert "admin" in verified_user.roles

        # Worker 1 creates an API key
        key_record = auth1.create_api_key(name="prod-key", user_id=user.id, scopes=["read", "write"])
        raw_key = key_record.key

        # Worker 2 verifies the API key
        verified_key = auth2.verify_api_key(raw_key)
        assert verified_key is not None
        assert verified_key.name == "prod-key"
        assert "write" in verified_key.scopes
        assert verified_key.usage_count == 1

        # Worker 2 revokes the token
        auth2.revoke_token(token)

        # Worker 1 should now reject the token
        assert auth1.verify_token(token) is None


def test_app_sqlite_storage_configuration():
    """Verify that App accepts storage parameter and configures SQLite stores correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "app_storage.db")
        storage_url = f"sqlite:///{db_path}"

        app = App(title="Test Storage App", storage=storage_url)
        assert isinstance(app._session_manager._store, SQLiteSessionStore)
        assert app._session_manager._store.db_path == db_path

        auth = AuthManager(secret_key="0123456789abcdef0123456789abcdef")
        app.setup_auth(auth)
        assert isinstance(app.auth._store, SQLiteAuthStore)
        assert app.auth._store.db_path == db_path
