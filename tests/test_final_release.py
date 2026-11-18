import pytest
import pydataui as pdu
from pydataui.dx import _default_page_components, session_state

def test_final_release_navbar():
    pdu.reset()
    nav = pdu.navbar(
        title="Acme Analytics",
        logo="🚀",
        links=[{"label": "Overview", "href": "/"}, {"label": "Logs", "href": "/logs"}],
        search=True,
        user={"name": "Alice", "role": "Admin"}
    )
    assert nav is not None
    html = nav.render({})
    assert "Acme Analytics" in html
    assert "Overview" in html
    assert "Alice" in html
    assert "Admin" in html
    assert "type='search'" in html or 'type="search"' in html

def test_final_release_breadcrumb():
    pdu.reset()
    bc = pdu.breadcrumb(["Home", "Clusters", "Node-04"])
    assert bc is not None
    html = bc.render({})
    assert "Home" in html
    assert "Clusters" in html
    assert "Node-04" in html

def test_final_release_media_image_video_audio():
    pdu.reset()
    img = pdu.image("https://example.com/photo.png", caption="Sample Photo", width=300)
    html_img = img.render({})
    assert "https://example.com/photo.png" in html_img
    assert "Sample Photo" in html_img

    vid = pdu.video("https://example.com/demo.mp4", caption="Demo Video")
    html_vid = vid.render({})
    assert "https://example.com/demo.mp4" in html_vid
    assert "Demo Video" in html_vid

    aud = pdu.audio("https://example.com/tune.mp3", caption="Audio Stream")
    html_aud = aud.render({})
    assert "https://example.com/tune.mp3" in html_aud
    assert "Audio Stream" in html_aud

def test_final_release_popover():
    pdu.reset()
    with pdu.popover("Filter Options", icon="⚙️"):
        pdu.text("Nested popover content")
    
    assert len(_default_page_components) >= 1
    html = _default_page_components[-1].render({})
    assert "Filter Options" in html
    assert "Nested popover content" in html

def test_final_release_tooltip_and_metric_help():
    pdu.reset()
    tt = pdu.tooltip("Detailed Help Text")
    html_tt = tt.render({})
    assert "Detailed Help Text" in html_tt

    m = pdu.metric("Throughput", "4.8k req/s", delta="+12%", help="Measured over 5-minute sliding window")
    html_m = m.render({})
    assert "Throughput" in html_m
    assert "Measured over 5-minute sliding window" in html_m

def test_final_release_write_stream():
    pdu.reset()
    def sample_token_stream():
        tokens = ["The ", "cluster ", "is ", "operating ", "normally."]
        for t in tokens:
            yield t

    full_response = pdu.write_stream(sample_token_stream, key="stream_out")
    assert full_response == "The cluster is operating normally."
    assert session_state["stream_out"] == "The cluster is operating normally."

def test_final_release_date_range_picker():
    pdu.reset()
    start, end = pdu.date_range_picker(
        "Quarter Range",
        value=("2026-01-01", "2026-03-31"),
        key="quarter_filter",
        help="Select calendar boundaries"
    )
    assert start == "2026-01-01"
    assert end == "2026-03-31"
    assert session_state["quarter_filter"] == ("2026-01-01", "2026-03-31")

def test_final_release_data_editor():
    pdu.reset()
    data = [
        {"model": "Llama-3.3", "vram_gb": 70, "status": "Ready"},
        {"model": "DeepSeek-R1", "vram_gb": 140, "status": "Running"}
    ]
    edited = pdu.data_editor(data, key="models_table")
    assert edited is not None
    assert len(edited) == 2
    html = _default_page_components[-1].render({})
    assert "Interactive Data Editor" in html
    assert "Llama-3.3" in html
    assert "DeepSeek-R1" in html
