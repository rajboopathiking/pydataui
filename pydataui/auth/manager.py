"""Local authentication manager. Storage is process-local, not a distributed identity store."""
import hashlib
import hmac
import os
import secrets
import threading
import uuid
from contextvars import ContextVar
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import jwt

from .models import APIKey, User
from ..exceptions import AuthenticationThrottledError

_current_user_var: ContextVar[Optional[User]] = ContextVar('current_user', default=None)
_current_auth_var: ContextVar[Optional[Any]] = ContextVar('current_auth', default=None)


def utcnow():
    return datetime.now(timezone.utc)


class _CurrentUserProxy:
    def get(self) -> Optional[User]:
        return _current_user_var.get()

    def __getattr__(self, name):
        user = self.get()
        if user is None:
            raise AttributeError('No authenticated user in current context')
        return getattr(user, name)

    def __bool__(self):
        return self.get() is not None


current_user = _CurrentUserProxy()


import collections.abc

class _UsersDictProxy(collections.abc.MutableMapping):
    def __init__(self, store):
        self._store = store

    def __getitem__(self, key: str) -> User:
        user = self._store.get_user(key)
        if user is None:
            raise KeyError(key)
        return user

    def __setitem__(self, key: str, value: User) -> None:
        self._store.save_user(value)

    def __delitem__(self, key: str) -> None:
        if hasattr(self._store, "delete_user"):
            self._store.delete_user(key)

    def __iter__(self):
        return iter(self._store.get_all_users())

    def __len__(self) -> int:
        return len(self._store.get_all_users())

    def get(self, key: str, default: Any = None) -> Optional[User]:
        user = self._store.get_user(key)
        return user if user is not None else default

    def values(self):
        return self._store.get_all_users().values()

    def items(self):
        return self._store.get_all_users().items()


class _UsersByUsernameProxy(collections.abc.Mapping):
    def __init__(self, store):
        self._store = store

    def __getitem__(self, username: str) -> str:
        user = self._store.get_user_by_username(username)
        if user is None:
            raise KeyError(username)
        return user.id

    def __iter__(self):
        return iter({u.username for u in self._store.get_all_users().values()})

    def __len__(self) -> int:
        return len(self._store.get_all_users())

    def get(self, username: str, default: Any = None) -> Optional[str]:
        user = self._store.get_user_by_username(username)
        return user.id if user is not None else default

    def __contains__(self, username: object) -> bool:
        if not isinstance(username, str):
            return False
        return self._store.get_user_by_username(username) is not None


class _ApiKeysDictProxy(collections.abc.MutableMapping):
    def __init__(self, store):
        self._store = store

    def __getitem__(self, digest: str) -> APIKey:
        key = self._store.get_api_key(digest)
        if key is None:
            raise KeyError(digest)
        return key

    def __setitem__(self, digest: str, value: APIKey) -> None:
        self._store.save_api_key(digest, value)

    def __delitem__(self, digest: str) -> None:
        pass

    def __iter__(self):
        return iter(self._store.get_all_api_keys())

    def __len__(self) -> int:
        return len(self._store.get_all_api_keys())

    def get(self, digest: str, default: Any = None) -> Optional[APIKey]:
        key = self._store.get_api_key(digest)
        return key if key is not None else default

    def values(self):
        return self._store.get_all_api_keys().values()

    def items(self):
        return self._store.get_all_api_keys().items()


class AuthManager:
    _default_instance = None

    @classmethod
    def get_default(cls):
        return _current_auth_var.get() or cls._default_instance

    @classmethod
    def set_default(cls, instance):
        cls._default_instance = instance

    def __init__(self, secret_key=None, token_expire_hours=24, store: Optional[Any] = None,
                 max_login_attempts: int = 5, lockout_duration_seconds: int = 900,
                 attempt_window_seconds: int = 900, enable_throttling: bool = True):
        secret_key = secret_key or os.environ.get('PYDATAUI_AUTH_SECRET') or secrets.token_hex(32)
        if not isinstance(secret_key, str) or len(secret_key.encode()) < 32:
            raise ValueError('Authentication secret must contain at least 32 bytes')
        self.secret_key = secret_key
        self.token_expire_hours = token_expire_hours
        self.max_login_attempts = max_login_attempts
        self.lockout_duration_seconds = lockout_duration_seconds
        self.attempt_window_seconds = attempt_window_seconds
        self.enable_throttling = enable_throttling
        from ..storage import BaseAuthStore, MemoryAuthStore
        self._store = store if store is not None else MemoryAuthStore()
        if isinstance(self._store, MemoryAuthStore):
            self.users = self._store._users
            self.api_keys = self._store._api_keys
            self.users_by_username = self._store._users_by_username
        else:
            self.users = _UsersDictProxy(self._store)
            self.api_keys = _ApiKeysDictProxy(self._store)
            self.users_by_username = _UsersByUsernameProxy(self._store)
        self._revoked_tokens = {}
        self._lock = threading.RLock()
        AuthManager._default_instance = self

    def _hash_password(self, password):
        if not isinstance(password, str) or not password or len(password) > 1024:
            raise ValueError('Password must be a non-empty string of at most 1024 characters')
        salt = secrets.token_bytes(16)
        iterations = 600000
        digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        return f'pbkdf2_sha256${iterations}${salt.hex()}${digest.hex()}'

    def _verify_password(self, password, password_hash):
        if not isinstance(password, str) or len(password) > 1024:
            return False
        try:
            algorithm, iterations, salt, expected = password_hash.split('$')
            if algorithm != 'pbkdf2_sha256' or not 600000 <= int(iterations) <= 2000000:
                return False
            actual = hashlib.pbkdf2_hmac('sha256', password.encode(), bytes.fromhex(salt), int(iterations))
            return hmac.compare_digest(actual.hex(), expected)
        except (TypeError, ValueError):
            return False

    def add_user(self, username, password, email='', roles=None):
        if not isinstance(username, str) or not username.strip() or len(username) > 128:
            raise ValueError('Username must be a non-empty string of at most 128 characters')
        if not isinstance(email, str):
            raise ValueError('Email must be a string')
        with self._lock:
            if username in self.users_by_username:
                raise ValueError('Username already exists')
            user = User(str(uuid.uuid4()), username, email, self._hash_password(password),
                        list(roles) if roles is not None else ['user'], True,
                        utcnow().isoformat(), None, {})
            self._store.save_user(user)
            if hasattr(self._store, '_users'):
                self._store._users[user.id] = user
                self._store._users_by_username[username] = user.id
            return user

    def get_or_create_user(self, username, password, email='', roles=None):
        """Idempotent user helper for seed data and migrations."""
        with self._lock:
            if username in self.users_by_username:
                uid = self.users_by_username[username]
                user = self._store.get_user(uid)
                if user:
                    return user
            return self.add_user(username, password, email=email, roles=roles)

    def save_user(self, user: User) -> None:
        """Persist a modified user object back to storage."""
        with self._lock:
            self._store.save_user(user)
            if hasattr(self._store, '_users'):
                self._store._users[user.id] = user
                self._store._users_by_username[user.username] = user.id

    def delete_user(self, user_id: str) -> bool:
        """Permanently delete a user by user_id."""
        with self._lock:
            user = self._store.get_user(user_id)
            if not user:
                return False
            success = self._store.delete_user(user_id) if hasattr(self._store, "delete_user") else False
            if hasattr(self._store, '_users'):
                self._store._users.pop(user_id, None)
                self._store._users_by_username.pop(user.username, None)
            return success

    def set_user_password(self, user_id: str, new_password: str) -> bool:
        """Securely set a new password for a user using PBKDF2-SHA256."""
        with self._lock:
            user = self._store.get_user(user_id)
            if not user:
                return False
            user.password_hash = self._hash_password(new_password)
            self.save_user(user)
            return True

    def authenticate(self, username, password, client_ip: Optional[str] = None):
        if not isinstance(username, str):
            return None

        # Brute-force throttling check
        keys_to_check = [f"user:{username.lower().strip()}"]
        if client_ip:
            keys_to_check.append(f"ip:{client_ip}")

        if self.enable_throttling and hasattr(self._store, "is_login_locked"):
            for k in keys_to_check:
                is_locked, remaining = self._store.is_login_locked(k)
                if is_locked:
                    raise AuthenticationThrottledError(
                        f"Too many failed login attempts. Temporarily locked out. Please try again in {remaining} seconds."
                    )

        user_id = self.users_by_username.get(username)
        user = self._store.get_user(user_id) if user_id else self._store.get_user_by_username(username)
        if not user or not user.is_active or not self._verify_password(password, user.password_hash):
            if self.enable_throttling and hasattr(self._store, "record_failed_login"):
                for k in keys_to_check:
                    self._store.record_failed_login(
                        k,
                        window_seconds=self.attempt_window_seconds,
                        max_attempts=self.max_login_attempts,
                        lockout_seconds=self.lockout_duration_seconds
                    )
            return None

        # Reset failed attempts on success
        if self.enable_throttling and hasattr(self._store, "reset_failed_logins"):
            for k in keys_to_check:
                self._store.reset_failed_logins(k)

        user.last_login = utcnow().isoformat()
        self._store.save_user(user)
        return jwt.encode({'sub': user.id, 'jti': uuid.uuid4().hex,
                           'exp': utcnow() + timedelta(hours=self.token_expire_hours)},
                          self.secret_key, algorithm='HS256')

    def verify_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'],
                                 options={'require': ['sub', 'exp', 'jti']})
            with self._lock:
                if self._store.is_token_revoked(payload['jti']):
                    return None
            user = self._store.get_user(payload['sub'])
            return user if user and user.is_active else None
        except (jwt.PyJWTError, TypeError, KeyError):
            return None

    def revoke_token(self, token):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'],
                                 options={'require': ['jti', 'exp']})
            with self._lock:
                self._store.revoke_token(payload['jti'], payload['exp'])
        except (jwt.PyJWTError, TypeError):
            pass

    def create_api_key(self, name, user_id, scopes=None, expires_days=None):
        user = self._store.get_user(user_id)
        if not user or not user.is_active:
            raise ValueError('Active user required')
        scopes = ['read'] if scopes is None else scopes
        if not isinstance(scopes, list) or not all(s in ('read', 'write') for s in scopes):
            raise ValueError('Supported API key scopes are read and write')
        if not isinstance(name, str) or not name.strip() or len(name) > 128:
            raise ValueError('Key name must contain 1 to 128 characters')
        if expires_days is not None and (type(expires_days) is not int or not 1 <= expires_days <= 3650):
            raise ValueError('expires_days must be between 1 and 3650')
        raw_key = 'pdu_live_' + secrets.token_hex(32)
        expires_at = (utcnow() + timedelta(days=expires_days)).isoformat() if expires_days else None
        key = APIKey(raw_key, uuid.uuid4().hex, name, user_id, list(scopes),
                     utcnow().isoformat(), expires_at, None, True, 0)
        with self._lock:
            digest = hashlib.sha256(raw_key.encode()).hexdigest()
            saved_key = replace(key, key='')
            self._store.save_api_key(digest, saved_key)
            if hasattr(self._store, '_api_keys'):
                self._store._api_keys[digest] = saved_key
        return key  # raw token is available only at creation

    def verify_api_key(self, key):
        if not isinstance(key, str):
            return None
        with self._lock:
            digest = hashlib.sha256(key.encode()).hexdigest()
            record = self._store.get_api_key(digest)
            if not record or not record.is_active:
                return None
            user = self._store.get_user(record.user_id)
            if not user or not user.is_active:
                return None
            if record.expires_at and utcnow() >= datetime.fromisoformat(record.expires_at):
                return None
            record.usage_count += 1
            record.last_used = utcnow().isoformat()
            self._store.save_api_key(digest, record)
            return replace(record, scopes=list(record.scopes))

    def revoke_api_key(self, key_id, user_id=None):
        with self._lock:
            all_keys = self._store.get_all_api_keys()
            for digest, key in all_keys.items():
                if key.key_id == key_id and (user_id is None or key.user_id == user_id):
                    key.is_active = False
                    self._store.save_api_key(digest, key)
                    if hasattr(self._store, '_api_keys'):
                        self._store._api_keys[digest] = key
                    return True
        return False

    def list_api_keys(self, user_id):
        with self._lock:
            all_keys = self._store.get_all_api_keys()
            return [replace(k, scopes=list(k.scopes)) for k in all_keys.values()
                    if k.user_id == user_id and k.is_active]

    @staticmethod
    def request_token(request):
        headers = {str(k).lower(): v for k, v in getattr(request, 'headers', {}).items()}
        authorization = headers.get('authorization', '')
        if authorization:
            parts = authorization.split()
            return parts[1] if len(parts) == 2 and parts[0].lower() == 'bearer' else ''
        for cookie in headers.get('cookie', '').split(';'):
            name, _, value = cookie.strip().partition('=')
            if name == 'pdu-auth':
                return value
        session = getattr(request, '_pdu_session', None)
        return session.data.get('auth_token', '') if session else ''

    def require_auth_middleware(self, request):
        token = self.request_token(request)
        if token.startswith('pdu_live_'):
            key = self.verify_api_key(token)
            return self.users.get(key.user_id) if key else None
        return self.verify_token(token) if token else None
