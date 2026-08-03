import re
import json
import sys
import statistics

# text_detector.py — identifies AI writing patterns in Hebrew and English.
# Architecture mirrors detector.py: independent detectors, weighted verdict.
# Applicability-aware: detectors that cannot run on short text are excluded
# from the weighted aggregate instead of dragging it down.

HE_LEXICON = {
    "cliche_phrases": [
        "חשוב לציין", "יתרה מזאת", "בנוסף לכך", "בעולם של היום", "בסופו של דבר",
        "למעשה", "במהות", "בפועל", "בגדול", "אם כן", "כך גם",
        "מדובר ב", "ניתן לראות", "ניתן לומר", "ראוי לציין", "כדאי לזכור",
    ],
    "abstract_nouns": [
        "מסע", "חוויה", "תהליך", "צמיחה", "עומק", "מרחב", "רבדים", "הוויה",
        "העצמה", "תובנות", "תובנה", "העמקה", "נוכחות", "כוונה", "שחרור",
        "התעוררות", "הארה", "חיבור", "איזון", "זרימה",
    ],
    "comparison_formula": [
        "קרא לזה", "קראה לזה", "קראו לזה", "תיאר זאת", "כינה זאת", "כינו זאת",
        "הגיע לאותה תובנה", "הגיעו לאותה תובנה", "בדומה ל", "בדומה לכך",
        "גם כאן", "כמו ב", "כמו אצל", "כשם ש",
    ],
    "contrast_pairs": [
        (r"אינ[והןם]\s+[^,.;]{2,40}?\s+אלא", 1),
        (r"לא\s+[^,.;]{2,40}?\s+אלא", 1),
        (r"בניגוד\s+ל", 1),
        (r"במקום\s+[^,.;]{2,40}?\s+—?", 0.7),
    ],
    "aphorism_openers": ["מי ש", "מי שמ", "מה ש", "מי שחוזר", "מי שמקשיב", "מי שנשרף"],
}

EN_LEXICON = {
    "cliche_phrases": [
        "delve", "tapestry", "navigate the", "unlock", "unleash", "elevate",
        "seamless", "robust", "leverage", "foster", "underscore", "pivotal",
        "realm", "landscape", "in today's fast-paced", "it's worth noting",
        "it is worth noting", "furthermore", "moreover", "additionally",
        "a testament to", "sheds light", "embark on a journey", "harness",
        "cutting-edge", "game-changer", "streamline", "holistic", "paradigm",
        "dive deep", "take a closer look", "at the end of the day",
    ],
    "abstract_nouns": [
        "journey", "experience", "growth", "transformation", "empowerment",
        "insights", "mindfulness", "wellness", "alignment", "synergy",
    ],
    "comparison_formula": [
        "similarly", "likewise", "in the same vein", "echoes this",
        "resonates with", "parallels",
    ],
    "contrast_pairs": [
        (r"not\s+only\s+[^.]{5,80}?\s+but\s+also", 1),
        (r"it'?s\s+not\s+(?:just|about|only)\s+[^.]{5,80}?\s+it'?s", 1),
        (r"rather\s+than", 0.6),
        (r"instead\s+of", 0.5),
    ],
    "aphorism_openers": ["those who", "he who", "she who", "one who", "what we"],
}

WEIGHTS = {
    "lexical_cliches": 0.22,
    "sentence_uniformity": 0.16,
    "paragraph_uniformity": 0.10,
    "parallelism": 0.14,
    "contrast_density": 0.12,
    "aphorism_closers": 0.14,
    "cross_reference_formula": 0.12,
}


def detect_language(text):
    he_chars = len(re.findall(r"[\u0590-\u05FF]", text))
    total = len(re.sub(r"\s", "", text))
    if total == 0:
        return "en"
    return "he" if he_chars / total > 0.4 else "en"


def _split_sentences(text):
    text = re.sub(r"\s+", " ", text.strip())
    parts = re.split(r"(?<=[.!?;])\s+|(?<=[.!?])(?=[\u0590-\u05FF\"'])", text)
    return [p.strip() for p in parts if len(p.strip()) > 2]


def _split_paragraphs(text):
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if len(paras) <= 1:
        paras = [p.strip() for p in text.split("\n") if p.strip()]
    return paras


def detect_lexical_cliches(text, lang):
    lex = HE_LEXICON if lang == "he" else EN_LEXICON
    low = text.lower()
    words = max(1, len(re.findall(r"\S+", text)))
    phrase_hits = sum(low.count(p) for p in lex["cliche_phrases"])
    noun_hits = sum(len(re.findall(r"\b" + re.escape(n) + r"\b", low)) for n in lex["abstract_nouns"])
    density = (phrase_hits * 2 + noun_hits) / (words / 100)
    score = min(1.0, density / 6.0)
    return {"score": round(score, 2),
            "detail": f"{phrase_hits} cliches, {noun_hits} abstract nouns / {words} words",
            "applicable": words >= 25}


def detect_sentence_uniformity(text, lang):
    sents = _split_sentences(text)
    if len(sents) < 4:
        return {"score": 0.0, "detail": "too short", "applicable": False}
    lens = [len(s) for s in sents]
    mean = statistics.mean(lens)
    if mean == 0:
        return {"score": 0.0, "detail": "empty", "applicable": False}
    cv = statistics.stdev(lens) / mean if len(lens) > 1 else 0
    score = max(0.0, min(1.0, (0.62 - cv) / 0.37))
    return {"score": round(score, 2),
            "detail": f"sentence CV {cv:.2f} over {len(sents)} sentences",
            "applicable": True}


def detect_paragraph_uniformity(text, lang):
    paras = _split_paragraphs(text)
    if len(paras) < 3:
        return {"score": 0.0, "detail": "single block", "applicable": False}
    lens = [len(p) for p in paras]
    mean = statistics.mean(lens)
    cv = statistics.stdev(lens) / mean if len(lens) > 1 else 0
    score = max(0.0, min(1.0, (0.55 - cv) / 0.35))
    return {"score": round(score, 2),
            "detail": f"paragraph CV {cv:.2f} over {len(paras)} paragraphs",
            "applicable": True}


def detect_parallelism(text, lang):
    sents = _split_sentences(text)
    if len(sents) < 5:
        return {"score": 0.0, "detail": "too short", "applicable": False}
    openers = {}
    for s in sents:
        ws = re.findall(r"\S+", s)[:2]
        if len(ws) == 2:
            key = " ".join(ws).lower()
            openers[key] = openers.get(key, 0) + 1
    repeats = sum(c - 1 for c in openers.values() if c > 1)
    opener_score = min(1.0, repeats / (len(sents) * 0.35))
    lens = sorted(len(s) for s in sents)
    diffs = [abs(lens[i+1] - lens[i]) for i in range(len(lens)-1)]
    cluster_score = 1.0 - min(1.0, (statistics.mean(diffs) if diffs else 0) / 25)
    score = max(opener_score, cluster_score * 0.8)
    return {"score": round(score, 2), "detail": f"{repeats} repeated openers", "applicable": True}


def detect_contrast_density(text, lang):
    lex = HE_LEXICON if lang == "he" else EN_LEXICON
    hits = 0
    for pattern, weight in lex["contrast_pairs"]:
        hits += len(re.findall(pattern, text, re.IGNORECASE)) * weight
    words = max(1, len(re.findall(r"\S+", text)))
    density = hits / (words / 100)
    score = min(1.0, density / 3.5)
    return {"score": round(score, 2),
            "detail": f"{hits:.0f} paired contrast constructions",
            "applicable": words >= 30}


def detect_aphorism_closers(text, lang):
    lex = HE_LEXICON if lang == "he" else EN_LEXICON
    sents = _split_sentences(text)
    if len(sents) < 3:
        return {"score": 0.0, "detail": "too short", "applicable": False}
    candidates = []
    for p in _split_paragraphs(text):
        ps = _split_sentences(p)
        if ps:
            candidates.append(ps[-1])
    candidates.append(sents[-1])
    hits = 0
    for c in candidates:
        cl = c.strip()
        if len(cl) < 90 and any(cl.startswith(o) for o in lex["aphorism_openers"]):
            hits += 1
        elif len(cl) < 60 and re.search(r"(מתחיל|נגמר|נשאר|הוא התשובה|היא התשובה|is the answer|begins|remains)\.?$", cl):
            hits += 1
        elif re.search(r"^(ultimately|in essence|in conclusion|בסופו של דבר|לסיכום|במהות)", cl.lower()):
            hits += 1
    score = min(1.0, hits / max(1, len(candidates)) * 1.4)
    return {"score": round(score, 2),
            "detail": f"{hits}/{len(candidates)} aphoristic closers",
            "applicable": len(candidates) >= 2}


def detect_cross_reference_formula(text, lang):
    lex = HE_LEXICON if lang == "he" else EN_LEXICON
    hits = sum(len(re.findall(re.escape(f), text)) for f in lex["comparison_formula"])
    citations = len(re.findall(r"[\u0590-\u05FF\w]+\s*\(\d{4}\)", text))
    words = max(1, len(re.findall(r"\S+", text)))
    density = (hits + citations * 1.5) / (words / 100)
    score = min(1.0, density / 3.5)
    return {"score": round(score, 2),
            "detail": f"{hits} formula refs, {citations} name(year) citations",
            "applicable": words >= 40}


def analyze_text(text, lang=None):
    if lang is None:
        lang = detect_language(text)
    detectors = {
        "lexical_cliches": detect_lexical_cliches(text, lang),
        "sentence_uniformity": detect_sentence_uniformity(text, lang),
        "paragraph_uniformity": detect_paragraph_uniformity(text, lang),
        "parallelism": detect_parallelism(text, lang),
        "contrast_density": detect_contrast_density(text, lang),
        "aphorism_closers": detect_aphorism_closers(text, lang),
        "cross_reference_formula": detect_cross_reference_formula(text, lang),
    }
    active = {k: WEIGHTS[k] for k in WEIGHTS if detectors[k].get("applicable", True)}
    if active:
        wsum = sum(active.values())
        total = sum(active[k] * detectors[k]["score"] for k in active) / wsum
    else:
        total = 0.0
    lex = detectors["lexical_cliches"]["score"]
    if lex >= 0.85:
        total = max(total, 0.75)
    elif lex >= 0.6:
        total = max(total, 0.55)
    total = round(total, 2)
    verdict = "ai_likely" if total > 0.6 else "uncertain" if total > 0.4 else "human_likely"
    return {"lang": lang, "total_score": total, "verdict": verdict, "detectors": detectors}


if __name__ == "__main__":
    text = sys.stdin.read() if len(sys.argv) < 2 else open(sys.argv[1]).read()
    print(json.dumps(analyze_text(text), indent=2, ensure_ascii=False))
