"""
design_scan.py — scans CSS for AI design tells (registry signals, CSS layer).
Outputs a clean-score (0..1, higher = cleaner) + the tells found.
"""
import re
import json
import sys
import colorsys

FRAMEWORK_DEFAULTS = [
    "#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#ec4899", "#f43f5e",
    "#22c55e", "#ef4444", "#eab308", "#0ea5e9", "#14b8a6", "#f97316",
]
GENERIC_FONTS = ["Inter", "Poppins", "Montserrat", "Roboto", "Open Sans", "Lato", "Nunito"]


def scan_css(css):
    tells = []
    css_low = css.lower()

    # 1. framework default palette (exact hex match)
    hits = [h for h in FRAMEWORK_DEFAULTS if h in css_low]
    if hits:
        tells.append({"id": "color.default_palette", "w": 0.8, "evidence": hits[:4]})

    # 2. uniform radius: collect all border-radius values
    radii = re.findall(r"border-radius\s*:\s*([^;]+);", css_low)
    distinct = set(r.strip() for r in radii if r.strip())
    if len(radii) >= 3 and len(distinct) == 1:
        tells.append({"id": "layout.uniform_radius", "w": 0.8, "evidence": sorted(distinct)})

    # 3. glassmorphism
    if "backdrop-filter" in css_low and "blur(" in css_low:
        tells.append({"id": "mat.glassmorphism", "w": 0.75, "evidence": "backdrop-filter: blur"})

    # 4. neumorphism (dual opposing soft shadows on same-bg elements)
    if re.search(r"box-shadow\s*:[^;]*rgba\([^)]*\)\s*,\s*[^;]*rgba\([^)]*\)", css_low) and "neumorph" not in css_low:
        pass  # multi-shadow alone is not neumorphism; require light+dark pair
    nd = re.findall(r"(-?\d+)px\s+(-?\d+)px\s+\d+px\s+rgba\(255\s*,\s*255\s*,\s*255", css_low)
    if nd:
        tells.append({"id": "mat.neumorphism", "w": 0.6, "evidence": "white-highlight shadow"})

    # 5. no grain / no texture at all
    has_grain = any(k in css_low for k in ["feturbulence", "grain", "noise"] )
    if not has_grain:
        tells.append({"id": "mat.no_grain", "w": 0.8, "evidence": "no turbulence/grain/noise"})

    # 6. flat gray shadows only
    shadows = re.findall(r"box-shadow\s*:\s*([^;]+);", css_low)
    if shadows:
        all_gray = all(re.match(r"^[\s\d.,-]*rgba?\(0\s*,\s*0\s*,\s*0", s.strip()) for s in shadows)
        if all_gray:
            tells.append({"id": "mat.flat_shadow", "w": 0.6, "evidence": "all shadows rgba(0,0,0,x)"})

    # 7. generic fonts as the voice
    gf = [f for f in GENERIC_FONTS if re.search(r"\b" + re.escape(f) + r"\b", css, re.IGNORECASE)]
    if gf:
        tells.append({"id": "type.font_generic", "w": 0.9, "evidence": gf})

    # 8. generic gradient bands (purple->blue etc.)
    grads = re.findall(r"linear-gradient\s*\(([^;]+)\)", css_low)
    ai_grad = [g for g in grads if ("#7b2ff7" in g or "#2196f3" in g or "#ff6b9d" in g or "#ffa751" in g or "#00d2ff" in g)]
    if ai_grad:
        tells.append({"id": "color.gradient_generic", "w": 0.9, "evidence": ai_grad[:2]})

    # 9. aurora = 3+ LARGE radial blobs of DIFFERING hues.
    #    Starfields (tiny px dots) and warm glows/vignettes (one hue family) are not aurora.
    def _blob_colors(g):
        out = []
        for hx in re.findall(r"#[0-9a-f]{6}", g):
            out.append(tuple(int(hx[i:i+2], 16) for i in (0, 2, 4)))
        for rr in re.findall(r"rgba?\(([^)]+)\)", g):
            parts = [float(x) for x in re.findall(r"[\d.]+", rr)[:3]]
            if len(parts) == 3:
                out.append(tuple(int(p) for p in parts))
        return out
    def _hue(rgb):
        return colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)[0] * 360
    grads_all = re.findall(r"radial-gradient\s*\((?:[^()]*|\([^()]*\))*\)", css_low, re.S)
    blob_hues = []
    for g in grads_all:
        m = re.match(r"\s*radial-gradient\s*\(\s*(?:circle|ellipse)?\s*(\d+(?:\.\d+)?)(px|%)", g)
        is_large = (m is None) or (m.group(2) == "%" and float(m.group(1)) > 20)
        if not is_large:
            continue
        cols = _blob_colors(g)
        if cols:
            blob_hues.append(_hue(max(cols, key=lambda c: c[0]+c[1]+c[2])))
    if len(blob_hues) >= 3:
        spread = 0
        for i in range(len(blob_hues)):
            for j in range(i + 1, len(blob_hues)):
                d = abs(blob_hues[i] - blob_hues[j])
                spread = max(spread, min(d, 360 - d))
        if spread > 60 or "aurora" in css_low:
            tells.append({"id": "color.aurora_bg", "w": 0.85,
                          "evidence": f"{len(blob_hues)} large blobs, hue spread {spread:.0f}deg"})

    # 10. uniform easing on everything
    eases = re.findall(r"transition[^;]*?\b(ease[-\w]*)\b", css_low) + re.findall(r"animation[^;]*?\b(ease[-\w]*)\b", css_low)
    if len(eases) >= 3 and len(set(eases)) == 1:
        tells.append({"id": "motion.uniform_easing", "w": 0.6, "evidence": sorted(set(eases))})

    # clean score: 1 - weighted tell mass (capped)
    mass = sum(t["w"] for t in tells)
    clean = max(0.0, round(1 - mass / 4.0, 3))
    return {"clean_score": clean, "tells_found": len(tells), "tells": tells}


if __name__ == "__main__":
    css = open(sys.argv[1]).read()
    print(json.dumps(scan_css(css), ensure_ascii=False, indent=1))