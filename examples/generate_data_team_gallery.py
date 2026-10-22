from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from pydataui.components import base as component_base
from pydataui.compiler.templates import _build_css_variables
from pydataui.utils import escape_html

from data_team_samples import SAMPLES

OUTPUT = PROJECT / "docs" / "examples" / "data-team-gallery.html"
CSS_PATH = PROJECT / "pydataui" / "styling" / "css" / "pydataui.css"

_TAILWIND_CONFIG = {
    "darkMode": "class",
    "theme": {
        "extend": {
            "colors": {
                "border": "hsl(var(--border))",
                "input": "hsl(var(--input))",
                "ring": "hsl(var(--ring))",
                "background": "hsl(var(--background))",
                "foreground": "hsl(var(--foreground))",
                "primary": {
                    "DEFAULT": "hsl(var(--primary))",
                    "foreground": "hsl(var(--primary-foreground))",
                },
                "secondary": {
                    "DEFAULT": "hsl(var(--secondary))",
                    "foreground": "hsl(var(--secondary-foreground))",
                },
                "destructive": {
                    "DEFAULT": "hsl(var(--destructive))",
                    "foreground": "hsl(var(--destructive-foreground))",
                },
                "muted": {
                    "DEFAULT": "hsl(var(--muted))",
                    "foreground": "hsl(var(--muted-foreground))",
                },
                "accent": {
                    "DEFAULT": "hsl(var(--accent))",
                    "foreground": "hsl(var(--accent-foreground))",
                },
                "card": {
                    "DEFAULT": "hsl(var(--card))",
                    "foreground": "hsl(var(--card-foreground))",
                },
            },
            "borderRadius": {
                "lg": "var(--radius)",
                "md": "calc(var(--radius) - 2px)",
                "sm": "calc(var(--radius) - 4px)",
            },
        },
    },
}

_custom_css = """
:root { color-scheme: light; }
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  background: #f6f8fb;
  color: #0f172a;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
    "Segoe UI", sans-serif;
}
a { color: #2563eb; }
.gallery-header {
  background: radial-gradient(circle at top right, #dbeafe 0, #f8fafc 45%, #f8fafc 100%);
  border-bottom: 1px solid #e2e8f0;
}
.gallery-wrap { width: 100%; max-width: 1400px; margin: 0 auto; padding: 0 24px; }
.gallery-hero { padding: 64px 0 36px; }
.gallery-kicker {
  display: inline-block; margin-bottom: 12px; padding: 5px 10px;
  border: 1px solid #bfdbfe; border-radius: 999px; background: #eff6ff;
  color: #1d4ed8; font-size: 12px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase;
}
.gallery-hero h1 { margin: 0 0 12px; font-size: clamp(32px, 5vw, 52px); line-height: 1.05; }
.gallery-hero p { max-width: 760px; margin: 0; color: #475569; font-size: 18px; line-height: 1.65; }
.gallery-nav { display: flex; flex-wrap: wrap; gap: 8px; padding: 0 0 32px; }
.gallery-nav a {
  padding: 8px 14px; border: 1px solid #cbd5e1; border-radius: 999px;
  background: #fff; color: #334155; font-size: 14px; font-weight: 600;
  text-decoration: none;
}
.gallery-nav a:hover { border-color: #2563eb; color: #1d4ed8; }
.gallery-main { padding: 48px 0 24px; }
.gallery-sample { margin: 0 0 64px; scroll-margin-top: 24px; }
.gallery-meta {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 24px; margin-bottom: 14px;
}
.gallery-role {
  display: block; margin-bottom: 4px; color: #64748b; font-size: 12px;
  font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
}
.gallery-meta h2 { margin: 0 0 6px; font-size: 24px; }
.gallery-meta p { max-width: 760px; margin: 0; color: #475569; line-height: 1.55; }
.gallery-meta a { flex: none; font-size: 13px; font-weight: 600; text-decoration: none; }
.gallery-canvas {
  overflow: hidden; border: 1px solid #dbe2ea; border-radius: 18px;
  background: #fff; box-shadow: 0 24px 60px rgba(15, 23, 42, .08);
}
.gallery-canvas > .pdu-container { max-width: 1180px !important; }
.gallery-footer { padding: 28px 0 56px; color: #64748b; font-size: 13px; }
.gallery-footer code { color: #334155; }
@media (max-width: 720px) {
  .gallery-hero { padding-top: 40px; }
  .gallery-meta { display: block; }
  .gallery-meta a { display: inline-block; margin-top: 8px; }
  .gallery-canvas { border-radius: 12px; }
}
"""


def _deterministic_ids() -> None:
    counter = itertools.count(1)

    def next_id(prefix: str = "pdu") -> str:
        return f"{prefix}-gallery-{next(counter):04d}"

    component_base.generate_id = next_id


def _section(sample: dict) -> str:
    body = sample["builder"]().render({})
    return f"""
    <section class="gallery-sample" id="{escape_html(sample['id'])}">
      <div class="gallery-meta">
        <div>
          <span class="gallery-role">{escape_html(sample['role'])}</span>
          <h2>{escape_html(sample['title'])}</h2>
          <p>{escape_html(sample['description'])}</p>
        </div>
        <a href="#top">Back to top</a>
      </div>
      <div class="gallery-canvas">{body}</div>
    </section>
    """


def build_gallery() -> str:
    framework_css = CSS_PATH.read_text(encoding="utf-8")
    theme_css = _build_css_variables("zinc")
    tailwind_config = json.dumps(_TAILWIND_CONFIG)
    nav = "".join(
        f'<a href="#{escape_html(sample["id"])}">{escape_html(sample["title"])}</a>'
        for sample in SAMPLES
    )
    sections = "".join(_section(sample) for sample in SAMPLES)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%232563eb'/%3E%3Cpath d='M16 42l10-12 8 7 14-19' fill='none' stroke='white' stroke-width='5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
<title>PyDataUI Data Team Template Gallery</title>
<script src="https://cdn.tailwindcss.com"></script>
<script>
if (window.tailwind) {{
  tailwind.config = {tailwind_config};
}}
</script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
{theme_css}
</style>
<style>
{framework_css}
</style>
<style>
{_custom_css}
</style>
</head>
<body id="top">
<header class="gallery-header">
  <div class="gallery-wrap">
    <div class="gallery-hero">
      <span class="gallery-kicker">PyDataUI template gallery</span>
      <h1>Low-code pages for data professionals</h1>
      <p>
        Four complete page layouts composed from the same Python components used by
        live PyDataUI applications. Each example below uses the public
        <code>pydataui.templates</code> API and sample data from
        <code>examples/data_team_samples.py</code>.
      </p>
    </div>
    <nav class="gallery-nav" aria-label="Template examples">{nav}</nav>
  </div>
</header>
<main class="gallery-main">
  <div class="gallery-wrap">{sections}</div>
</main>
<footer class="gallery-footer">
  <div class="gallery-wrap">
    Generated by <code>python examples/generate_data_team_gallery.py</code>.
    Run <code>python examples/data_team_templates.py</code> to use the same pages
    as a live app.
  </div>
</footer>
</body>
</html>
"""


def main() -> None:
    _deterministic_ids()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(build_gallery(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(PROJECT)}")


if __name__ == "__main__":
    main()
