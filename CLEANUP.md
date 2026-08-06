# CLEANUP PLAN for the design repo

The repo has 44 Python files, many of which are redundant. This document
outlines a cleanup plan to consolidate the codebase.

## Essential modules (KEEP)

These are the core modules that the system depends on:

- detector.py — image AI detection
- text_detector.py — text AI detection (100% accuracy on comprehensive test)
- design_scan.py — CSS AI detection
- code_detector.py — code AI detection
- coherence.py — coherence detection
- apply.py — CSS redesign
- text_rewriter.py — text de-AI
- generative_design.py — TRULY GENERATIVE design system
- generative_pipeline.py — unified generative pipeline
- design_tool.py — CLI tool
- identity_miner.py — identity mining
- he_text.py — Hebrew text utilities
- calibrate.py — calibration
- eval_harness.py — evaluation harness
- feature_extractor.py — feature extraction
- trained_classifier.py — trained classifier
- color_system_generator.py — color harmony generation
- text_deep.py — deep text analysis

## Redundant design generation modules (CONSOLIDATE into generative_design.py)

These modules do similar things to generative_design.py and should be consolidated:

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

The generative_design.py module is the TRULY GENERATIVE one (computes values
from algorithms, not lookup tables). The other modules are template-based and
should be consolidated or removed.

## Redundant identity mining modules (CONSOLIDATE into identity_miner.py)

These modules do similar things to identity_miner.py and should be consolidated:

- identity_extractor.py
- identity_miner_v2.py
- dna_miner.py

The identity_miner.py module is the primary one. The others are redundant.

## Other modules (REVIEW)

These modules need review to determine if they are essential or redundant:

- codegen.py
- coherence_lifter.py
- corpus_detector.py
- machine.py
- pagegen.py
- pipeline.py
- redesigner.py
- server.py
- tell_registry.py
- variations.py
- conftest.py

## Recommended action

1. Consolidate the 11 redundant design generation modules into generative_design.py
2. Consolidate the 3 redundant identity mining modules into identity_miner.py
3. Review the 11 other modules and remove any that are redundant
4. This would reduce the codebase from 44 files to ~20 files

## Note

This cleanup would make the system more maintainable and easier to use.
However, it requires careful testing to ensure nothing breaks.
