"""
coherence.py — the capstone detection layer: does the whole project speak
with ONE voice across content + code + design?

AI patches layers independently; human work has a throughline. This measures
the throughline, not the absence of tells. Two flaws fixed in calibration:
  1. AI style-particles (אינו/אלא) are EXCLUDED from the vocabulary signal
     — they are tells, not domain words.
  2. A diversity signal penalizes repetitive boilerplate, which otherwise
     fakes high concentration.
"""
import re
from collections import Counter

STOP_HE = set("של על את הוא היא הם הן לא כן אם כי אבל או גם זה זאת אלה מה מי איך למה כאשר אז רק עוד מאוד יותר בין בתוך אל עד מתחת מעל לפני אחרי".split()
              + ["ה","ו","ב","כ","ל","מ","ש","כש","שה","בה","לו","לה","בהם","אין","יש","כל","היה"])
TELL_PARTICLES = {"אינו","אינה","אלא","אינם","אינן","איננו"}
GENERIC_CODE = {"data","result","results","item","items","temp","tmp","val","value","obj","arr","res","resp","info",
                "element","elem","handle","process","event","events","props","state","render","content","contents",
                "list","lists","object","objects","thing","things","stuff","newdata","finalresult","myvar"}
GENERIC_HE_BUZZ = re.compile(r"ייחודי|מרגש|חדשני|חוויה מושלמת|הכי טוב|ברמה אחרת|פורץ דרך|מהפכני")


def he_tokens(text):
    words = re.findall(r"[\u0590-\u05FF]{2,}", text)
    out = []
    for w in words:
        if w in STOP_HE or w in TELL_PARTICLES:
            continue
        if len(w) > 3 and w[0] in "הובכלמש":
            w2 = w[1:]
            if w2 not in STOP_HE and w2 not in TELL_PARTICLES:
                out.append(w2)
        else:
            out.append(w)
    return out


def analyze_coherence(content_text, code_text="", css_text=""):
    evidence = {}
    toks = he_tokens(content_text)
    total = len(toks)
    if total == 0:
        return {"total_score": 0.0, "verdict": "insufficient", "signals": {}, "top_terms": []}
    terms = Counter(toks)
    top15 = terms.most_common(15)
    focus = sum(c for _, c in top15) / total
    focus_score = min(1.0, focus / 0.18)
    diversity = len(terms) / total
    diversity_score = min(1.0, diversity / 0.45)
    css_hits = sum(1 for t, _ in top15 if css_text and t in css_text)
    echo_score = min(1.0, css_hits / 5.0) if css_text else 0.0
    body = re.sub(r'"[^"]*"', "", code_text)
    idents = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]{2,})\b", body)
    if idents:
        gshare = sum(1 for i in idents if i.lower() in GENERIC_CODE) / len(idents)
        code_score = max(0.0, 1.0 - gshare / 0.15)
    else:
        gshare, code_score = 0.0, 0.0
    buzz = len(GENERIC_HE_BUZZ.findall(content_text))
    buzz_score = max(0.0, 1.0 - buzz / 5.0)
    evidence = {
        "content_focus":    {"top15_share": round(focus, 3), "score": round(focus_score, 2)},
        "content_diversity":{"unique_ratio": round(diversity, 3), "score": round(diversity_score, 2)},
        "css_echo":         {"hits": css_hits, "score": round(echo_score, 2)},
        "code_voice":       {"generic_share": round(gshare, 3), "score": round(code_score, 2)},
        "buzz_absence":     {"count": buzz, "score": round(buzz_score, 2)},
    }
    weights = {"content_focus": 0.25, "content_diversity": 0.20, "css_echo": 0.20,
               "code_voice": 0.20, "buzz_absence": 0.15}
    sig = {"content_focus": focus_score, "content_diversity": diversity_score,
           "css_echo": echo_score, "code_voice": code_score, "buzz_absence": buzz_score}
    total_score = round(sum(weights[k] * sig[k] for k in weights), 2)
    verdict = "coherent" if total_score > 0.6 else "mixed" if total_score > 0.35 else "incoherent"
    return {"total_score": total_score, "verdict": verdict, "signals": evidence,
            "top_terms": [t for t, _ in top15]}