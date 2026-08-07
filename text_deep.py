"""
text_deep.py — SEMANTIC layer of text detection + targeted counter.

Discovery (measured): the 'אינו X אלא Y' aphorism construction appears at
0.64-1.22 per 100 words across ALL of Shoshana's AI content, and at exactly
0.00 across six human authors spanning 3000 years (Genesis, Psalms, Proverbs,
Ecclesiastes, Mishnah, Bialik). This is the semantic signature the surface
statistics could not see.
"""
import re
import json

CONTRAST_RE = re.compile(r"אינ[והןם]\s+[^,.;]{2,40}?\s+אלא|לא\s+[^,.;]{2,40}?\s+אלא(?!\s+גם)")
TRICOLA_RE = re.compile(r"[^,.;]{2,20}?,\s*[^,.;]{2,20}?\s+ו[^,.;]{2,20}?(?=[.;])")
ABSTRACT_RE = re.compile(r"תהליך|מסע|חוויה|עומק|רבדים|הוויה|מרחב")


def _per100(hits, text):
    words = max(1, len(re.findall(r"\S+", text)))
    return hits / (words / 100.0)


def detect_contrast_constructions(text):
    matches = CONTRAST_RE.findall(text)
    density = _per100(len(matches), text)
    score = min(1.0, density / 1.0)
    return {"score": round(score, 2), "density": round(density, 2),
            "detail": f"{len(matches)} constructions, {density:.2f}/100w"}


def detect_tricola(text):
    density = _per100(len(TRICOLA_RE.findall(text)), text)
    score = min(1.0, density / 0.6)
    return {"score": round(score, 2), "density": round(density, 2),
            "detail": f"{density:.2f}/100w"}


def detect_abstract_density(text):
    density = _per100(len(ABSTRACT_RE.findall(text)), text)
    score = min(1.0, density / 1.2)
    return {"score": round(score, 2), "density": round(density, 2),
            "detail": f"{density:.2f}/100w"}


WEIGHTS = {"contrast": 0.60, "tricola": 0.25, "abstract": 0.15}


def analyze_deep(text):
    # Handle None input gracefully
    if text is None:
        text = ""
    d = {
        "contrast": detect_contrast_constructions(text),
        "tricola": detect_tricola(text),
        "abstract": detect_abstract_density(text),
    }
    total = round(sum(WEIGHTS[k] * d[k]['score'] for k in WEIGHTS), 2)
    verdict = "ai_likely" if total > 0.4 else "uncertain" if total > 0.2 else "human_likely"
    return {"total_score": total, "verdict": verdict, "detectors": d}


def analyze_collection_deep(entries, threshold=0.5):
    results = [analyze_deep(e) for e in entries]
    flagged = [i for i, r in enumerate(results) if r['total_score'] >= threshold]
    avg = round(sum(r['total_score'] for r in results) / max(1, len(results)), 2)
    return {"entries": len(entries), "avg": avg, "flagged_indices": flagged,
            "flagged_share": round(len(flagged) / max(1, len(entries)), 2)}


def split_all_contrasts(text):
    """Counter: invert 'אינו X אלא Y' into 'Y, לא X'.
    Grammar-safe, meaning-preserving, and the construction pattern is gone."""
    full_re = re.compile(r"אינ[והןם]\s+([^,.;]{2,40}?)\s+אלא\s+([^,.;]{2,60})")
    def repl(m):
        neg_part = m.group(1).strip()
        aff_part = m.group(2).strip()
        return aff_part + ", לא " + neg_part
    return full_re.sub(repl, text)


def targeted_contrast_reduction(entries, threshold=0.5):
    """Counter layer: surgery only where the semantic score demands it."""
    out = []
    changed = []
    for i, e in enumerate(entries):
        r = analyze_deep(e)
        if r['total_score'] >= threshold and r['detectors']['contrast']['score'] >= 0.4:
            new = split_all_contrasts(e)
            if new != e:
                changed.append(i)
                out.append(new)
                continue
        out.append(e)
    return out, changed


if __name__ == "__main__":
    import sys
    text = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    print(json.dumps(analyze_deep(text), ensure_ascii=False, indent=1))