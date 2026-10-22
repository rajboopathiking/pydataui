import importlib.util
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
GENERATOR = PROJECT / "examples" / "generate_data_team_gallery.py"
STATIC_GALLERY = PROJECT / "docs" / "examples" / "data-team-gallery.html"


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "data_team_gallery_generator", GENERATOR
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_data_team_gallery_is_deterministic_and_complete():
    generator = _load_generator()

    generator._deterministic_ids()
    first = generator.build_gallery()
    generator._deterministic_ids()
    second = generator.build_gallery()

    assert first == second
    assert first.count('<section class="gallery-sample"') == 4
    for sample in generator.SAMPLES:
        assert f'id="{sample["id"]}"' in first
        assert generator.escape_html(sample["title"]) in first
        assert sample["role"] in first
    assert "Low-code pages for data professionals" in first
    assert "cdn.tailwindcss.com" in first
    assert "cdn.jsdelivr.net/npm/chart.js" in first
    assert "Data Quality &amp; Catalog" in first
    assert "warehouse_daily" in first
    assert "churn_classifier" in first


def test_checked_in_gallery_is_current_and_complete():
    assert STATIC_GALLERY.is_file()
    html = STATIC_GALLERY.read_text(encoding="utf-8")
    assert html.count('<section class="gallery-sample"') == 4
    assert "Data Team Template Gallery" in html
    assert "examples/generate_data_team_gallery.py" in html
    assert html.count("pdu-gallery-") > 20
