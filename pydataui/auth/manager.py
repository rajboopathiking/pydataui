import os
import time
import uuid
import hashlib
import binascii
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import jwt

from .models import User, APIKey

from contextvars import ContextVar

_current_user_var: ContextVar[Optional[User]] = ContextVar("current_user", default=None)

class _CurrentUserProxy:
    """Proxy object so `current_user` can be inspected or evaluated as a User."""
    def get(self) -> Optional[User]:
        return _current_user_var.get()
    
    def __getattr__(self, name: str) -> Any:
        u = _current_user_var.get()
        if u is None:
            raise AttributeError(f"No authenticated user in current context")
        return getattr(u, name)
    
    def __bool__(self) -> bool:
        return _current_user_var.get() is not None

current_user = _CurrentUserProxy()

class AuthManager:
    _default_instance: Optional['AuthManager'] = None

    @classmethod
    def get_default(cls) -> Optional['AuthManager']:
        return cls._default_instance

    @classmethod
    def set_default(cls, instance: 'AuthManager') -> None:
        cls._default_instance = instance

    def __init__(self, secret_key: str = "default_secret", token_expire_hours: int = 24):
        self.secret_key = secret_key
        self.token_expire_hours = token_expire_hours
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.users_by_username: Dict[str, str] = {}
        AuthManager._default_instance = self

    def _hash_password(self, password: str) -> str:
        # Using a fixed salt for simplicity, but in production use a random salt per user
        salt = b"somesalt"
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        return binascii.hexlify(pwd_hash).decode('ascii')
        
    def _verify_password(self, password: str, password_hash: str) -> bool:
        return self._hash_password(password) == password_hash

    def add_user(self, username: str, password: str, email: str = "", roles: List[str] = None) -> User:
        if roles is None:
            roles = ["user"]
        
        if username in self.users_by_username:
            raise ValueError(f"User {username} already exists")
            
        user_id = str(uuid.uuid4())
        pwd_hash = self._hash_password(password)
        
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=pwd_hash,
            roles=roles,
            is_active=True,
            created_at=datetime.utcnow().isoformat(),
            last_login=None,
            metadata={}
        )
        self.users[user_id] = user
        self.users_by_username[username] = user_id
        return user

    def authenticate(self, username: str, password: str) -> Optional[str]:
        user_id = self.users_by_username.get(username)
        if not user_id:
            return None
            
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return None
            
        if self._verify_password(password, user.password_hash):
            user.last_login = datetime.utcnow().isoformat()
            
            payload = {
                "sub": user.id,
                "username": user.username,
                "roles": user.roles,
                "exp": datetime.utcnow() + timedelta(hours=self.token_expire_hours)
            }
            return jwt.encode(payload, self.secret_key, algorithm="HS256")
        return None

    def verify_token(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            user_id = payload.get("sub")
            if user_id in self.users:
                return self.users[user_id]
        except jwt.PyJWTError:
            return None
        return None

    def create_api_key(self, name: str, user_id: str, scopes: List[str] = None, expires_days: Optional[int] = None) -> APIKey:
        if scopes is None:
            scopes = ["read"]
            
        if user_id not in self.users:
            raise ValueError("User not found")
            
        raw_key = "pdu_live_" + binascii.hexlify(os.urandom(16)).decode('ascii')
        key_id = str(uuid.uuid4())[:8]
        
        expires_at = None
        if expires_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_days)).isoformat()
            
        api_key = APIKey(
            key=raw_key,
            key_id=key_id,
            name=name,
            user_id=user_id,
            scopes=scopes,
            created_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
            last_used=None,
            is_active=True,
            usage_count=0
        )
        self.api_keys[raw_key] = api_key
        return api_key

    def verify_api_key(self, key: str) -> Optional[APIKey]:
        api_key = self.api_keys.get(key)
        if not api_key or not api_key.is_active:
            return None
            
        if api_key.expires_at:
            if datetime.utcnow().isoformat() > api_key.expires_at:
                return None
                
        api_key.usage_count += 1
        api_key.last_used = datetime.utcnow().isoformat()
        return api_key

    def revoke_api_key(self, key_id: str):
        for key, api_key in self.api_keys.items():
            if api_key.key_id == key_id:
                api_key.is_active = False
                break

    def list_api_keys(self, user_id: str) -> List[APIKey]:
        return [k for k in self.api_keys.values() if k.user_id == user_id and k.is_active]

    def require_auth_middleware(self, request) -> Optional[User]:
        headers = getattr(request, 'headers', {})
        
        # Check API Key
        auth_header = headers.get('authorization', headers.get('Authorization', ''))
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            if token.startswith('pdu_live_'):
                api_key = self.verify_api_key(token)
                if api_key:
                    return self.users.get(api_key.user_id)
            else:
                return self.verify_token(token)
                
        # Check Cookie for JWT
        cookies_header = headers.get('cookie', headers.get('Cookie', ''))
        for cookie in cookies_header.split(';'):
            cookie = cookie.strip()
            if cookie.startswith('pdu-auth='):
                token = cookie.split('=', 1)[1]
                return self.verify_token(token)
                
        return None
