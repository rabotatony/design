import sys
import json
import random
import colorsys
import numpy as np
from PIL import Image
from detector import detect_palette

FEELING_MAP = {
    "trust": ["workbench", "anchor", "bedrock"], "warm": ["clay", "ember", "linen"],
    "precise": ["caliper", "grid", "wire"], "bold": ["forge", "stamp", "anvil"],
    "calm": ["tide", "moss", "stone"], "fast": ["spark", "current", "pulse"],
    "premium": ["vault", "slate", "ingot"], "playful": ["confetti", "bounce", "pop"],
}
GENERIC_WORDS = {"corporate", "modern", "clean", "innovation", "synergy", "dynamic", "seamless", "elegant"}
GENERIC_FONTS = ["Inter", "Poppins", "Montserrat", "Roboto", "Open Sans"]

CONCEPT_PALETTES = {
    "workbench": {"primary": "#2D5A27", "secondary": "#E8D5B7", "accent": "#C44536", "tension": "#8B8000", "surface": "#1A1A2E", "text": "#E8E4DC"},
    "clay": {"primary": "#A0522D", "secondary": "#F5E6D3", "accent": "#4A6741", "tension": "#704214", "surface": "#1C1917", "text": "#EDE5DB"},
    "ember": {"primary": "#B7410E", "secondary": "#F0D9B5", "accent": "#2F4F4F", "tension": "#8B4513", "surface": "#1A1512", "text": "#E8DFD5"},
    "caliper": {"primary": "#36454F", "secondary": "#D4C5A9", "accent": "#B8860B", "tension": "#556B2F", "surface": "#141419", "text": "#DCD8D0"},
    "tide": {"primary": "#5F7A6A", "secondary": "#E0D8C8", "accent": "#8B6914", "tension": "#4A6670", "surface": "#151A1E", "text": "#D8D4CC"},
    "forge": {"primary": "#8B0000", "secondary": "#D2B48C", "accent": "#2F4F4F", "tension": "#B8860B", "surface": "#1A1210", "text": "#E0D8CC"},
    "vault": {"primary": "#2C3E50", "secondary": "#C0B283", "accent": "#722F37", "tension": "#4A4A4A", "surface": "#121218", "text": "#D8D4CC"},
    "craft": {"primary": "#5B4A3F", "secondary": "#E8DCC8", "accent": "#6B4423", "tension": "#556B2F", "surface": "#181512", "text": "#DCD5C8"},
}

FONT_PAIRS = {
    "workbench": {"display": "Space Grotesk", "body": "IBM Plex Sans", "mono": "IBM Plex Mono"},
    "clay": {"display": "Fraunces", "body": "Source Sans 3", "mono": "Source Code Pro"},
    "ember": {"display": "Playfair Display", "body": "Nunito Sans", "mono": "Fira Code"},
    "caliper": {"display": "Archivo", "body": "Inter", "mono": "JetBrains Mono"},
    "tide": {"display": "Lora", "body": "Karla", "mono": "Space Mono"},
    "forge": {"display": "Oswald", "body": "Roboto Slab", "mono": "IBM Plex Mono"},
    "vault": {"display": "Cormorant Garamond", "body": "Jost", "mono": "Fira Code"},
    "craft": {"display": "Bitter", "body": "Work Sans", "mono": "Space Mono"},
}

TENSION_RULES = {
    "workbench": "headings lowercase, body sentence case, numbers tabular",
    "clay": "body uses 15px instead of 16px", "ember": "line-height 1.4 instead of 1.5",
    "caliper": "letter-spacing -0.5px on buttons", "tide": "headings italic on first line only",
    "forge": "display uppercase, body sentence case", "vault": "small caps for labels",
    "craft": "body uses 15px, headings 17px",
}

SPACING_TENSION = {
    "workbench": "section spacing asymmetric: 96px top, 64px bottom",
    "forge": "section spacing asymmetric: 96px top, 64px bottom",
    "clay": "section spacing asymmetric: 80px top, 48px bottom",
    "tide": "section spacing asymmetric: 80px top, 48px bottom",
    "caliper": "section spacing symmetric: 64px top, 64px bottom — tension is elsewhere",
    "vault": "section spacing symmetric: 64px top, 64px bottom — tension is elsewhere",
    "craft": "section spacing asymmetric: 80px top, 48px bottom",
}

RADIUS_MAP = {
    "workbench": {"sm": 6, "md": 10, "lg": 16, "tension": "cards use 10px, buttons use 6px — deliberately different"},
    "clay": {"sm": 8, "md": 12, "lg": 20, "tension": "cards use 12px, buttons use 8px — deliberately different"},
    "caliper": {"sm": 2, "md": 4, "lg": 8, "tension": "cards use 4px, buttons use 2px — sharp, precise"},
    "tide": {"sm": 12, "md": 16, "lg": 24, "tension": "cards use 16px, buttons use 12px — soft, flowing"},
    "forge": {"sm": 4, "md": 8, "lg": 12, "tension": "cards use 8px, buttons use 4px — industrial"},
    "vault": {"sm": 4, "md": 8, "lg": 12, "tension": "cards use 8px, buttons use 4px — restrained"},
    "craft": {"sm": 6, "md": 10, "lg": 14, "tension": "cards use 10px, buttons use 6px — handmade feel"},
    "ember": {"sm": 8, "md": 12, "lg": 18, "tension": "cards use 12px, buttons use 8px — warm, rounded"},
}


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return [int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)]


def _rgb_to_hex(rgb):
    return "#" + "".join(f"{int(max(0,min(1,v))*255):02X}" for v in rgb)


def _saturation(hex_color):
    r, g, b = _hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return s


def _desaturate(hex_color, factor=0.85):
    r, g, b = _hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    s = min(s * factor, 0.85)
    return _rgb_to_hex(colorsys.hsv_to_rgb(h, s, v))


def _shift_hue(hex_color, degrees):
    r, g, b = _hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + degrees / 360.0) % 1.0
    return _rgb_to_hex(colorsys.hsv_to_rgb(h, s, v))


def extract_concept(brief):
    feeling = brief.get("feeling", "").lower()
    for word, concepts in FEELING_MAP.items():
        if word in feeling:
            return concepts[0]
    for word in GENERIC_WORDS:
        if word in feeling:
            continue
    project = brief.get("project", "").lower()
    domain_map = {"fintech": "vault", "finance": "vault", "tech": "caliper", "health": "tide",
                  "food": "clay", "art": "craft", "game": "forge", "education": "workbench"}
    for word, concept in domain_map.items():
        if word in project:
            return concept
    return "craft"


def generate_palette(concept, brief):
    pal = dict(CONCEPT_PALETTES.get(concept, CONCEPT_PALETTES["craft"]))
    constraints = brief.get("constraints", [])
    cons_str = " ".join(constraints).lower() if isinstance(constraints, list) else str(constraints).lower()
    if "light mode" in cons_str and "dark mode" not in cons_str:
        pal["surface"], pal["text"] = "#F5F0E8", "#1A1A2E"
    pal["surface_alt"] = _shift_hue(pal["surface"], 5)
    pal["text_muted"] = _desaturate(pal["text"], 0.6)
    pal["border"] = _shift_hue(pal["surface"], 10)
    pal["success"] = _desaturate("#4A7C59", 0.7)
    pal["warning"] = _desaturate("#B8860B", 0.7)
    pal["error"] = _desaturate("#A63D40", 0.7)
    for key in list(pal.keys()):
        if _saturation(pal[key]) > 0.85:
            pal[key] = _desaturate(pal[key], 0.85)
    return pal


def generate_typography(concept, brief):
    fonts = FONT_PAIRS.get(concept, FONT_PAIRS["craft"])
    if fonts["display"] in GENERIC_FONTS:
        fonts["display"] = FONT_PAIRS["craft"]["display"]
    disp_track = "-0.04em" if concept in ("caliper", "forge") else "-0.02em"
    return {
        "display": {"family": fonts["display"], "weight": 500, "tracking": disp_track},
        "heading": {"family": fonts["display"], "weight": 600, "tracking": "-0.01em"},
        "body": {"family": fonts["body"], "weight": 400, "tracking": "0.01em"},
        "mono": {"family": fonts["mono"], "weight": 400, "tracking": "0.02em"},
        "tension_rule": TENSION_RULES.get(concept, TENSION_RULES["craft"]),
    }


def generate_system(concept, brief):
    spacing = {
        "base": 8, "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
        "tension": SPACING_TENSION.get(concept, SPACING_TENSION["craft"]),
        "container": "max-width 1200px, padding-left 24px, padding-right 32px",
    }
    radius = dict(RADIUS_MAP.get(concept, RADIUS_MAP["craft"]))
    warm = concept in ("clay", "ember", "craft", "workbench")
    effects = {
        "shadow": "0 1px 3px rgba(0,0,0,0.4)",
        "grain": warm, "grain_amount": round(random.uniform(0.02, 0.04), 3) if warm else 0,
        "border_style": "1px solid",
        "tension": "one element uses 2px border instead of 1px",
    }
    return {"spacing": spacing, "radius": radius, "effects": effects}


def _palette_image(palette, size=100):
    colors = ["primary", "secondary", "accent", "tension", "surface", "text"]
    n = len(colors)
    img = np.zeros((size, size, 3))
    for i, key in enumerate(colors):
        rgb = _hex_to_rgb(palette[key])
        img[i * size // n:(i + 1) * size // n] = rgb
    return img


def validate_design(design):
    import tempfile, os
    pal = design["palette"]
    img = _palette_image(pal)
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    Image.fromarray((img * 255).astype(np.uint8)).save(path)
    try:
        result = detect_palette(path)
    finally:
        os.unlink(path)
    score = result["score"]
    fonts = design["typography"]
    font_generic = fonts["display"]["family"] in GENERIC_FONTS
    has_tension = all(design[k].get("tension") or design[k].get("tension_rule") for k in ("typography", "spacing", "radius", "effects"))
    return {
        "palette_distance_from_ai": round(1.0 - score, 2),
        "genericity_score": round(score, 2),
        "has_tension_element": has_tension,
        "has_concept": design.get("concept") not in GENERIC_WORDS and bool(design.get("concept")),
        "font_is_generic": font_generic,
    }


def generate_design(brief):
    random.seed(42)
    concept = extract_concept(brief)
    palette = generate_palette(concept, brief)
    typography = generate_typography(concept, brief)
    system = generate_system(concept, brief)
    design = {
        "concept": concept, "palette": palette, "typography": typography,
        "spacing": system["spacing"], "radius": system["radius"], "effects": system["effects"],
    }
    validation = validate_design(design)
    if validation["genericity_score"] > 0.4:
        for k in ("primary", "accent", "tension"):
            palette[k] = _shift_hue(palette[k], 15)
        design["palette"] = palette
        validation = validate_design(design)
    if validation["font_is_generic"]:
        typography["display"]["family"] = FONT_PAIRS["craft"]["display"]
        design["typography"] = typography
        validation = validate_design(design)
    design["anti_ai_validation"] = validation
    return design


def to_css_variables(design):
    lines = [":root {"]
    for key, val in design["palette"].items():
        lines.append(f"  --color-{key}: {val};")
    for role in ("display", "heading", "body", "mono"):
        fam = design["typography"][role]["family"]
        lines.append(f"  --font-{role}: '{fam}', sans-serif;")
    for key, val in design["radius"].items():
        if isinstance(val, (int, float)):
            lines.append(f"  --radius-{key}: {val}px;")
    lines.append(f"  --spacing-base: {design['spacing']['base']}px;")
    lines.append("}")
    return "\n".join(lines)


def to_tailwind_config(design):
    pal = design["palette"]
    typ = design["typography"]
    rad = design["radius"]
    return json.dumps({
        "theme": {
            "extend": {
                "colors": {k: v for k, v in pal.items()},
                "fontFamily": {r: [typ[r]["family"]] for r in ("display", "heading", "body", "mono")},
                "borderRadius": {k: f"{v}px" for k, v in rad.items() if isinstance(v, (int, float))},
                "spacing": {str(d): f"{d}px" for d in design["spacing"]["scale"]},
            }
        }
    }, indent=2)


def to_json(design):
    return json.dumps(design, indent=2)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: designer.py \'{"project":"...","feeling":"..."}\' [--css|--tailwind|--all]')
        sys.exit(1)
    brief = json.loads(sys.argv[1])
    design = generate_design(brief)
    fmt = sys.argv[2] if len(sys.argv) > 2 else None
    if fmt == "--css":
        print(to_css_variables(design))
    elif fmt == "--tailwind":
        print(to_tailwind_config(design))
    elif fmt == "--all":
        print(to_json(design))
        print("\n---\n")
        print(to_css_variables(design))
        print("\n---\n")
        print(to_tailwind_config(design))
    else:
        print(to_json(design))
