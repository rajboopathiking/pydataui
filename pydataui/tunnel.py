"""
PyDataUI Tunnel Manager: Zero-config public port forwarding.
Provides Gradio-like `share=True` functionality without requiring manual accounts,
API keys, or sign-up. Uses resilient SSH tunneling with automatic fallbacks.
"""
import subprocess
import time
import re
import atexit
import threading
from typing import Optional, List, Tuple


class TunnelManager:
    """
    Manages public internet tunnels (port forwarding) for PyDataUI apps,
    similar to Gradio's `share=True` feature.
    
    Tunnels to localhost using secure reverse SSH tunneling with zero manual setup:
    1. localhost.run (direct HTTPS tunnel via TLS termination on lhr.life)
    2. pinggy.io (fallback HTTPS tunnel on port 443)
    3. serveo.net (fallback HTTPS tunnel)
    4. pyngrok (if pyngrok is installed and an auth token is provided)
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
            r"https://[a-zA-Z0-9]+\.lhr\.life",
            8
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
            r"https://[a-zA-Z0-9-]+\.(?:free\.pinggy\.net|run\.pinggy-free\.link|a\.pinggy\.link)",
            8
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
            r"https://[a-zA-Z0-9-]+\.serveo\.net",
            8
        )
    ]

    def __init__(self, port: Optional[int] = None):
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.public_url: Optional[str] = None
        self._provider_name: Optional[str] = None
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

        # 1. Try pyngrok if an auth_token was explicitly provided
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

        # 2. Try zero-config SSH providers sequentially
        for name, cmd_template, pattern, timeout in self.PROVIDERS:
            cmd = [arg.format(port=p) if "{port}" in arg else arg for arg in cmd_template]
            url = self._attempt_ssh_tunnel(name, cmd, pattern, timeout)
            if url:
                self.public_url = url
                self._provider_name = name
                return self.public_url

        return None

    def _attempt_ssh_tunnel(self, name: str, cmd: List[str], pattern: str, timeout: int) -> Optional[str]:
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            start_time = time.time()
            while time.time() - start_time < timeout:
                line = proc.stdout.readline() if proc.stdout else ""
                if not line:
                    if proc.poll() is not None:
                        break
                    time.sleep(0.1)
                    continue

                m = re.search(pattern, line)
                if m:
                    self.process = proc
                    url = m.group(0)
                    return url

            # Timed out or failed
            self._kill_process(proc)
        except Exception:
            pass
        return None

    def _kill_process(self, proc: Optional[subprocess.Popen]):
        if proc is None:
            return
        try:
            proc.terminate()
            proc.wait(timeout=1)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass

    def stop_tunnel(self):
        """Cleanly terminate the background tunnel process."""
        if self.process:
            self._kill_process(self.process)
            self.process = None
        self.public_url = None

    def stop(self):
        """Convenience alias for stop_tunnel."""
        self.stop_tunnel()
