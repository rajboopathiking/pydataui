def get_base_html(title: str, content: str, css_url: str, htmx_version: str = '1.9.12') -> str:
    """Generate the full HTML shell with HTMX loaded."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://unpkg.com/htmx.org@{htmx_version}"></script>
    <link rel="stylesheet" href="{css_url}">
</head>
<body>
    <div id="pdu-root">
        {content}
    </div>
</body>
</html>'''

def get_fragment_html(content: str) -> str:
    """Generate HTML fragment for HTMX partial updates."""
    return content
