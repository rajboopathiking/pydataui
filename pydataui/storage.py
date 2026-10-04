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
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import asdict

from .auth.models import User, APIKey


# ==============================================================================
# Base Interfaces
# ==============================================================================

class BaseSessionStore(ABC):
    @abstractmethod
    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve raw session payload by session_id."""
        pass

    @abstractmethod
    def save(self, session_id: str, payload: Dict[str, Any], last_accessed: float) -> None:
        """Save session payload."""
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


# ==============================================================================
# In-Memory Storage Implementations (Default)
# ==============================================================================

class MemorySessionStore(BaseSessionStore):
    def __init__(self):
        self._sessions: Dict[str, Tuple[Dict[str, Any], float]] = {}
        self._lock = threading.RLock()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            record = self._sessions.get(session_id)
            if record:
                return record[0]
            return None

    def save(self, session_id: str, payload: Dict[str, Any], last_accessed: float) -> None:
        with self._lock:
            self._sessions[session_id] = (payload, last_accessed)

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def cleanup_expired(self, max_age: int) -> int:
        now = time.time()
        with self._lock:
            expired = [sid for sid, (_, la) in self._sessions.items() if now - la > max_age]
            for sid in expired:
                del self._sessions[sid]
            return len(expired)


class MemoryAuthStore(BaseAuthStore):
    def __init__(self):
        self._users: Dict[str, User] = {}
        self._users_by_username: Dict[str, str] = {}
        self._api_keys: Dict[str, APIKey] = {}
        self._revoked_tokens: Dict[str, float] = {}
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
                    last_accessed REAL NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_pdu_sessions_accessed ON pdu_sessions(last_accessed);")
            conn.commit()
        finally:
            conn.close()

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT payload FROM pdu_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        try:
            return json.loads(row[0])
        except Exception:
            return None

    def save(self, session_id: str, payload: Dict[str, Any], last_accessed: float) -> None:
        conn = self._get_connection()
        data_str = json.dumps(payload)
        conn.execute("""
            INSERT INTO pdu_sessions (session_id, payload, last_accessed)
            VALUES (?, ?, ?)
            ON CONFLICT(session_id) DO UPDATE SET
                payload = excluded.payload,
                last_accessed = excluded.last_accessed
        """, (session_id, data_str, last_accessed))
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


# ==============================================================================
# Factory Helper
# ==============================================================================

def parse_storage_path(storage_url: Optional[str]) -> Optional[str]:
    """Extract SQLite path from storage URL (e.g. 'sqlite:///app.db' -> 'app.db')."""
    if not storage_url:
        return None
    url = storage_url.strip()
    if url in ("memory", ":memory:"):
        return None
    if url == "sqlite":
        return ".pydataui_storage.db"
    if url.startswith("sqlite:///"):
        return url[len("sqlite:///"):]
    if url.startswith("sqlite://"):
        return url[len("sqlite://"):]
    if url.endswith(".db") or url.endswith(".sqlite") or url.endswith(".sqlite3"):
        return url
    return None
