"""
PyDataUI Tunnel & Reverse Proxy Manager: Zero-config public sharing & production Nginx.
Provides Gradio-like `share=True` functionality without requiring manual accounts,
API keys, or sign-up. Uses resilient SSH tunneling, Cloudflare Quick Tunnels,
and production-ready Nginx reverse proxy templates.
"""
import subprocess
import time
import re
import atexit
import shutil
import threading
from typing import Optional, List, Tuple


def generate_nginx_config(
    port: int = 8000,
    domain: str = "app.example.com",
    ssl: bool = False,
    ssl_cert_path: str = "/etc/letsencrypt/live/app.example.com/fullchain.pem",
    ssl_key_path: str = "/etc/letsencrypt/live/app.example.com/privkey.pem"
) -> str:
    """
    Generates a production-grade Nginx reverse proxy configuration for PyDataUI.
    Includes WebSocket / SSE support, client-side caching, streaming buffers,
    and automatic HTTPS forwarding.
    """
    ssl_block = ""
    http_redirect = ""
    listen_directive = "listen 80;"
    
    if ssl:
        listen_directive = "listen 443 ssl http2;"
        ssl_block = f"""
    ssl_certificate {ssl_cert_path};
    ssl_certificate_key {ssl_key_path};
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
"""
        http_redirect = f"""
server {{
    listen 80;
    server_name {domain};
    return 301 https://$host$request_uri;
}}
"""

    return f"""# PyDataUI Production Nginx Reverse Proxy Configuration
# Place in /etc/nginx/sites-available/{domain} and symlink to /etc/nginx/sites-enabled/
{http_redirect}
server {{
    {listen_directive}
    server_name {domain};
    {ssl_block}
    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Maximum file upload size (e.g. for FileUpload component)
    client_max_body_size 100M;

    # Static Asset Caching
    location /static/ {{
        proxy_pass http://127.0.0.1:{port}/static/;
        proxy_cache_valid 200 30d;
        access_log off;
        expires max;
    }}

    # Application & API Reverse Proxy
    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_http_version 1.1;

        # WebSocket & Server-Sent Events (SSE) support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Standard Proxy Headers
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Streaming & Buffering Optimization for HTMX and LLM token streams
        proxy_buffering off;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }}
}}
"""


class TunnelManager:
    """
    Manages public internet tunnels (port forwarding) for PyDataUI apps,
    similar to Gradio's `share=True` feature.
    
    Tunnels to localhost using secure reverse SSH tunneling with zero manual setup:
    1. cloudflared (if installed locally: fast, zero-account Cloudflare Edge tunnel)
    2. localhost.run (direct HTTPS tunnel via TLS termination on lhr.life)
    3. pinggy.io (fallback HTTPS tunnel on port 443)
    4. serveo.net (fallback HTTPS tunnel)
    5. pyngrok (if pyngrok is installed and an auth token is provided)
    """

    PROVIDERS: List[Tuple[str, List[str], str, int]] = [
        (
            "localhost.run",
            [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ServerAliveInterval=30",
                "-o", "ServerAliveCountMax=3",
                "-o", "ExitOnForwardFailure=yes",
                "-R", "80:localhost:{port}",
                "nokey@localhost.run"
            ],
            r"https://[a-zA-Z0-9.-]+\.lhr\.life",
            12
        ),
        (
            "pinggy.io",
            [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ServerAliveInterval=30",
                "-o", "ServerAliveCountMax=3",
                "-o", "ExitOnForwardFailure=yes",
                "-p", "443",
                "-R", "0:localhost:{port}",
                "a.pinggy.io"
            ],
            r"https://[a-zA-Z0-9.-]+\.(?:free\.pinggy\.net|run\.pinggy-free\.link|a\.pinggy\.link|pinggy\.io)",
            12
        ),
        (
            "serveo.net",
            [
                "ssh",
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ServerAliveInterval=30",
                "-o", "ServerAliveCountMax=3",
                "-o", "ExitOnForwardFailure=yes",
                "-R", "80:localhost:{port}",
                "serveo.net"
            ],
            r"https://[a-zA-Z0-9.-]+\.serveo\.net",
            10
        )
    ]

    def __init__(self, port: Optional[int] = None):
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.public_url: Optional[str] = None
        self._provider_name: Optional[str] = None
        self._pty_master: Optional[int] = None
        atexit.register(self.stop_tunnel)

    def start(self, port: Optional[int] = None) -> Optional[str]:
        """Convenience method to start a tunnel."""
        return self.create_tunnel(port=port or self.port or 8000)

    def create_tunnel(self, port: Optional[int] = None, auth_token: Optional[str] = None) -> Optional[str]:
        """
        Create a live public HTTPS tunnel forwarding traffic to the local port.
        Returns the public URL (e.g. https://xxxx.lhr.life), or None if all providers fail.
        """
        p = port or self.port or 8000
        self.port = p

        # 1. Try cloudflared if installed (100% free, high performance Cloudflare Edge)
        if shutil.which("cloudflared"):
            cf_cmd = ["cloudflared", "tunnel", "--url", f"http://localhost:{p}", "--no-autoupdate"]
            cf_pattern = r"https://[a-zA-Z0-9-]+\.trycloudflare\.com"
            url = self._attempt_ssh_tunnel("cloudflared", cf_cmd, cf_pattern, 10)
            if url:
                self.public_url = url
                self._provider_name = "cloudflared"
                return self.public_url

        # 2. Try pyngrok if an auth_token was explicitly provided
        if auth_token:
            try:
                from pyngrok import ngrok
                ngrok.set_auth_token(auth_token)
                tunnel = ngrok.connect(p)
                self.public_url = tunnel.public_url
                self._provider_name = "ngrok"
                return self.public_url
            except Exception:
                pass

        # 3. Try zero-config SSH providers sequentially (localhost.run, pinggy, serveo)
        for name, cmd_template, pattern, timeout in self.PROVIDERS:
            cmd = [arg.format(port=p) if "{port}" in arg else arg for arg in cmd_template]
            url = self._attempt_ssh_tunnel(name, cmd, pattern, timeout)
            if url:
                self.public_url = url
                self._provider_name = name
                return self.public_url

        return None

    def _attempt_ssh_tunnel(self, name: str, cmd: List[str], pattern: str, timeout: int) -> Optional[str]:
        import os
        try:
            import pty
            has_pty = True
        except ImportError:
            has_pty = False

        try:
            if has_pty and os.name != "nt":
                master, slave = pty.openpty()
                try:
                    os.set_blocking(master, False)
                except Exception:
                    pass

                proc = subprocess.Popen(
                    cmd,
                    stdin=slave,
                    stdout=slave,
                    stderr=slave,
                    close_fds=True
                )
                os.close(slave)

                start_time = time.time()
                buf = ""
                while time.time() - start_time < timeout:
                    if proc.poll() is not None:
                        break
                    try:
                        data = os.read(master, 2048).decode("utf-8", errors="ignore")
                        if data:
                            buf += data
                            m = re.search(pattern, buf)
                            if m:
                                self.process = proc
                                self._pty_master = master
                                return m.group(0)
                    except (BlockingIOError, OSError):
                        pass
                    time.sleep(0.1)

                self._kill_process(proc)
                try:
                    os.close(master)
                except OSError:
                    pass
                return None
            else:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                start_time = time.time()
                buf = ""
                while time.time() - start_time < timeout:
                    if proc.poll() is not None:
                        break
                    line = proc.stdout.readline() if proc.stdout else ""
                    if line:
                        buf += line
                        m = re.search(pattern, buf)
                        if m:
                            self.process = proc
                            return m.group(0)
                    time.sleep(0.1)

                # Timed out or failed
                self._kill_process(proc)
                return None
        except Exception:
            pass
        return None

    def _kill_process(self, proc: Optional[subprocess.Popen]):
        if proc is None:
            return
        try:
            proc.kill()
            proc.wait(timeout=1)
        except Exception:
            pass

    def stop_tunnel(self):
        """Cleanly terminate the background tunnel process."""
        if self.process:
            self._kill_process(self.process)
            self.process = None

        if hasattr(self, '_pty_master') and self._pty_master is not None:
            try:
                import os
                os.close(self._pty_master)
            except Exception:
                pass
            self._pty_master = None

        self.public_url = None

    def stop(self):
        """Convenience alias for stop_tunnel."""
        self.stop_tunnel()
