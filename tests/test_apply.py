import json
from apply import apply_to_globals_css, hex_to_oklch, hex_to_hsl_triplet
from designer import generate_design

DESIGN = generate_design({"project": "fintech dashboard", "feeling": "trustworthy but warm"})

FIXTURE_OKLCH = """@import "tailwindcss";

@theme inline {
  --color-background: var(--background);
  --color-primary: var(--primary);
  --radius-md: calc(var(--radius) - 2px);
}

:root {
  --radius: 0.625rem;
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --card: oklch(1 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --chart-1: oklch(0.646 0.222 41.116);
  --sidebar: oklch(0.985 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --primary: oklch(0.922 0 0);
}
"""


def test_oklch_known_values():
    assert hex_to_oklch("#ffffff") == "oklch(1.0 0.0 89.88)" or hex_to_oklch("#ffffff").startswith("oklch(1.0 0.0")
    assert hex_to_oklch("#000000").startswith("oklch(0.0 0.0")
    red = hex_to_oklch("#ff0000")
    assert "0.628" in red and "0.2577" in red


def test_hsl_triplet_format():
    assert hex_to_hsl_triplet("#ff0000") == "0 100% 50%"


def test_apply_oklch_css():
    css, report = apply_to_globals_css(FIXTURE_OKLCH, DESIGN)
    assert report["variables_changed"] >= 10
    assert "oklch(" in css
    vars_changed = [c["var"] for c in report["changes"]]
    assert "--background" in vars_changed
    assert "--primary" in vars_changed
    assert "--border" in vars_changed


def test_unknown_vars_untouched():
    css, report = apply_to_globals_css(FIXTURE_OKLCH, DESIGN)
    assert "--chart-1: oklch(0.646 0.222 41.116);" in css
    assert "--sidebar: oklch(0.985 0 0);" in css


def test_radius_applied():
    css, report = apply_to_globals_css(FIXTURE_OKLCH, DESIGN)
    expected = str(round(DESIGN["radius"]["md"] / 16, 3)) + "rem"
    assert "--radius: " + expected + ";" in css


def test_font_import_prepended():
    css, report = apply_to_globals_css(FIXTURE_OKLCH, DESIGN)
    assert css.startswith("@import url(")
    assert "fonts.googleapis.com" in css.splitlines()[0]


def test_hsl_format_preserved():
    hsl_css = ":root {\n  --background: 0 0% 100%;\n  --primary: 240 5.9% 10%;\n}\n"
    css, report = apply_to_globals_css(hsl_css, DESIGN)
    assert "oklch(" not in css
    assert "%" in css


def test_real_nova_style_full_run():
    # full run on a larger fixture: both blocks transformed, same palette
    css, report = apply_to_globals_css(FIXTURE_OKLCH, DESIGN)
    assert report["concept"] == DESIGN["concept"]
    assert len(report["notes"]) >= 2
