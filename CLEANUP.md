# CLEANUP PLAN for the design repo — COMPLETED

The repo originally had 44 Python files, many redundant. This cleanup
consolidated the codebase from 44 files down to 35 files.

## COMPLETED ACTIONS

### 1. Consolidated identity mining
- identity_miner.py + identity_miner_v2.py -> identity_miner.py
- Added mine_identity_full() that combines both versions
- identity_miner_v2.py removed

### 2. Consolidated design generation
- Created design.py: single clean module combining 11 redundant modules
- Everything is TRULY GENERATIVE (computed from algorithms, not lookup tables)
- Removed the 10 redundant modules:
  - design_generator.py, design_language.py, design_pipeline.py,
    design_system_generator.py, layout_generator.py, component_generator.py,
    pattern_generator.py, guidelines_generator.py, style_generator.py,
    identity_miner_v2.py

### 3. Kept modules that are in use
- designer.py (used by codegen.py, pipeline.py, redesigner.py)
- composer.py (used by machine.py)

## CURRENT STATE (35 Python files)

Core detection:
- detector.py, text_detector.py, design_scan.py, code_detector.py, coherence.py

Redesign:
- apply.py, text_rewriter.py

Design generation:
- design.py (CONSOLIDATED, truly generative)
- generative_design.py, generative_pipeline.py (kept for reference)

Identity:
- identity_miner.py (CONSOLIDATED v1+v2)
- dna_miner.py, identity_extractor.py (kept, different functions)

Tools:
- design_tool.py (CLI), eval_harness.py, calibrate.py

Supporting:
- he_text.py, color_system_generator.py, feature_extractor.py,
  trained_classifier.py, text_deep.py, code_counter.py

Legacy (review later):
- codegen.py, coherence_lifter.py, corpus_detector.py, machine.py,
  pagegen.py, pipeline.py, redesigner.py, server.py, tell_registry.py,
  variations.py, conftest.py, designer.py, composer.py

## RESULT

Reduced from 44 to 35 Python files. The codebase is now cleaner and
more maintainable. The core design generation is consolidated into a
single truly-generative module (design.py).
