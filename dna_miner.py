"""
dna_miner.py — reads an existing project (CSS + content) and proposes a
DomainDNA with per-root confidence and evidence. Closes the auto-loop:
project in -> DNA proposed -> composer generates -> detectors verify -> apply.

Honest design: roots that cannot be derived (signature) are flagged
needs_human with raw hints, not invented.
"""
import re
import json

try:
    from he_text import domain_terms as _he_domain_terms, tokenize_he as _he_tokenize
except Exception:
    _he_domain_terms = None
    _he_tokenize = None
try:
    from he_text import domain_terms_auto as _domain_terms_auto, detect_language as _detect_lang
except Exception:
    _domain_terms_auto = None
    _detect_lang = None
import hashlib
from collections import Counter


def _luminance(rgb):
    r, g, b = (c / 255.0 for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def mine_css(css):
    evidence = []
    vars_colors = re.findall(r'(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})', css)
    structural = {}
    for name, hx in vars_colors:
        key = name.lower()
        if 'background' in key and 'background' not in structural:
            structural['background'] = hx
        if 'foreground' in key and 'ink' not in structural:
            structural['ink'] = hx
        if 'primary' in key and 'primary' not in structural:
            structural['primary'] = hx
    anchors = [structural[r] for r in ('background', 'ink', 'primary') if r in structural]
    materials = []
    light_source = None
    if 'background' in structural:
        bg = _hex_to_rgb(structural['background'])
        lum = _luminance(bg)
        warm = (bg[0] - bg[2]) > 15
        if lum > 0.65 and warm:
            materials.append('parchment')
            evidence.append('background %s: warm light surface = parchment family' % structural['background'])
        elif lum < 0.3:
            materials.append('ink')
            evidence.append('background %s: deep dark = ink/night family' % structural['background'])
        elif lum < 0.45:
            materials.append('night')
    if 'primary' in structural:
        pr = _hex_to_rgb(structural['primary'])
        if 0.2 < _luminance(pr) < 0.65 and pr[0] > pr[2]:
            light_source = 'candle'
            materials.append('candle-metal')
            evidence.append('primary %s: warm aged-metal note = candlelight' % structural['primary'])
    vocab = {'קלף': 'parchment', 'דיו': 'ink', 'נר': 'candle', 'לילה': 'night',
             'שנהב': 'ivory', 'זהב': 'gold', 'אבן': 'stone', 'מים': 'water'}
    found_vocab = sorted(set(mat for word, mat in vocab.items() if word in css))
    if found_vocab:
        evidence.append('material vocabulary in CSS comments: %s' % found_vocab)
        for mat in found_vocab:
            if mat not in materials:
                materials.append(mat)
    durations = re.findall(r'(?:animation|transition)[^;]*?(\d+(?:\.\d+)?)(m?s)', css)
    rhythm = None
    if durations:
        secs = [float(v) * (0.001 if u == 'ms' else 1) for v, u in durations]
        base = Counter(round(s * 10) / 10 for s in secs).most_common(1)[0]
        share = base[1] / len(secs)
        rhythm = {'dominant_s': base[0], 'share': round(share, 2), 'n': len(secs)}
        evidence.append('motion: %d durations, share %.2f of %.1fs' % (len(secs), share, base[0]))
    radii = re.findall(r'--radius[a-z-]*\s*:\s*([^;]+);', css)
    radius_uniform = len(set(r.strip() for r in radii)) <= 1 if radii else None
    layout = 'emanation-candidate' if css.count('flex-direction: column') > css.count('grid-template') else 'grid-mixed'
    return {'anchors': anchors, 'materials': materials, 'light_source': light_source,
            'rhythm': rhythm, 'radius_uniform': radius_uniform, 'layout': layout,
            'evidence': evidence}


def mine_text(texts):
    full = ' '.join(t for t in texts if t)
    if len(full) < 200:
        return {'voice': None, 'confidence': 0.0, 'evidence': ['insufficient text']}
    sents = [s.strip() for s in re.split(r'[.!?]\s+', full) if len(s.strip()) > 2]
    words = re.findall(r'\S+', full)
    n_words = max(1, len(words))
    avg_len = sum(len(s) for s in sents) / max(1, len(sents))
    sources = len(re.findall(r'[\u0590-\u05FF\w]+\s*[\(]\d{4}[\)]', full))
    source_density = sources / (n_words / 100.0)
    excl = full.count('!') / (n_words / 100.0)
    first_pl = len(re.findall(r'אנחנו', full)) / (n_words / 100.0)
    traits = []
    if avg_len < 90:
        traits.append('short declarative sentences')
    if source_density > 0.3:
        traits.append('sources named plainly (%.1f/100w)' % source_density)
    if excl < 0.1:
        traits.append('no exclamations')
    if first_pl > 0.05:
        traits.append('first-person plural')
    if source_density > 0.3 and excl < 0.1:
        voice = 'Quiet scholar'
    elif excl < 0.3:
        voice = 'Measured, plain register'
    else:
        voice = 'Open, expressive register'
    if traits:
        voice += ': ' + ', '.join(traits)
    conf = min(1.0, 0.3 + 0.2 * (1 if source_density > 0.3 else 0)
               + 0.2 * (1 if excl < 0.1 else 0) + 0.3 * (1 if avg_len < 120 else 0))
    return {'voice': voice, 'confidence': round(conf, 2),
            'evidence': ['avg_sent_len=%.0f' % avg_len, 'source_density=%.2f/100w' % source_density,
                         'exclamations=%.2f/100w' % excl, 'words=%d' % n_words]}


KNOWN_STRUCTURES = {22: 'letters/paths (22)', 10: 'sefirot/tree (10)', 7: 'days/branches (7)',
                    12: 'tribes/zodiac (12)', 5: 'petals/books (5)', 4: 'worlds/elements (4)'}


def mine_structure(content_sources):
    counts = []
    for src in content_sources:
        nums = re.findall(r'\bnumber\s*:\s*(\d+)', src)
        if nums:
            counts.append(len(set(int(i) for i in nums)))
        letters = re.findall(r'\bletter\s*:\s*([\u0590-\u05FF])', src)
        if letters:
            counts.append(len(set(letters)))
    evidence = []
    candidates = []
    for c in sorted(set(counts)):
        note = KNOWN_STRUCTURES.get(c, '%d-fold structure' % c)
        candidates.append({'count': c, 'reading': note})
        evidence.append('repeated structure of %d items -> %s' % (c, note))
    field_names = Counter()
    for src in content_sources:
        for f in re.findall(r'^\s{2,6}([a-zA-Z_]\w*)\??:', src, re.M):
            field_names[f] += 1
    schema = [f for f, c in field_names.most_common(8) if c >= 5]
    if schema:
        evidence.append('repeated field schema: %s' % ', '.join(schema[:6]))
    conf = min(1.0, 0.2 * len(candidates) + (0.3 if schema else 0))
    return {'candidates': candidates, 'schema': schema, 'confidence': round(conf, 2), 'evidence': evidence}




def mine_domain_vocab(texts):
    """Extract the project's own DOMAIN vocabulary from its content.
    Multilingual: detects language (he/en/mixed) and routes to the right
    tokenizer, so function words don't leak in. Returns the most distinctive
    domain terms + the detected language."""
    full = " ".join(t for t in texts if t)
    lang = _detect_lang(full) if _detect_lang else "unknown"
    extractor = _domain_terms_auto or _he_domain_terms
    if extractor is None or len(full) < 100:
        return {"terms": [], "confidence": 0.0, "language": lang,
                "evidence": ["he_text unavailable or insufficient text"]}
    terms = extractor(full, top_n=12, min_count=2)
    if not terms:
        return {"terms": [], "confidence": 0.0, "language": lang,
                "evidence": ["no distinctive domain terms found"]}
    conf = min(1.0, 0.3 + 0.05 * len(terms))
    return {"terms": terms, "confidence": round(conf, 2), "language": lang,
            "evidence": ["language=%s, top domain terms: %s" % (lang, ", ".join(terms[:8]))]}


def mine_project(css, texts, content_sources):
    # Handle None inputs gracefully
    if css is None:
        css = ""
    if texts is None:
        texts = []
    if content_sources is None:
        content_sources = []
    css_f = mine_css(css)
    voice_f = mine_text(texts)
    motif_f = mine_structure(content_sources)
    dna, confidence, evidence = {}, {}, {}
    if css_f['materials']:
        dna['material'] = ' + '.join(css_f['materials'])
        confidence['material'] = min(1.0, 0.4 + 0.2 * len(css_f['materials']))
    else:
        dna['material'] = None
        confidence['material'] = 0.0
    evidence['material'] = css_f['evidence']
    if css_f['anchors']:
        dna['palette_logic'] = 'anchors from existing system: %s' % ', '.join(css_f['anchors'])
        confidence['palette_logic'] = 0.9
    else:
        dna['palette_logic'] = None
        confidence['palette_logic'] = 0.0
    evidence['palette_logic'] = ['structural colors parsed from CSS']
    dna['voice'] = voice_f['voice']
    confidence['voice'] = voice_f['confidence']
    vocab_f = mine_domain_vocab(texts)
    dna['domain_vocab'] = vocab_f['terms']
    confidence['domain_vocab'] = vocab_f['confidence']
    evidence['domain_vocab'] = vocab_f['evidence']
    evidence['voice'] = voice_f['evidence']
    if motif_f['candidates']:
        dna['motif'] = 'the %s as organizing principle' % motif_f['candidates'][0]['reading']
        confidence['motif'] = motif_f['confidence']
        evidence['motif'] = motif_f['evidence']
    else:
        # Infer motif from domain_vocab when structure detection fails
        vocab_f = mine_domain_vocab(texts)
        if vocab_f['terms']:
            top_terms = vocab_f['terms'][:3]
            dna['motif'] = 'the %s as organizing principle' % ', '.join(top_terms)
            confidence['motif'] = min(0.4, vocab_f['confidence'])
            evidence['motif'] = ['inferred from domain vocab: ' + ', '.join(top_terms)]
        else:
            dna['motif'] = None
            confidence['motif'] = 0.0
            evidence['motif'] = ['no motif detected from structure or domain vocab']
    dna['hierarchy_logic'] = css_f['layout']
    confidence['hierarchy_logic'] = 0.5
    evidence['hierarchy_logic'] = ['layout signal from CSS']
    if css_f['rhythm']:
        dna['rhythm_logic'] = 'dominant duration %.1fs (share %.2f)' % (css_f['rhythm']['dominant_s'], css_f['rhythm']['share'])
        confidence['rhythm_logic'] = min(1.0, css_f['rhythm']['share'])
    else:
        dna['rhythm_logic'] = None
        confidence['rhythm_logic'] = 0.0
    evidence['rhythm_logic'] = [e for e in css_f['evidence'] if 'motion' in e]
    dna['signature'] = None
    confidence['signature'] = 0.0
    hints = [c['reading'] for c in motif_f['candidates']]
    evidence['signature'] = ['signature cannot be mined; raw hints: %s' % (hints if hints else 'none')]
    needs_human = sorted([k for k in dna if dna[k] is None or confidence[k] < 0.5])
    return {'dna': dna, 'confidence': confidence, 'evidence': evidence, 'needs_human': needs_human}


def fingerprint(result):
    return hashlib.md5(json.dumps(result, sort_keys=True, ensure_ascii=False).encode()).hexdigest()