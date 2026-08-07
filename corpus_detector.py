import re
import json
import sys
import statistics
from collections import Counter

# corpus_detector.py — detects AI-generation signatures at the COLLECTION level.
# Single AI entries can be well-written; the giveaway is the collection itself:
# uniform lengths, cloned openers, identical narrative arcs, templated schemas.
# Complements text_detector.py (entry-level).

WEIGHTS = {
    "length_uniformity": 0.24,
    "sentence_count_uniformity": 0.14,
    "opener_cloning": 0.22,
    "closer_cloning": 0.16,
    "shared_vocabulary": 0.14,
    "length_targeting": 0.10,
}

HE_STOP = set("של על את הוא היא הם הן לא כן אם כי אבל ו גם או זה זאת אלה those".split() +
             ["ש", "ה", "ו", "כ", "ל", "מ", "ב", "ד", "הם", "הן", "את", "על", "של", "עם", "אל", "לו", "לה"])
EN_STOP = set("the a an of to in and or but is are was were it this that with for on at by from as be".split())


def _split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?;])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 2]


def detect_length_uniformity(entries):
    if len(entries) < 4:
        return {"score": 0.0, "detail": "too few entries", "applicable": False}
    lens = [len(e) for e in entries]
    cv = statistics.stdev(lens) / statistics.mean(lens)
    # AI collections with length specs: cv ~0.1-0.25; human collections: 0.5+
    score = max(0.0, min(1.0, (0.45 - cv) / 0.35))
    if len(entries) < 12:
        score = score * (len(entries) / 12.0)
    return {"score": round(score, 2), "detail": f"length CV {cv:.2f} over {len(entries)} entries", "applicable": True}


def detect_sentence_count_uniformity(entries):
    counts = [len(_split_sentences(e)) for e in entries]
    if len(counts) < 4:
        return {"score": 0.0, "detail": "too few entries", "applicable": False}
    mean = statistics.mean(counts)
    if mean < 2:
        return {"score": 0.0, "detail": "entries too short", "applicable": False}
    cv = statistics.stdev(counts) / mean
    score = max(0.0, min(1.0, (0.42 - cv) / 0.32))
    return {"score": round(score, 2), "detail": f"sentence-count CV {cv:.2f} (mean {mean:.1f})", "applicable": True}


def _opener_key(text):
    ws = re.findall(r"\S+", text.strip())[:2]
    if not ws:
        return ""
    first = ws[0]
    # normalize: keep only the syntactic head of the opener
    return first


def detect_opener_cloning(entries):
    if len(entries) < 5:
        return {"score": 0.0, "detail": "too few entries", "applicable": False}
    # clone level 1: exact same first word
    heads = Counter(_opener_key(e) for e in entries if _opener_key(e))
    top_share = max(heads.values()) / len(entries) if heads else 0
    # clone level 2: same first TWO words
    pairs = Counter(" ".join(re.findall(r"\S+", e.strip())[:2]).lower() for e in entries)
    top_pair_share = max(pairs.values()) / len(entries) if pairs else 0
    # human collections: top first-word share < 0.25; AI templates: > 0.5
    score = max(0.0, min(1.0, (top_share - 0.25) / 0.45)) * 0.6 + \
            max(0.0, min(1.0, (top_pair_share - 0.1) / 0.3)) * 0.4
    most = heads.most_common(1)[0] if heads else ("", 0)
    return {"score": round(score, 2),
            "detail": f"top opener '{most[0]}' in {most[1]}/{len(entries)} entries",
            "applicable": True}


def _closer_style(text):
    sents = _split_sentences(text)
    if not sents:
        return "none"
    last = sents[-1].strip()
    if len(last) < 70 and (last.startswith("מי ש") or last.startswith("מה ש")):
        return "aphorism_he"
    if len(last) < 70:
        return "short_he"
    return "long"


def detect_closer_cloning(entries):
    if len(entries) < 5:
        return {"score": 0.0, "detail": "too few entries", "applicable": False}
    styles = Counter(_closer_style(e) for e in entries)
    top_style, top_count = styles.most_common(1)[0]
    share = top_count / len(entries)
    # aphorism closers are a strong AI tell when cloned across a collection
    base = max(0.0, min(1.0, (share - 0.45) / 0.4))
    if top_style == "aphorism_he":
        base = min(1.0, base + 0.25)
    elif len(entries) < 15 or share < 0.85:
        base = base * 0.35  # bare style cloning: weak unless massive + consistent
    return {"score": round(base, 2),
            "detail": f"closer style '{top_style}' in {top_count}/{len(entries)}",
            "applicable": True}


def detect_shared_vocabulary(entries, lang="he"):
    if len(entries) < 4:
        return {"score": 0.0, "detail": "too few entries", "applicable": False}
    stop = HE_STOP if lang == "he" else EN_STOP
    doc_freq = Counter()
    for e in entries:
        words = set(w.strip(".,;:!?'\"()[]") for w in re.findall(r"\S+", e.lower()))
        for w in words:
            if len(w) > 2 and w not in stop:
                doc_freq[w] += 1
    n = len(entries)
    # words appearing in >55% of all entries = templated vocabulary
    shared = [w for w, c in doc_freq.items() if c >= max(3, n * 0.55)]
    density = len(shared) / 25.0  # ~25 such words = fully templated
    score = min(1.0, density)
    sample = ", ".join(shared[:6])
    return {"score": round(score, 2),
            "detail": f"{len(shared)} words in >55% of entries ({sample})",
            "applicable": True}


def detect_length_targeting(entries):
    if len(entries) < 6:
        return {"score": 0.0, "detail": "too few entries", "applicable": False}
    lens = sorted(len(e) for e in entries)
    median = lens[len(lens) // 2]
    # share of entries within ±15% of median — AI targeting clusters hard
    near = sum(1 for l in lens if abs(l - median) <= median * 0.15) / len(lens)
    score = max(0.0, min(1.0, (near - 0.4) / 0.45))
    return {"score": round(score, 2),
            "detail": f"{near:.0%} of entries within ±15% of median length",
            "applicable": True}


def analyze_corpus(entries, lang="he"):
    # Handle None input gracefully
    if entries is None:
        entries = []
    entries = [e for e in entries if e and len(e.strip()) > 20]
    if len(entries) < 4:
        return {"total_score": 0.0, "verdict": "insufficient", "entries": len(entries), "detectors": {}}
    detectors = {
        "length_uniformity": detect_length_uniformity(entries),
        "sentence_count_uniformity": detect_sentence_count_uniformity(entries),
        "opener_cloning": detect_opener_cloning(entries),
        "closer_cloning": detect_closer_cloning(entries),
        "shared_vocabulary": detect_shared_vocabulary(entries, lang),
        "length_targeting": detect_length_targeting(entries),
    }
    active = {k: WEIGHTS[k] for k in WEIGHTS if detectors[k].get("applicable", True)}
    wsum = sum(active.values()) or 1
    total = round(sum(active[k] * detectors[k]["score"] for k in active) / wsum, 2)
    verdict = "ai_collection" if total > 0.6 else "uncertain" if total > 0.4 else "human_collection"
    return {"entries": len(entries), "lang": lang, "total_score": total,
            "verdict": verdict, "detectors": detectors}


if __name__ == "__main__":
    data = json.load(sys.stdin if len(sys.argv) < 2 else open(sys.argv[1]))
    lang = data.get("lang", "he")
    print(json.dumps(analyze_corpus(data["entries"], lang), indent=2, ensure_ascii=False))
