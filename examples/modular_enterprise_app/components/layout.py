"""layout.py - Reusable App Shell and Navigation Components

Just like in React (e.g. Layout.tsx, Navbar.tsx), this module provides
shared visual chrome: the top navigation bar, brand title, active page highlighting,
and consistent container padding.
"""

from typing import Any
import pydataui as pdu


def NavItem(label: str, path: str, current_path: str) -> pdu.Link:
    """Renders a single navigation link with active state highlighting."""
    is_active = (path == current_path)
    
    # Tailwind styling: highlighted when active, muted when inactive
    if is_active:
        class_name = "px-3 py-1.5 rounded-md text-sm font-semibold bg-primary text-primary-foreground shadow-sm transition"
    else:
        class_name = "px-3 py-1.5 rounded-md text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-muted transition"

    return pdu.Link(
        label,
        href=path,
        class_name=class_name,
        # HTMX smooth client-side transition (SPA-like without full-page flash)
        **{"hx-get": path, "hx-target": "#pdu-root", "hx-push-url": "true"}
    )


def AppHeader(current_path: str = "/") -> pdu.Row:
    """Global navigation bar with logo, page links, and live system status."""
    return pdu.Row(
        # Left: Brand Logo & Title
        pdu.Row(
            pdu.Badge("PyDataUI", variant="default", class_name="font-bold text-xs px-2.5 py-1"),
            pdu.Heading("Enterprise Portal", level=3, class_name="text-lg font-bold tracking-tight"),
            class_name="items-center space-x-3"
        ),

        # Center: Navigation Links
        pdu.Row(
            NavItem("Dashboard", "/", current_path),
            NavItem("Data Hub", "/data", current_path),
            NavItem("AI Copilot", "/copilot", current_path),
            NavItem("Settings", "/settings", current_path),
            class_name="items-center space-x-2 bg-secondary/50 p-1 rounded-lg border border-border"
        ),

        # Right: Quick Status Badge
        pdu.Row(
            pdu.Badge("v1.2.2 Stable", variant="outline", class_name="text-xs text-muted-foreground"),
            pdu.Badge("Cluster Online", variant="secondary", class_name="text-xs text-emerald-500 font-medium"),
            class_name="items-center space-x-2"
        ),

        class_name="justify-between items-center pb-6 border-b border-border mb-8"
    )


def AppShell(title: str, subtitle: str, content: Any, current_path: str = "/") -> pdu.Container:
    """Master application layout wrapper for all pages."""
    return pdu.Container(
        AppHeader(current_path=current_path),

        # Page Heading Banner
        pdu.Col(
            pdu.Heading(title, level=1, class_name="text-3xl font-extrabold tracking-tight"),
            pdu.Text(subtitle, class_name="text-muted-foreground text-sm mt-1"),
            class_name="mb-6"
        ),

        # Page Content
        content,

        # Global Footer
        pdu.Row(
            pdu.Text("Built with PyDataUI • Compiled Rust Core & Reactive Python", class_name="text-xs text-muted-foreground"),
            pdu.Link("GitHub Repository", href="https://github.com/rajboopathiking/pydataui", external=True, class_name="text-xs text-primary hover:underline"),
            class_name="justify-between items-center pt-8 border-t border-border mt-12"
        ),

        class_name="max-w-6xl py-6"
    )
