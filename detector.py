import sys
import os
import json
import random
import numpy as np
from scipy.ndimage import uniform_filter, laplace, gaussian_filter, zoom
from sklearn.cluster import KMeans
from PIL import Image

AI_PALETTES = {
    "purple_blue": [[0.48, 0.18, 0.97], [0.13, 0.59, 0.95], [0.95, 0.95, 0.97]],
    "teal_orange": [[0.0, 0.82, 1.0], [1.0, 0.65, 0.32], [0.1, 0.1, 0.12]],
    "pink_purple": [[1.0, 0.42, 0.62], [0.48, 0.18, 0.97], [0.98, 0.94, 0.96]],
    "dark_neon":   [[0.05, 0.05, 0.1], [0.0, 1.0, 0.8], [1.0, 0.0, 0.5]],
    "soft_pastel": [[0.85, 0.75, 0.95], [0.75, 0.9, 0.95], [0.95, 0.85, 0.8]],
}

WEIGHTS = {
    # Recalibrated on a real 6-image sample (2 photoreal AI + 4 real photos):
    # noise_pattern is the ONLY reliable discriminator (AI 0.65-1.0 vs real ~0.05).
    # frequency_ceiling + metadata fire on BOTH real and AI (non-discriminative),
    # so they are dropped. HONEST NOTE: tuned on a small sample; the statistical
    # approach has a ceiling for photoreal AI — a trained model is the real fix.
    "frequency_ceiling": 0.00,
    "noise_pattern": 0.60,
    "palette": 0.20,
    "composition": 0.10,
    "texture_uniformity": 0.10,
    "metadata": 0.00,
}

AI_SOFTWARE_TAGS = [
    "stable diffusion", "comfyui", "diffusers", "midjourney",
    "dall-e", "openai", "novelai", "automatic1111", "fooocus", "invokeai",
]


def _load_gray(image_path):
    img = Image.open(image_path).convert("L")
    return np.asarray(img, dtype=float) / 255.0


def _load_rgb(image_path):
    img = Image.open(image_path).convert("RGB")
    return np.asarray(img, dtype=float) / 255.0


def detect_frequency_ceiling(image_path):
    gray = _load_gray(image_path)
    h, w = gray.shape
    if min(h, w) < 8:
        return {"score": 0.0, "detail": "image too small"}
    f = np.fft.fftshift(np.fft.fft2(gray))
    mag = np.abs(f)
    cy, cx = h // 2, w // 2
    y, x = np.ogrid[:h, :w]
    r = np.sqrt((y - cy) ** 2 + (x - cx) ** 2).astype(int)
    rmax = int(r.max())
    sums = np.bincount(r.ravel(), weights=mag.ravel())
    cnt = np.bincount(r.ravel())
    radial = sums / np.maximum(cnt, 1)
    radial = radial[1:] / (radial[1:].max() + 1e-10)
    n = len(radial)
    freqs = np.arange(n) / rmax
    lo_s, hi_s = slice(int(n * .05), int(n * .30)), slice(int(n * .50), int(n * .90))
    lo_sl = np.polyfit(freqs[lo_s], np.log(radial[lo_s] + 1e-10), 1)[0]
    hi_sl = np.polyfit(freqs[hi_s], np.log(radial[hi_s] + 1e-10), 1)[0]
    knee = abs(hi_sl) - abs(lo_sl)
    sf_high = radial[int(n * .60):int(n * .95)].mean() / (radial[int(n * .05):int(n * .40)].mean() + 1e-10)
    fullness = (radial[int(n * .05):int(n * .50)] > 0.01).mean()
    s_sharp = float(np.clip((knee - 5) / 10, 0, 1))
    s_flat = float(np.clip((0.20 - sf_high) / 0.15, 0, 1))
    if knee < 0:
        s_flat = min(s_flat, 0.5)
    score = max(s_sharp, s_flat)
    if fullness < 0.15:
        score = min(score, 0.35 if knee < 0 else 0.6)
    elif fullness < 0.3:
        score = min(score, 0.6)
    return {"score": float(score), "detail": f"knee_sharpness: {knee:.1f}, spectral_flatness_high: {sf_high:.3f}"}


def _noise_raw_mode(gray):
    if min(gray.shape) < 10:
        return {"score": 0.0, "detail": "image too small"}
    blurred = uniform_filter(gray, size=5)
    noise = gray - blurred
    b = blurred.ravel()
    n = noise.ravel()
    lo, hi = b.min(), b.max()
    if hi - lo < 1e-6:
        return {"score": 0.0, "detail": "flat image, no intensity range"}
    bins = np.linspace(lo, hi, 11)
    idx = np.clip(np.digitize(b, bins) - 1, 0, 9)
    means = np.zeros(10); vsum = np.zeros(10); cnt = np.zeros(10)
    np.add.at(means, idx, b)
    np.add.at(vsum, idx, n * n)
    np.add.at(cnt, idx, 1)
    means = means / np.maximum(cnt, 1)
    vars_ = vsum / np.maximum(cnt, 1)
    valid = cnt > 20
    if valid.sum() < 3:
        return {"score": 0.0, "detail": "insufficient bins"}
    corr = float(np.corrcoef(means[valid], vars_[valid])[0, 1])
    if np.isnan(corr):
        corr = 0.0
    score = float(np.clip((0.5 - corr) / 0.25, 0, 1))
    return {"score": score, "detail": f"Raw mode. intensity-variance corr: {corr:.2f}"}


def detect_noise_pattern(image_path):
    is_jpeg = image_path.lower().endswith((".jpg", ".jpeg"))
    if not is_jpeg:
        return _noise_raw_mode(_load_gray(image_path))
    rgb = _load_rgb(image_path)
    gray = rgb.mean(axis=2)
    h, w = gray.shape
    gy = np.abs(np.diff(gray, axis=0))
    gx = np.abs(np.diff(gray, axis=1))
    br = np.concatenate([gy[7::8, :].ravel(), gx[:, 7::8].ravel()]).mean()
    nb = np.concatenate([np.delete(gy, range(7, h - 1, 8), 0).ravel(),
                         np.delete(gx, range(7, w - 1, 8), 1).ravel()]).mean() + 1e-10
    block_ratio = float(br / nb)
    ycbcr = np.array(Image.fromarray((rgb * 255).astype(np.uint8)).convert("YCbCr"), dtype=float) / 255.0
    cb, cr, yl = ycbcr[:, :, 1], ycbcr[:, :, 2], ycbcr[:, :, 0]
    chroma_var = ((cb - uniform_filter(cb, 3)).var() + (cr - uniform_filter(cr, 3)).var()) / 2
    chroma_ratio = float(chroma_var / ((yl - uniform_filter(yl, 3)).var() + 1e-10))
    block_score = float(np.clip((block_ratio - 1.2) / 0.6, 0, 1))
    if chroma_ratio < 0.05:
        chroma_score = 0.0
    elif chroma_ratio > 0.3:
        chroma_score = float(np.clip((chroma_ratio - 0.3) / 0.5 + 0.5, 0, 1))
    else:
        chroma_score = float(np.clip((chroma_ratio - 0.05) / 0.25 * 0.5, 0, 0.5))
    score = float(max(block_score, chroma_score))
    return {"score": score, "detail": f"JPEG mode. block_ratio: {block_ratio:.2f}, chroma_ratio: {chroma_ratio:.3f}"}


def detect_palette(image_path):
    rgb = _load_rgb(image_path)
    px = rgb.reshape(-1, 3)
    n = len(px)
    rng = np.random.default_rng(0)
    if n > 5000:
        sample = px[rng.choice(n, 5000, replace=False)]
    else:
        sample = px
    uniq = np.unique(sample, axis=0)
    nc = max(1, min(5, len(uniq)))
    km = KMeans(n_clusters=nc, n_init=3, random_state=0).fit(sample)
    centers = km.cluster_centers_
    best_name, best_dist = None, 9.0
    for name, pal in AI_PALETTES.items():
        pal = np.asarray(pal)
        d = np.min(np.linalg.norm(centers[:, None, :] - pal[None, :, :], axis=2), axis=1).mean()
        if d < best_dist:
            best_dist, best_name = float(d), name
    score = float(np.clip((0.4 - best_dist) / 0.25, 0, 1))
    return {"score": score, "detail": f"closest cluster: {best_name}, dist {best_dist:.2f}"}


def detect_composition(image_path):
    gray = _load_gray(image_path)
    g = gray.astype(float)
    sd = g.std() + 1e-10
    h_sym = 1 - np.abs(g - np.fliplr(g)).mean() / sd
    v_sym = 1 - np.abs(g - np.flipud(g)).mean() / sd
    sym = max(float(h_sym), float(v_sym))
    h, w = gray.shape
    ch, cw = max(1, h // 6), max(1, w // 6)
    center = g[ch:h - ch, cw:w - cw].mean() if h > 2 * ch and w > 2 * cw else g.mean()
    edges = np.concatenate([g[:ch].ravel(), g[h - ch:].ravel(), g[:, :cw].ravel(), g[:, w - cw:].ravel()])
    edge = float(edges.mean())
    centrality = float((center + 1e-6) / (edge + 1e-6))
    sym_score = float(np.clip((sym - 0.6) / 0.25, 0, 1))
    cen_score = float(np.clip((centrality - 1.05) / 0.25, 0, 1))
    score = float(max(sym_score, cen_score))
    return {"score": score, "detail": f"h_symmetry: {h_sym:.2f}, centrality: {centrality:.2f}"}


def detect_texture_uniformity(image_path):
    gray = _load_gray(image_path)
    if min(gray.shape) < 64:
        return {"score": 0.0, "detail": "image too small for 64x64 blocks"}
    lap = laplace(gray)
    h, w = gray.shape
    vars_ = []
    for i in range(0, h - 63, 64):
        for j in range(0, w - 63, 64):
            vars_.append(lap[i:i + 64, j:j + 64].var())
    vars_ = np.array(vars_)
    cv = float(vars_.std() / (vars_.mean() + 1e-6))
    score = float(np.clip((0.5 - cv) / 0.3, 0, 1))
    return {"score": score, "detail": f"roughness CV: {cv:.2f} (expected >0.4)"}


def detect_metadata(image_path):
    from PIL import ExifTags
    TAG = {ExifTags.TAGS[k]: k for k in ExifTags.TAGS}
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        fmt = img.format
        text = getattr(img, "text", {}) or {}
        info = img.info or {}
    except Exception as e:
        return {"score": 0.3, "detail": f"Metadata unreadable: {e}"}
    if exif == {}:
        return {"score": 0.3, "detail": "Metadata unreadable: corrupt EXIF"}
    software = None
    if exif:
        software = exif.get(TAG.get("Software"))
    if not software and isinstance(info.get("Software"), str):
        software = info["Software"]
    if not software:
        for v in text.values():
            if isinstance(v, str):
                for tag in AI_SOFTWARE_TAGS:
                    if tag in v.lower():
                        return {"score": 1.0, "detail": f"AI software tag: {v}"}
    if software:
        low = str(software).lower()
        for tag in AI_SOFTWARE_TAGS:
            if tag in low:
                return {"score": 1.0, "detail": f"AI software tag: {software}"}
    if exif:
        make = exif.get(TAG.get("Make"))
        model = exif.get(TAG.get("Model"))
        fl = exif.get(TAG.get("FocalLength"))
        et = exif.get(TAG.get("ExposureTime"))
        fn = exif.get(TAG.get("FNumber"))
        if make and model and fl and et and fn:
            return {"score": 0.0, "detail": f"Full camera EXIF: {make} {model}"}
        if make and model:
            return {"score": 0.2, "detail": f"Partial camera EXIF: {make} {model}"}
        return {"score": 0.35, "detail": "EXIF present but no camera identification"}
    if fmt == "PNG" and (text or "Software" in info):
        sw = software or text.get("Software") or info.get("Software")
        return {"score": 0.4, "detail": f"PNG text metadata, no camera: {sw}"}
    return {"score": 0.5, "detail": "No EXIF data"}


DETECTORS = {
    "frequency_ceiling": detect_frequency_ceiling,
    "noise_pattern": detect_noise_pattern,
    "palette": detect_palette,
    "composition": detect_composition,
    "texture_uniformity": detect_texture_uniformity,
    "metadata": detect_metadata,
}

CORRECTABLE = {
    "frequency_ceiling", "noise_pattern", "palette",
    "composition", "texture_uniformity",
}


def analyze(image_path):
    results = {}
    for name, fn in DETECTORS.items():
        results[name] = fn(image_path)
    total = sum(WEIGHTS[n] * results[n]["score"] for n in DETECTORS)
    if total > 0.6:
        verdict = "ai_likely"
    elif total < 0.4:
        verdict = "human_likely"
    else:
        verdict = "uncertain"
    return {
        "file": os.path.basename(image_path),
        "verdict": verdict,
        "total_score": round(total, 2),
        "detectors": results,
    }


def fix_palette(img, score):
    if score <= 0.5:
        return img, False
    fl = img.astype(float) / 255.0
    r, g, b = fl[..., 0], fl[..., 1], fl[..., 2]
    mx = np.maximum(np.maximum(r, g), b)
    mn = np.minimum(np.minimum(r, g), b)
    delta = mx - mn
    hue = np.zeros_like(mx)
    nz = delta > 0
    mask = (mx == r) & nz
    hue[mask] = ((g[mask] - b[mask]) / delta[mask]) % 6.0
    mask = (mx == g) & nz
    hue[mask] = (b[mask] - r[mask]) / delta[mask] + 2.0
    mask = (mx == b) & nz
    hue[mask] = (r[mask] - g[mask]) / delta[mask] + 4.0
    hue = hue / 6.0 % 1.0
    sat = np.where(mx > 0, delta / np.where(mx == 0, 1, mx), 0)
    val = mx
    shift = random.uniform(8, 15) / 360.0
    if random.random() < 0.5:
        shift = -shift
    hue = (hue + shift) % 1.0
    sat = np.clip(sat * (1.0 - random.uniform(0.05, 0.10)), 0, 1)
    h6 = hue * 6.0
    i = np.floor(h6).astype(int)
    f = h6 - i
    p = val * (1 - sat)
    q = val * (1 - sat * f)
    t = val * (1 - sat * (1 - f))
    i = i % 6
    rc = np.choose(i, [val, q, p, p, t, val])
    gc = np.choose(i, [t, val, val, q, p, p])
    bc = np.choose(i, [p, p, t, val, val, q])
    out = np.stack([rc, gc, bc], axis=-1)
    return np.clip(out * 255, 0, 255).astype(np.uint8), True


def fix_texture(img, score):
    if score <= 0.5:
        return img, False
    g = img.astype(float)
    h, w = g.shape[:2]
    grid = np.random.choice([0.0, 3.0], (4, 4))
    mult = zoom(grid, max(h, w) / 4, order=1)[:h, :w]
    if mult.shape[0] < h or mult.shape[1] < w:
        mult = np.pad(mult, ((0, h - mult.shape[0]), (0, w - mult.shape[1])), mode="edge")[:h, :w]
    tex = np.zeros((h, w))
    rng = np.random.default_rng()
    for _ in range(150):
        y0, x0 = int(rng.integers(0, h)), int(rng.integers(0, w))
        length = int(rng.integers(5, 20))
        angle = rng.uniform(0, 6.28)
        dy, dx = int(np.cos(angle) * length), int(np.sin(angle) * length)
        y1, x1 = np.clip(y0 + dy, 0, h - 1), np.clip(x0 + dx, 0, w - 1)
        steps = max(abs(dy), abs(dx), 1)
        ys = np.linspace(y0, y1, steps).astype(int)
        xs = np.linspace(x0, x1, steps).astype(int)
        tex[ys, xs] += rng.uniform(-10, 10)
    tex = gaussian_filter(tex, sigma=0.5) * mult
    for c in range(3):
        g[:, :, c] = g[:, :, c] + tex
    return np.clip(g, 0, 255).astype(np.uint8), True


def fix_composition(img, score):
    if score <= 0.5:
        return img, False
    h, w = img.shape[:2]
    if h < 100 or w < 100:
        return img, False
    left = random.uniform(0.03, 0.07)
    right = random.uniform(0.01, 0.03)
    if random.random() < 0.5:
        left, right = right, left
    top = random.uniform(0.03, 0.07)
    bot = random.uniform(0.01, 0.03)
    if random.random() < 0.5:
        top, bot = bot, top
    y0 = int(h * top); y1 = h - int(h * bot)
    x0 = int(w * left); x1 = w - int(w * right)
    min_dim = 128
    if y1 - y0 < min_dim:
        y0, y1 = max(0, h // 2 - min_dim // 2), min(h, h // 2 + min_dim // 2)
    if x1 - x0 < min_dim:
        x0, x1 = max(0, w // 2 - min_dim // 2), min(w, w // 2 + min_dim // 2)
    cropped = img[y0:y1, x0:x1]
    angle = random.uniform(0.4, 1.2)
    if random.random() < 0.5:
        angle = -angle
    pimg = Image.fromarray(cropped)
    corner = tuple(int(c) for c in cropped[0, 0])
    rotated = pimg.rotate(angle, resample=Image.BICUBIC, expand=False, fillcolor=corner)
    arr = np.asarray(rotated)
    if arr.shape[0] > 132 and arr.shape[1] > 132:
        arr = arr[2:-2, 2:-2]
    return arr, True


def correct(image_path, diagnosis_json_path, output_path):
    with open(diagnosis_json_path) as f:
        diag = json.load(f)
    dets = diag.get("detectors", {})
    img = Image.open(image_path).convert("RGB")
    arr = np.asarray(img)
    applied = []
    pal = dets.get("palette", {})
    arr, ok = fix_palette(arr, pal.get("score", 0))
    if ok:
        applied.append({"fix": "palette", "from_score": pal.get("score")})
    tex = dets.get("texture_uniformity", {})
    arr, ok = fix_texture(arr, tex.get("score", 0))
    if ok:
        applied.append({"fix": "texture", "from_score": tex.get("score")})
    comp = dets.get("composition", {})
    arr, ok = fix_composition(arr, comp.get("score", 0))
    if ok:
        applied.append({"fix": "composition", "from_score": comp.get("score")})
    Image.fromarray(arr).save(output_path)
    summary = {
        "input": os.path.basename(image_path),
        "output": os.path.basename(output_path),
        "corrections_applied": applied,
        "count": len(applied),
    }
    print(json.dumps(summary, indent=2))
    return summary


def process(image_path, output_path=None):
    if output_path is None:
        root, ext = os.path.splitext(image_path)
        output_path = root + "_fixed" + ext
    diagnosis = analyze(image_path)
    if diagnosis["total_score"] < 0.4:
        print("human_likely, no correction needed")
        return diagnosis
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
        json.dump(diagnosis, tf)
        tmp_diag = tf.name
    import contextlib
    with contextlib.redirect_stdout(open(os.devnull, "w")):
        summary = correct(image_path, tmp_diag, output_path)
    os.unlink(tmp_diag)
    diagnosis_after = analyze(output_path)
    per_detector = {}
    for name in CORRECTABLE:
        b = diagnosis["detectors"][name]["score"]
        a = diagnosis_after["detectors"][name]["score"]
        per_detector[name] = {"before": round(b, 2), "after": round(a, 2), "delta": round(a - b, 2)}
    applied = [c["fix"] for c in summary["corrections_applied"]]
    report = {
        "input": image_path,
        "output": output_path,
        "before": {"total_score": diagnosis["total_score"], "verdict": diagnosis["verdict"]},
        "after": {"total_score": diagnosis_after["total_score"], "verdict": diagnosis_after["verdict"]},
        "improvement": round(diagnosis["total_score"] - diagnosis_after["total_score"], 2),
        "corrections_applied": applied,
        "per_detector": per_detector,
    }
    print(json.dumps(report, indent=2))
    return report


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".next"}
MAX_FILE_SIZE = 50 * 1024 * 1024


def scan(directory, fix=False, output_dir=None):
    from pathlib import Path
    root = Path(directory)
    errors = []
    results = []
    fixed_count = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in IMAGE_EXTS:
            continue
        rel = str(path.relative_to(root))
        try:
            if path.stat().st_size > MAX_FILE_SIZE:
                msg = f"{rel}: file too large ({path.stat().st_size // 1024 // 1024}MB)"
                print(f"warning: {msg}")
                errors.append(msg)
                continue
            diag = analyze(str(path))
        except Exception as e:
            errors.append(f"{rel}: {e}")
            continue
        score = diag["total_score"]
        verdict = diag["verdict"]
        md_detail = diag["detectors"]["metadata"]["detail"]
        entry = {"file": rel, "score": score, "verdict": verdict, "fixed": False, "output": None, "improvement": None, "metadata_detail": md_detail}
        if fix and score >= 0.4:
            if output_dir is not None:
                out = Path(output_dir) / rel
                out = out.with_name(out.stem + "_fixed" + out.suffix)
                out.parent.mkdir(parents=True, exist_ok=True)
            else:
                out = path.with_name(path.stem + "_fixed" + path.suffix)
            try:
                import contextlib
                with contextlib.redirect_stdout(open(os.devnull, "w")):
                    proc = process(str(path), str(out))
                entry["fixed"] = True
                entry["output"] = str(out.relative_to(root)) if output_dir is None else str(out.relative_to(output_dir))
                entry["improvement"] = proc["improvement"]
                fixed_count += 1
            except Exception as e:
                errors.append(f"{rel}: fix failed: {e}")
        results.append(entry)
    results.sort(key=lambda r: r["score"], reverse=True)
    summary = {
        "directory": str(root),
        "total_images": len(results),
        "ai_likely": sum(1 for r in results if r["verdict"] == "ai_likely"),
        "uncertain": sum(1 for r in results if r["verdict"] == "uncertain"),
        "human_likely": sum(1 for r in results if r["verdict"] == "human_likely"),
        "fixed": fixed_count,
        "errors": errors,
        "results": results,
    }
    print(json.dumps(summary, indent=2))
    return summary


def report(results_dict, output_path):
    from pathlib import Path
    total = results_dict["total_images"]
    ai = results_dict["ai_likely"]
    unc = results_dict["uncertain"]
    hum = results_dict["human_likely"]
    fixed = results_dict["fixed"]
    pct = lambda n: f"{n/total*100:.1f}%" if total else "0.0%"
    lines = ["# AI Detection Report", "", "## Summary",
             f"- Scanned: {total} images",
             f"- AI likely: {ai} ({pct(ai)})",
             f"- Uncertain: {unc} ({pct(unc)})",
             f"- Human likely: {hum} ({pct(hum)})",
             f"- Fixed: {fixed}", ""]
    attn = [r for r in results_dict["results"] if r["score"] >= 0.6]
    lines.append("## Needs Attention (score >= 0.6)")
    lines.append("| File | Score | Verdict | Fixed | Improvement |")
    lines.append("|------|-------|---------|-------|-------------|")
    for r in attn:
        mk = "yes" if r["fixed"] else "no"
        imp = f"+{r['improvement']}" if r["improvement"] is not None else "-"
        lines.append(f"| {r['file']} | {r['score']} | {r['verdict']} | {mk} | {imp} |")
    lines.append("")
    ai_sw = [r for r in results_dict["results"]
             if "AI software tag" in str(r.get("metadata_detail", ""))]
    lines.append("## Detected AI Software")
    lines.append("| File | Software | Score |")
    lines.append("|------|----------|-------|")
    if ai_sw:
        for r in ai_sw:
            sw = str(r.get("metadata_detail", "")).replace("AI software tag: ", "")
            lines.append(f"| {r['file']} | {sw} | {r['score']} |")
    else:
        lines.append("| _No AI software tags detected._ | | |")
    lines.append("")
    mid = [r for r in results_dict["results"] if 0.4 <= r["score"] < 0.6]
    lines.append("## Uncertain (0.4 - 0.6)")
    lines.append("| File | Score | Verdict |")
    lines.append("|------|-------|---------|")
    for r in mid:
        lines.append(f"| {r['file']} | {r['score']} | {r['verdict']} |")
    lines.append("")
    low = sum(1 for r in results_dict["results"] if r["score"] < 0.4)
    lines.append(f"## Clean (< 0.4)")
    lines.append(f"{low} images — no action needed." if low else "None.")
    lines.append("")
    if results_dict["errors"]:
        lines.append("## Errors")
        for e in results_dict["errors"]:
            lines.append(f"- {e}")
        lines.append("")
    Path(output_path).write_text("\n".join(lines))
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python detector.py <image|dir> [--fix] [--scan] [-o out] [--report md]")
        sys.exit(1)
    args = sys.argv[1:]
    target = args[0]
    if "--scan" in args or os.path.isdir(target):
        out_dir = args[args.index("-o") + 1] if "-o" in args else None
        md = args[args.index("--report") + 1] if "--report" in args else None
        res = scan(target, fix=("--fix" in args), output_dir=out_dir)
        if md:
            report(res, md)
    elif "--fix" in args:
        process(target, args[args.index("-o") + 1] if "-o" in args else None)
    else:
        print(json.dumps(analyze(target), indent=2))
