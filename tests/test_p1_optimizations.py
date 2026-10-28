import pytest
import time
import gzip
from pydataui import App, State, AppConfig
from pydataui.components import Button, Input, Container, Heading, Card
from pydataui.components.shadcn import ShadSelect, ShadCheckbox


class ProfileState(State):
    username: str = "alice"
    bio: str = "Engineer"
    likes: int = 42

    def update_bio(self, new_bio: str = "Architect"):
        self.bio = new_bio

    def like(self):
        self.likes += 1


def test_lazy_imports_pep_562():
    """Verify PEP 562 lazy loading in pydataui."""
    import pydataui
    
    # Check that dir(pydataui) includes key symbols
    d = dir(pydataui)
    assert 'App' in d
    assert 'State' in d
    assert 'button' in d
    assert 'ConcurrencyError' in d
    assert '__version__' in d

    # Access attributes lazily
    assert pydataui.App is not None
    assert pydataui.State is not None
    assert callable(pydataui.button)
    assert issubclass(pydataui.ConcurrencyError, Exception)

    # Invalid attribute raises AttributeError
    with pytest.raises(AttributeError):
        _ = pydataui.NonExistentModuleSymbol123


def test_state_dirty_tracking():
    """Verify state variable dirty tracking."""
    state = ProfileState()
    assert not state.is_dirty()
    assert state.get_dirty_fields() == set()

    state.update_bio("Senior Architect")
    assert state.is_dirty()
    assert "bio" in state.get_dirty_fields()
    assert "likes" not in state.get_dirty_fields()

    state.like()
    assert state.get_dirty_fields() == {"bio", "likes"}

    state.clear_dirty()
    assert not state.is_dirty()
    assert state.get_dirty_fields() == set()


def test_minimal_payloads_no_global_hx_include():
    """Verify that buttons and general components do NOT have hx-include='#pdu-root'."""
    btn = Button("Click Me", on_click=ProfileState.like)
    rendered_btn = btn.render({})
    assert 'hx-post="/_pdu/event/ProfileState/like"' in rendered_btn
    assert 'hx-include="#pdu-root"' not in rendered_btn

    inp = Input(name="bio", on_change=ProfileState.update_bio)
    rendered_inp = inp.render({})
    assert 'hx-include="this"' in rendered_inp
    assert 'hx-include="#pdu-root"' not in rendered_inp

    chk = ShadCheckbox("Accept Terms", name="terms", on_change=ProfileState.like)
    rendered_chk = chk.render({})
    assert 'hx-include="this"' in rendered_chk
    assert 'hx-include="#pdu-root"' not in rendered_chk

    sel = ShadSelect(name="theme", on_change=ProfileState.like)
    rendered_sel = sel.render({})
    assert 'hx-include="this"' in rendered_sel
    assert 'hx-include="#pdu-root"' not in rendered_sel


def test_targeted_event_handlers():
    """Verify EventHandler.target_to and EventSpec.target_to."""
    handler = ProfileState.like.target_to("#likes-counter")
    attrs = handler.get_htmx_attrs()
    assert attrs['hx-target'] == "#likes-counter"
    assert attrs['hx-swap'] == "innerHTML"

    spec = ProfileState.update_bio.with_args(new_bio="Chief Scientist").target_to("#bio-card", swap="outerHTML")
    spec_attrs = spec.get_htmx_attrs()
    assert spec_attrs['hx-target'] == "#bio-card"
    assert spec_attrs['hx-swap'] == "outerHTML"
    assert '"new_bio": "Chief Scientist"' in spec_attrs['hx-vals']


@pytest.mark.anyio
async def test_partial_ssr_re_render_and_dirty_headers():
    """Verify that targeting a component re-renders only that component and emits X-PDU-Dirty."""
    app = App(title="Test Partial SSR", debug=True)

    @app.page("/")
    def index():
        return Container(
            Heading("Dashboard", id="title-heading"),
            Card(
                Heading(ProfileState.likes, id="likes-count"),
                id="likes-card"
            ),
            Button("Like", id="like-btn", on_click=ProfileState.like.target_to("#likes-card")),
            id="main-container"
        )

    # 1. Initial page load
    s, b, h = await app._engine.dispatch_request('GET', '/', '', {}, '')
    assert s == 200
    assert 'Dashboard' in b
    assert 'id="likes-card"' in b
    cookie = h['set-cookie'].split(';', 1)[0]
    import re
    token = re.search(r'name="pdu-csrf-token" content="([^"]+)"', b).group(1)

    # 2. Fire targeted event to #likes-card
    event_headers = {
        'cookie': cookie,
        'x-csrf-token': token,
        'hx-target': '#likes-card',
        'hx-request': 'true',
    }
    s, b, h = await app._engine.dispatch_request(
        'POST',
        '/_pdu/event/ProfileState/like',
        '',
        event_headers,
        ''
    )
    assert s == 200
    # Targeted partial re-render should return only #likes-card, NOT #main-container or #title-heading!
    assert 'id="likes-card"' in b
    assert '43' in b
    assert 'Dashboard' not in b
    assert 'id="title-heading"' not in b

    # Check X-PDU-Dirty header
    assert 'x-pdu-dirty' in h
    assert 'likes' in h['x-pdu-dirty']


def test_mobile_mode_preset_config():
    """Verify that mobile_mode preset turns on gzip, turns off PWA boilerplate, and enables partial rendering."""
    cfg = AppConfig(mobile_mode=True)
    assert cfg.mobile_mode is True
    assert cfg.gzip is True
    assert cfg.pwa is False
    assert cfg.partial_re_render is True


@pytest.mark.anyio
async def test_mobile_mode_pwa_boilerplate_stripped():
    """Verify that in mobile_mode (pwa=False), PWA manifest and service worker tags are stripped."""
    app = App(title="Mobile App", mobile_mode=True)

    @app.page("/")
    def index():
        return Heading("Mobile View")

    s, b, h = await app._engine.dispatch_request('GET', '/', '', {}, '')
    assert s == 200
    assert 'Mobile View' in b
    assert 'manifest.json' not in b
    assert 'serviceWorker.register' not in b
    assert 'apple-mobile-web-app-capable' not in b


@pytest.mark.anyio
async def test_gzip_compression_on_mobile_mode():
    """Verify that responses are gzip compressed when GZip is active and Accept-Encoding allows it."""
    app = App(title="Gzip Test App", mobile_mode=True)

    @app.page("/")
    def index():
        # Large content to exceed 500 byte gzip threshold
        return Container(*[Heading(f"Data Item {i}") for i in range(100)])

    headers = {'accept-encoding': 'gzip'}
    s, b, h = await app._engine.dispatch_request('GET', '/', '', headers, '')
    assert s == 200
    assert h.get('content-encoding') == 'gzip'
    assert 'Data Item 0' in b
