"""
Comprehensive tests for PyDataUI dual-storage engine:
PostgreSQL and SQLite storage backends, URL parsing, OCC versioning,
cluster secret sharing, login throttling, and the unified Database client.
"""
import json
import os
import sqlite3
import time
import pytest
from unittest.mock import MagicMock, patch

from pydataui import (
    App, AuthManager, User, Role, APIKey,
    PostgresSessionStore, PostgresAuthStore,
    SQLiteSessionStore, SQLiteAuthStore,
    MemorySessionStore, MemoryAuthStore,
    Database, parse_storage_backend, parse_storage_path,
    create_session_store, create_auth_store,
    ConcurrencyError
)


# ==============================================================================
# 1. URL Parsing & Factory Tests
# ==============================================================================

def test_parse_storage_backend_postgres():
    urls = [
        "postgresql://user:pass@localhost:5432/dbname",
        "postgres://user:pass@localhost:5432/dbname",
        "postgresql+psycopg://user:pass@localhost:5432/dbname",
        "postgresql+psycopg2://user:pass@localhost:5432/dbname",
    ]
    for url in urls:
        backend, target = parse_storage_backend(url)
        assert backend == "postgres"
        assert target == "postgresql://user:pass@localhost:5432/dbname"


def test_parse_storage_backend_sqlite():
    cases = [
        ("sqlite:///custom.db", "custom.db"),
        ("sqlite://data/app.sqlite", "data/app.sqlite"),
        ("sqlite", ".pydataui_storage.db"),
        ("my_database.db", "my_database.db"),
        ("production.sqlite3", "production.sqlite3"),
    ]
    for raw, expected in cases:
        backend, target = parse_storage_backend(raw)
        assert backend == "sqlite"
        assert target == expected


def test_parse_storage_backend_memory():
    for raw in ["memory", ":memory:", "", None]:
        backend, target = parse_storage_backend(raw)
        assert backend == "memory"
        assert target == ""


def test_parse_storage_path_backward_compat():
    assert parse_storage_path("sqlite:///app.db") == "app.db"
    assert parse_storage_path("app.sqlite") == "app.sqlite"
    assert parse_storage_path("postgresql://localhost/db") is None
    assert parse_storage_path("memory") is None


def test_create_stores_factories(tmp_path):
    # SQLite
    db_file = str(tmp_path / "factory.db")
    s_store = create_session_store(f"sqlite:///{db_file}")
    a_store = create_auth_store(f"sqlite:///{db_file}")
    assert isinstance(s_store, SQLiteSessionStore)
    assert isinstance(a_store, SQLiteAuthStore)

    # Memory
    m_s = create_session_store("memory")
    m_a = create_auth_store(None)
    assert isinstance(m_s, MemorySessionStore)
    assert isinstance(m_a, MemoryAuthStore)


# ==============================================================================
# 2. Driver Missing Error Handling
# ==============================================================================

def test_missing_postgres_driver_raises_clear_error():
    from pydataui.storage import _get_pg_driver
    orig_import = __import__
    def mock_import(name, *args, **kwargs):
        if name in ("psycopg", "psycopg2"):
            raise ImportError(f"No module named {name}")
        return orig_import(name, *args, **kwargs)
    with patch("builtins.__import__", side_effect=mock_import):
        with pytest.raises(ImportError) as exc_info:
            _get_pg_driver()
        assert "PostgreSQL storage requires 'psycopg'" in str(exc_info.value)
        assert "pip install 'pydataui[postgres]'" in str(exc_info.value)


# ==============================================================================
# 3. Simulated PostgreSQL In-Memory Engine for Store Validation
# ==============================================================================

class PostgresMockCursor:
    """Simulates a DB-API cursor converting %s parameter syntax to ? for in-memory SQLite backing."""
    def __init__(self, conn):
        self._conn = conn
        self._cur = conn.cursor()
        self.rowcount = 0
        self.description = None

    def execute(self, sql, params=()):
        # Replace %s with ? for SQLite test engine
        import re
        adapted = re.sub(r'(?<!%)(%s)', '?', sql)
        # Adapt RETURNING version in INSERT
        if "RETURNING version" in adapted:
            adapted = adapted.replace("RETURNING version", "")
            self._cur.execute(adapted, params)
            self.rowcount = self._cur.rowcount
            # Fetch version of inserted row
            cur2 = self._conn.cursor()
            cur2.execute("SELECT version FROM pdu_sessions WHERE session_id = ?", (params[0],))
            self._mock_returning = cur2.fetchone()
        else:
            self._mock_returning = None
            self._cur.execute(adapted, params)
            self.rowcount = self._cur.rowcount
        self.description = self._cur.description
        return self

    def fetchone(self):
        if getattr(self, "_mock_returning", None):
            res = self._mock_returning
            self._mock_returning = None
            return res
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def close(self):
        self._cur.close()


class PostgresMockConnection:
    """Wraps an in-memory SQLite connection to present a PostgreSQL-like DB-API interface."""
    def __init__(self):
        self._sqlite = sqlite3.connect(":memory:", check_same_thread=False)
        self.closed = False

    def cursor(self):
        return PostgresMockCursor(self._sqlite)

    def commit(self):
        self._sqlite.commit()

    def rollback(self):
        self._sqlite.rollback()

    def close(self):
        self.closed = True
        self._sqlite.close()


# ==============================================================================
# 4. PostgresSessionStore Unit Tests
# ==============================================================================

def test_postgres_session_store_crud_and_occ():
    mock_conn = PostgresMockConnection()
    store = PostgresSessionStore(
        dsn="postgresql://user:pass@localhost:5432/testdb",
        connection_factory=lambda: mock_conn
    )

    # 1. Cluster Secret
    secret1 = store.get_or_create_cluster_secret()
    assert secret1 and len(secret1) == 64
    secret2 = store.get_or_create_cluster_secret()
    assert secret1 == secret2

    # 2. Initial Save (version 1)
    payload = {"user_id": "u1", "role": "admin"}
    now = time.time()
    ver1 = store.save("sess_100", payload, now, expected_version=None)
    assert ver1 == 1

    # 3. Get Session
    loaded = store.get("sess_100")
    assert loaded is not None
    assert loaded["user_id"] == "u1"
    assert loaded["_version"] == 1

    # 4. OCC Safe Update (expected_version matches)
    payload["role"] = "superadmin"
    ver2 = store.save("sess_100", payload, now + 1, expected_version=1)
    assert ver2 == 2

    # 5. OCC Conflict (stale expected_version)
    with pytest.raises(ConcurrencyError) as exc_info:
        store.save("sess_100", {"role": "hacked"}, now + 2, expected_version=1)
    assert "expected version 1, but found 2" in str(exc_info.value)

    # 6. Touch
    store.touch("sess_100", now + 10)
    assert store.get("sess_100")["_version"] == 2

    # 7. Cleanup Expired
    cleaned = store.cleanup_expired(max_age=5)
    # last_accessed is now + 10, so not expired
    assert cleaned == 0
    cleaned2 = store.cleanup_expired(max_age=-100)
    assert cleaned2 == 1
    assert store.get("sess_100") is None


def test_postgres_concurrent_state_field_increments_no_lost_updates():
    """
    Validates that two independent session managers with PostgreSQL storage
    concurrently updating a reactive State field do NOT suffer from lost updates.
    """
    from pydataui import State
    from pydataui.session import SessionManager

    class CounterState(State):
        count: int = 0
        def increment(self):
            self.count += 1

    mock_conn = PostgresMockConnection()
    store1 = PostgresSessionStore(
        dsn="postgresql://user:pass@localhost:5432/testdb",
        connection_factory=lambda: mock_conn
    )
    store2 = PostgresSessionStore(
        dsn="postgresql://user:pass@localhost:5432/testdb",
        connection_factory=lambda: mock_conn
    )

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


# ==============================================================================
# 5. PostgresAuthStore Unit Tests
# ==============================================================================

def test_postgres_auth_store_users_and_keys():
    mock_conn = PostgresMockConnection()
    store = PostgresAuthStore(
        dsn="postgresql://user:pass@localhost:5432/testdb",
        connection_factory=lambda: mock_conn
    )

    # 1. User Persistence
    u = User(
        id="usr_pg_1",
        username="alice",
        email="alice@example.com",
        password_hash="argon2id$hashed",
        roles=["admin", "ml_engineer"],
        is_active=True,
        created_at="2026-10-04T00:00:00Z",
        last_login=None,
        metadata={}
    )
    store.save_user(u)

    by_id = store.get_user("usr_pg_1")
    assert by_id is not None
    assert by_id.username == "alice"
    assert by_id.roles == ["admin", "ml_engineer"]

    by_name = store.get_user_by_username("alice")
    assert by_name is not None
    assert by_name.id == "usr_pg_1"

    all_users = store.get_all_users()
    assert "usr_pg_1" in all_users

    # 2. API Key Persistence
    key = APIKey(
        key="",
        key_id="key_123",
        name="CI-Inference",
        user_id="usr_pg_1",
        scopes=["read", "write"],
        created_at="2026-10-04T00:00:00Z",
        expires_at=None,
        last_used=None,
        is_active=True,
        usage_count=0
    )
    store.save_api_key("digest_sha256_abc", key)
    loaded_key = store.get_api_key("digest_sha256_abc")
    assert loaded_key is not None
    assert loaded_key.name == "CI-Inference"
    assert "write" in loaded_key.scopes

    # 3. Token Revocation
    assert not store.is_token_revoked("jti_xyz_99")
    store.revoke_token("jti_xyz_99", exp=time.time() + 3600)
    assert store.is_token_revoked("jti_xyz_99")

    # 4. Login Throttling
    key_ip = "192.168.1.50"
    for i in range(4):
        locked, sec = store.record_failed_login(key_ip, max_attempts=5)
        assert not locked

    locked, sec = store.record_failed_login(key_ip, max_attempts=5, lockout_seconds=300)
    assert locked
    assert sec == 300

    is_l, rem = store.is_login_locked(key_ip)
    assert is_l
    assert rem > 0

    store.reset_failed_logins(key_ip)
    is_l_after, _ = store.is_login_locked(key_ip)
    assert not is_l_after


# ==============================================================================
# 6. Unified Database Client Tests
# ==============================================================================

def test_database_client_sqlite(tmp_path):
    db_file = str(tmp_path / "app_data.db")
    db = Database(f"sqlite:///{db_file}")

    db.create_tables("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stars INTEGER NOT NULL DEFAULT 0
        );
    """)

    # Test auto placeholder adaptation (%s -> ?)
    db.execute("INSERT INTO projects (id, name, stars) VALUES (%s, %s, %s)", ("p1", "Alpha", 42))
    
    # Test query with ? placeholder
    row = db.query_one("SELECT * FROM projects WHERE id = ?", ("p1",))
    assert row is not None
    assert row["name"] == "Alpha"
    assert row["stars"] == 42

    # Test query returning list of dicts
    db.execute("INSERT INTO projects (id, name, stars) VALUES (?, ?, ?)", ("p2", "Beta", 100))
    all_rows = db.query("SELECT * FROM projects ORDER BY stars DESC")
    assert len(all_rows) == 2
    assert all_rows[0]["name"] == "Beta"
    assert all_rows[1]["name"] == "Alpha"

    # Test transaction rollback
    try:
        with db.transaction():
            db.execute("INSERT INTO projects (id, name, stars) VALUES (?, ?, ?)", ("p3", "Gamma", 5))
            raise RuntimeError("Force abort transaction")
    except RuntimeError:
        pass

    assert db.query_one("SELECT * FROM projects WHERE id = ?", ("p3",)) is None
    db.close()


def test_database_client_simulated_postgres():
    mock_conn = PostgresMockConnection()
    db = Database(
        url_or_path="postgresql://user:pass@localhost:5432/mydb",
        connection_factory=lambda: mock_conn
    )
    assert db.backend == "postgres"

    db.create_tables([
        "CREATE TABLE models (id TEXT PRIMARY KEY, name TEXT NOT NULL, latency REAL NOT NULL)"
    ])

    # Written with ? placeholder, Database translates to %s for PostgreSQL
    db.execute("INSERT INTO models (id, name, latency) VALUES (?, ?, ?)", ("m1", "Sonnet 3.5", 138.5))

    row = db.query_one("SELECT * FROM models WHERE id = %s", ("m1",))
    assert row is not None
    assert row["name"] == "Sonnet 3.5"
    assert row["latency"] == 138.5


# ==============================================================================
# 7. App Integration with PostgreSQL Storage
# ==============================================================================

def test_app_configured_with_postgres_storage():
    mock_conn = PostgresMockConnection()
    with patch("pydataui.storage.PostgresSessionStore._get_connection", return_value=mock_conn), \
         patch("pydataui.storage.PostgresAuthStore._get_connection", return_value=mock_conn):
        
        app = App(
            title="Postgres App",
            storage="postgresql://user:pass@localhost:5432/production_app"
        )
        assert isinstance(app._session_manager._store, PostgresSessionStore)

        auth = AuthManager(secret_key="secret-key-32-bytes-minimum-length!")
        app.setup_auth(auth)
        assert isinstance(auth._store, PostgresAuthStore)
