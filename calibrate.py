import os
import re
import sys
import json
from pathlib import Path
import numpy as np
from detector import analyze, correct, WEIGHTS, DETECTORS

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
SKIP_DIRS = {"node_modules", ".git", "__pycache__", ".next"}


def _list_images(directory):
    root = Path(directory)
    out = []
    if not root.exists():
        return out
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() in IMAGE_EXTS:
            out.append(p)
    return out


def _safe_analyze(path):
    try:
        return analyze(str(path))
    except Exception as e:
        return {"error": str(e), "total_score": None, "detectors": {}}


def evaluate(ai_dir, human_dir):
    ai_paths = _list_images(ai_dir)
    hum_paths = _list_images(human_dir)
    ai_scores, hum_scores = [], []
    ai_dets, hum_dets = [], []
    for p in ai_paths:
        d = _safe_analyze(p)
        if d.get("total_score") is not None:
            ai_scores.append((str(p.relative_to(Path(ai_dir))), d["total_score"]))
            ai_dets.append(d["detectors"])
    for p in hum_paths:
        d = _safe_analyze(p)
        if d.get("total_score") is not None:
            hum_scores.append((str(p.relative_to(Path(human_dir))), d["total_score"]))
            hum_dets.append(d["detectors"])
    total = len(ai_scores) + len(hum_scores)
    threshold = 0.5

    def acc_at(t):
        tp = sum(1 for _, s in ai_scores if s >= t)
        tn = sum(1 for _, s in hum_scores if s < t)
        return (tp + tn) / total if total else 0.0

    accuracy = acc_at(threshold)
    best_t, best_acc = threshold, accuracy
    for i in range(10, 91):
        t = i / 100.0
        a = acc_at(t)
        if a > best_acc:
            best_acc, best_t = a, t
    fp = sorted(
        [{"file": f, "score": s, "verdict": "ai_likely" if s >= 0.6 else "uncertain"} for f, s in hum_scores if s >= threshold],
        key=lambda x: x["score"], reverse=True,
    )
    fn = sorted(
        [{"file": f, "score": s, "verdict": "human_likely" if s < 0.4 else "uncertain"} for f, s in ai_scores if s < threshold],
        key=lambda x: x["score"],
    )
    per_det = {}
    seps = {}
    for name in DETECTORS:
        am = float(np.mean([d[name]["score"] for d in ai_dets])) if ai_dets else 0.0
        hm = float(np.mean([d[name]["score"] for d in hum_dets])) if hum_dets else 0.0
        sep = am - hm
        seps[name] = sep
        per_det[name] = {"ai_mean": round(am, 2), "human_mean": round(hm, 2), "separation": round(sep, 2)}
    total_sep = sum(max(s, 0) for s in seps.values())
    if total_sep > 0:
        suggested = {n: round(max(seps[n], 0) / total_sep, 2) for n in DETECTORS}
    else:
        suggested = {n: round(1.0 / len(DETECTORS), 2) for n in DETECTORS}
    diff = 1.0 - sum(suggested.values())
    if abs(diff) > 1e-6 and suggested:
        mx = max(suggested, key=suggested.get)
        suggested[mx] = round(suggested[mx] + diff, 2)
    result = {
        "ai_images": len(ai_scores),
        "human_images": len(hum_scores),
        "accuracy": round(accuracy, 2),
        "threshold_used": threshold,
        "optimal_threshold": round(best_t, 2),
        "false_positives": fp,
        "false_negatives": fn,
        "per_detector_accuracy": per_det,
        "suggested_weights": suggested,
        "weakest_detector": min(seps, key=seps.get) if seps else None,
        "strongest_detector": max(seps, key=seps.get) if seps else None,
    }
    print(json.dumps(result, indent=2))
    return result


def apply_weights(weights_dict):
    path = Path(__file__).parent / "detector.py"
    src = path.read_text()
    old_match = re.search(r"WEIGHTS\s*=\s*\{[^}]*\}", src)
    if not old_match:
        print("ERROR: WEIGHTS dict not found in detector.py")
        return None
    old_block = old_match.group(0)
    lines = []
    for k in DETECTORS:
        v = weights_dict.get(k, WEIGHTS.get(k, 0))
        lines.append(f'    "{k}": {v},')
    new_block = "WEIGHTS = {\n" + "\n".join(lines) + "\n}"
    new_src = src.replace(old_block, new_block)
    path.write_text(new_src)
    print("Old weights:")
    print(old_block)
    print("New weights:")
    print(new_block)
    return {"old": old_block, "new": new_block}


def compare(before_dir, after_dir):
    before = {p.name: p for p in _list_images(before_dir)}
    after = {p.name: p for p in _list_images(after_dir)}
    common = sorted(set(before) & set(after))
    deltas = {n: [] for n in DETECTORS}
    improvements = []
    improved = unchanged = worse = 0
    for name in common:
        b = _safe_analyze(before[name])
        a = _safe_analyze(after[name])
        if b.get("total_score") is None or a.get("total_score") is None:
            continue
        imp = b["total_score"] - a["total_score"]
        improvements.append(imp)
        if imp > 0.01:
            improved += 1
        elif imp < -0.01:
            worse += 1
        else:
            unchanged += 1
        for n in DETECTORS:
            deltas[n].append(a["detectors"][n]["score"] - b["detectors"][n]["score"])
    n = len(improvements)
    avg_delta = {n: round(float(np.mean(deltas[n])), 2) for n in DETECTORS} if n else {}
    nonzero = {n: v for n, v in avg_delta.items() if v != 0}
    result = {
        "images_compared": n,
        "avg_improvement": round(float(np.mean(improvements)), 2) if n else 0.0,
        "per_detector_avg_delta": avg_delta,
        "best_correction": min(nonzero, key=nonzero.get) if nonzero else None,
        "worst_correction": max(nonzero, key=nonzero.get) if nonzero else None,
        "images_improved": improved,
        "images_unchanged": unchanged,
        "images_worse": worse,
    }
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: calibrate.py evaluate <ai> <human> [--apply] | compare <before> <after>")
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "evaluate" and len(sys.argv) >= 4:
        res = evaluate(sys.argv[2], sys.argv[3])
        if "--apply" in sys.argv:
            apply_weights(res["suggested_weights"])
    elif cmd == "compare" and len(sys.argv) >= 4:
        compare(sys.argv[2], sys.argv[3])
    else:
        print("usage: calibrate.py evaluate <ai> <human> [--apply] | compare <before> <after>")
        sys.exit(1)
