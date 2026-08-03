import re
import json
import random
import numpy as np
from PIL import Image
from detector import AI_PALETTES, detect_palette
from designer import extract_concept, generate_design, GENERIC_FONTS, _hex_to_rgb, _rgb_to_hex, _shift_hue

GENERIC_FONTS_EXT = GENERIC_FONTS + ["SF Pro", "Helvetica Neue", "Arial", "Lato", "Nunito"]
AI_EFFECTS = ["glassmorphism", "neumorphism", "gradient-text", "neon-glow",
              "generic-bokeh", "particle-overlay", "aurora-background"]
HUMAN_EFFECTS = ["film-grain", "subtle-shadow", "border-accent"]


def _color_dist(c1, c2):
    r1, g1, b1 = _hex_to_rgb(c1)
    r2, g2, b2 = c2
    return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5


def _match_ai_palette(hex_color):
    rgb = _hex_to_rgb(hex_color)
    best_name, best_dist = None, 9.0
    for name, pal in AI_PALETTES.items():
        for c in pal:
            d = _color_dist(hex_color, c)
            if d < best_dist:
                best_dist, best_name = d, name
    return best_name, best_dist


def diagnose(input_design):
    problems = []
    score = 0
    colors = input_design.get("colors", {})
    for key, hex_val in colors.items():
        if not isinstance(hex_val, str) or not hex_val.startswith("#"):
            continue
        name, dist = _match_ai_palette(hex_val)
        if dist < 0.15:
            problems.append({"element": f"colors.{key}", "issue": f"matches AI palette {name}", "severity": "high"})
            score += 0.15
    fonts = input_design.get("fonts", {})
    for key, font in fonts.items():
        if font in GENERIC_FONTS_EXT:
            problems.append({"element": f"fonts.{key}", "issue": f"{font} is a generic AI font", "severity": "high"})
            score += 0.12
    effects = input_design.get("effects", [])
    if isinstance(effects, str):
        effects = [effects]
    for i, eff in enumerate(effects):
        if eff in AI_EFFECTS:
            problems.append({"element": f"effects[{i}]", "issue": f"{eff} is an AI trend", "severity": "medium"})
            score += 0.08
    radius = input_design.get("radius")
    if isinstance(radius, (str, int)) and radius not in (None, ""):
        problems.append({"element": "radius", "issue": f"uniform {radius} everywhere", "severity": "low"})
        score += 0.05
    spacing = input_design.get("spacing_base")
    if spacing:
        try:
            base = int(re.search(r"\d+", str(spacing)).group())
            if base > 12:
                problems.append({"element": "spacing_base", "issue": f"{base}px too spacious (AI loves whitespace)", "severity": "low"})
                score += 0.04
        except (AttributeError, ValueError):
            pass
    score = min(score, 1.0)
    verdict = "ai_likely" if score > 0.5 else "human_likely" if score < 0.3 else "uncertain"
    return {"genericity_score": round(score, 2), "problems": problems, "verdict": verdict}


def _infer_concept(input_design):
    colors = input_design.get("colors", {})
    for key in ("primary", "accent", "secondary"):
        hex_val = colors.get(key, "")
        if hex_val.startswith("#"):
            r, g, b = _hex_to_rgb(hex_val)
            if b > r and b > g:
                return "workbench"
            if r > 0.7 and b > 0.4:
                return "craft"
    return "craft"


def _palette_image(colors, size=100):
    keys = [k for k in ("primary", "secondary", "accent", "tension") if k in colors]
    if not keys:
        keys = [k for k in colors if colors[k].startswith("#") and k not in ("surface", "surface_alt", "border", "text", "text_muted", "background")][:4]
    if not keys:
        keys = list(colors.keys())[:4]
    n = max(len(keys), 1)
    img = np.zeros((size, size, 3))
    for i, k in enumerate(keys):
        rgb = _hex_to_rgb(colors[k])
        img[i * size // n:(i + 1) * size // n] = rgb
    return img


def _validate_palette(colors):
    import tempfile, os
    img = _palette_image(colors)
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    Image.fromarray((img * 255).astype(np.uint8)).save(path)
    try:
        return detect_palette(path)["score"]
    finally:
        os.unlink(path)


def redesign(input_design, brief_hint=None):
    random.seed(42)
    diagnosis = diagnose(input_design)
    if brief_hint:
        concept = extract_concept({"feeling": brief_hint, "project": brief_hint})
    else:
        concept = _infer_concept(input_design)
    new_design = generate_design({"project": brief_hint or "redesign", "feeling": brief_hint or concept})
    fallback_concepts = ["craft", "clay", "ember", "workbench", "tide"]
    for attempt in range(5):
        gen_score = _validate_palette(new_design["palette"])
        if gen_score < 0.3:
            break
        if attempt < 3:
            new_design["palette"]["primary"] = _shift_hue(new_design["palette"]["primary"], 25)
            new_design["palette"]["accent"] = _shift_hue(new_design["palette"]["accent"], 25)
        else:
            fb = fallback_concepts[attempt - 3]
            new_design = generate_design({"project": brief_hint or "redesign", "feeling": fb})
    redesigned = {
        "colors": new_design["palette"],
        "fonts": {
            "heading": new_design["typography"]["display"]["family"],
            "body": new_design["typography"]["body"]["family"],
            "mono": new_design["typography"]["mono"]["family"],
        },
        "radius": {"cards": f"{new_design['radius']['md']}px", "buttons": f"{new_design['radius']['sm']}px"},
        "spacing_base": f"{new_design['spacing']['base']}px",
        "spacing_scale": [f"{s}px" for s in new_design["spacing"]["scale"]],
        "effects": ["film-grain" if new_design["effects"]["grain"] else "subtle-shadow", "border-accent"],
        "tension_elements": [
            new_design["radius"]["tension"],
            new_design["spacing"]["tension"],
            new_design["effects"]["tension"],
        ],
    }
    changes = []
    old_colors = input_design.get("colors", {})
    for key in ("primary", "secondary", "accent"):
        if key in old_colors and key in redesigned["colors"]:
            changes.append(f"{key.capitalize()}: {old_colors[key]} → {redesigned['colors'][key]}")
    old_fonts = input_design.get("fonts", {})
    for key in ("heading", "body"):
        if key in old_fonts:
            changes.append(f"{key.capitalize()} font: {old_fonts[key]} → {redesigned['fonts'][key]}")
    removed = [e for e in (input_design.get("effects", []) if isinstance(input_design.get("effects"), list) else []) if e in AI_EFFECTS]
    if removed:
        changes.append(f"Removed: {', '.join(removed)}")
    changes.append(f"Added: {', '.join(redesigned['effects'])}")
    changes.append(f"Radius: uniform → cards {redesigned['radius']['cards']} / buttons {redesigned['radius']['buttons']}")
    css_lines = [":root {"]
    for k, v in redesigned["colors"].items():
        css_lines.append(f"  --color-{k}: {v};")
    for k, v in redesigned["fonts"].items():
        css_lines.append(f"  --font-{k}: '{v}', sans-serif;")
    css_lines.append(f"  --radius-cards: {redesigned['radius']['cards']};")
    css_lines.append(f"  --radius-buttons: {redesigned['radius']['buttons']};")
    css_lines.append(f"  --spacing-base: {redesigned['spacing_base']};")
    css_lines.append("}")
    return {
        "original": input_design,
        "diagnosis": diagnosis,
        "redesigned": redesigned,
        "css_variables": "\n".join(css_lines),
        "changes_summary": changes,
        "improvement": {
            "genericity_before": diagnosis["genericity_score"],
            "genericity_after": round(gen_score, 2),
            "delta": round(gen_score - diagnosis["genericity_score"], 2),
        },
    }


def parse_css(css_text):
    design = {"colors": {}, "fonts": {}, "effects": []}
    for m in re.finditer(r"--(?:color-)?([\w-]+)\s*:\s*([^;]+);", css_text):
        key, val = m.group(1).lower().strip(), m.group(2).strip()
        if val.startswith("#"):
            design["colors"][key.replace("-", "_")] = val
        elif "font" in key:
            font = val.strip("'\"").split(",")[0].strip()
            role = "heading" if "head" in key or "display" in key else "body" if "body" in key else "mono" if "mono" in key else "body"
            design["fonts"][role] = font
    rm = re.search(r"--radius\s*:\s*(\d+)px", css_text)
    if rm:
        design["radius"] = f"{rm.group(1)}px"
    sm = re.search(r"--spacing-base\s*:\s*(\d+)px", css_text)
    if sm:
        design["spacing_base"] = f"{sm.group(1)}px"
    if not design["colors"] and not design["fonts"]:
        return None
    return design


if __name__ == "__main__":
    import sys
    inp = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
    brief = sys.argv[2] if len(sys.argv) > 2 else None
    print(json.dumps(redesign(inp, brief), indent=2))
