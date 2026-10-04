import threading
import time
import uuid
import hashlib
import hmac
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State
    from .storage import BaseSessionStore

class Session:
    """Represents a user session."""
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.data: Dict[str, Any] = {}
        self.state_instances: Dict[str, 'State'] = {}
        self.created_at: float = time.time()
        self.last_accessed: float = self.created_at
        self.current_page: Optional[str] = None
        self.lock = threading.RLock()

    def to_dict(self) -> Dict[str, Any]:
        with self.lock:
            states_dict = {}
            for name, inst in self.state_instances.items():
                if hasattr(inst, "to_dict"):
                    states_dict[name] = inst.to_dict(include_private=True)
            return {
                "session_id": self.session_id,
                "data": self.data,
                "created_at": self.created_at,
                "last_accessed": self.last_accessed,
                "current_page": self.current_page,
                "state_instances": states_dict,
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        from .state import StateMeta
        session = cls(data["session_id"])
        session.data = data.get("data", {})
        session.created_at = data.get("created_at", time.time())
        session.last_accessed = data.get("last_accessed", session.created_at)
        session.current_page = data.get("current_page")
        state_data = data.get("state_instances", {})
        for state_name, fields in state_data.items():
            state_cls = StateMeta._registry.get(state_name)
            if state_cls:
                inst = state_cls()
                for k, v in fields.items():
                    setattr(inst, k, v)
                session.state_instances[state_name] = inst
        return session

class SessionManager:
    """Thread-safe session manager with pluggable storage."""
    def __init__(self, secret: str, max_age: int = 3600, store: Optional[Any] = None):
        from .storage import MemorySessionStore
        self._lock = threading.RLock()
        self._secret = secret.encode('utf-8')
        self._max_age = max_age
        self._store = store if store is not None else MemorySessionStore()
        self._active_sessions: Dict[str, Session] = {}

    @property
    def _sessions(self) -> Dict[str, Session]:
        return self._active_sessions

    def create_session(self) -> Session:
        session_id = uuid.uuid4().hex
        session = Session(session_id)
        with self._lock:
            self._active_sessions[session_id] = session
            self._store.save(session_id, session.to_dict(), session.last_accessed)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        with self._lock:
            now = time.time()
            payload = self._store.get(session_id)
            if not payload:
                self._active_sessions.pop(session_id, None)
                return None
            last_accessed = payload.get("last_accessed", payload.get("created_at", now))
            if now - last_accessed > self._max_age:
                self.delete_session(session_id)
                return None

            session = self._active_sessions.get(session_id)
            if session is not None:
                session.last_accessed = now
                session.data = payload.get("data", session.data)
                session.current_page = payload.get("current_page", session.current_page)
                state_data = payload.get("state_instances", {})
                from .state import StateMeta
                for sname, sfields in state_data.items():
                    if sname in session.state_instances:
                        inst = session.state_instances[sname]
                        for k, v in sfields.items():
                            setattr(inst, k, v)
                    else:
                        scls = StateMeta._registry.get(sname)
                        if scls:
                            inst = scls()
                            for k, v in sfields.items():
                                setattr(inst, k, v)
                            session.state_instances[sname] = inst
            else:
                session = Session.from_dict(payload)
                session.last_accessed = now
                self._active_sessions[session_id] = session

            self._store.save(session_id, session.to_dict(), session.last_accessed)
            return session

    def save_session(self, session: Session) -> None:
        with self._lock:
            session.last_accessed = time.time()
            self._active_sessions[session.session_id] = session
            self._store.save(session.session_id, session.to_dict(), session.last_accessed)

    def get_or_create_session(self, session_id: Optional[str]) -> Session:
        if session_id:
            verified_id = self.verify_session_id(session_id)
            if verified_id:
                session = self.get_session(verified_id)
                if session:
                    return session
        return self.create_session()

    def delete_session(self, session_id: str) -> None:
        with self._lock:
            self._active_sessions.pop(session_id, None)
            self._store.delete(session_id)

    def cleanup_expired(self) -> int:
        now = time.time()
        with self._lock:
            expired = [sid for sid, s in list(self._active_sessions.items()) if now - s.last_accessed > self._max_age]
            for sid in expired:
                self._active_sessions.pop(sid, None)
            return self._store.cleanup_expired(self._max_age)

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
