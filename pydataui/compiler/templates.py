import json
from typing import Any, Dict, List, Optional, Union

PALETTES: Dict[str, Dict[str, Dict[str, str]]] = {
    'zinc': {
        'light': {
            '--background': '0 0% 100%',
            '--foreground': '240 10% 3.9%',
            '--card': '0 0% 100%',
            '--card-foreground': '240 10% 3.9%',
            '--primary': '240 5.9% 10%',
            '--primary-foreground': '0 0% 98%',
            '--secondary': '240 4.8% 95.9%',
            '--secondary-foreground': '240 5.9% 10%',
            '--muted': '240 4.8% 95.9%',
            '--muted-foreground': '240 3.8% 46.1%',
            '--accent': '240 4.8% 95.9%',
            '--accent-foreground': '240 5.9% 10%',
            '--destructive': '0 84.2% 60.2%',
            '--destructive-foreground': '0 0% 98%',
            '--border': '240 5.9% 90%',
            '--input': '240 5.9% 90%',
            '--ring': '240 5.9% 10%',
            '--radius': '0.5rem',
        },
        'dark': {
            '--background': '240 10% 3.9%',
            '--foreground': '0 0% 98%',
            '--card': '240 10% 3.9%',
            '--card-foreground': '0 0% 98%',
            '--primary': '0 0% 98%',
            '--primary-foreground': '240 5.9% 10%',
            '--secondary': '240 3.7% 15.9%',
            '--secondary-foreground': '0 0% 98%',
            '--muted': '240 3.7% 15.9%',
            '--muted-foreground': '240 5% 64.9%',
            '--accent': '240 3.7% 15.9%',
            '--accent-foreground': '0 0% 98%',
            '--destructive': '0 62.8% 30.6%',
            '--destructive-foreground': '0 0% 98%',
            '--border': '240 3.7% 15.9%',
            '--input': '240 3.7% 15.9%',
            '--ring': '240 4.9% 83.9%',
        }
    },
    'slate': {
        'light': {
            '--background': '0 0% 100%',
            '--foreground': '222.2 84% 4.9%',
            '--card': '0 0% 100%',
            '--card-foreground': '222.2 84% 4.9%',
            '--primary': '222.2 47.4% 11.2%',
            '--primary-foreground': '210 40% 98%',
            '--secondary': '210 40% 96.1%',
            '--secondary-foreground': '222.2 47.4% 11.2%',
            '--muted': '210 40% 96.1%',
            '--muted-foreground': '215.4 16.3% 46.9%',
            '--accent': '210 40% 96.1%',
            '--accent-foreground': '222.2 47.4% 11.2%',
            '--destructive': '0 84.2% 60.2%',
            '--destructive-foreground': '210 40% 98%',
            '--border': '214.3 31.8% 91.4%',
            '--input': '214.3 31.8% 91.4%',
            '--ring': '222.2 84% 4.9%',
            '--radius': '0.5rem',
        },
        'dark': {
            '--background': '222.2 84% 4.9%',
            '--foreground': '210 40% 98%',
            '--card': '222.2 84% 4.9%',
            '--card-foreground': '210 40% 98%',
            '--primary': '210 40% 98%',
            '--primary-foreground': '222.2 47.4% 11.2%',
            '--secondary': '217.2 32.6% 17.5%',
            '--secondary-foreground': '210 40% 98%',
            '--muted': '217.2 32.6% 17.5%',
            '--muted-foreground': '215 20.2% 65.1%',
            '--accent': '217.2 32.6% 17.5%',
            '--accent-foreground': '210 40% 98%',
            '--destructive': '0 62.8% 30.6%',
            '--destructive-foreground': '210 40% 98%',
            '--border': '217.2 32.6% 17.5%',
            '--input': '217.2 32.6% 17.5%',
            '--ring': '212.7 26.8% 83.9%',
        }
    },
    'blue': {
        'light': {
            '--background': '0 0% 100%',
            '--foreground': '222.2 84% 4.9%',
            '--card': '0 0% 100%',
            '--card-foreground': '222.2 84% 4.9%',
            '--primary': '221.2 83.2% 53.3%',
            '--primary-foreground': '210 40% 98%',
            '--secondary': '210 40% 96.1%',
            '--secondary-foreground': '222.2 47.4% 11.2%',
            '--muted': '210 40% 96.1%',
            '--muted-foreground': '215.4 16.3% 46.9%',
            '--accent': '210 40% 96.1%',
            '--accent-foreground': '222.2 47.4% 11.2%',
            '--destructive': '0 84.2% 60.2%',
            '--destructive-foreground': '210 40% 98%',
            '--border': '214.3 31.8% 91.4%',
            '--input': '214.3 31.8% 91.4%',
            '--ring': '221.2 83.2% 53.3%',
            '--radius': '0.5rem',
        },
        'dark': {
            '--background': '222.2 84% 4.9%',
            '--foreground': '210 40% 98%',
            '--card': '222.2 84% 4.9%',
            '--card-foreground': '210 40% 98%',
            '--primary': '217.2 91.2% 59.8%',
            '--primary-foreground': '222.2 47.4% 11.2%',
            '--secondary': '217.2 32.6% 17.5%',
            '--secondary-foreground': '210 40% 98%',
            '--muted': '217.2 32.6% 17.5%',
            '--muted-foreground': '215 20.2% 65.1%',
            '--accent': '217.2 32.6% 17.5%',
            '--accent-foreground': '210 40% 98%',
            '--destructive': '0 62.8% 30.6%',
            '--destructive-foreground': '210 40% 98%',
            '--border': '217.2 32.6% 17.5%',
            '--input': '217.2 32.6% 17.5%',
            '--ring': '217.2 91.2% 59.8%',
        }
    },
    'violet': {
        'light': {
            '--background': '0 0% 100%',
            '--foreground': '224 71.4% 4.1%',
            '--card': '0 0% 100%',
            '--card-foreground': '224 71.4% 4.1%',
            '--primary': '262.1 83.3% 57.8%',
            '--primary-foreground': '210 20% 98%',
            '--secondary': '220 14.3% 95.9%',
            '--secondary-foreground': '220.9 39.3% 11%',
            '--muted': '220 14.3% 95.9%',
            '--muted-foreground': '220 8.9% 46.1%',
            '--accent': '220 14.3% 95.9%',
            '--accent-foreground': '220.9 39.3% 11%',
            '--destructive': '0 84.2% 60.2%',
            '--destructive-foreground': '210 20% 98%',
            '--border': '220 13% 91%',
            '--input': '220 13% 91%',
            '--ring': '262.1 83.3% 57.8%',
            '--radius': '0.5rem',
        },
        'dark': {
            '--background': '224 71.4% 4.1%',
            '--foreground': '210 20% 98%',
            '--card': '224 71.4% 4.1%',
            '--card-foreground': '210 20% 98%',
            '--primary': '263.4 70% 50.4%',
            '--primary-foreground': '210 20% 98%',
            '--secondary': '215 27.9% 16.9%',
            '--secondary-foreground': '210 20% 98%',
            '--muted': '215 27.9% 16.9%',
            '--muted-foreground': '217.9 10.6% 64.9%',
            '--accent': '215 27.9% 16.9%',
            '--accent-foreground': '210 20% 98%',
            '--destructive': '0 62.8% 30.6%',
            '--destructive-foreground': '210 20% 98%',
            '--border': '215 27.9% 16.9%',
            '--input': '215 27.9% 16.9%',
            '--ring': '263.4 70% 50.4%',
        }
    },
    'green': {
        'light': {
            '--background': '0 0% 100%',
            '--foreground': '240 10% 3.9%',
            '--card': '0 0% 100%',
            '--card-foreground': '240 10% 3.9%',
            '--primary': '142.1 76.2% 36.3%',
            '--primary-foreground': '355.7 100% 97.3%',
            '--secondary': '240 4.8% 95.9%',
            '--secondary-foreground': '240 5.9% 10%',
            '--muted': '240 4.8% 95.9%',
            '--muted-foreground': '240 3.8% 46.1%',
            '--accent': '240 4.8% 95.9%',
            '--accent-foreground': '240 5.9% 10%',
            '--destructive': '0 84.2% 60.2%',
            '--destructive-foreground': '0 0% 98%',
            '--border': '240 5.9% 90%',
            '--input': '240 5.9% 90%',
            '--ring': '142.1 76.2% 36.3%',
            '--radius': '0.5rem',
        },
        'dark': {
            '--background': '240 10% 3.9%',
            '--foreground': '0 0% 98%',
            '--card': '240 10% 3.9%',
            '--card-foreground': '0 0% 98%',
            '--primary': '142.1 70.6% 45.3%',
            '--primary-foreground': '144.9 80.4% 10%',
            '--secondary': '240 3.7% 15.9%',
            '--secondary-foreground': '0 0% 98%',
            '--muted': '240 3.7% 15.9%',
            '--muted-foreground': '240 5% 64.9%',
            '--accent': '240 3.7% 15.9%',
            '--accent-foreground': '0 0% 98%',
            '--destructive': '0 62.8% 30.6%',
            '--destructive-foreground': '0 0% 98%',
            '--border': '240 3.7% 15.9%',
            '--input': '240 3.7% 15.9%',
            '--ring': '142.4 71.8% 29.2%',
        }
    },
    'rose': {
        'light': {
            '--background': '0 0% 100%',
            '--foreground': '240 10% 3.9%',
            '--card': '0 0% 100%',
            '--card-foreground': '240 10% 3.9%',
            '--primary': '346.8 77.2% 49.8%',
            '--primary-foreground': '355.7 100% 97.3%',
            '--secondary': '240 4.8% 95.9%',
            '--secondary-foreground': '240 5.9% 10%',
            '--muted': '240 4.8% 95.9%',
            '--muted-foreground': '240 3.8% 46.1%',
            '--accent': '240 4.8% 95.9%',
            '--accent-foreground': '240 5.9% 10%',
            '--destructive': '0 84.2% 60.2%',
            '--destructive-foreground': '0 0% 98%',
            '--border': '240 5.9% 90%',
            '--input': '240 5.9% 90%',
            '--ring': '346.8 77.2% 49.8%',
            '--radius': '0.5rem',
        },
        'dark': {
            '--background': '240 10% 3.9%',
            '--foreground': '0 0% 98%',
            '--card': '240 10% 3.9%',
            '--card-foreground': '0 0% 98%',
            '--primary': '346.8 77.2% 49.8%',
            '--primary-foreground': '355.7 100% 97.3%',
            '--secondary': '240 3.7% 15.9%',
            '--secondary-foreground': '0 0% 98%',
            '--muted': '240 3.7% 15.9%',
            '--muted-foreground': '240 5% 64.9%',
            '--accent': '240 3.7% 15.9%',
            '--accent-foreground': '0 0% 98%',
            '--destructive': '0 62.8% 30.6%',
            '--destructive-foreground': '0 0% 98%',
            '--border': '240 3.7% 15.9%',
            '--input': '240 3.7% 15.9%',
            '--ring': '346.8 77.2% 49.8%',
        }
    },
    'orange': {
        'light': {
            '--background': '0 0% 100%',
            '--foreground': '20 14.3% 4.1%',
            '--card': '0 0% 100%',
            '--card-foreground': '20 14.3% 4.1%',
            '--primary': '24.6 95% 53.1%',
            '--primary-foreground': '60 9.1% 97.8%',
            '--secondary': '60 4.8% 95.9%',
            '--secondary-foreground': '24 9.8% 10%',
            '--muted': '60 4.8% 95.9%',
            '--muted-foreground': '25 5.3% 44.7%',
            '--accent': '60 4.8% 95.9%',
            '--accent-foreground': '24 9.8% 10%',
            '--destructive': '0 84.2% 60.2%',
            '--destructive-foreground': '60 9.1% 97.8%',
            '--border': '20 5.9% 90%',
            '--input': '20 5.9% 90%',
            '--ring': '24.6 95% 53.1%',
            '--radius': '0.5rem',
        },
        'dark': {
            '--background': '20 14.3% 4.1%',
            '--foreground': '60 9.1% 97.8%',
            '--card': '20 14.3% 4.1%',
            '--card-foreground': '60 9.1% 97.8%',
            '--primary': '20.5 90.2% 48.2%',
            '--primary-foreground': '60 9.1% 97.8%',
            '--secondary': '12 6.5% 15.1%',
            '--secondary-foreground': '60 9.1% 97.8%',
            '--muted': '12 6.5% 15.1%',
            '--muted-foreground': '24 5.4% 63.9%',
            '--accent': '12 6.5% 15.1%',
            '--accent-foreground': '60 9.1% 97.8%',
            '--destructive': '0 62.8% 30.6%',
            '--destructive-foreground': '60 9.1% 97.8%',
            '--border': '12 6.5% 15.1%',
            '--input': '12 6.5% 15.1%',
            '--ring': '20.5 90.2% 48.2%',
        }
    }
}
PALETTES['emerald'] = PALETTES['green']


def _build_css_variables(palette_name: str) -> str:
    palette = PALETTES.get(palette_name.lower(), PALETTES['zinc'])
    light_vars = "\n        ".join(f"{k}: {v};" for k, v in palette['light'].items())
    dark_vars = "\n        ".join(f"{k}: {v};" for k, v in palette['dark'].items())
    return f"""
        :root {{
        {light_vars}
        }}
        .dark {{
        {dark_vars}
        }}
    """


def get_base_html(
    title: str,
    content: str,
    css_url: str,
    htmx_url: str = '/_pdu/static/htmx.min.js',
    htmx_version: str = '1.9.12',
    theme: str = 'light',
    palette: str = 'zinc',
    tailwind_config: Optional[Dict[str, Any]] = None,
    custom_css: Optional[str] = None,
    stylesheets: Optional[List[str]] = None,
    scripts: Optional[List[str]] = None,
    extra_head: Union[str, List[str]] = '',
    extra_body: str = '',
    csrf_token: str = "",
) -> str:
    """Generate the full HTML shell with HTMX, Tailwind, and theme customization."""
    theme_lower = theme.lower().strip()
    theme_class = 'dark' if theme_lower == 'dark' else ''
    
    # Auto system theme script if theme is 'auto' or 'system'
    system_theme_script = ""
    if theme_lower in ('auto', 'system'):
        system_theme_script = """
        <script>
            if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
                document.documentElement.classList.add('dark');
            }
        </script>
        """

    # Tailwind configuration
    base_tw_config = {
        'darkMode': 'class',
        'theme': {
            'extend': {
                'colors': {
                    'border': 'hsl(var(--border))',
                    'input': 'hsl(var(--input))',
                    'ring': 'hsl(var(--ring))',
                    'background': 'hsl(var(--background))',
                    'foreground': 'hsl(var(--foreground))',
                    'primary': {
                        'DEFAULT': 'hsl(var(--primary))',
                        'foreground': 'hsl(var(--primary-foreground))',
                    },
                    'secondary': {
                        'DEFAULT': 'hsl(var(--secondary))',
                        'foreground': 'hsl(var(--secondary-foreground))',
                    },
                    'destructive': {
                        'DEFAULT': 'hsl(var(--destructive))',
                        'foreground': 'hsl(var(--destructive-foreground))',
                    },
                    'muted': {
                        'DEFAULT': 'hsl(var(--muted))',
                        'foreground': 'hsl(var(--muted-foreground))',
                    },
                    'accent': {
                        'DEFAULT': 'hsl(var(--accent))',
                        'foreground': 'hsl(var(--accent-foreground))',
                    },
                    'card': {
                        'DEFAULT': 'hsl(var(--card))',
                        'foreground': 'hsl(var(--card-foreground))',
                    },
                },
                'borderRadius': {
                    'lg': 'var(--radius)',
                    'md': 'calc(var(--radius) - 2px)',
                    'sm': 'calc(var(--radius) - 4px)',
                },
            },
        },
    }

    if tailwind_config and isinstance(tailwind_config, dict):
        # Deep merge theme extensions
        if 'theme' in tailwind_config:
            if 'extend' in tailwind_config['theme']:
                base_tw_config['theme']['extend'].update(tailwind_config['theme']['extend'])
            for tk, tv in tailwind_config['theme'].items():
                if tk != 'extend':
                    base_tw_config['theme'][tk] = tv
        for k, v in tailwind_config.items():
            if k != 'theme':
                base_tw_config[k] = v

    tw_config_json = json.dumps(base_tw_config)
    css_variables = _build_css_variables(palette)
    user_css_block = f"\n/* Custom CSS */\n{custom_css}\n" if custom_css else ""

    # Extra stylesheets
    stylesheets_html = ""
    if stylesheets:
        stylesheets_html = "\n".join(f'<link rel="stylesheet" href="{sheet}">' for sheet in stylesheets)

    # Extra scripts
    scripts_html = ""
    if scripts:
        scripts_html = "\n".join(f'<script src="{sc}"></script>' for sc in scripts)

    # Extra head
    if isinstance(extra_head, (list, tuple)):
        extra_head_str = "\n".join(str(item) for item in extra_head)
    else:
        extra_head_str = str(extra_head or '')

    return f'''<!DOCTYPE html>
<html lang="en" class="{theme_class}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="pdu-csrf-token" content="{csrf_token}">
    <title>{title}</title>
    {system_theme_script}
    <!-- Tailwind CSS Play CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {tw_config_json};
    </script>
    <style>
        {css_variables}
        * {{ border-color: hsl(var(--border)); }}
        body {{ background-color: hsl(var(--background)); color: hsl(var(--foreground)); font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
        .htmx-indicator {{ opacity: 0; transition: opacity 200ms ease-in; }}
        .htmx-request .htmx-indicator {{ opacity: 1; }}
        .htmx-request.htmx-indicator {{ opacity: 1; }}
        {user_css_block}
    </style>
    <!-- HTMX -->
    <script src="{htmx_url}" onerror="this.onerror=null;this.src='https://cdn.jsdelivr.net/npm/htmx.org@{htmx_version}/dist/htmx.min.js'"></script>
    <!-- PyDataUI CSS -->
    <link rel="stylesheet" href="{css_url}">
    {stylesheets_html}
    {extra_head_str}
</head>
<body class="min-h-screen" hx-headers='{json.dumps({"X-CSRF-Token": csrf_token})}'>
    <div id="pdu-root" class="min-h-screen">
        {content}
    </div>
    {scripts_html}
    {extra_body}
</body>
</html>'''


def get_fragment_html(content: str) -> str:
    """Generate HTML fragment for HTMX partial updates."""
    return content
