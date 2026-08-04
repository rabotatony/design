"""
he_text.py — Hebrew text processing foundation.

A comprehensive Hebrew stopword list + affix stripping + tokenizer, built so the
machine can reliably extract DOMAIN vocabulary from Hebrew content (instead of
leaking function words). This is the base the DNA miner and coherence detector use.

Design: Hebrew is an agglutinative language. Prepositions/conjunctions/articles are
prefixed (ה,ו,ב,כ,ל,מ,ש) and pronominal endings are suffixed (ם,ן,ים,ות,ה,ך,כם,כן).
We strip these so 'הספירה'/'ספירות'/'ספירה' all normalize toward the same stem.
"""
import re
from collections import Counter

# Function words: pronouns, prepositions, conjunctions, articles, copulas, adverbs.
STOPWORDS_HE = set("""
של על את הוא היא הם הן לא כן אם כי אבל או גם זה זאת אלה אלו מה מי איך למה מתי איפה
כאשר אז רק עוד מאוד מאד יותר מדי בין בתוך אל עד מתחת מעל לפני אחרי מול נגד אל מול
אין יש כל כלום אף אחד אחת שנים שתיים שלוש ארבע חמש שש שבע שמונה תשע עשר
היה הייתה היו היו היתה להיות הוא היא הם הן עצמו עצמה עצמם עצמן
שלי שלך שלו שלה שלנו שלכם שלהם שלי שלך
אני אתה את הוא היא אנחנו אתם אתן הם הן
לי לך לו לה לנו לכם להם לי לך
אותי אותך אותו אותה אותנו אותם אותן
זה הזאת הזה אלה אלו אלו אלה
כן לא לאו אולי אולי גם גם אולי רק רק עוד עוד מאוד מאוד
אז אז עכשיו עכשיו היום היום אתמול אתמול מחר מחר כבר כבר תמיד תמיד אף פעם
כמו כמו ככה ככה כך כך לכן לכן כי כי משום משום בגלל בגלל למרות למרות
בשביל בשביל עבור עבור בשביל כדי כדי בשביל למען למען
אבל אבל אך אך אולם אולם ברם ברם
""".split())

# AI style particles (tells, never domain vocabulary).
TELL_PARTICLES = {"אינו", "אינה", "אלא", "אינם", "אינן", "איננו", "איננה"}

# Prefixed function-word forms (article/preposition + common word) to drop outright.
PREFIXED_STOP = set("""
הוא היא הם הן הזה הזאת האלה האלו האדם העולם החיים האמת הדרך העבודה
בכל בכל בכל בכל על על על על על אל אל אל אל אל אל אל אל אל אל אל אל אל אל
""".split())

HE_PREFIXES = "הובכלמש"          # one-letter proclitics
HE_SUFFIXES = ["כם", "כן", "ים", "ות", "ם", "ן", "ה", "ך"]  # pronominal/number suffixes


def strip_affixes(word):
    w = word
    # strip a single proclitic if the remainder is a plausible word
    if len(w) > 3 and w[0] in HE_PREFIXES:
        cand = w[1:]
        if cand not in STOPWORDS_HE:
            w = cand
    # strip one pronominal/number suffix if the remainder stays plausible
    for suf in HE_SUFFIXES:
        if len(w) > len(suf) + 2 and w.endswith(suf):
            cand = w[:-len(suf)]
            if cand not in STOPWORDS_HE:
                w = cand
                break
    return w


def tokenize_he(text):
    words = re.findall(r"[\u0590-\u05FF]{2,}", text)
    out = []
    for w in words:
        if w in STOPWORDS_HE or w in TELL_PARTICLES or w in PREFIXED_STOP:
            continue
        w2 = strip_affixes(w)
        if w2 in STOPWORDS_HE or w2 in TELL_PARTICLES or len(w2) < 2:
            continue
        out.append(w2)
    return out


def domain_terms(text, top_n=12, min_count=2):
    toks = tokenize_he(text)
    if not toks:
        return []
    c = Counter(toks)
    return [w for w, n in c.most_common(top_n) if n >= min_count]
