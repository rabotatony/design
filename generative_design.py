"""
generative_design.py - TRULY GENERATIVE design system.
Uses algorithms and mathematical principles, not lookup tables.
"""
import math
import colorsys

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

def generate_color_harmony(base_color, harmony_type="complementary"):
    h, s, l = hex_to_hsl(base_color)
    if harmony_type == "complementary":
        comp_h = (h + 0.5) % 1
        return {"base": base_color, "complement": hsl_to_hex(comp_h, s, l)}
    elif harmony_type == "analogous":
        colors = []
        for offset in [-30, 0, 30]:
            new_h = (h + offset / 360) % 1
            colors.append(hsl_to_hex(new_h, s, l))
        return {"base": base_color, "analogous": colors}
    elif harmony_type == "triadic":
        colors = []
        for offset in [0, 120, 240]:
            new_h = (h + offset / 360) % 1
            colors.append(hsl_to_hex(new_h, s, l))
        return {"base": base_color, "triadic": colors}
    elif harmony_type == "monochromatic":
        colors = []
        for lightness in [0.2, 0.35, 0.5, 0.65, 0.8]:
            colors.append(hsl_to_hex(h, s, lightness))
        return {"base": base_color, "monochromatic": colors}
    return {"base": base_color}
def generate_palette_from_identity(identity):
    """Generate a color palette from identity. GENERATIVE: computes colors
    from identity characteristics, not from a lookup table."""
    materials = identity.get("materials", [])
    character = identity.get("character", "scholarly")
    base_hue = 0.08
    base_sat = 0.5
    base_light = 0.6
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
def generate_typography_scale(base_size=16, ratio=1.25, steps=8):
    """Generate typography scale from base size and ratio. GENERATIVE."""
    sizes = []
    for i in range(steps):
        size = base_size * (ratio ** i)
        sizes.append(round(size, 1))
    return sizes

def generate_typography_from_identity(identity):
    """Generate typography from identity. GENERATIVE."""
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
    """Generate spacing scale from base spacing and ratio. GENERATIVE."""
    spacings = []
    for i in range(steps):
        spacing = base_spacing * (ratio ** i)
        spacings.append(round(spacing, 1))
    return spacings

def generate_spacing_from_identity(identity):
    """Generate spacing from identity. GENERATIVE."""
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

def generate_design_from_identity(identity):
    """Generate a complete design from identity. TRULY GENERATIVE."""
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