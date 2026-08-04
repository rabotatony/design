# Hebrew text-layer deepening - proof

The biggest gap identified was: Hebrew morphology was heuristic, so function
words leaked into domain-vocabulary and coherence signals. This round deepens
the Hebrew layer in three steps, all proven on real rose content.

## 1. he_text.py (the foundation)

Comprehensive Hebrew stopword list (pronouns, prepositions, conjunctions,
copulas, adverbs) + affix stripping (proclitics ה,ו,ב,כ,ל,מ,ש and pronominal
suffixes ם,ן,ים,ות,ה,ך,כם,כן) + a tokenizer. So הספירה/ספירות/ספירה normalize
toward one stem instead of leaking as three 'domain' words.

## 2. dna_miner.mine_domain_vocab

Extracts the project's own domain vocabulary from its Hebrew content. On rose
tarot (pshat+remez) it returns confidence 0.9 with real words:
אות, ספר, מים, קראולי, פאפוס, נתיב, יציר (letter, book, water, Crowley, Papus, path).
mine_project now emits dna['domain_vocab'] + confidence + evidence.

## 3. coherence.he_tokens delegates to he_text

coherence's top-term/focus signals no longer leak function words. On rose content
the top terms are now סמל, פאפוס, אות, קראולי, לבן, צייר - real content words.

## Module-load note

dna_miner and coherence import he_text with a try/except fallback, so they keep
working even if he_text is not loaded. Load order for full functionality:
he_text, then dna_miner / coherence, then machine.

## Honest limits

- Affix stripping is rule-based, not a full morphological analyzer; rare or
  irregular forms can still leak.
- Domain-vocab confidence is a heuristic (term count), not semantic.
- The stopword list is broad but not exhaustive.