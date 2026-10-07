"""
Pluggable Storage Engine for PyDataUI Sessions and Authentication.

Supports:
1. MemoryStore: Ultra-fast in-memory storage (ideal for single-worker and test suites).
2. SQLiteStore: High-concurrency, cross-process persistent storage using standard library sqlite3
   with Write-Ahead Logging (WAL) mode. Allows multiple worker processes (--workers 4+)
   and container replicas sharing a disk volume to access shared sessions and auth state
   with zero external infrastructure.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union
from dataclasses import asdict
from contextlib import contextmanager

from .auth.models import User, APIKey
from .exceptions import ConcurrencyError


# ==============================================================================
# Base Interfaces
# ==============================================================================

class BaseSessionStore(ABC):
    @abstractmethod
    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve raw session payload by session_id."""
        pass

    @abstractmethod
    def save(self, session_id: str, payload: Dict[str, Any], last_accessed: float, expected_version: Optional[int] = None) -> int:
        """
        Save session payload with optimistic concurrency control.
        Returns the new version integer. Raises ConcurrencyError on conflict.
        """
        pass

    @abstractmethod
    def touch(self, session_id: str, last_accessed: float) -> None:
        """Update last_accessed timestamp without modifying payload or version."""
        pass

    @abstractmethod
    def delete(self, session_id: str) -> None:
        """Delete session by session_id."""
        pass

    @abstractmethod
    def cleanup_expired(self, max_age: int) -> int:
        """Remove sessions older than max_age seconds. Returns count removed."""
        pass


class BaseAuthStore(ABC):
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        pass

    @abstractmethod
    def save_user(self, user: User) -> None:
        pass

    @abstractmethod
    def get_all_users(self) -> Dict[str, User]:
        pass

    @abstractmethod
    def get_api_key(self, digest: str) -> Optional[APIKey]:
        pass

    @abstractmethod
    def save_api_key(self, digest: str, key: APIKey) -> None:
        pass

    @abstractmethod
    def get_all_api_keys(self) -> Dict[str, APIKey]:
        pass

    @abstractmethod
    def is_token_revoked(self, jti: str) -> bool:
        pass

    @abstractmethod
    def revoke_token(self, jti: str, exp: float) -> None:
        pass

    @abstractmethod
    def record_failed_login(self, key: str, window_seconds: int = 900, max_attempts: int = 5, lockout_seconds: int = 900) -> Tuple[bool, int]:
        """Record failed login attempt. Returns (is_locked_out: bool, remaining_seconds: int)."""
        pass

    @abstractmethod
    def is_login_locked(self, key: str) -> Tuple[bool, int]:
        """Check if key is locked out. Returns (is_locked: bool, remaining_seconds: int)."""
        pass

    @abstractmethod
    def reset_failed_logins(self, key: str) -> None:
        """Reset failed login attempts on successful login."""
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        """Delete user by user_id. Returns True if deleted, False otherwise."""
        pass


# ==============================================================================
# In-Memory Storage Implementations (Default)
# ==============================================================================

class MemorySessionStore(BaseSessionStore):
    def __init__(self):
        # session_id -> (payload, last_accessed, version)
        self._sessions: Dict[str, Tuple[Dict[str, Any], float, int]] = {}
        self._lock = threading.RLock()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._sessions.get(session_id)
            if record:
                payload = dict(record[0])
                payload["_version"] = record[2]
                return payload
            return None

    def save(self, session_id: str, payload: Dict[str, Any], last_accessed: float, expected_version: Optional[int] = None) -> int:
        with self._lock:
            record = self._sessions.get(session_id)
            if expected_version is not None and record is not None:
                curr_ver = record[2]
                if curr_ver != expected_version:
                    raise ConcurrencyError(
                        f"Concurrent update conflict for session '{session_id}': expected version {expected_version}, found {curr_ver}."
                    )
                new_ver = curr_ver + 1
            elif record is not None:
                new_ver = record[2] + 1
            else:
                new_ver = 1
            self._sessions[session_id] = (payload, last_accessed, new_ver)
            return new_ver

    def touch(self, session_id: str, last_accessed: float) -> None:
        with self._lock:
            record = self._sessions.get(session_id)
            if record:
                self._sessions[session_id] = (record[0], last_accessed, record[2])

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def cleanup_expired(self, max_age: int) -> int:
        now = time.time()
        with self._lock:
            expired = [sid for sid, (_, la, _) in self._sessions.items() if now - la > max_age]
            for sid in expired:
                del self._sessions[sid]
            return len(expired)


class MemoryAuthStore(BaseAuthStore):
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._users_by_username: Dict[str, str] = {}
        self._api_keys: Dict[str, APIKey] = {}
        self._revoked_tokens: Dict[str, float] = {}
        # key -> (attempts: int, last_attempt: float, locked_until: float)
        self._login_attempts: Dict[str, Tuple[int, float, float]] = {}
        self._lock = threading.RLock()

    def get_user(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._users.get(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        with self._lock:
            uid = self._users_by_username.get(username)
            return self._users.get(uid) if uid else None

    def save_user(self, user: User) -> None:
        with self._lock:
            self._users[user.id] = user
            self._users_by_username[user.username] = user.id

    def get_all_users(self) -> Dict[str, User]:
        with self._lock:
            return dict(self._users)

    def get_api_key(self, digest: str) -> Optional[APIKey]:
        with self._lock:
            return self._api_keys.get(digest)

    def save_api_key(self, digest: str, key: APIKey) -> None:
        with self._lock:
            self._api_keys[digest] = key

    def get_all_api_keys(self) -> Dict[str, APIKey]:
        with self._lock:
            return dict(self._api_keys)

    def is_token_revoked(self, jti: str) -> bool:
        now = time.time()
        with self._lock:
            self._revoked_tokens = {k: v for k, v in self._revoked_tokens.items() if v > now}
            return jti in self._revoked_tokens

    def revoke_token(self, jti: str, exp: float) -> None:
        with self._lock:
            self._revoked_tokens[jti] = exp

    def record_failed_login(self, key: str, window_seconds: int = 900, max_attempts: int = 5, lockout_seconds: int = 900) -> Tuple[bool, int]:
        now = time.time()
        with self._lock:
            record = self._login_attempts.get(key)
            if record:
                attempts, last_attempt, locked_until = record
                if locked_until > now:
                    return True, int(locked_until - now)
                if now - last_attempt > window_seconds:
                    attempts = 1
                else:
                    attempts += 1
            else:
                attempts = 1
                locked_until = 0.0

            if attempts >= max_attempts:
                locked_until = now + lockout_seconds
                self._login_attempts[key] = (attempts, now, locked_until)
                return True, lockout_seconds

            self._login_attempts[key] = (attempts, now, 0.0)
            return False, 0

    def is_login_locked(self, key: str) -> Tuple[bool, int]:
        now = time.time()
        with self._lock:
            record = self._login_attempts.get(key)
            if not record:
                return False, 0
            attempts, last_attempt, locked_until = record
            if locked_until > now:
                return True, int(locked_until - now)
            return False, 0

    def reset_failed_logins(self, key: str) -> None:
        with self._lock:
            self._login_attempts.pop(key, None)

    def delete_user(self, user_id: str) -> bool:
        with self._lock:
            user = self._users.pop(user_id, None)
            if user:
                self._users_by_username.pop(user.username, None)
                return True
            return False


# ==============================================================================
# SQLite Multi-Process Persistent Storage (WAL Mode)
# ==============================================================================

class SQLiteSessionStore(BaseSessionStore):
    """
    High-performance, cross-process SQLite session store.
    Uses WAL (Write-Ahead Logging) mode and busy timeouts to allow concurrent
    multi-process workers (--workers 4+) to read and write sessions safely.
    """
    def __init__(self, db_path: str = ".pydataui_storage.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA busy_timeout = 30000;")
            self._local.conn = conn
        return self._local.conn

    def _init_db(self) -> None:
        parent = os.path.dirname(os.path.abspath(self.db_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdu_sessions (
                    session_id TEXT PRIMARY KEY,
                    payload TEXT NOT NULL,
                    last_accessed REAL NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pdu_sessions_accessed ON pdu_sessions(last_accessed);")
            
            # Migration check for existing databases lacking version column
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(pdu_sessions);")
            cols = [row[1] for row in cursor.fetchall()]
            if "version" not in cols:
                conn.execute("ALTER TABLE pdu_sessions ADD COLUMN version INTEGER NOT NULL DEFAULT 1;")

            # Cluster metadata table for cross-worker secrets
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdu_cluster_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def get_or_create_cluster_secret(self, key_name: str = "cluster_session_secret") -> str:
        """
        Retrieves or initializes a cluster-wide high-entropy HMAC secret shared across all workers.
        Guarantees that independent worker processes accept each other's signed cookies by default.
        """
        import secrets
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM pdu_cluster_metadata WHERE key = ?", (key_name,))
        row = cursor.fetchone()
        if row:
            return row[0]
        
        new_secret = secrets.token_hex(32)
        try:
            conn.execute("""
                INSERT INTO pdu_cluster_metadata (key, value)
                VALUES (?, ?)
                ON CONFLICT(key) DO NOTHING
            """, (key_name, new_secret))
            conn.commit()
        except sqlite3.IntegrityError:
            pass
            
        cursor.execute("SELECT value FROM pdu_cluster_metadata WHERE key = ?", (key_name,))
        row = cursor.fetchone()
        return row[0] if row else new_secret

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT payload, version FROM pdu_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        try:
            payload = json.loads(row[0])
            payload["_version"] = row[1]
            return payload
        except Exception:
            return None

    def save(self, session_id: str, payload: Dict[str, Any], last_accessed: float, expected_version: Optional[int] = None) -> int:
        conn = self._get_connection()
        data_str = json.dumps(payload)
        cursor = conn.cursor()

        if expected_version is not None:
            cursor.execute("SELECT version FROM pdu_sessions WHERE session_id = ?", (session_id,))
            existing = cursor.fetchone()
            if existing is None:
                new_ver = 1
                conn.execute("""
                    INSERT INTO pdu_sessions (session_id, payload, last_accessed, version)
                    VALUES (?, ?, ?, ?)
                """, (session_id, data_str, last_accessed, new_ver))
                conn.commit()
                return new_ver
            else:
                curr_ver = existing[0]
                if curr_ver != expected_version:
                    raise ConcurrencyError(
                        f"Concurrent update conflict for session '{session_id}': expected version {expected_version}, but found {curr_ver}."
                    )
                new_ver = curr_ver + 1
                cursor.execute("""
                    UPDATE pdu_sessions
                    SET payload = ?, last_accessed = ?, version = ?
                    WHERE session_id = ? AND version = ?
                """, (data_str, last_accessed, new_ver, session_id, expected_version))
                if cursor.rowcount == 0:
                    conn.rollback()
                    raise ConcurrencyError(
                        f"Concurrent update race condition for session '{session_id}'."
                    )
                conn.commit()
                return new_ver
        else:
            cursor.execute("""
                INSERT INTO pdu_sessions (session_id, payload, last_accessed, version)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(session_id) DO UPDATE SET
                    payload = excluded.payload,
                    last_accessed = excluded.last_accessed,
                    version = pdu_sessions.version + 1
            """, (session_id, data_str, last_accessed))
            conn.commit()
            cursor.execute("SELECT version FROM pdu_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            return row[0] if row else 1

    def touch(self, session_id: str, last_accessed: float) -> None:
        conn = self._get_connection()
        conn.execute("UPDATE pdu_sessions SET last_accessed = ? WHERE session_id = ?", (last_accessed, session_id))
        conn.commit()

    def delete(self, session_id: str) -> None:
        conn = self._get_connection()
        conn.execute("DELETE FROM pdu_sessions WHERE session_id = ?", (session_id,))
        conn.commit()

    def cleanup_expired(self, max_age: int) -> int:
        conn = self._get_connection()
        cutoff = time.time() - max_age
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pdu_sessions WHERE last_accessed < ?", (cutoff,))
        conn.commit()
        return cursor.rowcount


class SQLiteAuthStore(BaseAuthStore):
    """
    High-performance, cross-process SQLite auth store.
    Shares users, API keys, and token revocations across all workers.
    """
    def __init__(self, db_path: str = ".pydataui_storage.db"):
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "conn") or self._local.conn is None:
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA busy_timeout = 30000;")
            self._local.conn = conn
        return self._local.conn

    def _init_db(self) -> None:
        parent = os.path.dirname(os.path.abspath(self.db_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        try:
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdu_users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT NOT NULL,
                    password_hash TEXT NOT NULL,
                    roles TEXT NOT NULL,
                    is_active INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    metadata TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdu_api_keys (
                    digest TEXT PRIMARY KEY,
                    key_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    scopes TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT,
                    last_used TEXT,
                    is_active INTEGER NOT NULL,
                    usage_count INTEGER NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdu_revoked_tokens (
                    jti TEXT PRIMARY KEY,
                    exp REAL NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pdu_login_attempts (
                    key TEXT PRIMARY KEY,
                    attempts INTEGER NOT NULL,
                    last_attempt REAL NOT NULL,
                    locked_until REAL NOT NULL
                );
            """)
            conn.commit()
        finally:
            conn.close()

    def _row_to_user(self, row: tuple) -> User:
        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            roles=json.loads(row[4]),
            is_active=bool(row[5]),
            created_at=row[6],
            last_login=row[7],
            metadata=json.loads(row[8]) if row[8] else {}
        )

    def _row_to_api_key(self, row: tuple) -> APIKey:
        return APIKey(
            key="",  # Raw key is never stored in DB
            key_id=row[1],
            name=row[2],
            user_id=row[3],
            scopes=json.loads(row[4]),
            created_at=row[5],
            expires_at=row[6],
            last_used=row[7],
            is_active=bool(row[8]),
            usage_count=int(row[9])
        )

    def get_user(self, user_id: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password_hash, roles, is_active, created_at, last_login, metadata FROM pdu_users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return self._row_to_user(row) if row else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password_hash, roles, is_active, created_at, last_login, metadata FROM pdu_users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return self._row_to_user(row) if row else None

    def save_user(self, user: User) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM pdu_users WHERE username = ?", (user.username,))
        existing = cursor.fetchone()
        if existing and existing[0] != user.id:
            user.id = existing[0]

        conn.execute("""
            INSERT INTO pdu_users (id, username, email, password_hash, roles, is_active, created_at, last_login, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                username = excluded.username,
                email = excluded.email,
                password_hash = excluded.password_hash,
                roles = excluded.roles,
                is_active = excluded.is_active,
                created_at = excluded.created_at,
                last_login = excluded.last_login,
                metadata = excluded.metadata
        """, (
            user.id, user.username, user.email, user.password_hash,
            json.dumps(user.roles), 1 if user.is_active else 0,
            user.created_at, user.last_login, json.dumps(user.metadata or {})
        ))
        conn.commit()

    def get_all_users(self) -> Dict[str, User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password_hash, roles, is_active, created_at, last_login, metadata FROM pdu_users")
        result = {}
        for row in cursor.fetchall():
            u = self._row_to_user(row)
            result[u.id] = u
        return result

    def get_api_key(self, digest: str) -> Optional[APIKey]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT digest, key_id, name, user_id, scopes, created_at, expires_at, last_used, is_active, usage_count FROM pdu_api_keys WHERE digest = ?", (digest,))
        row = cursor.fetchone()
        return self._row_to_api_key(row) if row else None

    def save_api_key(self, digest: str, key: APIKey) -> None:
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO pdu_api_keys (digest, key_id, name, user_id, scopes, created_at, expires_at, last_used, is_active, usage_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(digest) DO UPDATE SET
                name = excluded.name,
                scopes = excluded.scopes,
                expires_at = excluded.expires_at,
                last_used = excluded.last_used,
                is_active = excluded.is_active,
                usage_count = excluded.usage_count
        """, (
            digest, key.key_id, key.name, key.user_id,
            json.dumps(key.scopes), key.created_at, key.expires_at,
            key.last_used, 1 if key.is_active else 0, key.usage_count
        ))
        conn.commit()

    def get_all_api_keys(self) -> Dict[str, APIKey]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT digest, key_id, name, user_id, scopes, created_at, expires_at, last_used, is_active, usage_count FROM pdu_api_keys")
        result = {}
        for row in cursor.fetchall():
            k = self._row_to_api_key(row)
            result[row[0]] = k
        return result

    def is_token_revoked(self, jti: str) -> bool:
        now = time.time()
        conn = self._get_connection()
        cursor = conn.cursor()
        # Clean expired revocations
        conn.execute("DELETE FROM pdu_revoked_tokens WHERE exp < ?", (now,))
        conn.commit()
        cursor.execute("SELECT 1 FROM pdu_revoked_tokens WHERE jti = ?", (jti,))
        return cursor.fetchone() is not None

    def revoke_token(self, jti: str, exp: float) -> None:
        conn = self._get_connection()
        conn.execute("""
            INSERT INTO pdu_revoked_tokens (jti, exp)
            VALUES (?, ?)
            ON CONFLICT(jti) DO UPDATE SET exp = excluded.exp
        """, (jti, exp))
        conn.commit()

    def record_failed_login(self, key: str, window_seconds: int = 900, max_attempts: int = 5, lockout_seconds: int = 900) -> Tuple[bool, int]:
        now = time.time()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT attempts, last_attempt, locked_until FROM pdu_login_attempts WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            attempts, last_attempt, locked_until = row
            if locked_until > now:
                return True, int(locked_until - now)
            if now - last_attempt > window_seconds:
                attempts = 1
            else:
                attempts += 1
        else:
            attempts = 1
            locked_until = 0.0

        if attempts >= max_attempts:
            locked_until = now + lockout_seconds
            conn.execute("""
                INSERT INTO pdu_login_attempts (key, attempts, last_attempt, locked_until)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    attempts = excluded.attempts,
                    last_attempt = excluded.last_attempt,
                    locked_until = excluded.locked_until
            """, (key, attempts, now, locked_until))
            conn.commit()
            return True, lockout_seconds

        conn.execute("""
            INSERT INTO pdu_login_attempts (key, attempts, last_attempt, locked_until)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                attempts = excluded.attempts,
                last_attempt = excluded.last_attempt,
                locked_until = excluded.locked_until
        """, (key, attempts, now, 0.0))
        conn.commit()
        return False, 0

    def is_login_locked(self, key: str) -> Tuple[bool, int]:
        now = time.time()
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT locked_until FROM pdu_login_attempts WHERE key = ?", (key,))
        row = cursor.fetchone()
        if not row:
            return False, 0
        locked_until = row[0]
        if locked_until > now:
            return True, int(locked_until - now)
        return False, 0

    def reset_failed_logins(self, key: str) -> None:
        conn = self._get_connection()
        conn.execute("DELETE FROM pdu_login_attempts WHERE key = ?", (key,))
        conn.commit()

    def delete_user(self, user_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM pdu_users WHERE id = ?", (user_id,))
        count = cursor.rowcount
        conn.commit()
        return count > 0



# ==============================================================================
# PostgreSQL Multi-Worker & Multi-Instance Storage Engine
# ==============================================================================

def _get_pg_driver():
    """
    Dynamically loads psycopg (psycopg 3) or psycopg2.
    Raises ImportError with clear installation instructions if neither is present.
    """
    try:
        import psycopg
        return ("psycopg", psycopg)
    except ImportError:
        pass

    try:
        import psycopg2
        return ("psycopg2", psycopg2)
    except ImportError:
        pass

    raise ImportError(
        "PostgreSQL storage requires 'psycopg' (v3) or 'psycopg2'. "
        "Install via: pip install 'pydataui[postgres]' or pip install 'psycopg[binary]>=3.1.0'"
    )


class PostgresSessionStore(BaseSessionStore):
    """
    High-performance, multi-instance PostgreSQL session store.
    Shares sessions across independent worker processes, containers, and server instances
    with Optimistic Concurrency Control (OCC) and automatic cluster secret sharing.
    """
    def __init__(self, dsn: str, connection_factory: Optional[Callable] = None):
        self.dsn = dsn
        self.connection_factory = connection_factory
        self._local = threading.local()
        self._init_db()

    def _get_connection(self):
        if self.connection_factory is not None:
            return self.connection_factory()
        conn = getattr(self._local, "conn", None)
        if conn is None or getattr(conn, "closed", False):
            driver_type, driver = _get_pg_driver()
            if driver_type == "psycopg":
                conn = driver.connect(self.dsn, autocommit=False)
            else:
                conn = driver.connect(self.dsn)
                conn.autocommit = False
            self._local.conn = conn
        return self._local.conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdu_sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
                    payload TEXT NOT NULL,
                    last_accessed DOUBLE PRECISION NOT NULL,
                    version INTEGER NOT NULL DEFAULT 1
                );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pdu_sessions_accessed ON pdu_sessions(last_accessed);")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdu_cluster_metadata (
                    key VARCHAR(255) PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def get_or_create_cluster_secret(self, key_name: str = "cluster_session_secret") -> str:
        """
        Retrieves or initializes a cluster-wide high-entropy HMAC secret shared across all workers.
        Guarantees that independent worker processes and server instances accept each other's signed cookies by default.
        """
        import secrets
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT value FROM pdu_cluster_metadata WHERE key = %s", (key_name,))
            row = cursor.fetchone()
            if row:
                return row[0]
            
            new_secret = secrets.token_hex(32)
            try:
                cursor.execute("""
                    INSERT INTO pdu_cluster_metadata (key, value)
                    VALUES (%s, %s)
                    ON CONFLICT (key) DO NOTHING
                """, (key_name, new_secret))
                conn.commit()
            except Exception:
                conn.rollback()

            cursor.execute("SELECT value FROM pdu_cluster_metadata WHERE key = %s", (key_name,))
            row = cursor.fetchone()
            return row[0] if row else new_secret
        finally:
            cursor.close()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT payload, version FROM pdu_sessions WHERE session_id = %s", (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            try:
                payload = json.loads(row[0])
                payload["_version"] = row[1]
                return payload
            except Exception:
                return None
        finally:
            cursor.close()

    def save(self, session_id: str, payload: Dict[str, Any], last_accessed: float, expected_version: Optional[int] = None) -> int:
        conn = self._get_connection()
        data_str = json.dumps(payload)
        cursor = conn.cursor()
        try:
            if expected_version is not None:
                cursor.execute("SELECT version FROM pdu_sessions WHERE session_id = %s", (session_id,))
                existing = cursor.fetchone()
                if existing is None:
                    new_ver = 1
                    cursor.execute("""
                        INSERT INTO pdu_sessions (session_id, payload, last_accessed, version)
                        VALUES (%s, %s, %s, %s)
                    """, (session_id, data_str, last_accessed, new_ver))
                    conn.commit()
                    return new_ver
                else:
                    curr_ver = existing[0]
                    if curr_ver != expected_version:
                        raise ConcurrencyError(
                            f"Concurrent update conflict for session '{session_id}': expected version {expected_version}, but found {curr_ver}."
                        )
                    new_ver = curr_ver + 1
                    cursor.execute("""
                        UPDATE pdu_sessions
                        SET payload = %s, last_accessed = %s, version = %s
                        WHERE session_id = %s AND version = %s
                    """, (data_str, last_accessed, new_ver, session_id, expected_version))
                    if cursor.rowcount == 0:
                        conn.rollback()
                        raise ConcurrencyError(
                            f"Concurrent update race condition for session '{session_id}'."
                        )
                    conn.commit()
                    return new_ver
            else:
                cursor.execute("""
                    INSERT INTO pdu_sessions (session_id, payload, last_accessed, version)
                    VALUES (%s, %s, %s, 1)
                    ON CONFLICT (session_id) DO UPDATE SET
                        payload = EXCLUDED.payload,
                        last_accessed = EXCLUDED.last_accessed,
                        version = pdu_sessions.version + 1
                    RETURNING version
                """, (session_id, data_str, last_accessed))
                row = cursor.fetchone()
                new_ver = row[0] if row else 1
                conn.commit()
                return new_ver
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def touch(self, session_id: str, last_accessed: float) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE pdu_sessions SET last_accessed = %s WHERE session_id = %s", (last_accessed, session_id))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def delete(self, session_id: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pdu_sessions WHERE session_id = %s", (session_id,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def cleanup_expired(self, max_age: int) -> int:
        conn = self._get_connection()
        cutoff = time.time() - max_age
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pdu_sessions WHERE last_accessed < %s", (cutoff,))
            count = cursor.rowcount
            conn.commit()
            return count
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


class PostgresAuthStore(BaseAuthStore):
    """
    High-performance, multi-instance PostgreSQL auth store.
    Shares users, API keys, login throttling, and token revocations across all workers.
    """
    def __init__(self, dsn: str, connection_factory: Optional[Callable] = None):
        self.dsn = dsn
        self.connection_factory = connection_factory
        self._local = threading.local()
        self._init_db()

    def _get_connection(self):
        if self.connection_factory is not None:
            return self.connection_factory()
        conn = getattr(self._local, "conn", None)
        if conn is None or getattr(conn, "closed", False):
            driver_type, driver = _get_pg_driver()
            if driver_type == "psycopg":
                conn = driver.connect(self.dsn, autocommit=False)
            else:
                conn = driver.connect(self.dsn)
                conn.autocommit = False
            self._local.conn = conn
        return self._local.conn

    def _init_db(self) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdu_users (
                    id VARCHAR(255) PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    password_hash TEXT NOT NULL,
                    roles TEXT NOT NULL,
                    is_active INTEGER NOT NULL,
                    created_at VARCHAR(255) NOT NULL,
                    last_login VARCHAR(255),
                    metadata TEXT NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdu_api_keys (
                    digest VARCHAR(255) PRIMARY KEY,
                    key_id VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) NOT NULL,
                    scopes TEXT NOT NULL,
                    created_at VARCHAR(255) NOT NULL,
                    expires_at VARCHAR(255),
                    last_used VARCHAR(255),
                    is_active INTEGER NOT NULL,
                    usage_count INTEGER NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdu_revoked_tokens (
                    jti VARCHAR(255) PRIMARY KEY,
                    exp DOUBLE PRECISION NOT NULL
                );
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pdu_login_attempts (
                    key VARCHAR(255) PRIMARY KEY,
                    attempts INTEGER NOT NULL,
                    last_attempt DOUBLE PRECISION NOT NULL,
                    locked_until DOUBLE PRECISION NOT NULL
                );
            """)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def _row_to_user(self, row: tuple) -> User:
        return User(
            id=row[0],
            username=row[1],
            email=row[2],
            password_hash=row[3],
            roles=json.loads(row[4]),
            is_active=bool(row[5]),
            created_at=row[6],
            last_login=row[7],
            metadata=json.loads(row[8]) if row[8] else {}
        )

    def _row_to_api_key(self, row: tuple) -> APIKey:
        return APIKey(
            key="",  # Raw key is never stored in DB
            key_id=row[1],
            name=row[2],
            user_id=row[3],
            scopes=json.loads(row[4]),
            created_at=row[5],
            expires_at=row[6],
            last_used=row[7],
            is_active=bool(row[8]),
            usage_count=row[9]
        )

    def get_user(self, user_id: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username, email, password_hash, roles, is_active, created_at, last_login, metadata FROM pdu_users WHERE id = %s", (user_id,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
        finally:
            cursor.close()

    def get_user_by_username(self, username: str) -> Optional[User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username, email, password_hash, roles, is_active, created_at, last_login, metadata FROM pdu_users WHERE username = %s", (username,))
            row = cursor.fetchone()
            return self._row_to_user(row) if row else None
        finally:
            cursor.close()

    def save_user(self, user: User) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id FROM pdu_users WHERE username = %s", (user.username,))
            existing = cursor.fetchone()
            if existing and existing[0] != user.id:
                user.id = existing[0]

            cursor.execute("""
                INSERT INTO pdu_users (id, username, email, password_hash, roles, is_active, created_at, last_login, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    username = EXCLUDED.username,
                    email = EXCLUDED.email,
                    password_hash = EXCLUDED.password_hash,
                    roles = EXCLUDED.roles,
                    is_active = EXCLUDED.is_active,
                    created_at = EXCLUDED.created_at,
                    last_login = EXCLUDED.last_login,
                    metadata = EXCLUDED.metadata
            """, (
                user.id, user.username, user.email, user.password_hash,
                json.dumps(user.roles), 1 if user.is_active else 0,
                user.created_at, user.last_login, json.dumps(user.metadata or {})
            ))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def get_all_users(self) -> Dict[str, User]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT id, username, email, password_hash, roles, is_active, created_at, last_login, metadata FROM pdu_users")
            result = {}
            for row in cursor.fetchall():
                u = self._row_to_user(row)
                result[u.id] = u
            return result
        finally:
            cursor.close()

    def get_api_key(self, digest: str) -> Optional[APIKey]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT digest, key_id, name, user_id, scopes, created_at, expires_at, last_used, is_active, usage_count FROM pdu_api_keys WHERE digest = %s", (digest,))
            row = cursor.fetchone()
            return self._row_to_api_key(row) if row else None
        finally:
            cursor.close()

    def save_api_key(self, digest: str, key: APIKey) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO pdu_api_keys (digest, key_id, name, user_id, scopes, created_at, expires_at, last_used, is_active, usage_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (digest) DO UPDATE SET
                    name = EXCLUDED.name,
                    scopes = EXCLUDED.scopes,
                    expires_at = EXCLUDED.expires_at,
                    last_used = EXCLUDED.last_used,
                    is_active = EXCLUDED.is_active,
                    usage_count = EXCLUDED.usage_count
            """, (
                digest, key.key_id, key.name, key.user_id,
                json.dumps(key.scopes), key.created_at, key.expires_at,
                key.last_used, 1 if key.is_active else 0, key.usage_count
            ))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def get_all_api_keys(self) -> Dict[str, APIKey]:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT digest, key_id, name, user_id, scopes, created_at, expires_at, last_used, is_active, usage_count FROM pdu_api_keys")
            result = {}
            for row in cursor.fetchall():
                k = self._row_to_api_key(row)
                result[row[0]] = k
            return result
        finally:
            cursor.close()

    def is_token_revoked(self, jti: str) -> bool:
        now = time.time()
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pdu_revoked_tokens WHERE exp < %s", (now,))
            conn.commit()
            cursor.execute("SELECT 1 FROM pdu_revoked_tokens WHERE jti = %s", (jti,))
            return cursor.fetchone() is not None
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def revoke_token(self, jti: str, exp: float) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO pdu_revoked_tokens (jti, exp)
                VALUES (%s, %s)
                ON CONFLICT (jti) DO UPDATE SET exp = EXCLUDED.exp
            """, (jti, exp))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def record_failed_login(self, key: str, window_seconds: int = 900, max_attempts: int = 5, lockout_seconds: int = 900) -> Tuple[bool, int]:
        now = time.time()
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT attempts, last_attempt, locked_until FROM pdu_login_attempts WHERE key = %s", (key,))
            row = cursor.fetchone()
            if row:
                attempts, last_attempt, locked_until = row
                if locked_until > now:
                    return True, int(locked_until - now)
                if now - last_attempt > window_seconds:
                    attempts = 1
                else:
                    attempts += 1
            else:
                attempts = 1
                locked_until = 0.0

            if attempts >= max_attempts:
                locked_until = now + lockout_seconds
                cursor.execute("""
                    INSERT INTO pdu_login_attempts (key, attempts, last_attempt, locked_until)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (key) DO UPDATE SET
                        attempts = EXCLUDED.attempts,
                        last_attempt = EXCLUDED.last_attempt,
                        locked_until = EXCLUDED.locked_until
                """, (key, attempts, now, locked_until))
                conn.commit()
                return True, lockout_seconds

            cursor.execute("""
                INSERT INTO pdu_login_attempts (key, attempts, last_attempt, locked_until)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (key) DO UPDATE SET
                    attempts = EXCLUDED.attempts,
                    last_attempt = EXCLUDED.last_attempt,
                    locked_until = EXCLUDED.locked_until
            """, (key, attempts, now, 0.0))
            conn.commit()
            return False, 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def is_login_locked(self, key: str) -> Tuple[bool, int]:
        now = time.time()
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT locked_until FROM pdu_login_attempts WHERE key = %s", (key,))
            row = cursor.fetchone()
            if not row:
                return False, 0
            locked_until = row[0]
            if locked_until > now:
                return True, int(locked_until - now)
            return False, 0
        finally:
            cursor.close()

    def reset_failed_logins(self, key: str) -> None:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pdu_login_attempts WHERE key = %s", (key,))
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def delete_user(self, user_id: str) -> bool:
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM pdu_users WHERE id = %s", (user_id,))
            count = cursor.rowcount
            conn.commit()
            return count > 0
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


# ==============================================================================
# Unified Database Client (SQLite & PostgreSQL Dual Support)
# ==============================================================================

class Database:
    """
    Lightweight, dual-engine (SQLite & PostgreSQL) database client for PyDataUI applications.
    
    Automatically adapts query placeholders (? vs %s) so the exact same SQL queries run on both
    SQLite (for local development/pilot) and PostgreSQL (for production multi-instance clusters).
    """
    def __init__(self, url_or_path: str = "sqlite:///.pydataui_app.db", connection_factory: Optional[Callable] = None):
        self.url = (url_or_path or "").strip()
        self.connection_factory = connection_factory
        self.backend, self.target = parse_storage_backend(self.url)
        self._local = threading.local()

    def _get_connection(self):
        if self.connection_factory is not None:
            return self.connection_factory()
        conn = getattr(self._local, "conn", None)
        if conn is None or (self.backend == "postgres" and getattr(conn, "closed", False)):
            if self.backend == "postgres":
                driver_type, driver = _get_pg_driver()
                if driver_type == "psycopg":
                    conn = driver.connect(self.target, autocommit=False)
                else:
                    conn = driver.connect(self.target)
                    conn.autocommit = False
            else:
                db_path = self.target if self.target and self.target != ":memory:" else ":memory:"
                if db_path != ":memory:":
                    parent = os.path.dirname(os.path.abspath(db_path))
                    if parent:
                        os.makedirs(parent, exist_ok=True)
                conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
                if db_path != ":memory:":
                    conn.execute("PRAGMA journal_mode = WAL;")
                    conn.execute("PRAGMA synchronous = NORMAL;")
                    conn.execute("PRAGMA busy_timeout = 30000;")
            self._local.conn = conn
        return self._local.conn

    def _adapt_sql(self, sql: str) -> str:
        """
        Normalizes SQL placeholders (? vs %s) to match the current backend engine.
        Allows writing cross-compatible SQL without manual dialect adjustments.
        """
        import re
        if self.backend == "sqlite":
            return re.sub(r'(?<!%)(%s)', '?', sql)
        elif self.backend == "postgres":
            return re.sub(r'\?', '%s', sql)
        return sql

    def execute(self, sql: str, params: Union[tuple, list, dict] = ()) -> int:
        """Execute a write/mutation query. Returns affected rowcount."""
        adapted_sql = self._adapt_sql(sql)
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(adapted_sql, params)
            count = cursor.rowcount
            if not getattr(self._local, "in_transaction", False):
                conn.commit()
            return count
        except Exception:
            if not getattr(self._local, "in_transaction", False):
                conn.rollback()
            raise
        finally:
            cursor.close()

    def query(self, sql: str, params: Union[tuple, list, dict] = ()) -> List[Dict[str, Any]]:
        """Execute a read query and return all rows as a list of column-keyed dictionaries."""
        adapted_sql = self._adapt_sql(sql)
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(adapted_sql, params)
            col_names = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(col_names, row)) for row in rows]
        finally:
            cursor.close()

    def query_one(self, sql: str, params: Union[tuple, list, dict] = ()) -> Optional[Dict[str, Any]]:
        """Execute a read query and return the first row as a dictionary, or None."""
        adapted_sql = self._adapt_sql(sql)
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(adapted_sql, params)
            col_names = [desc[0] for desc in cursor.description] if cursor.description else []
            row = cursor.fetchone()
            return dict(zip(col_names, row)) if row else None
        finally:
            cursor.close()

    def create_tables(self, ddl_statements: Union[str, List[str]]) -> None:
        """Execute DDL statements to initialize tables, indexes, and schemas."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            if isinstance(ddl_statements, str):
                if self.backend == "sqlite":
                    conn.executescript(ddl_statements)
                    conn.commit()
                    return
                else:
                    statements = [s.strip() for s in ddl_statements.split(";") if s.strip()]
            else:
                statements = ddl_statements

            for stmt in statements:
                if stmt:
                    cursor.execute(stmt)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()

    @contextmanager
    def transaction(self):
        """Context manager for multi-statement atomic transactions."""
        conn = self._get_connection()
        self._local.in_transaction = True
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self._local.in_transaction = False

    def close(self) -> None:
        """Close current connection."""
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass
            self._local.conn = None


# ==============================================================================
# Storage Backend Factory & URL Parsing Helpers
# ==============================================================================

def parse_storage_backend(storage_url: Optional[str]) -> Tuple[str, str]:
    """
    Parses storage URL into (backend_type, target/dsn).
    
    Supported URL formats:
    - PostgreSQL:
      - 'postgresql://user:pass@host:port/dbname'
      - 'postgres://user:pass@host:port/dbname'
      - 'postgresql+psycopg://...'
      - 'postgresql+psycopg2://...'
      -> returns ('postgres', dsn)
    - SQLite:
      - 'sqlite:///path/to/db.sqlite'
      - 'sqlite://path/to/db.sqlite'
      - 'sqlite'
      - 'file.db', 'file.sqlite', 'file.sqlite3'
      -> returns ('sqlite', file_path)
    - Memory:
      - 'memory', ':memory:', '', None
      -> returns ('memory', '')
    """
    if not storage_url:
        return ("memory", "")
    url = str(storage_url).strip()
    if url in ("memory", ":memory:", ""):
        return ("memory", "")

    # PostgreSQL detection
    for prefix in ("postgresql+psycopg://", "postgresql+psycopg2://", "postgresql://", "postgres://"):
        if url.startswith(prefix):
            if prefix in ("postgresql+psycopg://", "postgresql+psycopg2://", "postgres://"):
                normalized = "postgresql://" + url[len(prefix):]
            else:
                normalized = url
            return ("postgres", normalized)

    # SQLite detection
    if url == "sqlite":
        return ("sqlite", ".pydataui_storage.db")
    if url.startswith("sqlite:///"):
        return ("sqlite", url[len("sqlite:///"):])
    if url.startswith("sqlite://"):
        return ("sqlite", url[len("sqlite://"):])
    if url.endswith((".db", ".sqlite", ".sqlite3")):
        return ("sqlite", url)

    # Fallback: if contains :// assume postgres if name matches
    if "://" in url:
        scheme = url.split("://")[0].lower()
        if "postgres" in scheme:
            return ("postgres", url)

    return ("memory", "")


def parse_storage_path(storage_url: Optional[str]) -> Optional[str]:
    """Extract SQLite path from storage URL for backward compatibility."""
    backend, target = parse_storage_backend(storage_url)
    if backend == "sqlite":
        return target
    return None


def create_session_store(storage_url: Optional[str], **kwargs) -> BaseSessionStore:
    """Instantiate appropriate session store based on storage URL."""
    backend, target = parse_storage_backend(storage_url)
    if backend == "postgres":
        return PostgresSessionStore(target, **kwargs)
    elif backend == "sqlite":
        return SQLiteSessionStore(target, **kwargs)
    else:
        return MemorySessionStore()


def create_auth_store(storage_url: Optional[str], **kwargs) -> BaseAuthStore:
    """Instantiate appropriate auth store based on storage URL."""
    backend, target = parse_storage_backend(storage_url)
    if backend == "postgres":
        return PostgresAuthStore(target, **kwargs)
    elif backend == "sqlite":
        return SQLiteAuthStore(target, **kwargs)
    else:
        return MemoryAuthStore()
