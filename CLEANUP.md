# CLEANUP PLAN for the design repo

The repo has 44 Python files, many of which are redundant. This document
outlines a cleanup plan to consolidate the codebase.

## PROGRESS

- [x] identity_miner.py + identity_miner_v2.py consolidated (identity_miner_v2.py now redundant)
- [x] Design generation consolidated into design.py (replaces 11 redundant modules)
- [ ] Remove the redundant modules (needs testing first)
- [ ] Review 11 other modules

## Consolidated modules

### design.py (NEW - consolidated design generation)

This single module replaces the 11 redundant design generation modules:
- design_generator.py
- design_language.py
- design_pipeline.py
- design_system_generator.py
- designer.py
- composer.py
- layout_generator.py
- component_generator.py
- pattern_generator.py
- guidelines_generator.py
- style_generator.py

Everything in design.py is TRULY GENERATIVE (computed from algorithms,
not lookup tables). The redundant modules are template-based and should
be removed.

### identity_miner.py (CONSOLIDATED v1+v2)

Combined identity_miner.py (motifs, materials, character, voice) with
identity_miner_v2.py (narrative, audience, purpose, tone). The
identity_miner_v2.py file is now redundant.

## Essential modules (KEEP)

- detector.py — image AI detection
- text_detector.py — text AI detection (100% accuracy on comprehensive test)
- design_scan.py — CSS AI detection
- code_detector.py — code AI detection
- coherence.py — coherence detection
- apply.py — CSS redesign
- text_rewriter.py — text de-AI
- design.py — CONSOLIDATED design generation (TRULY GENERATIVE)
- generative_design.py — original generative design (keep for reference)
- generative_pipeline.py — unified generative pipeline
- design_tool.py — CLI tool
- identity_miner.py — identity mining (CONSOLIDATED v1+v2)
- he_text.py — Hebrew text utilities
- calibrate.py — calibration
- eval_harness.py — evaluation harness
- feature_extractor.py — feature extraction
- trained_classifier.py — trained classifier
- color_system_generator.py — color harmony generation
- text_deep.py — deep text analysis

## Redundant modules (TO REMOVE after testing)

Design generation (replaced by design.py):
- design_generator.py, design_language.py, design_pipeline.py,
  design_system_generator.py, designer.py, composer.py,
  layout_generator.py, component_generator.py, pattern_generator.py,
  guidelines_generator.py, style_generator.py

Identity mining (replaced by identity_miner.py):
- identity_miner_v2.py

## Other modules (REVIEW)

- codegen.py, coherence_lifter.py, corpus_detector.py, machine.py,
  pagegen.py, pipeline.py, redesigner.py, server.py, tell_registry.py,
  variations.py, conftest.py

## Recommended action

1. [x] Consolidate identity_miner.py + identity_miner_v2.py
2. [x] Consolidate design generation into design.py
3. [ ] Remove the redundant modules (needs testing first)
4. [ ] Review the 11 other modules
5. This would reduce the codebase from 44 files to ~20 files

## Note

This cleanup would make the system more maintainable and easier to use.
However, it requires careful testing to ensure nothing breaks.
