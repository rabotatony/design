import re
import sys
import json
import math

# apply.py — applies a generated design system to an existing project's
# globals.css. Supports shadcn/Tailwind-4 oklch, legacy HSL triplets, and hex.
# Only known variables are touched; everything else stays exactly as-is.

VAR_MAP = {
    "--background": "surface",
    "--foreground": "text",
    "--card": "surface",
    "--card-foreground": "text",
    "--popover": "surface_alt",
    "--popover-foreground": "text",
    "--primary": "primary",
    "--primary-foreground": "surface",
    "--secondary": "surface_alt",
    "--secondary-foreground": "text",
    "--muted": "surface_alt",
    "--muted-foreground": "text_muted",
    "--accent": "accent",
    "--accent-foreground": "surface",
    "--destructive": "error",
    "--destructive-foreground": "text",
    "--border": "border",
    "--input": "border",
    "--ring": "primary",
    "--success": "success",
    "--warning": "warning",
    "--error": "error",
}


def _hex_channels(hex_color):
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def hex_to_oklch(hex_color):
    r0, g0, b0 = _hex_channels(hex_color)

    def s2l(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = s2l(r0), s2l(g0), s2l(b0)
    l_ = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m_ = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s_ = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_c, m_c, s_c = l_ ** (1 / 3), m_ ** (1 / 3), s_ ** (1 / 3)
    L = 0.2104542553 * l_c + 0.7936177850 * m_c - 0.0040720468 * s_c
    a = 1.9779984951 * l_c - 2.4285922050 * m_c + 0.4505937099 * s_c
    bb = 0.0259040371 * l_c + 0.7827717662 * m_c - 0.8086757660 * s_c
    C = (a ** 2 + bb ** 2) ** 0.5
    Hh = math.degrees(math.atan2(bb, a)) % 360
    return "oklch(" + str(round(L, 4)) + " " + str(round(C, 4)) + " " + str(round(Hh, 2)) + ")"


def hex_to_hsl_triplet(hex_color):
    import colorsys
    r0, g0, b0 = _hex_channels(hex_color)
    h, l, s = colorsys.rgb_to_hls(r0 / 255.0, g0 / 255.0, b0 / 255.0)
    return str(round(h * 360)) + " " + str(round(s * 100)) + "% " + str(round(l * 100)) + "%"


def _detect_format(value):
    if "oklch" in value:
        return "oklch"
    if "%" in value and "#" not in value:
        return "hsl"
    return "hex"


def _format_color(hex_color, fmt):
    if fmt == "oklch":
        return hex_to_oklch(hex_color)
    if fmt == "hsl":
        return hex_to_hsl_triplet(hex_color)
    return hex_color


def apply_to_globals_css(css_text, design):
    palette = design["palette"]
    radius_md = design.get("radius", {}).get("md", 10)
    changes = []

    def replace_var(match):
        name = match.group(1)
        old = match.group(2).strip()
        if name == "--radius":
            new = str(round(radius_md / 16, 3)) + "rem"
            if old != new:
                changes.append({"var": name, "from": old, "to": new})
            return name + ": " + new + ";"
        token = VAR_MAP.get(name)
        if not token or token not in palette:
            return match.group(0)
        fmt = _detect_format(old)
        new = _format_color(palette[token], fmt)
        if old != new:
            changes.append({"var": name, "from": old, "to": new, "token": token})
        return name + ": " + new + ";"

    result = re.sub(r"(--[a-z][a-z0-9-]*)\s*:\s*([^;]+);", replace_var, css_text)

    notes = []
    typ = design.get("typography", {})
    fams = []
    for role in ("display", "heading", "body", "mono"):
        if role in typ:
            fam = typ[role].get("family")
            if fam and fam not in fams:
                fams.append(fam)
    if fams:
        parts = ["family=" + f.replace(" ", "+") + ":wght@400;500;600;700" for f in fams]
        import_line = "@import url('https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap');"
        result = import_line + "\n" + result
        notes.append("Google Fonts @import added: " + ", ".join(fams))
    notes.append("--font-sans and next/font variables untouched — update layout.tsx to switch fonts fully.")
    notes.append("Dark-first palette applied to every block (:root and .dark look the same by design).")

    report = {
        "concept": design.get("concept"),
        "variables_changed": len(changes),
        "changes": changes,
        "notes": notes,
    }
    return result, report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: apply.py <design.json> < globals.css > globals.new.css")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        design = json.load(f)
    css_in = sys.stdin.read()
    css_out, report = apply_to_globals_css(css_in, design)
    sys.stdout.write(css_out)
    print(json.dumps(report, indent=2), file=sys.stderr)
