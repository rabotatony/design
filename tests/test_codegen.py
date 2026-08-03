import io
import zipfile
import codegen
from codegen import generate_components, generate_zip, generate_all

SAMPLE = {
    "concept": "workbench",
    "palette": {
        "primary": "#2D5A27", "secondary": "#E8D5B7", "accent": "#C44536",
        "tension": "#8B8000", "surface": "#1A1A2E", "surface_alt": "#232340",
        "text": "#E8E4DC", "text_muted": "#9B968E", "border": "#3A3A52",
        "success": "#4A7C59", "warning": "#B8860B", "error": "#A63D40",
    },
    "typography": {
        "display": {"family": "Space Grotesk", "weight": 500, "tracking": "-0.02em"},
        "heading": {"family": "Space Grotesk", "weight": 600, "tracking": "-0.01em"},
        "body": {"family": "IBM Plex Sans", "weight": 400, "tracking": "0.01em"},
        "mono": {"family": "IBM Plex Mono", "weight": 400, "tracking": "0.02em"},
        "tension_rule": "headings lowercase, body sentence case",
    },
    "spacing": {
        "base": 8, "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
        "tension": "section spacing asymmetric: 96px top, 64px bottom",
    },
    "radius": {"sm": 6, "md": 10, "lg": 16, "tension": "cards 10px, buttons 6px"},
    "effects": {
        "shadow": "0 1px 3px rgba(0,0,0,0.4)", "grain": True, "grain_amount": 0.03,
        "border_style": "1px solid", "tension": "one element uses 2px border",
    },
}


def test_generates_all_files():
    files = generate_components(SAMPLE)
    assert len(files) == 10
    assert ":root {" in files["tokens.css"]
    assert "export" in files["components/Button.tsx"]
    assert "variant" in files["components/Button.tsx"]
    assert "tension" in files["components/Card.tsx"]


def test_zip_creation():
    zb = generate_zip(SAMPLE)
    zf = zipfile.ZipFile(io.BytesIO(zb))
    names = zf.namelist()
    assert len(names) == 10
    assert len(zb) > 1024
    assert any("tokens.css" in n for n in names)
    assert any("Button.tsx" in n for n in names)


def test_button_uses_tokens():
    files = generate_components(SAMPLE)
    btn = files["components/Button.tsx"]
    assert "var(--color-primary)" in btn
    assert "var(--radius-sm)" in btn


def test_showcase_renders_all():
    files = generate_components(SAMPLE)
    sc = files["showcase.tsx"]
    for comp in ("Button", "Card", "Input", "Alert", "Nav", "Hero"):
        assert "<" + comp in sc, f"showcase missing <{comp}"


def test_readme_exists():
    files = generate_components(SAMPLE)
    rm = files["README.md"]
    assert "Anti-AI" in rm
    assert "Component" in rm


def test_total_lines_reasonable():
    files = generate_components(SAMPLE)
    total = sum(len(c.splitlines()) for c in files.values())
    assert total < 800, f"total lines {total} >= 800"
    result = generate_all(SAMPLE)
    assert result["file_count"] == 10
    assert result["concept"] == "workbench"
    assert len(result["zip_base64"]) > 0
