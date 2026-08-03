#!/usr/bin/env python3
"""run_text_eval.py — reproducible evaluation harness for the text layer.

Usage:
  python3 run_text_eval.py <ai_dir> <human_dir>

Each dir contains .txt files (one entry per file) OR .json with {"entries": [...]}.
Prints: determinism check, entry-level P/R/F1 sweep, corpus-level classification.

This harness exists because claims without reproducible tests are not results.
"""
import os, sys, json, hashlib, statistics

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from text_detector import analyze_text
from corpus_detector import analyze_corpus


def load_entries(path):
    entries = []
    if os.path.isdir(path):
        for fn in sorted(os.listdir(path)):
            p = os.path.join(path, fn)
            if fn.endswith(".txt"):
                entries.append(open(p).read().strip())
            elif fn.endswith(".json"):
                entries.extend(json.load(open(p)).get("entries", []))
    elif path.endswith(".json"):
        entries = json.load(open(path)).get("entries", [])
    return [e for e in entries if e and len(e.strip()) > 20]


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    ai_entries = load_entries(sys.argv[1])
    human_entries = load_entries(sys.argv[2])
    print(f"loaded: {len(ai_entries)} AI entries, {len(human_entries)} human entries")

    # 1. determinism
    h = [hashlib.md5(json.dumps(analyze_text(ai_entries[0]), sort_keys=True).encode()).hexdigest() for _ in range(3)]
    print("determinism:", "PASS" if len(set(h)) == 1 else "FAIL")

    # 2. entry-level sweep
    ai_scores = [(analyze_text(e)["total_score"], e) for e in ai_entries]
    hu_scores = [(analyze_text(e)["total_score"], e) for e in human_entries]
    print(f"\n{'thr':>5} {'prec':>6} {'rec':>6} {'F1':>6} {'FP':>3}")
    for thr in [0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50, 0.60]:
        tp = sum(1 for s, _ in ai_scores if s >= thr)
        fp = sum(1 for s, _ in hu_scores if s >= thr)
        fn = len(ai_scores) - tp
        prec = tp / (tp + fp) if tp + fp else 0
        rec = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0
        print(f"{thr:>5.2f} {prec:>6.2f} {rec:>6.2f} {f1:>6.2f} {fp:>3}")

    # 3. failures at 0.20
    thr = 0.20
    fp_items = [(s, e) for s, e in hu_scores if s >= thr]
    fn_items = [(s, e) for s, e in ai_scores if s < thr]
    print(f"\nfalse positives @0.20: {len(fp_items)}")
    for s, e in sorted(fp_items, reverse=True)[:5]:
        print(f"  {s:.2f} {e[:70]}")
    print(f"false negatives @0.20: {len(fn_items)}")
    for s, e in sorted(fn_items, reverse=True)[:5]:
        print(f"  {s:.2f} {e[:70]}")


if __name__ == "__main__":
    main()
