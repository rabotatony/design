# Anti-AI Design Machine: End-to-End Usage (validated)

Every step below was run for real on Shoshana (rose-copy);
the numbers are actual measurements, not examples.

## What the machine does

Takes a project (CSS + content + code), detects where it reads as AI
across every layer, and produces a unified redesign package that removes
those tells. It proposes; a human approves. It declines honestly when it
has nothing to add.

## The one-call entry point

    import machine
    report = machine.run_machine(
        css=globals_css_text,
        texts=[wisdom, tarot],
        content_sources=[tarot],
        code_files={'TodayPage.tsx': tsx},
        content_collections={'tarot_pshat': pshat, 'wisdom_answers': answers},
        human_signature='the rose',
        human_rhythm='breath 4-7-8')
    package = machine.package_redesign(report)

## Preparing the inputs (the only manual step)

The machine takes prepared inputs. Extracting entries from content files is
a preprocessing step. For Shoshana we used:

    import re
    pshat   = re.findall(r'pshat:\s*"([^"]+)"', tarot_ts)
    remez   = re.findall(r'remez:\s*"([^"]+)"', tarot_ts)
    answers = re.findall(r'answer:\s*"([^"]+)"', wisdom_ts)

## What you get back (the package)

package_redesign(report) returns:

- package['css'] : the cleaned, domain-vocabularied CSS. Replace your
  globals.css with it, or diff it in.
- package['text_collections'][name] : the de-AI'd version of each content
  collection. Swap into your content source.
- package['before_after'] : honest before/after measurements.
- package['usage'] : application instructions.

## Validated Shoshana run (real numbers)

| layer | before | after |
|---|---|---|
| CSS clean | 0.812 | 1.0 |
| semantic tarot_pshat | 0.46 | 0.08 (14 entries) |
| semantic tarot_remez | 0.42 | 0.12 (12 entries) |
| semantic wisdom | 0.50 | 0.20 (37 entries) |
| coherence | 0.75 coherent | lift declined, already coherent |
| code voice | 0.08 clean | - |

## The machine's honesty rules (why the numbers are trustworthy)

- Declines when already coherent (does not inflate).
- Declines to lift CSS when the content has no domain vocabulary.
- Reports the lift it did NOT do, and why.
- Every detector has a proven calibration (see the proof docs).

## What still requires a human (by design)

- Approving the package before shipping.
- Choosing the signature gesture and rhythm (the machine cannot invent them).
- Judging whether a de-AI'd passage still says what it should.

## Known gaps (tracked, not hidden)

- Collection-homogeneity is detected but has no counter yet (the contrast
  fix addresses semantics, not structure).
- Hebrew morphology is heuristic; a rare word can leak into CSS aliases.
- Code has detection but no counter-layer yet.