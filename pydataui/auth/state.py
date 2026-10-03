from ..state import State
from .manager import AuthManager, _current_user_var

class LoginState(State):
    """
    Reactive State for Authentication in PyDataUI.
    Handles user login, credentials, session tokens, and logout.
    """
    username: str = ""
    password: str = ""
    error: str = ""
    loading: bool = False
    is_authenticated: bool = False
    current_user_name: str = ""
    token: str = ""
    
    def login(self):
        """Perform user authentication using the registered AuthManager."""
        self.loading = True
        auth_mgr = AuthManager.get_default()
        if not auth_mgr:
            self.error = "AuthManager is not configured on this application"
            self.loading = False
            return
            
        token = auth_mgr.authenticate(self.username, self.password)
        if token:
            user = auth_mgr.verify_token(token)
            self.is_authenticated = True
            self.token = token
            self.current_user_name = user.username if user else self.username
            self.error = ""
            self.password = ""
            _current_user_var.set(user)
        else:
            self.error = "Invalid username or password"
            self.is_authenticated = False
            self.token = ""
            
        self.loading = False
        
    def logout(self):
        """Sign out the current user and reset state."""
        self.is_authenticated = False
        self.token = ""
        self.current_user_name = ""
        self.username = ""
        self.password = ""
        self.error = ""
        self.loading = False
        _current_user_var.set(None)
