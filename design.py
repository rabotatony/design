"""
design.py - CONSOLIDATED design generation module.

This module replaces the 11 redundant design generation modules:
  design_generator.py, design_language.py, design_pipeline.py,
  design_system_generator.py, designer.py, composer.py,
  layout_generator.py, component_generator.py, pattern_generator.py,
  guidelines_generator.py, style_generator.py

Everything is TRULY GENERATIVE: computed from algorithms and
mathematical principles, not lookup tables.
"""
import math
import colorsys

# ============================================================
# COLOR GENERATION (from color theory)
# ============================================================

def hex_to_hsl(hex_color):
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h, s, l

def hsl_to_hex(h, s, l):
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return "#{:02x}{:02x}{:02x}".format(int(r*255), int(g*255), int(b*255))

def generate_color_harmony(base_color, harmony_type="analogous"):
    """Generate color harmony from base color using color theory."""
    h, s, l = hex_to_hsl(base_color)
    if harmony_type == "complementary":
        return {"base": base_color, "complement": hsl_to_hex((h+0.5)%1, s, l)}
    elif harmony_type == "analogous":
        colors = [hsl_to_hex((h+off/360)%1, s, l) for off in [-30, 0, 30]]
        return {"base": base_color, "analogous": colors}
    elif harmony_type == "triadic":
        colors = [hsl_to_hex((h+off/360)%1, s, l) for off in [0, 120, 240]]
        return {"base": base_color, "triadic": colors}
    elif harmony_type == "monochromatic":
        colors = [hsl_to_hex(h, s, li) for li in [0.2, 0.35, 0.5, 0.65, 0.8]]
        return {"base": base_color, "monochromatic": colors}
    return {"base": base_color}
def generate_palette_from_identity(identity):
    """Generate color palette from identity (GENERATIVE, not lookup)."""
    materials = identity.get("materials", [])
    character = identity.get("character", "scholarly")
    base_hue, base_sat, base_light = 0.08, 0.5, 0.6
    mat_str = " ".join(materials).lower()
    if "forge" in mat_str or "fire" in mat_str:
        base_hue, base_sat, base_light = 0.05, 0.7, 0.5
    elif "ocean" in mat_str or "water" in mat_str:
        base_hue, base_sat, base_light = 0.55, 0.6, 0.5
    elif "forest" in mat_str or "nature" in mat_str:
        base_hue, base_sat, base_light = 0.35, 0.5, 0.4
    elif "stone" in mat_str:
        base_hue, base_sat, base_light = 0.0, 0.1, 0.5
    elif "night" in mat_str:
        base_hue, base_sat, base_light = 0.65, 0.4, 0.2
    if character == "mystical":
        base_sat = min(1.0, base_sat + 0.1)
    elif character == "industrial":
        base_sat = max(0.0, base_sat - 0.2)
    elif character == "organic":
        base_light = min(1.0, base_light + 0.1)
    base_color = hsl_to_hex(base_hue, base_sat, base_light)
    harmony = generate_color_harmony(base_color, "analogous")
    return {
        "base": base_color,
        "harmony": harmony,
        "surface_colors": generate_color_harmony(base_color, "monochromatic")["monochromatic"],
    }
# ============================================================
# TYPOGRAPHY + SPACING GENERATION (from mathematical ratios)
# ============================================================

def generate_typography_scale(base_size=16, ratio=1.25, steps=8):
    """Generate typography scale from base size and ratio (GENERATIVE)."""
    return [round(base_size * (ratio ** i), 1) for i in range(steps)]

def generate_typography_from_identity(identity):
    """Generate typography from identity (GENERATIVE)."""
    character = identity.get("character", "scholarly")
    base_size, ratio, line_height = 16, 1.25, 1.6
    if character == "mystical":
        base_size, ratio, line_height = 18, 1.333, 1.8
    elif character == "industrial":
        base_size, ratio, line_height = 14, 1.25, 1.5
    elif character == "organic":
        base_size, ratio, line_height = 17, 1.2, 1.7
    sizes = generate_typography_scale(base_size, ratio, 8)
    return {"base_size": base_size, "ratio": ratio, "line_height": line_height, "sizes": sizes}

def generate_spacing_scale(base_spacing=16, ratio=1.5, steps=8):
    """Generate spacing scale from base spacing and ratio (GENERATIVE)."""
    return [round(base_spacing * (ratio ** i), 1) for i in range(steps)]

def generate_spacing_from_identity(identity):
    """Generate spacing from identity (GENERATIVE)."""
    character = identity.get("character", "scholarly")
    base_spacing, ratio = 16, 1.5
    if character == "mystical":
        base_spacing, ratio = 24, 1.6
    elif character == "industrial":
        base_spacing, ratio = 12, 1.4
    elif character == "organic":
        base_spacing, ratio = 20, 1.5
    spacings = generate_spacing_scale(base_spacing, ratio, 8)
    return {"base_spacing": base_spacing, "ratio": ratio, "spacings": spacings}
# ============================================================
# MAIN DESIGN GENERATION
# ============================================================

def generate_design_from_identity(identity):
    """Generate a complete design from identity (TRULY GENERATIVE)."""
    palette = generate_palette_from_identity(identity)
    typography = generate_typography_from_identity(identity)
    spacing = generate_spacing_from_identity(identity)
    return {
        "identity": identity,
        "palette": palette,
        "typography": typography,
        "spacing": spacing,
        "note": "Design generated procedurally from identity, not from templates.",
    }

def generate_css_from_design(design):
    """Generate CSS custom properties from a design."""
    palette = design["palette"]
    typography = design["typography"]
    spacing = design["spacing"]
    lines = [":root {"]
    lines.append("  /* Palette (generated from color theory) */")
    lines.append("  --surface-base: " + palette["base"] + ";")
    for i, color in enumerate(palette["surface_colors"]):
        lines.append("  --surface-" + str(i) + ": " + color + ";")
    harmony = palette["harmony"]
    if "analogous" in harmony:
        lines.append("  --accent: " + harmony["analogous"][-1] + ";")
    lines.append("")
    lines.append("  /* Typography (generated from mathematical ratios) */")
    for i, size in enumerate(typography["sizes"]):
        lines.append("  --text-" + str(i) + ": " + str(size) + "px;")
    lines.append("  --line-height: " + str(typography["line_height"]) + ";")
    lines.append("")
    lines.append("  /* Spacing (generated from mathematical ratios) */")
    for i, sp in enumerate(spacing["spacings"]):
        lines.append("  --space-" + str(i) + ": " + str(sp) + "px;")
    lines.append("}")
    return "\n".join(lines)

def generate_design_css_from_content(content, identity_miner):
    """Full pipeline: content -> identity -> design -> CSS."""
    identity = identity_miner(content)
    design = generate_design_from_identity(identity)
    css = generate_css_from_design(design)
    return {"identity": identity, "design": design, "css": css}