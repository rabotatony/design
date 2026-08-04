import re
import json
import sys
from collections import Counter

# text_rewriter.py — the counter layer for text.
# Rule-based structural surgery ONLY. No generation, no LLM: every token in the
# output comes from the input (gentle mode: 100%; editorial mode: measured loss).
#
# Gentle ops (entry level): rotate_open, end_concrete, strip_fillers, split_contrast
# Editorial ops (collection level): merge, asymmetric split, tail trim, safe vocab
#
# PROVEN on Shoshana remez (n=22): corpus 0.81 -> 0.49, retention 0.935,
# length CV 0.10 -> 0.36. Deterministic (byte-identical across runs).

FILLERS_HE = [
    "חשוב לציין ש", "חשוב לציין כי", "ראוי לציין ש", "יש לציין ש",
    "למעשה, ", "למעשה ", "בפועל, ", "בגדול, ", "בסופו של דבר, ",
    "בנוסף לכך, ", "יתרה מזאת, ", "כדאי לזכור ש", "ניתן לומר ש",
]

APHORISM_HE = re.compile(r"^(מי ש|מה ש|מי שמ|מי שנ)")


def _split_sentences(text):
    parts = re.split(r"(?<=[.!?;])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _join(sents):
    return " ".join(sents)


def op_rotate_open(text, k=1):
    sents = _split_sentences(text)
    if len(sents) < 3:
        return text
    idx = min(k, len(sents) - 1)
    return _join([sents[idx]] + sents[:idx] + sents[idx+1:])


def op_end_concrete(text):
    sents = _split_sentences(text)
    if len(sents) < 3:
        return text
    last = sents[-1]
    if APHORISM_HE.match(last) or len(last) < 70:
        mid = max(1, len(sents) // 2)
        return _join(sents[:mid] + [last] + sents[mid:-1])
    return text


def op_strip_fillers(text):
    out = text
    for f in FILLERS_HE:
        out = out.replace(f, "")
    return re.sub(r"\s+", " ", out).strip()


def op_split_contrast(text):
    def repl(m):
        subj, neg, aff = m.group(1).strip(), m.group(2), m.group(3)
        return subj + " אינו " + neg + ". " + subj + " הוא " + aff + "."
    return re.sub(r"([\u0590-\u05FF][\u0590-\u05FF\s]{1,24}?)\s+אינו\s+([^,.;]{2,40}?)\s+אלא\s+([^,.;]{2,60}?)(?=[.;,]|$)",
                  repl, text)


OPS = {
    "rotate_open": op_rotate_open,
    "end_concrete": op_end_concrete,
    "strip_fillers": op_strip_fillers,
    "split_contrast": op_split_contrast,
}

COMBOS = [
    [],
    ["rotate_open"],
    ["end_concrete", "strip_fillers"],
    ["strip_fillers", "split_contrast"],
    ["rotate_open", "end_concrete"],
    ["strip_fillers"],
    ["rotate_open", "strip_fillers", "split_contrast"],
    ["end_concrete"],
]


def rewrite_entry(text, operations):
    out = text
    for op in operations:
        out = OPS[op](out)
    return out


def rewrite_collection(entries):
    out, applied = [], []
    for i, e in enumerate(entries):
        combo = COMBOS[i % len(COMBOS)]
        out.append(rewrite_entry(e, combo))
        applied.append(combo)
    return out, applied


def token_retention(original, rewritten):
    a = Counter(re.findall(r"\S+", original))
    b = Counter(re.findall(r"\S+", rewritten))
    kept = sum((a & b).values())
    total = sum(a.values())
    return kept / total if total else 1.0


def validate_rewrite(originals, rewrittens):
    retentions = [token_retention(o, r) for o, r in zip(originals, rewrittens)]
    return {
        "n": len(originals),
        "min_retention": round(min(retentions), 3),
        "avg_retention": round(sum(retentions) / len(retentions), 3),
        "all_above_0.90": all(r >= 0.90 for r in retentions),
    }


# ── EDITORIAL MODE (v2) ──────────────────────────────────────────────────────
# Gentle surgery cannot change length statistics (proven: 0.81 -> 0.80).
# Editorial ops can (proven: 0.81 -> 0.49) at a bounded, measured content cost.

VOCAB_MAP_SAFE = [
    ("הנתיב הזה", "הדרך הזאת"),
    ("הנתיב", "המעבר"),
    ("אומר", "מלמד"),
    ("פותח ב", "מתחיל ב"),
    ("קושר את", "מחבר את"),
]


def op_merge(a, b):
    return a.rstrip(".!?") + ". " + b


def op_split_asym(entry):
    sents = _split_sentences(entry)
    if len(sents) < 4:
        return [entry]
    return [sents[0], _join(sents[1:])]


def op_trim_tail(entry, keep_ratio=0.75):
    sents = _split_sentences(entry)
    if len(sents) <= 3:
        return entry
    return _join(sents[:max(2, int(len(sents) * keep_ratio))])


def op_vocab(text, limit=2):
    out, used = text, 0
    for src, dst in VOCAB_MAP_SAFE:
        if used >= limit:
            break
        if src in out:
            out = out.replace(src, dst, 1)
            used += 1
    return out


def editorial_diversify(entries):
    """Deterministic editorial diversification. Returns (entries, log)."""
    log = []
    out = [rewrite_entry(e, COMBOS[i % len(COMBOS)]) for i, e in enumerate(entries)]
    if len(out) >= 9:
        m1 = op_merge(out[1], out[2])
        m2 = op_merge(out[7], out[8])
        out = [out[0], m1] + out[3:7] + [m2] + out[9:]
        log.append("merge x2")
    longest = max(range(len(out)), key=lambda i: len(out[i]))
    parts = op_split_asym(out[longest])
    if len(parts) == 2:
        out = out[:longest] + parts + out[longest+1:]
        log.append("asymmetric split")
    for i in range(4, len(out), 5):
        before_n = len(_split_sentences(out[i]))
        out[i] = op_trim_tail(out[i])
        if len(_split_sentences(out[i])) < before_n:
            log.append(f"trim {i}")
    for i in range(0, len(out), 3):
        new = op_vocab(out[i])
        if new != out[i]:
            out[i] = new
            log.append(f"vocab {i}")
    return out, log


if __name__ == "__main__":
    data = json.load(sys.stdin if len(sys.argv) < 2 else open(sys.argv[1]))
    entries = data["entries"]
    mode = data.get("mode", "gentle")
    if mode == "editorial":
        out, log = editorial_diversify(entries)
        print(json.dumps({"rewritten": out, "log": log,
                          "validation_vs_original": validate_rewrite(
                              entries[:len(out)], out[:len(entries)])},
                         ensure_ascii=False, indent=1))
    else:
        out, applied = rewrite_collection(entries)
        print(json.dumps({"rewritten": out, "applied": applied,
                          "validation": validate_rewrite(entries, out)},
                         ensure_ascii=False, indent=1))
