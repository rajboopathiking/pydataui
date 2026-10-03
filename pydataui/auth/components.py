from typing import Optional, List, Any
from ..components.base import Component
from ..components.layout import Container, Card, Flex, Box
from ..components.typography import Heading, Text, Paragraph
from ..components.forms import Button, Input
from ..components.feedback import Alert
from .models import User
from .state import LoginState


class LoginPage(Component):
    """
    Pre-built production-grade Login Page component.
    Integrates with LoginState and PyDataUI authentication.
    """
    def __init__(
        self,
        logo: Optional[Component] = None,
        title: str = "Sign in to PyDataUI",
        subtitle: str = "Enter your credentials to access your data workspace",
        redirect_to: str = "/",
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.logo = logo
        self.page_title = title
        self.subtitle = subtitle
        self.redirect_to = redirect_to

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        login_snap = snap.get("LoginState", {})
        error_msg = login_snap.get("error", "")
        
        error_alert = (
            f'<div class="mb-4 rounded-md bg-destructive/15 p-3 text-sm text-destructive border border-destructive/20">'
            f'{error_msg}</div>'
            if error_msg else ""
        )
        
        logo_html = self.logo.render(snap) if self.logo else (
            '<div class="flex items-center justify-center w-12 h-12 rounded-xl bg-primary text-primary-foreground font-bold text-xl mb-4">'
            'PDU</div>'
        )

        return f'''<div class="min-h-screen flex items-center justify-center bg-muted/40 p-4">
  <div class="w-full max-w-md rounded-xl border bg-card text-card-foreground shadow-lg p-8">
    <div class="flex flex-col items-center text-center mb-6">
      {logo_html}
      <h1 class="text-2xl font-bold tracking-tight">{self.page_title}</h1>
      <p class="text-sm text-muted-foreground mt-1">{self.subtitle}</p>
    </div>
    {error_alert}
    <form hx-post="/_pdu/event/LoginState/login" hx-target="#pdu-root" hx-swap="innerHTML" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1.5" for="login-username">Username</label>
        <input id="login-username" name="username" type="text" required autocomplete="username"
               class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
               placeholder="username" value="{login_snap.get('username', '')}" />
      </div>
      <div>
        <label class="block text-sm font-medium mb-1.5" for="login-password">Password</label>
        <input id="login-password" name="password" type="password" required autocomplete="current-password"
               class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
               placeholder="••••••••" />
      </div>
      <button type="submit"
              class="w-full inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 transition-colors">
        Sign In
      </button>
    </form>
    <div class="mt-6 text-center text-xs text-muted-foreground">
      Powered by PyDataUI & pyrustapi
    </div>
  </div>
</div>'''


class UserMenu(Component):
    """
    Displays logged-in user profile, role tags, and logout action.
    """
    def __init__(self, user: Optional[User] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.user = user

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        if not self.user:
            return '<div class="text-sm text-muted-foreground">Not signed in</div>'
        
        roles_html = "".join(
            f'<span class="inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-semibold bg-secondary text-secondary-foreground">{r}</span>'
            for r in self.user.roles
        )
        
        return f'''<div class="flex items-center gap-3 p-2 rounded-lg border bg-card shadow-sm">
  <div class="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold text-sm">
    {self.user.username[:2].upper()}
  </div>
  <div class="flex flex-col min-w-0">
    <span class="text-sm font-medium truncate">{self.user.username}</span>
    <div class="flex gap-1 mt-0.5">{roles_html}</div>
  </div>
  <button hx-post="/_pdu/event/LoginState/logout" hx-target="#pdu-root" hx-swap="innerHTML"
          class="ml-auto inline-flex items-center justify-center rounded-md text-xs font-medium border border-input bg-background hover:bg-accent hover:text-accent-foreground h-8 px-3 transition-colors">
    Logout
  </button>
</div>'''


class APIKeyManager(Component):
    """
    UI Component for viewing, generating, and revoking API keys.
    """
    def __init__(self, keys: Optional[List[Any]] = None, **kwargs: Any):
        super().__init__(**kwargs)
        self.keys = keys or []

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        keys_rows = ""
        if self.keys:
            for k in self.keys:
                key_str = getattr(k, 'key', str(k))
                name = getattr(k, 'name', 'Key')
                created = getattr(k, 'created_at', '')[:10]
                scopes = ", ".join(getattr(k, 'scopes', ['read']))
                masked = key_str[:12] + "..." + key_str[-4:] if len(key_str) > 16 else key_str
                key_id = getattr(k, 'key_id', '')
                keys_rows += f'''<tr class="border-b transition-colors hover:bg-muted/50">
  <td class="p-3 font-medium">{name}</td>
  <td class="p-3 font-mono text-xs">{masked}</td>
  <td class="p-3 text-xs text-muted-foreground">{scopes}</td>
  <td class="p-3 text-xs text-muted-foreground">{created}</td>
  <td class="p-3 text-right">
    <button hx-delete="/api/auth/keys/{key_id}" hx-confirm="Are you sure you want to revoke this API key?"
            class="text-xs text-destructive hover:underline">Revoke</button>
  </td>
</tr>'''
        else:
            keys_rows = '<tr><td colspan="5" class="p-6 text-center text-sm text-muted-foreground">No active API keys found. Generate one below.</td></tr>'

        return f'''<div class="rounded-xl border bg-card text-card-foreground shadow p-6 max-w-4xl w-full">
  <div class="flex items-center justify-between pb-4 border-b">
    <div>
      <h3 class="text-lg font-semibold tracking-tight">API Key Management</h3>
      <p class="text-sm text-muted-foreground">Authenticate automated scripts, ML pipelines, and external integrations.</p>
    </div>
    <button onclick="let name=prompt('Enter key name:'); if(name) fetch('/api/auth/keys', {{method:'POST', headers:{{'Content-Type':'application/json'}}, body:JSON.stringify({{name:name}})}}).then(r=>r.json()).then(d=>alert('Key created: ' + d.key.key)).then(()=>location.reload())"
            class="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2 transition-colors">
      + Generate API Key
    </button>
  </div>
  <div class="overflow-x-auto mt-4">
    <table class="w-full text-sm text-left">
      <thead class="text-xs text-muted-foreground bg-muted/50 border-b">
        <tr>
          <th class="p-3">Name</th>
          <th class="p-3">Key Token</th>
          <th class="p-3">Scopes</th>
          <th class="p-3">Created</th>
          <th class="p-3 text-right">Actions</th>
        </tr>
      </thead>
      <tbody>
        {keys_rows}
      </tbody>
    </table>
  </div>
</div>'''


class AuthGuard(Component):
    """
    Wraps children, rendering them if user is authenticated or rendering a fallback/redirect.
    """
    def __init__(self, *children: Any, redirect_to: str = "/login", **kwargs: Any):
        super().__init__(*children, **kwargs)
        self.redirect_to = redirect_to

    def render(self, state_snapshot: Optional[dict] = None) -> str:
        snap = state_snapshot or {}
        login_snap = snap.get("LoginState", {})
        if login_snap.get("is_authenticated", False):
            return self._render_children(snap)
        return (
            f'<div class="flex flex-col items-center justify-center p-8 text-center">'
            f'<p class="text-muted-foreground mb-4">Authentication required to view this content.</p>'
            f'<a href="{self.redirect_to}" class="inline-flex items-center justify-center rounded-md text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 h-9 px-4 py-2 transition-colors">Sign In</a>'
            f'</div>'
        )
