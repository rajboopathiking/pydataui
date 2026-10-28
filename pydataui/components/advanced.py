"""
Advanced Python-first browser components for PyDataUI.
No user-authored JavaScript required.
"""
from __future__ import annotations
import html
from typing import Any, Callable, Dict, List, Optional, Union
from .base import Component
from ..utils import escape_html, generate_id, sanitize_html
from ..state import EventHandler


class Markdown(Component):
    """
    Render Markdown content into safe, styled HTML without requiring JavaScript.

    Usage::

        Markdown("# Hello\\n\\nThis is **bold** text.")
    """
    tag = "div"

    def __init__(self, content: str = "", **kwargs):
        super().__init__(**kwargs)
        self.content = content

    def render(self, state_snapshot: Optional[Dict[str, Any]] = None) -> str:
        text = self._resolve_value(self.content, state_snapshot) or ""
        text = str(text)

        # Try to use python-markdown if available
        try:
            import markdown
            html_content = markdown.markdown(text, extensions=["fenced_code", "tables"])
        except ImportError:
            # Fallback pure-Python converter for basic markdown
            lines = text.split("\n")
            out = []
            in_code = False
            for line in lines:
                if line.startswith("```"):
                    if in_code:
                        out.append("</code></pre>")
                        in_code = False
                    else:
                        out.append('<pre class="bg-muted p-3 rounded-lg font-mono text-sm overflow-x-auto"><code>')
                        in_code = True
                    continue
                if in_code:
                    out.append(html.escape(line) + "\n")
                    continue
                if line.startswith("# "):
                    out.append(f'<h1 class="text-2xl font-bold mt-4 mb-2">{html.escape(line[2:])}</h1>')
                elif line.startswith("## "):
                    out.append(f'<h2 class="text-xl font-bold mt-3 mb-2">{html.escape(line[3:])}</h2>')
                elif line.startswith("### "):
                    out.append(f'<h3 class="text-lg font-semibold mt-2 mb-1">{html.escape(line[4:])}</h3>')
                elif line.startswith("- "):
                    out.append(f'<li class="ml-4 list-disc">{html.escape(line[2:])}</li>')
                elif line.strip() == "":
                    out.append('<div class="h-2"></div>')
                else:
                    out.append(f'<p class="mb-2 leading-relaxed">{html.escape(line)}</p>')
            if in_code:
                out.append("</code></pre>")
            html_content = "".join(out)

        # Markdown permits raw HTML and unsafe link schemes by default.
        # Always pass the result through the allowlist sanitizer.
        html_content = sanitize_html(html_content)

        return f'<div class="prose dark:prose-invert max-w-none pdu-markdown">{html_content}</div>'


class CodeEditor(Component):
    """
    Python-first interactive code editor component.
    Provides line numbers, language tagging, copy button, and Python event callbacks.
    Zero user JavaScript needed.

    Usage::

        CodeEditor(code="print('Hello World')", language="python", theme="dark", on_change=my_callback)
    """
    tag = "div"

    def __init__(
        self,
        code: str = "",
        value: Optional[str] = None,
        language: str = "python",
        theme: str = "dark",
        name: str = "code",
        readonly: bool = False,
        read_only: Optional[bool] = None,
        rows: int = 12,
        on_change: Optional[Union[EventHandler, Callable]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.code = value if value is not None else code
        self.language = language
        self.theme = theme
        self.name = name
        self.readonly = read_only if read_only is not None else readonly
        self.rows = rows
        if on_change:
            self._event_props["on_change"] = on_change

    def render(self, state_snapshot: Optional[Dict[str, Any]] = None) -> str:
        current_code = self._resolve_value(self.code, state_snapshot) or ""
        current_code = str(current_code)
        theme_bg = "bg-zinc-950 text-zinc-100" if self.theme == "dark" else "bg-zinc-50 text-zinc-900 border"
        editor_id = self.id or generate_id("editor")

        attrs = self._build_attrs(state_snapshot or {})
        ro_attr = "readonly" if self.readonly else ""

        escaped = html.escape(current_code)
        return f'''<div class="rounded-xl overflow-hidden shadow-sm border border-border {theme_bg} font-sans" id="{editor_id}" data-language="{html.escape(self.language)}">
  <div class="flex items-center justify-between px-4 py-2 border-b border-border/50 text-xs font-mono text-muted-foreground bg-muted/20">
    <span class="flex items-center gap-2">
      <span class="w-2.5 h-2.5 rounded-full bg-red-500/80 inline-block"></span>
      <span class="w-2.5 h-2.5 rounded-full bg-yellow-500/80 inline-block"></span>
      <span class="w-2.5 h-2.5 rounded-full bg-green-500/80 inline-block"></span>
      <span class="font-semibold uppercase tracking-wider ml-2">{html.escape(self.language)}</span>
    </span>
    <button type="button" onclick="navigator.clipboard.writeText(document.getElementById('{editor_id}-textarea').value)" class="copy-code-btn hover:text-foreground transition px-2 py-1 rounded bg-muted/40 text-xs">Copy</button>
  </div>
  <textarea id="{editor_id}-textarea" name="{html.escape(self.name)}" rows="{self.rows}" {ro_attr} class="w-full p-4 font-mono text-sm bg-transparent border-0 outline-none resize-y leading-relaxed" spellcheck="false" {attrs}>{escaped}</textarea>
</div>'''


class Chat(Component):
    """
    Python-first interactive chat component for AI agents, UnifiedNexus, and LangGraph.
    Renders message history and handles message submissions via Python event callbacks.

    Usage::

        Chat(
            messages=[{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hi!"}],
            on_send=handle_chat_message
        )
    """
    tag = "div"

    def __init__(
        self,
        messages: Optional[List[Dict[str, str]]] = None,
        placeholder: str = "Type your message...",
        title: str = "Agent Chat",
        on_send: Optional[Union[EventHandler, Callable]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.messages = messages or []
        self.placeholder = placeholder
        self.chat_title = title
        if on_send:
            self._event_props["on_send"] = on_send

    def render(self, state_snapshot: Optional[Dict[str, Any]] = None) -> str:
        msgs = self._resolve_value(self.messages, state_snapshot) or []
        chat_id = self.id or generate_id("chat")

        bubbles = []
        for m in msgs:
            role = m.get("role", "user")
            content = html.escape(str(m.get("content", "")))
            if role == "user":
                bubbles.append(
                    f'<div class="flex justify-end mb-3">'
                    f'<div class="max-w-[80%] rounded-2xl px-4 py-2.5 bg-primary text-primary-foreground text-sm shadow-sm">{content}</div>'
                    f'</div>'
                )
            else:
                bubbles.append(
                    f'<div class="flex justify-start mb-3">'
                    f'<div class="max-w-[80%] rounded-2xl px-4 py-2.5 bg-muted text-foreground text-sm border shadow-sm">{content}</div>'
                    f'</div>'
                )

        bubbles_html = "".join(bubbles) if bubbles else '<div class="text-center text-muted-foreground text-sm py-8">No messages yet. Start a conversation below!</div>'

        send_handler = self._event_props.get("on_send")
        htmx_post = ""
        if send_handler:
            htmx_attrs = self._get_event_htmx_attrs("click", send_handler)
            if "hx-include" not in htmx_attrs:
                htmx_attrs["hx-include"] = f"#{chat_id}-input"
            htmx_post = " ".join(f'{k}="{v}"' for k, v in htmx_attrs.items())

        return f'''<div class="chat-container rounded-xl border bg-card text-card-foreground shadow-sm flex flex-col h-[500px] overflow-hidden" id="{chat_id}">
  <div class="p-3 border-b bg-muted/30 font-semibold text-sm flex items-center gap-2">
    <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
    {html.escape(self.chat_title)}
  </div>
  <div class="flex-1 p-4 overflow-y-auto space-y-2" id="{chat_id}-messages">
    {bubbles_html}
  </div>
  <div class="p-3 border-t bg-background flex gap-2">
    <input type="text" name="message" id="{chat_id}-input" placeholder="{html.escape(self.placeholder)}" class="chat-input flex-1 h-10 px-3 py-2 text-sm rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-primary" onkeydown="if(event.key==='Enter'){{event.preventDefault();this.nextElementSibling.click();}}" />
    <button type="button" class="h-10 px-4 py-2 bg-primary text-primary-foreground text-sm font-medium rounded-md hover:bg-primary/90 transition shadow-sm" {htmx_post}>Send</button>
  </div>
</div>'''
