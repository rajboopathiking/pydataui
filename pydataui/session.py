import threading
import time
import uuid
import hashlib
import hmac
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State

class Session:
    """Represents a user session."""
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.data: Dict[str, Any] = {}
        self.state_instances: Dict[str, 'State'] = {}
        self.created_at: float = time.time()
        self.last_accessed: float = self.created_at
        self.current_page: Optional[str] = None

class SessionManager:
    """Thread-safe session manager."""
    def __init__(self, secret: str, max_age: int = 3600):
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.RLock()
        self._secret = secret.encode('utf-8')
        self._max_age = max_age
        
    def create_session(self) -> Session:
        session_id = uuid.uuid4().hex
        session = Session(session_id)
        with self._lock:
            self._sessions[session_id] = session
        return session
        
    def get_session(self, session_id: str) -> Optional[Session]:
        with self._lock:
            session = self._sessions.get(session_id)
            if session:
                if time.time() - session.last_accessed > self._max_age:
                    self.delete_session(session_id)
                    return None
                session.last_accessed = time.time()
            return session
            
    def get_or_create_session(self, session_id: Optional[str]) -> Session:
        if session_id:
            if '.' in session_id:
                verified = self.verify_session_id(session_id)
                session_id = verified
            if session_id:
                session = self.get_session(session_id)
                if session:
                    return session
        return self.create_session()
        
    def delete_session(self, session_id: str) -> None:
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                
    def cleanup_expired(self) -> int:
        now = time.time()
        expired = []
        with self._lock:
            for sid, session in self._sessions.items():
                if now - session.last_accessed > self._max_age:
                    expired.append(sid)
            for sid in expired:
                del self._sessions[sid]
        return len(expired)
        
    def sign_session_id(self, session_id: str) -> str:
        signature = hmac.new(self._secret, session_id.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{session_id}.{signature}"
        
    def verify_session_id(self, signed_id: str) -> Optional[str]:
        try:
            session_id, signature = signed_id.split('.', 1)
        except ValueError:
            return None
        expected = hmac.new(self._secret, session_id.encode('utf-8'), hashlib.sha256).hexdigest()
        if hmac.compare_digest(signature, expected):
            return session_id
        return None
        
    def get_session_cookie_value(self, session: Session) -> str:
        return self.sign_session_id(session.session_id)
        
    def parse_session_cookie(self, cookie_value: str) -> Optional[Session]:
        session_id = self.verify_session_id(cookie_value)
        if session_id:
            return self.get_session(session_id)
        return None
