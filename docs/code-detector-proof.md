# code_detector — proof (detection layer complete)

## Battery results

| sample | score | verdict |
|---|---|---|
| SiteHeader.tsx (rose, 342L) | 0.00 | human_likely |
| TodayPage.tsx (rose, 1005L) | 0.08 | human_likely |
| GematriaCalculator.tsx (rose, 225L) | 0.09 | human_likely |
| TarotCardImage.tsx (rose, 32L) | 0.00 | human_likely |
| **rose average (1604 lines)** | **0.042** | human_likely |
| clean synthetic control | 0.00 | human_likely |
| AI-style sample (tells stuffed) | 0.97 | ai_likely |

## What it detects

- redundant_comments: 'This function/component...' restating patterns
- console_leftover: console.log/warn/error left in
- todo_trails: TODO/FIXME/HACK/XXX density
- generic_naming: data/result/item/temp/value identifier density
- placeholders: lorem/example/placeholder strings

## Reading of rose's code

Rose's TSX scores near zero: Hebrew intent-comments (not restating),
zero console.log, zero TODOs, domain naming. The code layer of Shoshana
is already clean — the machine confirms it, no changes needed there.

## Detection layer status

| layer | detector | proven on |
|---|---|---|
| images | detector.py | 95% calibration |
| text entries | text_detector.py | precision 1.00 |
| collections | corpus_detector.py | 0.81->caught |
| CSS | design_scan.py | rose 0.81 -> applied 1.0 |
| code | code_detector.py | this battery |