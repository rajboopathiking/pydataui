def get_base_html(title: str, content: str, css_url: str, htmx_url: str = '/_pdu/static/htmx.min.js',
                  htmx_version: str = '1.9.12', theme: str = 'light', extra_head: str = '', extra_body: str = '') -> str:
    """Generate the full HTML shell with HTMX and Tailwind loaded."""
    theme_class = 'dark' if theme == 'dark' else ''
    return f'''<!DOCTYPE html>
<html lang="en" class="{theme_class}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <!-- Tailwind CSS Play CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        border: 'hsl(var(--border))',
                        input: 'hsl(var(--input))',
                        ring: 'hsl(var(--ring))',
                        background: 'hsl(var(--background))',
                        foreground: 'hsl(var(--foreground))',
                        primary: {{
                            DEFAULT: 'hsl(var(--primary))',
                            foreground: 'hsl(var(--primary-foreground))',
                        }},
                        secondary: {{
                            DEFAULT: 'hsl(var(--secondary))',
                            foreground: 'hsl(var(--secondary-foreground))',
                        }},
                        destructive: {{
                            DEFAULT: 'hsl(var(--destructive))',
                            foreground: 'hsl(var(--destructive-foreground))',
                        }},
                        muted: {{
                            DEFAULT: 'hsl(var(--muted))',
                            foreground: 'hsl(var(--muted-foreground))',
                        }},
                        accent: {{
                            DEFAULT: 'hsl(var(--accent))',
                            foreground: 'hsl(var(--accent-foreground))',
                        }},
                        card: {{
                            DEFAULT: 'hsl(var(--card))',
                            foreground: 'hsl(var(--card-foreground))',
                        }},
                    }},
                    borderRadius: {{
                        lg: 'var(--radius)',
                        md: 'calc(var(--radius) - 2px)',
                        sm: 'calc(var(--radius) - 4px)',
                    }},
                }},
            }},
        }};
    </script>
    <style>
        :root {{
            --background: 0 0% 100%;
            --foreground: 222.2 84% 4.9%;
            --card: 0 0% 100%;
            --card-foreground: 222.2 84% 4.9%;
            --primary: 222.2 47.4% 11.2%;
            --primary-foreground: 210 40% 98%;
            --secondary: 210 40% 96.1%;
            --secondary-foreground: 222.2 47.4% 11.2%;
            --muted: 210 40% 96.1%;
            --muted-foreground: 215.4 16.3% 46.9%;
            --accent: 210 40% 96.1%;
            --accent-foreground: 222.2 47.4% 11.2%;
            --destructive: 0 84.2% 60.2%;
            --destructive-foreground: 210 40% 98%;
            --border: 214.3 31.8% 91.4%;
            --input: 214.3 31.8% 91.4%;
            --ring: 222.2 84% 4.9%;
            --radius: 0.5rem;
        }}
        .dark {{
            --background: 222.2 84% 4.9%;
            --foreground: 210 40% 98%;
            --card: 222.2 84% 4.9%;
            --card-foreground: 210 40% 98%;
            --primary: 210 40% 98%;
            --primary-foreground: 222.2 47.4% 11.2%;
            --secondary: 217.2 32.6% 17.5%;
            --secondary-foreground: 210 40% 98%;
            --muted: 217.2 32.6% 17.5%;
            --muted-foreground: 215 20.2% 65.1%;
            --accent: 217.2 32.6% 17.5%;
            --accent-foreground: 210 40% 98%;
            --destructive: 0 62.8% 30.6%;
            --destructive-foreground: 210 40% 98%;
            --border: 217.2 32.6% 17.5%;
            --input: 217.2 32.6% 17.5%;
            --ring: 212.7 26.8% 83.9%;
        }}
        * {{ border-color: hsl(var(--border)); }}
        body {{ background-color: hsl(var(--background)); color: hsl(var(--foreground)); font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
        .htmx-indicator {{ opacity: 0; transition: opacity 200ms ease-in; }}
        .htmx-request .htmx-indicator {{ opacity: 1; }}
        .htmx-request.htmx-indicator {{ opacity: 1; }}
    </style>
    <!-- HTMX -->
    <script src="{htmx_url}" onerror="this.onerror=null;this.src='https://cdn.jsdelivr.net/npm/htmx.org@{htmx_version}/dist/htmx.min.js'"></script>
    <!-- PyDataUI CSS -->
    <link rel="stylesheet" href="{css_url}">
    {extra_head}
</head>
<body class="min-h-screen">
    <div id="pdu-root" class="min-h-screen">
        {content}
    </div>
    {extra_body}
</body>
</html>'''

def get_fragment_html(content: str) -> str:
    """Generate HTML fragment for HTMX partial updates."""
    return content
