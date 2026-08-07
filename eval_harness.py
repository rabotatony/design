#!/usr/bin/env python3
"""eval_harness.py — reusable accuracy measurement for the image detector.

Downloads AI + real images from a config, runs the detector, and reports
accuracy / precision / recall / F1. Every future detector change is measured
by re-running this, so improvements are verifiable, not claimed.

Usage: python3 eval_harness.py [config.json]
"""
import os, sys, json, tempfile, types, base64
import requests

DEFAULT_CONFIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "eval_config.json")

def load_detector(detector_path):
    import importlib.util
    if not os.path.exists(detector_path):
        raise FileNotFoundError(f"Detector file not found: {detector_path}")
    spec = importlib.util.spec_from_file_location("detector", detector_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def download(url, dest, timeout=20):
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True)
        if r.status_code == 200 and len(r.content) > 2000:
            open(dest, "wb").write(r.content)
            return True
        return False
    except Exception:
        return False

def main():
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CONFIG
    cfg = json.load(open(cfg_path))
    det_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "detector.py")
    det = load_detector(det_path)

    tmp = tempfile.mkdtemp()
    ai_scores, real_scores = [], []

    # AI images
    for name, url in cfg.get("ai_images", {}).items():
        p = os.path.join(tmp, name + ".png")
        if download(url, p):
            r = det.analyze(p)
            ai_scores.append((name, r["total_score"], r["verdict"]))
        else:
            print(f"  skip {name} (download fail)")

    # Real photos (picsum fixed seeds)
    for seed in cfg.get("real_seeds", []):
        p = os.path.join(tmp, f"real_{seed}.jpg")
        if download(f"https://picsum.photos/200/200?random={seed}", p):
            r = det.analyze(p)
            real_scores.append((f"real_{seed}", r["total_score"], r["verdict"]))
        else:
            print(f"  skip real_{seed} (download fail)")

    print("=== AI images (expect ai_likely) ===")
    for n, s, v in ai_scores: print(f"  {n:16s} {s:.2f} {v}")
    print("=== REAL photos (expect human_likely) ===")
    for n, s, v in real_scores: print(f"  {n:16s} {s:.2f} {v}")

    # metrics (ai_likely threshold = total>=0.4 flagged as AI)
    tp = sum(1 for _, s, _ in ai_scores if s >= 0.4)
    fn = len(ai_scores) - tp
    tn = sum(1 for _, s, _ in real_scores if s < 0.4)
    fp = len(real_scores) - tn
    n_ai, n_real = len(ai_scores), len(real_scores)
    acc = (tp + tn) / max(1, n_ai + n_real)
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0
    print("\n=== METRICS ===")
    print(f"AI images: {n_ai} | REAL: {n_real}")
    print(f"TP {tp} FN {fn} TN {tn} FP {fp}")
    print(f"accuracy {acc:.2f} | precision {prec:.2f} | recall {rec:.2f} | F1 {f1:.2f}")
    ai_vals = [s for _, s, _ in ai_scores]; real_vals = [s for _, s, _ in real_scores]
    if ai_vals and real_vals:
        print(f"AI mean {sum(ai_vals)/len(ai_vals):.2f} | REAL mean {sum(real_vals)/len(real_vals):.2f} | separation {sum(ai_vals)/len(ai_vals)-sum(real_vals)/len(real_vals):+.2f}")

if __name__ == "__main__":
    main()
