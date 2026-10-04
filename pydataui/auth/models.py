from dataclasses import dataclass
from typing import List, Dict, Any, Optional

class Role:
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    DATA_ENGINEER = "data_engineer"
    DATA_ANALYST = "data_analyst"
    ML_ENGINEER = "ml_engineer"

@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    roles: List[str]
    is_active: bool
    created_at: str
    last_login: Optional[str]
    metadata: Dict[str, Any]

    def public_dict(self):
        return {name: getattr(self, name) for name in
                ('id', 'username', 'email', 'roles', 'is_active', 'created_at', 'last_login')}

@dataclass
class APIKey:
    key: str          # "pdu_live_..." prefix
    key_id: str       # Short ID
    name: str
    user_id: str
    scopes: List[str]  # ["read", "write", "admin"]
    created_at: str
    expires_at: Optional[str]
    last_used: Optional[str]
    is_active: bool
    usage_count: int

    def public_dict(self):
        return {name: getattr(self, name) for name in
                ('key_id', 'name', 'user_id', 'scopes', 'created_at', 'expires_at',
                 'last_used', 'is_active', 'usage_count')}
