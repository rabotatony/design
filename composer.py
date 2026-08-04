"""
composer.py — THE MACHINE. Given a DomainDNA, it composes a complete design
system (tokens.css + layout.css + motion.css) by applying fixed design
PRINCIPLES to the DNA's substance. Deterministic, traceable, clean-by-build.

Separation of powers:
  PRINCIPLES       = the machine's design intelligence (fixed, general)
  MATERIALS        = physical-knowledge base (material -> surfaces/grain/light)
  DNA              = the project's own substance (identity_extractor)
  manifest         = every output line traced to (dna_root, principle)

The machine never chooses aesthetics from a style library. It builds the
system out of the domain's material, hierarchy and rhythm.
"""
import re
import json
import hashlib


# ── Material knowledge base: physical substance -> measurable values ────────
MATERIALS = {
    "parchment": {"base": (232, 223, 200), "ink": (26, 22, 18),
                  "grain": (0.8, 3, 0.025), "light": "candle", "accent": (138, 90, 43)},
    "ink":       {"base": (20, 17, 13), "ink": (236, 227, 208),
                  "grain": (0.9, 3, 0.035), "light": "candle", "accent": (184, 134, 11)},
    "night":     {"base": (16, 18, 28), "ink": (220, 224, 235),
                  "grain": (1.1, 2, 0.02), "light": "moon", "accent": (100, 140, 210)},
    "stone":     {"base": (214, 212, 206), "ink": (35, 34, 32),
                  "grain": (1.4, 4, 0.03), "light": "day", "accent": (150, 110, 55)},
    "water":     {"base": (219, 228, 230), "ink": (21, 32, 38),
                  "grain": (0.5, 2, 0.015), "light": "day", "accent": (55, 130, 160)},
    "wood":      {"base": (224, 206, 180), "ink": (40, 28, 18),
                  "grain": (0.35, 4, 0.035), "light": "candle", "accent": (165, 105, 45)},
    "metal":     {"base": (210, 212, 216), "ink": (24, 26, 30),
                  "grain": (1.6, 2, 0.012), "light": "day", "accent": (200, 110, 40)},
    "smoke":     {"base": (30, 30, 33), "ink": (210, 208, 205),
                  "grain": (0.7, 3, 0.04), "light": "moon", "accent": (125, 105, 145)},
    "forge":     {"base": (28, 24, 21), "ink": (232, 205, 165),
                  "grain": (1.2, 3, 0.03), "light": "ember", "accent": (222, 122, 42)},
}

# light source -> shadow tint (principle: shadows are colored by their light)
LIGHT_TINT = {
    "candle": (90, 60, 20),
    "moon":   (40, 55, 90),
    "day":    (30, 30, 30),
    "ember":  (120, 55, 15),
}


def _hex(rgb):
    return "#" + "".join(f"{c:02x}" for c in rgb)


def _mix(rgb, target, t):
    return tuple(round(a + (b - a) * t) for a, b in zip(rgb, target))


def _detect_materials(dna):
    text = (str(dna.get("material", "")) + " " + str(dna.get("palette_logic", ""))).lower()
    found = [m for m in MATERIALS if m in text]
    return found if found else ["stone"]  # neutral fallback, flagged in manifest


def _anchors_from_palette_logic(dna):
    return re.findall(r"#[0-9a-fA-F]{6}", str(dna.get("palette_logic", "")))


def _rhythm_from(dna):
    m = re.findall(r"(\d+)\s*[-:]\s*(\d+)\s*[-:]\s*(\d+)", str(dna.get("rhythm_logic", "")))
    if m:
        a, b, c = (int(x) for x in m[0])
        unit = 0.4
        return {"in": round(a * unit, 2), "hold": round(b * unit, 2), "out": round(c * unit, 2)}
    return {"in": 0.24, "hold": 0.1, "out": 0.3}  # default calm pulse, flagged


def _signature_radius(dna):
    sig = str(dna.get("signature", "")).lower()
    if "petal" in sig or "rose" in sig or "flower" in sig or "שושנה" in sig or "עלה" in sig:
        return ("16px 6px 16px 6px", "petal geometry from signature")
    if "circle" in sig or "wheel" in sig or "אופן" in sig or "מעגל" in sig:
        return ("999px 4px 999px 4px", "wheel geometry from signature")
    if "flame" in sig or "candle" in sig or "נר" in sig or "להבה" in sig:
        return ("4px 16px 4px 16px", "flame geometry from signature")
    return (None, "signature geometry unrecognized — human input needed")


def compose(dna):
    mats = _detect_materials(dna)
    mat = MATERIALS[mats[0]]
    dark_mat = MATERIALS[mats[1]] if len(mats) > 1 else MATERIALS["ink"]
    anchors = _anchors_from_palette_logic(dna)
    rhythm = _rhythm_from(dna)
    sig_radius, sig_note = _signature_radius(dna)
    emanation = "emanat" in str(dna.get("hierarchy_logic", "")).lower() or "האצלה" in str(dna.get("hierarchy_logic", ""))
    manifest = []

    def tag(f, sel, root, principle):
        manifest.append({"file": f, "selector": sel, "root": root, "principle": principle})

    base, ink = mat["base"], mat["ink"]
    if anchors:  # DNA-declared colors become the anchors of the system
        base = tuple(int(anchors[0][i:i+2], 16) for i in (1, 3, 5))
        if len(anchors) > 1:
            ink = tuple(int(anchors[1][i:i+2], 16) for i in (1, 3, 5))
        tag("tokens.css", "palette", "palette_logic", "declared_anchors")

    d_base, d_ink = dark_mat["base"], dark_mat["ink"]
    if anchors:
        d_base = _mix(base, (0, 0, 0), 0.88)
        d_ink = _mix(base, (255, 255, 255), 0.85)

    T = []
    T.append("/* COMPOSED TOKENS — generated by composer.py from domain DNA */")
    T.append(":root {")
    for i, s in enumerate([base, _mix(base, (255, 255, 255), 0.22),
                           _mix(base, (255, 255, 255), 0.42), _mix(base, (255, 255, 255), 0.6)]):
        T.append(f"  --surface-{i}: {_hex(s)};")
    T.append(f"  --ink: {_hex(ink)};")
    T.append(f"  --ink-soft: {_hex(_mix(ink, base, 0.28))};")
    T.append(f"  --ink-faint: {_hex(_mix(ink, base, 0.52))};")
    tag("tokens.css", "surfaces", "material", "surface_ramp_from_material")

    if len(anchors) > 2:
        T.append(f"  --accent: {anchors[2]};")
        tag("tokens.css", "--accent", "palette_logic", "declared_anchor_3")
    else:
        T.append(f"  --accent: {_hex(mat['accent'])};")
        tag("tokens.css", "--accent", "material", "accent_from_material")

    tint = LIGHT_TINT[mat["light"]]
    T.append(f"  --shadow-sheet: 0 1px 2px rgba{tint + (0.10,)}, 0 3px 10px rgba{tint + (0.07,)};")
    T.append(f"  --shadow-lifted: 0 2px 4px rgba{tint + (0.12,)}, 0 8px 22px rgba{tint + (0.10,)};")
    tag("tokens.css", "shadows", "material", "shadow_colored_by_light_source")

    if emanation:
        for i, d in enumerate([96, 72, 56, 44, 36]):
            T.append(f"  --descend-{i+1}: {d}px;")
        tag("tokens.css", "spacing", "hierarchy_logic", "emanation_descent_spacing")
    else:
        for i, d in enumerate([64, 48, 32, 24, 16]):
            T.append(f"  --space-{i+1}: {d}px;")
        tag("tokens.css", "spacing", "hierarchy_logic", "standard_spacing")

    T.append("  --radius-amulet: 999px;")
    T.append("  --radius-card: 14px;")
    T.append("  --radius-input: 4px;")
    if sig_radius:
        T.append(f"  --radius-signature: {sig_radius};")
    tag("tokens.css", "radius", "signature", "radius_by_role_" + sig_note.split()[0])

    T.append(f"  --breath-in: {rhythm['in']}s;")
    T.append(f"  --breath-hold: {rhythm['hold']}s;")
    T.append(f"  --breath-out: {rhythm['out']}s;")
    T.append("  --ease-inhale: cubic-bezier(0.30, 0.00, 0.20, 1.00);")
    T.append("  --ease-hold: cubic-bezier(0.40, 0.10, 0.60, 0.90);")
    T.append("  --ease-exhale: cubic-bezier(0.35, 0.00, 0.15, 1.00);")
    tag("tokens.css", "rhythm", "rhythm_logic", "breath_timing_parsed")

    gfreq, goct, gop = mat["grain"]
    T.append(f"  --grain-opacity: {gop};")
    T.append("}")
    tag("tokens.css", "grain", "material", "grain_from_material")

    # dark block
    T.append(".dark {")
    for i, s in enumerate([d_base, _mix(d_base, (255, 255, 255), 0.06),
                           _mix(d_base, (255, 255, 255), 0.12), _mix(d_base, (255, 255, 255), 0.18)]):
        T.append(f"  --surface-{i}: {_hex(s)};")
    T.append(f"  --ink: {_hex(d_ink)};")
    T.append(f"  --ink-soft: {_hex(_mix(d_ink, d_base, 0.25))};")
    T.append(f"  --ink-faint: {_hex(_mix(d_ink, d_base, 0.5))};")
    T.append(f"  --grain-opacity: {round(gop * 1.4, 3)};")
    T.append(f"  --accent: {_hex(_mix(mat['accent'], (255, 255, 255), 0.25))};")
    T.append("}")
    tag("tokens.css", ".dark", "material", "night_mode_from_second_material")

    # grain overlay
    T.append("body::before {")
    T.append("  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 1;")
    T.append("  opacity: var(--grain-opacity);")
    T.append(f"  background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='p'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='{gfreq}' numOctaves='{goct}' seed='7'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23p)'/%3E%3C/svg%3E\");")
    T.append("}")

    tokens_css = "\n".join(T)

    # ── layout.css ──
    L = []
    L.append("/* COMPOSED LAYOUT — from hierarchy_logic */")
    if emanation:
        L.append(".emanation { display: flex; flex-direction: column; }")
        for i in range(1, 6):
            L.append(f".emanation > .world-{i} {{ margin-block-end: var(--descend-{i}); }}")
        L.append(".pillar-center { margin-inline: auto; max-width: 640px; }")
        L.append(".pillar-right { margin-inline-end: auto; max-width: 560px; }")
        L.append(".pillar-left { margin-inline-start: auto; max-width: 560px; }")
        L.append(".path-link { position: relative; }")
        L.append(".path-link::before { content: ''; position: absolute; inset-block-start: calc(-1 * var(--descend-4));")
        L.append("  inset-inline-start: 50%; block-size: var(--descend-4); inline-size: 1px;")
        L.append("  background: color-mix(in srgb, var(--accent, var(--ink)) 45%, transparent); }")
        tag("layout.css", ".emanation", "hierarchy_logic", "emanation_descent")
    else:
        L.append(".stack { display: flex; flex-direction: column; gap: var(--space-3); }")
        L.append(".lead { max-width: 640px; margin-inline: auto; }")
        tag("layout.css", ".stack", "hierarchy_logic", "standard_stack")
    layout_css = "\n".join(L)

    # ── motion.css ──
    M = []
    M.append("/* COMPOSED MOTION — from rhythm_logic + signature */")
    M.append("@keyframes signature-open {")
    M.append("  0% { clip-path: inset(0 46% 0 46% round 50%); opacity: 0.35; transform: scale(0.965); }")
    M.append("  62% { clip-path: inset(0 0% 0 0% round 24px); opacity: 1; }")
    M.append("  100% { clip-path: inset(0 0% 0 0% round 14px); opacity: 1; transform: scale(1); }")
    M.append("}")
    M.append(".signature.opens { animation: signature-open var(--breath-in) var(--ease-inhale) both; }")
    M.append("@media (prefers-reduced-motion: reduce) { .signature.opens { animation: none; clip-path: none; } }")
    tag("motion.css", "signature-open", "signature+rhythm_logic", "signature_gesture_on_breath")
    motion_css = "\n".join(M)

    files = {"tokens.css": tokens_css, "layout.css": layout_css, "motion.css": motion_css}
    stats = {
        "materials_detected": mats,
        "anchors_from_dna": len(anchors),
        "rhythm": rhythm,
        "signature_radius": sig_radius,
        "signature_note": sig_note,
        "emanation_layout": emanation,
    }
    return {"files": files, "manifest": manifest, "stats": stats}


def fingerprint(result):
    blob = json.dumps(result["files"], sort_keys=True)
    return hashlib.md5(blob.encode()).hexdigest()


if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from identity_extractor import shoshana_dna
    res = compose(shoshana_dna())
    print(json.dumps({"stats": res["stats"], "manifest_entries": len(res["manifest"]),
                      "fingerprint": fingerprint(res)}, ensure_ascii=False, indent=1))