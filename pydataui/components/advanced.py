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
        messages: Optional[List[Dict[str, Any]]] = None,
        placeholder: str = "Type your message... (Shift+Enter for newline)",
        title: str = "Agent Chat",
        subtitle: Optional[str] = None,
        on_send: Optional[Union[EventHandler, Callable]] = None,
        on_clear: Optional[Union[EventHandler, Callable]] = None,
        loading: Optional[Union[bool, Any]] = None,
        suggestions: Optional[List[str]] = None,
        height: str = "600px",
        show_clear: bool = True,
        user_avatar: Optional[str] = None,
        assistant_avatar: Optional[str] = None,
        enable_markdown: bool = True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.messages = messages or []
        self.placeholder = placeholder
        self.chat_title = title
        self.subtitle = subtitle
        self.loading = loading
        self.suggestions = suggestions or []
        self.height = height
        self.show_clear = show_clear
        self.user_avatar = user_avatar
        self.assistant_avatar = assistant_avatar
        self.enable_markdown = enable_markdown
        if on_send:
            self._event_props["on_send"] = on_send
        if on_clear:
            self._event_props["on_clear"] = on_clear

    def render(self, state_snapshot: Optional[Dict[str, Any]] = None) -> str:
        snap = state_snapshot if state_snapshot is not None else {}
        msgs = self._resolve_value(self.messages, snap) or []
        is_loading = bool(self._resolve_value(self.loading, snap)) if self.loading is not None else False
        chat_id = self.id or generate_id("chat")

        # Visual Avatars
        user_av_html = f'<img src="{self.user_avatar}" class="w-8 h-8 rounded-full object-cover shrink-0" alt="User" />' if self.user_avatar else '''<div class="w-8 h-8 rounded-full bg-primary/20 text-primary flex items-center justify-center text-xs font-bold shrink-0">U</div>'''
        
        asst_av_html = f'<img src="{self.assistant_avatar}" class="w-8 h-8 rounded-full object-cover shrink-0" alt="AI" />' if self.assistant_avatar else '''<div class="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-indigo-600 text-white flex items-center justify-center text-xs font-bold shrink-0 shadow-sm"><svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg></div>'''

        bubbles = []
        for m in msgs:
            role = m.get("role", "user")
            raw_content = str(m.get("content", ""))
            timestamp = m.get("timestamp", "")
            time_html = f'<span class="text-[10px] text-muted-foreground mt-1 block opacity-75">{html.escape(timestamp)}</span>' if timestamp else ''
            
            if role == "user":
                escaped_text = html.escape(raw_content).replace("\n", "<br/>")
                bubbles.append(
                    f'<div class="flex justify-end gap-2.5 mb-4 chat-bubble-container">'
                    f'  <div class="flex flex-col items-end max-w-[80%]">'
                    f'    <div class="rounded-2xl rounded-tr-sm px-4 py-2.5 bg-primary text-primary-foreground text-sm shadow-sm leading-relaxed">{escaped_text}</div>'
                    f'    {time_html}'
                    f'  </div>'
                    f'  {user_av_html}'
                    f'</div>'
                )
            else:
                # Assistant formatted content with Markdown support
                if self.enable_markdown:
                    try:
                        import markdown
                        parsed_content = markdown.markdown(raw_content, extensions=['fenced_code', 'tables'])
                    except Exception:
                        parsed_content = html.escape(raw_content).replace("\n", "<br/>")
                else:
                    parsed_content = html.escape(raw_content).replace("\n", "<br/>")

                escaped_raw = html.escape(raw_content, quote=True)
                copy_btn = f'''<button type="button" onclick="navigator.clipboard.writeText(this.getAttribute('data-clip')).then(()=>{{this.innerHTML='Copied!';setTimeout(()=>{{this.innerHTML='Copy'}},2000)}})" data-clip="{escaped_raw}" class="text-[11px] text-muted-foreground hover:text-foreground transition opacity-60 hover:opacity-100 flex items-center gap-1 mt-1 cursor-pointer">Copy</button>'''

                bubbles.append(
                    f'<div class="flex justify-start gap-2.5 mb-4 chat-bubble-container" data-content="{escaped_raw}">'
                    f'  {asst_av_html}'
                    f'  <div class="flex flex-col items-start max-w-[82%]">'
                    f'    <div class="rounded-2xl rounded-tl-sm px-4 py-3 bg-muted/80 text-foreground text-sm border border-border/60 shadow-sm leading-relaxed prose prose-sm dark:prose-invert max-w-none">{parsed_content}</div>'
                    f'    <div class="flex items-center gap-3">'
                    f'      {time_html}'
                    f'      {copy_btn}'
                    f'    </div>'
                    f'  </div>'
                    f'</div>'
                )

        # Typing / Thinking Indicator Bubble
        indicator_display = "flex" if is_loading else "none"
        indicator_bubble = f'''<div id="{chat_id}-loading" class="htmx-indicator justify-start gap-2.5 mb-4" style="display: {indicator_display};">
  {asst_av_html}
  <div class="rounded-2xl rounded-tl-sm px-4 py-2.5 bg-muted/80 text-foreground text-sm border border-border/60 shadow-sm flex items-center gap-2">
    <span class="inline-flex gap-1 items-center">
      <span class="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:-0.3s]"></span>
      <span class="w-2 h-2 rounded-full bg-primary animate-bounce [animation-delay:-0.15s]"></span>
      <span class="w-2 h-2 rounded-full bg-primary animate-bounce"></span>
    </span>
    <span class="text-xs text-muted-foreground ml-1.5 font-medium">{html.escape(self.chat_title)} is thinking...</span>
  </div>
</div>'''

        # Empty conversation state with friendly welcome
        empty_state = f'''<div class="text-center text-muted-foreground py-12 flex flex-col items-center justify-center gap-2">
  <div class="w-12 h-12 rounded-2xl bg-muted flex items-center justify-center text-primary mb-2 shadow-inner">
    <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
  </div>
  <p class="font-semibold text-foreground text-sm">Welcome to {html.escape(self.chat_title)}</p>
  <p class="text-xs max-w-sm text-muted-foreground">Ask questions, explore data, or generate code below.</p>
</div>'''

        bubbles_html = "".join(bubbles) if bubbles else empty_state

        # Suggestion chips
        chips_html = ""
        if self.suggestions:
            chip_elements = []
            for s in self.suggestions:
                s_esc = html.escape(s, quote=True)
                chip_elements.append(
                    f'<button type="button" onclick="const inp=document.getElementById(\'{chat_id}-input\');inp.value=\'{s_esc}\';document.getElementById(\'{chat_id}-send-btn\').click();" class="text-xs px-3 py-1.5 rounded-full border border-border/80 bg-background hover:bg-muted text-foreground/80 hover:text-foreground transition shadow-sm cursor-pointer whitespace-nowrap">'
                    f'💡 {html.escape(s)}'
                    f'</button>'
                )
            chips_html = f'<div class="px-3 py-2 border-t bg-muted/20 flex gap-2 overflow-x-auto no-scrollbar">{"".join(chip_elements)}</div>'

        # Event Handlers: on_send and on_clear
        send_handler = self._event_props.get("on_send")
        htmx_send_attrs = ""
        if send_handler:
            htmx_attrs = self._get_event_htmx_attrs("click", send_handler)
            if "hx-include" not in htmx_attrs:
                htmx_attrs["hx-include"] = f"#{chat_id}-input"
            if "hx-indicator" not in htmx_attrs:
                htmx_attrs["hx-indicator"] = f"#{chat_id}-loading, #{chat_id}-spinner"
            if "hx-disabled-elt" not in htmx_attrs:
                htmx_attrs["hx-disabled-elt"] = f"#{chat_id}-send-btn, #{chat_id}-input"
            htmx_send_attrs = " ".join(f'{k}="{v}"' for k, v in htmx_attrs.items())

        clear_btn_html = ""
        clear_handler = self._event_props.get("on_clear")
        if self.show_clear and clear_handler:
            htmx_clear = self._get_event_htmx_attrs("click", clear_handler)
            clear_attrs = " ".join(f'{k}="{v}"' for k, v in htmx_clear.items())
            clear_btn_html = f'''<button type="button" title="Clear Conversation" class="text-xs px-2.5 py-1 rounded-md text-muted-foreground hover:text-foreground hover:bg-muted transition flex items-center gap-1 cursor-pointer" {clear_attrs}>
  <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/></svg>
  <span>Clear</span>
</button>'''

        subtitle_html = f'<p class="text-xs text-muted-foreground">{html.escape(self.subtitle)}</p>' if self.subtitle else ''

        return f'''<style>
#{chat_id}-loading.htmx-request {{ display: flex !important; }}
#{chat_id}-spinner.htmx-request {{ display: inline-block !important; }}
#{chat_id} .chat-messages {{ scroll-behavior: smooth; }}
#{chat_id} .no-scrollbar::-webkit-scrollbar {{ display: none; }}
#{chat_id} .no-scrollbar {{ -ms-overflow-style: none; scrollbar-width: none; }}
</style>
<div class="chat-container rounded-2xl border border-border/80 bg-card text-card-foreground shadow-md flex flex-col overflow-hidden" style="height: {self.height};" id="{chat_id}">
  <div class="px-4 py-3 border-b bg-muted/30 flex items-center justify-between">
    <div class="flex items-center gap-3">
      {asst_av_html}
      <div>
        <div class="flex items-center gap-2">
          <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span class="font-semibold text-sm text-foreground">{html.escape(self.chat_title)}</span>
        </div>
        {subtitle_html}
      </div>
    </div>
    <div class="flex items-center gap-2">
      {clear_btn_html}
      <span class="text-[11px] font-medium text-emerald-600 bg-emerald-500/10 dark:text-emerald-400 px-2.5 py-0.5 rounded-full border border-emerald-500/20">Online</span>
    </div>
  </div>

  <div class="flex-1 p-4 overflow-y-auto space-y-2 chat-messages" id="{chat_id}-messages">
    {bubbles_html}
    {indicator_bubble}
  </div>

  {chips_html}

  <div class="p-3 border-t bg-background flex flex-col gap-1.5">
    <div class="flex items-end gap-2">
      <textarea name="message" id="{chat_id}-input" rows="1" placeholder="{html.escape(self.placeholder)}" class="chat-input flex-1 min-h-[42px] max-h-[140px] px-3.5 py-2.5 text-sm rounded-xl border border-input bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent resize-none leading-relaxed disabled:opacity-60 disabled:cursor-not-allowed" onkeydown="if(event.key==='Enter'&&!event.shiftKey){{if(event.isComposing||event.keyCode===229)return;event.preventDefault();document.getElementById('{chat_id}-send-btn').click();}}" oninput="this.style.height='auto';this.style.height=(this.scrollHeight)+'px';"></textarea>
      
      <button type="button" id="{chat_id}-send-btn" class="h-10 px-4 bg-primary text-primary-foreground text-sm font-medium rounded-xl hover:bg-primary/90 transition shadow-sm inline-flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed shrink-0 cursor-pointer" {htmx_send_attrs}>
        <span>Send</span>
        <svg id="{chat_id}-spinner" class="htmx-indicator animate-spin h-4 w-4 text-primary-foreground hidden" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </button>
    </div>
    <div class="flex justify-between items-center px-1 text-[11px] text-muted-foreground/70">
      <span>Shift + Enter for new line • Enter to send</span>
      <span class="text-[10px]">PyDataUI AI Chat</span>
    </div>
  </div>
</div>
<script>
(function() {{
  const el = document.getElementById('{chat_id}-messages');
  if (el) {{
    el.scrollTop = el.scrollHeight;
  }}
}})();
</script>'''
