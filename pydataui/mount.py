"""
Native FastAPI / Starlette mounting for PyDataUI applications.
"""
from __future__ import annotations
from typing import Any


def mount(parent_app: Any, pydataui_app: Any, path: str = "/ui") -> None:
    """
    Mount a PyDataUI App instance inside an existing FastAPI or Starlette application.

    Usage::

        from fastapi import FastAPI
        from pydataui import App, mount

        api = FastAPI()
        dashboard = App(title="Dashboard")

        @dashboard.page("/")
        def home():
            return "Dashboard Home"

        mount(api, dashboard, path="/dashboard")

    Parameters:
        parent_app: The parent FastAPI or Starlette application instance.
        pydataui_app: The PyDataUI App instance to mount.
        path: The URL prefix path to mount under (e.g. '/dashboard').
    """
    clean_path = "/" + path.strip("/")
    if hasattr(pydataui_app, "config"):
        pydataui_app.config.root_path = clean_path

    # Extract the ASGI application callable
    asgi_app = getattr(pydataui_app, "asgi_app", pydataui_app)
    parent_app.mount(clean_path, asgi_app)
