"""
color_system_generator.py — generates color harmony schemes from a design language.

Extends design generation to include color harmony schemes:
  - Complementary colors
  - Analogous colors
  - Triadic colors
  - Split-complementary colors
  - Monochromatic shades

The key: color harmonies are derived from the base color, not picked from templates.
"""

def hex_to_hsl(hex_color):
    # Handle None/empty/invalid input gracefully
    if hex_color is None or not isinstance(hex_color, str):
        return 0.0, 0.0, 0.5  # default: gray
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return 0.0, 0.0, 0.5  # default: gray
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    l = (max_c + min_c) / 2
    if max_c == min_c:
        h = s = 0
    else:
        d = max_c - min_c
        s = d / (2 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        if max_c == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_c == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return h, s, l

def hsl_to_hex(h, s, l):
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    if s == 0:
        r = g = b = l
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))

def generate_complementary(base_color):
    h, s, l = hex_to_hsl(base_color)
    comp_h = (h + 0.5) % 1
    return hsl_to_hex(comp_h, s, l)

def generate_analogous(base_color, angle=30):
    h, s, l = hex_to_hsl(base_color)
    colors = []
    for offset in [-angle, 0, angle]:
        new_h = (h + offset / 360) % 1
        colors.append(hsl_to_hex(new_h, s, l))
    return colors

def generate_triadic(base_color):
    h, s, l = hex_to_hsl(base_color)
    colors = []
    for offset in [0, 120, 240]:
        new_h = (h + offset / 360) % 1
        colors.append(hsl_to_hex(new_h, s, l))
    return colors

def generate_monochromatic(base_color, steps=5):
    h, s, l = hex_to_hsl(base_color)
    colors = []
    for i in range(steps):
        new_l = l * (i + 1) / steps
        colors.append(hsl_to_hex(h, s, new_l))
    return colors

def derive_color_harmony(design_language):
    palette = design_language.get("dimensions", {}).get("palette", {})
    accent = palette.get("accent", "#8a5a2b")
    return {
        "base": accent,
        "complementary": generate_complementary(accent),
        "analogous": generate_analogous(accent),
        "triadic": generate_triadic(accent),
        "monochromatic": generate_monochromatic(accent),
    }


if __name__ == "__main__":
    design_language = {
        "dimensions": {
            "palette": {"accent": "#8a5a2b"},
        },
    }
    harmony = derive_color_harmony(design_language)
    print("Color Harmony:")
    print("  base:", harmony["base"])
    print("  complementary:", harmony["complementary"])
    print("  analogous:", harmony["analogous"])
    print("  triadic:", harmony["triadic"])
    print("  monochromatic:", harmony["monochromatic"])
