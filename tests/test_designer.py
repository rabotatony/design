import json
import numpy as np
from PIL import Image
import designer
from designer import (
    extract_concept, generate_palette, generate_typography,
    generate_system, generate_design, to_css_variables, CONCEPT_PALETTES, FONT_PAIRS,
)


def test_concept_extraction():
    assert extract_concept({"feeling": "trustworthy but warm"}) in ["workbench", "anchor", "bedrock"]
    concept = extract_concept({"feeling": "modern clean approach"})
    assert concept not in ["modern", "clean"]
    assert extract_concept({"project": "unknown thing"}) == "craft"


def test_palette_not_generic():
    import tempfile, os
    from detector import detect_palette
    for concept in CONCEPT_PALETTES:
        pal = generate_palette(concept, {"constraints": ["dark mode"]})
        colors = ["primary", "secondary", "accent", "tension", "surface", "text"]
        img = np.zeros((100, 100, 3))
        for i, key in enumerate(colors):
            rgb = designer._hex_to_rgb(pal[key])
            img[i * 100 // len(colors):(i + 1) * 100 // len(colors)] = rgb
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        Image.fromarray((img * 255).astype(np.uint8)).save(path)
        try:
            result = detect_palette(path)
            assert result["score"] < 0.4, f"{concept}: score {result['score']} too high"
        finally:
            os.unlink(path)


def test_no_generic_fonts():
    generic = ["Inter", "Poppins", "Montserrat", "Roboto", "Open Sans"]
    for concept in FONT_PAIRS:
        typ = generate_typography(concept, {})
        assert typ["display"]["family"] not in generic, f"{concept}: {typ['display']['family']}"


def test_tension_exists():
    design = generate_design({"project": "test app", "feeling": "calm and precise"})
    assert "tension_rule" in design["typography"]
    assert design["typography"]["tension_rule"]
    for key in ("spacing", "radius", "effects"):
        assert "tension" in design[key]
        assert design[key]["tension"]


def test_css_output_valid():
    design = generate_design({"project": "test", "feeling": "bold"})
    css = to_css_variables(design)
    assert css.startswith(":root {")
    assert "--color-primary:" in css
    assert "--font-display:" in css


def test_full_generation():
    design = generate_design({"project": "fintech dashboard", "feeling": "trustworthy but warm"})
    required = {"concept", "palette", "typography", "spacing", "radius", "effects", "anti_ai_validation"}
    assert set(design.keys()) >= required
    assert len(design["palette"]) == 12
    assert design["anti_ai_validation"]["genericity_score"] < 0.5
    assert design["anti_ai_validation"]["has_concept"]
    assert design["anti_ai_validation"]["has_tension_element"]
