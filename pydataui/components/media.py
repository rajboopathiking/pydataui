from __future__ import annotations
import base64
import io
from typing import Any, List, Optional
from .base import Component
from ..utils import escape_html

def _normalize_media_src(src: Any, default_mime: str = "image/png") -> str:
    if isinstance(src, bytes):
        b64 = base64.b64encode(src).decode("utf-8")
        return f"data:{default_mime};base64,{b64}"
    if hasattr(src, "read") and callable(src.read):
        b = src.read()
        b64 = base64.b64encode(b).decode("utf-8")
        return f"data:{default_mime};base64,{b64}"
    if hasattr(src, "save") and callable(src.save):
        buf = io.BytesIO()
        src.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"
    return str(src)

class Image(Component):
    tag = 'img'
    def __init__(self, src='', alt='', caption=None, width=None, height=None, fit='cover', rounded=False, fallback=None, lazy=True, **props):
        super().__init__(**props)
        self.raw_src = src
        self.caption = caption
        self.props['src'] = _normalize_media_src(src, "image/png")
        self.props['alt'] = alt or (caption or '')
        if lazy: self.props['loading'] = 'lazy'
        self.width = width
        self.height = height
        self.fit = fit
        self.rounded = rounded
        self.fallback = fallback
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-image', 'max-w-full']
        if self.rounded: classes.append('pdu-image-rounded rounded-xl')
        classes.append(f'pdu-object-{self.fit}')
        return classes
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.width:
            w_val = f"{self.width}px" if isinstance(self.width, (int, float)) else str(self.width)
            s += f" width: {w_val};"
        if self.height:
            h_val = f"{self.height}px" if isinstance(self.height, (int, float)) else str(self.height)
            s += f" height: {h_val};"
        return s.strip()

    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        img_html = f"<{self.tag} {attrs}/>"
        if self.caption:
            return f"<figure class='pdu-media-figure inline-block my-2'>{img_html}<figcaption class='text-xs text-muted-foreground mt-1.5 text-center font-medium'>{escape_html(self.caption)}</figcaption></figure>"
        return img_html

class Video(Component):
    tag = 'video'
    def __init__(self, src='', poster=None, caption=None, controls=True, autoplay=False, muted=False, loop=False, width=None, height=None, aspect=None, fit=None, **props):
        super().__init__(**props)
        self.caption = caption
        self.props['src'] = _normalize_media_src(src, "video/mp4")
        if poster: self.props['poster'] = poster
        if controls: self.props['controls'] = 'controls'
        if autoplay: self.props['autoplay'] = 'autoplay'
        if muted: self.props['muted'] = 'muted'
        if loop: self.props['loop'] = 'loop'
        self.width = width
        self.height = height
        self.aspect = aspect
        self.fit = fit
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-video', 'max-w-full', 'rounded-xl']
        
    def _get_style_string(self) -> str:
        s = super()._get_style_string()
        if self.width:
            w_val = f"{self.width}px" if isinstance(self.width, (int, float)) else str(self.width)
            s += f" width: {w_val};"
        if self.height:
            h_val = f"{self.height}px" if isinstance(self.height, (int, float)) else str(self.height)
            s += f" height: {h_val};"
        if self.aspect:
            s += f" aspect-ratio: {self.aspect};"
        if self.fit:
            s += f" object-fit: {self.fit};"
        return s.strip()
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        vid_html = f"<{self.tag} {attrs}></{self.tag}>"
        if self.caption:
            return f"<figure class='pdu-media-figure inline-block my-2'>{vid_html}<figcaption class='text-xs text-muted-foreground mt-1.5 text-center font-medium'>{escape_html(self.caption)}</figcaption></figure>"
        return vid_html

class Audio(Component):
    tag = 'audio'
    def __init__(self, src='', caption=None, controls=True, autoplay=False, muted=False, loop=False, **props):
        super().__init__(**props)
        self.caption = caption
        self.props['src'] = _normalize_media_src(src, "audio/mp3")
        if controls: self.props['controls'] = 'controls'
        if autoplay: self.props['autoplay'] = 'autoplay'
        if muted: self.props['muted'] = 'muted'
        if loop: self.props['loop'] = 'loop'
        
    def _get_classes(self) -> List[str]:
        return super()._get_classes() + ['pdu-audio', 'w-full', 'my-2']
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        aud_html = f"<{self.tag} {attrs}></{self.tag}>"
        if self.caption:
            return f"<figure class='pdu-media-figure block my-2'>{aud_html}<figcaption class='text-xs text-muted-foreground mt-1 text-center font-medium'>{escape_html(self.caption)}</figcaption></figure>"
        return aud_html

class Icon(Component):
    tag = 'span'
    def __init__(self, name='', size='md', color=None, **props):
        super().__init__(**props)
        self.name = name
        self.size = size
        self.color = color
        
    def _get_classes(self) -> List[str]:
        classes = super()._get_classes() + ['pdu-icon', f'pdu-icon-{self.size}']
        if self.color: classes.append(f'pdu-text-{self.color}')
        return classes
        
    def render(self, state_snapshot: dict) -> str:
        attrs = self._build_attrs(state_snapshot)
        name = escape_html(str(self._resolve_value(self.name, state_snapshot)))
        return f"<{self.tag} {attrs}>{name}</{self.tag}>"
