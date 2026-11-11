"""
Universal Extensibility Engine for PyDataUI.
Allows Data & AI developers to directly ingest upcoming and community shadcn/ui
components from JSX snippets, HTML templates, or JSON registries without writing frontend JavaScript.
"""
from __future__ import annotations
import json
import re
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Union
from .base import Component
from ..utils import escape_html, generate_id


class ParsedComponent(Component):
    """
    Component produced from a JSX or HTML template.
    Resolves slot tokens {token} against passed kwargs and children.
    """
    def __init__(self, template: str, *children, **props):
        super().__init__(*children, **props)
        self.template = template
        self.slot_props = props

    def render(self, state_snapshot: Optional[Dict[str, Any]] = None) -> str:
        snap = state_snapshot or {}
        rendered = self.template

        # Render children slot
        children_html = self._render_children(snap)
        rendered = re.sub(r'\{children\}', children_html, rendered)

        # Replace prop slots {prop_name}
        for key, val in self.slot_props.items():
            if isinstance(val, Component):
                val_str = val.render(snap)
            elif isinstance(val, (list, tuple)):
                val_str = "".join(v.render(snap) if isinstance(v, Component) else str(v) for v in val)
            else:
                resolved = self._resolve_value(val, snap)
                val_str = escape_html(str(resolved)) if resolved is not None else ""
            pattern = re.compile(rf'\{{{key}\}}')
            rendered = pattern.sub(val_str, rendered)

        # Remove any unresolved optional slot tokens
        rendered = re.sub(r'\{[a-zA-Z0-9_]+\}', '', rendered)
        return rendered


def from_jsx(jsx_code: str) -> Callable[..., ParsedComponent]:
    """
    Transpile a raw JSX snippet (copied from ui.shadcn.com or 21st.dev)
    directly into a pure Python component factory.

    Example:
        SparkCard = from_jsx('''
        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <h3 className="font-semibold text-sm">{title}</h3>
          <div className="text-2xl font-bold">{metric}</div>
          <div>{children}</div>
        </div>
        ''')

        # Use immediately in pure Python:
        card = SparkCard(title="Active Nodes", metric="64", children=[...])
    """
    cleaned = jsx_code.strip()
    # Normalize className to class
    cleaned = re.sub(r'\bclassName\s*=\s*', 'class=', cleaned)
    # Remove self-closing tags like <img ... /> or JSX fragment artifacts
    cleaned = re.sub(r'</?>', '', cleaned)
    # Convert React style props if present
    cleaned = re.sub(r'style=\{\{([^}]+)\}\}', r'style="\1"', cleaned)

    def component_factory(*children, **props) -> ParsedComponent:
        return ParsedComponent(cleaned, *children, **props)

    return component_factory


def from_html(html_code: str) -> Callable[..., ParsedComponent]:
    """
    Transpile an HTML snippet with {slot} placeholders directly into
    a pure Python component factory.
    """
    cleaned = html_code.strip()

    def component_factory(*children, **props) -> ParsedComponent:
        return ParsedComponent(cleaned, *children, **props)

    return component_factory


def dynamic(schema_or_url: Union[str, Dict[str, Any]]) -> type:
    """
    Dynamically loads an external shadcn JSON schema or community registry item
    and returns a ready-to-use PyDataUI Component class.

    Example:
        SpotlightCard = dynamic("https://ui.shadcn.com/r/styles/default/card.json")
        card = SpotlightCard(title="AI Agent")
    """
    schema_data = None
    if isinstance(schema_or_url, dict):
        schema_data = schema_or_url
    elif isinstance(schema_or_url, str):
        schema_str = schema_or_url.strip()
        if schema_str.startswith("http://") or schema_str.startswith("https://"):
            req = urllib.request.Request(
                schema_str,
                headers={"User-Agent": "PyDataUI/1.1.1 (Extensibility Engine)"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                schema_data = json.loads(resp.read().decode("utf-8"))
        elif schema_str.startswith("{"):
            schema_data = json.loads(schema_str)
        else:
            raise ValueError(f"Invalid dynamic schema source: {schema_or_url}")

    name = schema_data.get("name", "DynamicComponent")
    tag = schema_data.get("tag", "div")
    base_classes = schema_data.get("tailwind", "") or schema_data.get("classes", "")

    from .shadcn import create_shadcn_component
    return create_shadcn_component(
        tag=tag,
        base_classes=base_classes,
        name=name
    )
