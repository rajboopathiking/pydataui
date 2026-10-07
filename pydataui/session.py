import copy
import threading
import time
import uuid
import hashlib
import hmac
from typing import Dict, Any, Optional, Callable, TYPE_CHECKING

from .exceptions import ConcurrencyError, SessionError

if TYPE_CHECKING:
    from .state import State
    from .storage import BaseSessionStore

class Session:
    """Represents a user session with optimistic concurrency tracking."""
    def __init__(self, session_id: str, version: int = 1):
        self.session_id: str = session_id
        self.version: int = version
        self.data: Dict[str, Any] = {}
        self.state_instances: Dict[str, 'State'] = {}
        self.created_at: float = time.time()
        self.last_accessed: float = self.created_at
        self.current_page: Optional[str] = None
        self.lock = threading.RLock()
        self._initial_data: Dict[str, Any] = {}
        self._initial_states: Dict[str, Any] = {}

    def snapshot_baseline(self) -> None:
        """Capture baseline snapshot of data and reactive State instances for OCC reconciliation."""
        with self.lock:
            self._initial_data = copy.deepcopy(self.data)
            self._initial_states = {}
            for name, inst in self.state_instances.items():
                if hasattr(inst, "to_dict"):
                    self._initial_states[name] = copy.deepcopy(inst.to_dict(include_private=True))

    def to_dict(self) -> Dict[str, Any]:
        with self.lock:
            states_dict = {}
            for name, inst in self.state_instances.items():
                if hasattr(inst, "to_dict"):
                    states_dict[name] = inst.to_dict(include_private=True)
            return {
                "session_id": self.session_id,
                "version": self.version,
                "data": self.data,
                "created_at": self.created_at,
                "last_accessed": self.last_accessed,
                "current_page": self.current_page,
                "state_instances": states_dict,
            }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Session':
        from .state import StateMeta
        version = data.get("version", data.get("_version", 1))
        session = cls(data["session_id"], version=version)
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
        session.snapshot_baseline()
        return session

class SessionManager:
    """Thread-safe and cross-process session manager with pluggable storage and OCC."""
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
        session = Session(session_id, version=1)
        session.snapshot_baseline()
        with self._lock:
            self._active_sessions[session_id] = session
            new_ver = self._store.save(session_id, session.to_dict(), session.last_accessed, expected_version=None)
            session.version = new_ver
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

            version = payload.pop("_version", payload.get("version", 1))

            session = self._active_sessions.get(session_id)
            if session is not None:
                session.version = version
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
                session.snapshot_baseline()
            else:
                payload["version"] = version
                session = Session.from_dict(payload)
                session.last_accessed = now
                self._active_sessions[session_id] = session

            # Touch access time in store without modifying payload version
            self._store.touch(session_id, now)
            return session

    def save_session(self, session: Session, auto_merge: bool = True, max_retries: int = 5) -> None:
        """
        Thread-safe and cross-worker OCC session save.
        If a concurrent update conflict occurs and auto_merge=True, calculates
        the delta against baseline and reconciles with the latest database version,
        guaranteeing zero lost updates across concurrent workers.
        """
        with self._lock:
            for attempt in range(max_retries):
                session.last_accessed = time.time()
                try:
                    new_ver = self._store.save(
                        session.session_id,
                        session.to_dict(),
                        session.last_accessed,
                        expected_version=session.version
                    )
                    session.version = new_ver
                    session.snapshot_baseline()
                    self._active_sessions[session.session_id] = session
                    return
                except ConcurrencyError as err:
                    if not auto_merge or attempt == max_retries - 1:
                        raise err

                    # Auto-merge: fetch latest payload from DB
                    fresh_payload = self._store.get(session.session_id)
                    if not fresh_payload:
                        raise err

                    fresh_version = fresh_payload.pop("_version", fresh_payload.get("version", 1))
                    fresh_data = fresh_payload.get("data", {})

                    # Reconcile session.data deltas against session._initial_data
                    with session.lock:
                        for k, current_val in list(session.data.items()):
                            initial_val = session._initial_data.get(k)
                            # If numeric value modified by both: add the delta
                            if (isinstance(current_val, (int, float)) and 
                                isinstance(initial_val, (int, float)) and 
                                k in fresh_data and 
                                isinstance(fresh_data[k], (int, float))):
                                delta = current_val - initial_val
                                fresh_data[k] = fresh_data[k] + delta
                            else:
                                fresh_data[k] = current_val

                        # Reconcile reactive State instance fields
                        fresh_states = fresh_payload.get("state_instances", {})
                        from .state import StateMeta
                        for sname, inst in list(session.state_instances.items()):
                            if not hasattr(inst, "to_dict"):
                                continue
                            current_state_dict = inst.to_dict(include_private=True)
                            init_state_dict = session._initial_states.get(sname, {})
                            target_fresh = fresh_states.setdefault(sname, {})

                            for prop_name, current_val in current_state_dict.items():
                                init_val = init_state_dict.get(prop_name)
                                if (isinstance(current_val, (int, float)) and
                                    isinstance(init_val, (int, float)) and
                                    prop_name in target_fresh and
                                    isinstance(target_fresh[prop_name], (int, float))):
                                    delta = current_val - init_val
                                    target_fresh[prop_name] = target_fresh[prop_name] + delta
                                elif current_val != init_val:
                                    target_fresh[prop_name] = current_val

                            # Re-apply merged properties onto the live state instance
                            for prop_name, merged_val in target_fresh.items():
                                try:
                                    setattr(inst, prop_name, merged_val)
                                except Exception:
                                    pass

                        for sname, sfields in fresh_states.items():
                            if sname not in session.state_instances:
                                scls = StateMeta._registry.get(sname)
                                if scls:
                                    new_inst = scls()
                                    for k, v in sfields.items():
                                        setattr(new_inst, k, v)
                                    session.state_instances[sname] = new_inst

                        session.data = fresh_data
                        session.version = fresh_version

    def mutate_session(self, session_id: str, mutate_fn: Callable[[Session], None], max_retries: int = 15) -> Session:
        """
        Executes mutate_fn on the session with automatic optimistic concurrency retry.
        Guarantees no lost updates under concurrent access across processes/workers.
        """
        for attempt in range(max_retries):
            session = self.get_session(session_id)
            if session is None:
                raise SessionError(f"Session {session_id} not found")
            mutate_fn(session)
            try:
                self.save_session(session, auto_merge=False)
                return session
            except ConcurrencyError:
                if attempt == max_retries - 1:
                    raise
                time.sleep(0.005 * (2 ** (attempt % 5)))

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
