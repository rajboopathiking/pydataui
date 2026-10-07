import os
import tempfile
import threading
import time
import pytest

from pydataui import App
from pydataui.session import SessionManager, Session
from pydataui.storage import SQLiteSessionStore, SQLiteAuthStore, MemoryAuthStore
from pydataui.auth import AuthManager
from pydataui.exceptions import ConcurrencyError, AuthenticationThrottledError


def test_sqlite_concurrent_session_updates_no_lost_updates():
    """
    Validates that two independent session managers (simulating two worker processes)
    updating the same session concurrently do NOT suffer from lost updates.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store1 = SQLiteSessionStore(db_path)
        store2 = SQLiteSessionStore(db_path)

        secret = "test-cluster-shared-secret-32bytes-minimum!"
        mgr1 = SessionManager(secret=secret, store=store1)
        mgr2 = SessionManager(secret=secret, store=store2)

        # 1. Initialize session with counter = 0
        s = mgr1.create_session()
        s.data["counter"] = 0
        mgr1.save_session(s)
        session_id = s.session_id

        # 2. Worker 1 and Worker 2 both load the session at version 1
        sess1 = mgr1.get_session(session_id)
        sess2 = mgr2.get_session(session_id)
        assert sess1 is not None and sess2 is not None
        assert sess1.data["counter"] == 0
        assert sess2.data["counter"] == 0

        # 3. Worker 1 increments and saves (advancing DB to version 2)
        sess1.data["counter"] += 1
        mgr1.save_session(sess1)

        # 4. Worker 2 increments its in-memory counter and attempts to save
        sess2.data["counter"] += 1
        # With auto-merge OCC, Worker 2 reconciles its +1 delta against the DB version
        mgr2.save_session(sess2, auto_merge=True)

        # 5. Reload session from store: counter MUST be 2, not 1!
        final_sess = mgr1.get_session(session_id)
        assert final_sess is not None
        assert final_sess.data["counter"] == 2, f"Expected counter=2 (no lost updates), got {final_sess.data['counter']}"
        assert final_sess.version >= 3
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_concurrency_error_raised_when_auto_merge_disabled():
    """
    Validates that ConcurrencyError is explicitly raised when auto_merge=False
    and an outdated version update is attempted.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store1 = SQLiteSessionStore(db_path)
        store2 = SQLiteSessionStore(db_path)
        secret = "test-cluster-shared-secret-32bytes-minimum!"
        mgr1 = SessionManager(secret=secret, store=store1)
        mgr2 = SessionManager(secret=secret, store=store2)

        s = mgr1.create_session()
        s.data["val"] = "initial"
        mgr1.save_session(s)

        sess1 = mgr1.get_session(s.session_id)
        sess2 = mgr2.get_session(s.session_id)

        sess1.data["val"] = "update_1"
        mgr1.save_session(sess1)

        sess2.data["val"] = "update_2"
        with pytest.raises(ConcurrencyError):
            mgr2.save_session(sess2, auto_merge=False)
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_session_continuity_across_independent_apps():
    """
    Validates that two independent App instances sharing SQLite storage
    automatically share the cluster session secret and accept each other's cookies.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        # App 1 and App 2 created without explicit session_secret
        app1 = App(storage=f"sqlite:///{db_path}")
        app2 = App(storage=f"sqlite:///{db_path}")

        # Both apps must have retrieved the identical cluster session secret
        assert app1.config.session_secret == app2.config.session_secret
        assert len(app1.config.session_secret) >= 32

        # App 1 creates and signs a session cookie
        s1 = app1._session_manager.create_session()
        s1.data["user_email"] = "analyst@enterprise.com"
        app1._session_manager.save_session(s1)
        signed_cookie = app1._session_manager.sign_session_id(s1.session_id)

        # App 2 verifies and loads App 1's cookie with 100% fidelity
        verified_id = app2._session_manager.verify_session_id(signed_cookie)
        assert verified_id == s1.session_id

        loaded_s2 = app2._session_manager.parse_session_cookie(signed_cookie)
        assert loaded_s2 is not None
        assert loaded_s2.data["user_email"] == "analyst@enterprise.com"
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_login_throttling_brute_force_lockout():
    """
    Validates that login throttling locks out attackers after max failed attempts
    and returns AuthenticationThrottledError.
    """
    store = MemoryAuthStore()
    auth = AuthManager(
        secret_key="test-secret-key-32bytes-minimum-length!",
        store=store,
        max_login_attempts=3,
        lockout_duration_seconds=60,
        attempt_window_seconds=60
    )
    auth.add_user("target_user", "CorrectPassword123!")

    # 1. First 2 failed attempts: credentials invalid, not locked out yet
    assert auth.authenticate("target_user", "WrongPassword1") is None
    assert auth.authenticate("target_user", "WrongPassword2") is None

    # 2. Third failed attempt: reaches max_attempts (3)
    assert auth.authenticate("target_user", "WrongPassword3") is None

    # 3. Fourth attempt (even with correct password!): must be throttled and locked out
    with pytest.raises(AuthenticationThrottledError) as exc_info:
        auth.authenticate("target_user", "CorrectPassword123!")
    assert "Too many failed login attempts" in str(exc_info.value)

    # 4. Successful login on another user resets attempts
    auth.add_user("other_user", "OtherPass123!")
    assert auth.authenticate("other_user", "Wrong1") is None
    token = auth.authenticate("other_user", "OtherPass123!")
    assert token is not None
    # Next failed attempt for other_user starts at 1, not locked
    assert auth.authenticate("other_user", "WrongAgain") is None


def test_sqlite_login_throttling_cross_process():
    """
    Validates that login throttling persists across independent SQLite store instances.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store1 = SQLiteAuthStore(db_path)
        store2 = SQLiteAuthStore(db_path)

        secret = "test-secret-key-32bytes-minimum-length!"
        auth1 = AuthManager(secret_key=secret, store=store1, max_login_attempts=2, lockout_duration_seconds=60)
        auth2 = AuthManager(secret_key=secret, store=store2, max_login_attempts=2, lockout_duration_seconds=60)

        auth1.add_user("enterprise_admin", "MasterKey123!")

        # Worker 1 registers 1 failed attempt
        assert auth1.authenticate("enterprise_admin", "bad1") is None

        # Worker 2 registers 2nd failed attempt -> triggers lockout
        assert auth2.authenticate("enterprise_admin", "bad2") is None

        # Worker 1 now sees lockout from Worker 2's action
        with pytest.raises(AuthenticationThrottledError):
            auth1.authenticate("enterprise_admin", "MasterKey123!")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_mutate_session_multithreaded_concurrency():
    """
    Validates that mutate_session handles high-contention concurrent increments
    across multiple threads without losing any updates.
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store = SQLiteSessionStore(db_path)
        mgr = SessionManager(secret="test-secret-key-32bytes-minimum-length!", store=store)

        s = mgr.create_session()
        s.data["count"] = 0
        mgr.save_session(s)
        session_id = s.session_id

        num_threads = 10
        increments_per_thread = 5

        def worker():
            local_store = SQLiteSessionStore(db_path)
            local_mgr = SessionManager(secret="test-secret-key-32bytes-minimum-length!", store=local_store)
            for _ in range(increments_per_thread):
                def inc(sess):
                    sess.data["count"] += 1
                local_mgr.mutate_session(session_id, inc)

        threads = [threading.Thread(target=worker) for _ in range(num_threads)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final = mgr.get_session(session_id)
        assert final is not None
        assert final.data["count"] == num_threads * increments_per_thread
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


def test_sqlite_concurrent_state_field_increments_no_lost_updates():
    """
    Validates that two independent session managers (simulating two worker processes)
    updating the same reactive State instance field concurrently do NOT suffer from lost updates.
    """
    from pydataui import State

    class CounterState(State):
        count: int = 0
        def increment(self):
            self.count += 1

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    try:
        store1 = SQLiteSessionStore(db_path)
        store2 = SQLiteSessionStore(db_path)
        secret = "test-cluster-shared-secret-32bytes-minimum!"
        mgr1 = SessionManager(secret=secret, store=store1)
        mgr2 = SessionManager(secret=secret, store=store2)

        # 1. Initialize session with CounterState count = 0
        s = mgr1.create_session()
        c = CounterState()
        c.count = 0
        s.state_instances["CounterState"] = c
        mgr1.save_session(s)
        session_id = s.session_id

        # 2. Worker 1 and Worker 2 both load the session at version 1
        sess1 = mgr1.get_session(session_id)
        sess2 = mgr2.get_session(session_id)
        assert sess1 is not None and sess2 is not None
        assert sess1.state_instances["CounterState"].count == 0
        assert sess2.state_instances["CounterState"].count == 0

        # 3. Worker 1 increments and saves (advancing DB to version 2)
        sess1.state_instances["CounterState"].increment()
        mgr1.save_session(sess1)

        # 4. Worker 2 increments its in-memory state and saves (auto-merge reconciles State delta)
        sess2.state_instances["CounterState"].increment()
        mgr2.save_session(sess2, auto_merge=True)

        # 5. Reload session from store: CounterState.count MUST be 2, not 1!
        final_sess = mgr1.get_session(session_id)
        assert final_sess is not None
        actual_count = final_sess.state_instances["CounterState"].count
        assert actual_count == 2, f"Expected CounterState.count=2 (no lost updates), got {actual_count}"
        assert final_sess.version >= 3
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
