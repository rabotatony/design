import json
from redesigner import diagnose, redesign, parse_css


def test_diagnosis_detects_generic():
    d = diagnose({
        "colors": {"primary": "#7B2FF7", "secondary": "#2196F3", "accent": "#FF6B9D"},
        "fonts": {"heading": "Poppins", "body": "Inter"},
        "effects": ["glassmorphism", "gradient-text"],
        "radius": "12px",
    })
    assert d["genericity_score"] > 0.6, d
    assert len(d["problems"]) >= 3, d
    assert d["verdict"] == "ai_likely", d


def test_diagnosis_passes_human():
    d = diagnose({
        "colors": {"primary": "#A0522D", "secondary": "#F5E6D3", "accent": "#4A6741"},
        "fonts": {"heading": "Fraunces", "body": "Karla"},
        "effects": [],
    })
    assert d["genericity_score"] < 0.3, d
    assert d["verdict"] in ("human_likely", "uncertain"), d


def test_redesign_improves():
    result = redesign({
        "colors": {"primary": "#7B2FF7", "secondary": "#2196F3", "accent": "#FF6B9D"},
        "fonts": {"heading": "Poppins", "body": "Inter"},
        "effects": ["glassmorphism", "gradient-text"],
        "radius": "12px",
    }, "fintech dashboard")
    assert result["improvement"]["genericity_before"] > 0.6, result["improvement"]
    assert result["improvement"]["genericity_after"] < 0.3, result["improvement"]
    assert result["improvement"]["delta"] < -0.3, result["improvement"]


def test_redesign_replaces_fonts():
    result = redesign({
        "colors": {"primary": "#7B2FF7", "secondary": "#2196F3"},
        "fonts": {"heading": "Poppins", "body": "Inter"},
        "effects": ["glassmorphism"],
    }, "warm and precise")
    fonts = result["redesigned"]["fonts"]
    assert "Poppins" not in fonts.values(), fonts
    assert "Inter" not in fonts.values(), fonts


def test_redesign_removes_effects():
    result = redesign({
        "colors": {"primary": "#7B2FF7"},
        "fonts": {"heading": "Poppins"},
        "effects": ["glassmorphism", "gradient-text", "neon-glow"],
    })
    effects = result["redesigned"]["effects"]
    assert "glassmorphism" not in effects, effects
    assert "gradient-text" not in effects, effects
    assert "neon-glow" not in effects, effects


def test_redesign_adds_tension():
    result = redesign({
        "colors": {"primary": "#7B2FF7"},
        "fonts": {"heading": "Poppins"},
        "effects": ["glassmorphism"],
    })
    assert "tension_elements" in result["redesigned"]
    assert len(result["redesigned"]["tension_elements"]) >= 2, result["redesigned"]["tension_elements"]


def test_css_parsing():
    css = ":root { --primary: #7B2FF7; --secondary: #2196F3; --font-heading: 'Poppins'; --font-body: 'Inter'; --radius: 12px; }"
    design = parse_css(css)
    assert design is not None
    assert design["colors"]["primary"] == "#7B2FF7", design["colors"]
    assert design["fonts"]["heading"] == "Poppins", design["fonts"]
