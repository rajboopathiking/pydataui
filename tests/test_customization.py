import pytest
from pydataui import App, Component, Html, RawHtml
from pydataui.html import Div, Span, Section, Header, Footer, Nav, Svg, Path, P, H1, H2, A, Main, FormTag, InputTag, ButtonTag
from pydataui.components.shadcn import ShadButton, ShadCard, ShadCardTitle, ShadCardContent, ShadBadge

def test_html_tags_rendering():
    elem = Section(
        Header(
            Nav(
                Span("Logo", class_name="font-bold text-lg"),
                class_name="flex justify-between items-center"
            ),
            class_name="border-b"
        ),
        Main(
            H1("Welcome to PyDataUI", class_name="text-3xl font-extrabold"),
            P("Building reactive apps in Python.", class_name="text-muted-foreground mt-2"),
            A("Get Started", href="/start", class_name="text-primary underline"),
            class_name="p-8"
        ),
        Footer(
            P("© 2026 PyDataUI", class_name="text-xs text-center"),
            class_name="border-t p-4"
        ),
        class_name="min-h-screen bg-background"
    )
    rendered = elem.render()
    assert "<section" in rendered
    assert "<header" in rendered
    assert "<nav" in rendered
    assert "<span" in rendered
    assert "Logo" in rendered
    assert "<main" in rendered
    assert "<h1" in rendered
    assert "Welcome to PyDataUI" in rendered
    assert "<a " in rendered
    assert 'href="/start"' in rendered
    assert "<footer" in rendered

def test_svg_rendering():
    icon = Svg(
        Path(d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"),
        viewBox="0 0 24 24",
        class_name="w-6 h-6 text-indigo-500"
    )
    rendered = icon.render()
    assert '<svg' in rendered
    assert 'viewBox="0 0 24 24"' in rendered
    assert '<path' in rendered
    assert 'd="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"' in rendered
    assert 'text-indigo-500' in rendered

def test_raw_html_embedding():
    raw = Html('<div class="custom-badge"><svg viewBox="0 0 10 10"></svg><span>Live</span></div>')
    rendered = raw.render()
    assert '<div class="custom-badge"><svg viewBox="0 0 10 10"></svg><span>Live</span></div>' in rendered

def test_boolean_attributes_handling():
    inp_enabled = InputTag(type="text", placeholder="Type here", disabled=False, value="")
    rendered_enabled = inp_enabled.render()
    assert 'disabled' not in rendered_enabled
    assert 'placeholder="Type here"' in rendered_enabled
    assert 'value=""' in rendered_enabled

    inp_disabled = InputTag(type="text", disabled=True, required=True)
    rendered_disabled = inp_disabled.render()
    assert ' disabled' in rendered_disabled or 'disabled="disabled"' in rendered_disabled
    assert ' required' in rendered_disabled or 'required="required"' in rendered_disabled

def test_app_theme_and_palette_rendering():
    app = App(
        title="Custom Palette App",
        theme="dark",
        palette="violet",
        tailwind_config={
            "theme": {
                "extend": {
                    "colors": {
                        "brand": "#ff5722"
                    }
                }
            }
        },
        custom_css="body { font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11'; }",
        stylesheets=["https://fonts.googleapis.com/css2?family=Fira+Code&display=swap"],
        scripts=["https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"],
        head="<meta name='author' content='PyDataUI Team'>"
    )

    @app.page("/")
    def index():
        return Div("Hello Violet Dark Theme", class_name="text-brand font-mono")

    html_page = app._renderer.render_page(index, {})
    assert 'class="dark"' in html_page
    assert '262.1 83.3% 57.8%' in html_page  # violet primary token
    assert '"brand": "#ff5722"' in html_page  # custom tailwind extension
    assert "font-feature-settings" in html_page  # custom css
    assert "fonts.googleapis.com" in html_page  # stylesheet
    assert "canvas-confetti" in html_page  # script
    assert "PyDataUI Team" in html_page  # extra head tag


@pytest.mark.anyio
async def test_protected_page_redirects_browser_to_login():
    from pydataui import AuthManager
    from pydataui.auth import LoginPage

    app = App()
    auth = AuthManager()
    auth.add_user("admin", "secret123")
    app.setup_auth(auth)

    @app.page("/login")
    def login_page():
        return LoginPage()

    @app.page("/protected")
    def secret_view():
        return "Protected Data"

    # API / non-browser request receives 401
    status, _, _ = await app._engine.dispatch_request("GET", "/protected", "", {}, "")
    assert status == 401

    # Browser request receives 303 Redirect to /login
    status, _, headers = await app._engine.dispatch_request(
        "GET", "/protected", "", {"accept": "text/html,application/xhtml+xml"}, ""
    )
    assert status == 303
    assert headers["location"] == "/login?next=/protected"

