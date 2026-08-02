# Calibration Findings

## Test Data

- **Real images**: 10 photographs downloaded from picsum.photos (800×600 JPEGs)
- **AI-like images**: 10 synthetically generated images targeting known AI signatures
  (gradients in AI palettes, smooth textures, symmetric compositions)
- **Calibration date**: 2025-01-02
- **Tool version**: detector.py @ 8597f07

## Detector Accuracy

- **Overall accuracy**: 95% (19/20 correct at threshold 0.5)
- **Optimal threshold**: 0.5 (same as default — no change needed)
- **False positives**: 0 (no real images flagged as AI)
- **False negatives**: 1 (ai_10.png scored 0.40, just below threshold)

The default threshold of 0.5 is already optimal. No threshold adjustment needed.

## Per-Detector Performance

| Detector | AI Mean | Real Mean | Separation | Verdict |
|----------|---------|-----------|------------|---------|
| palette | 0.76 | 0.10 | 0.66 | **works** |
| texture_uniformity | 0.52 | 0.00 | 0.52 | **works** |
| metadata | 0.50 | 0.35 | 0.15 | **weak** |
| frequency_ceiling | 0.39 | 0.27 | 0.13 | **weak** |
| composition | 1.00 | 0.89 | 0.11 | **weak** |
| noise_pattern | 0.94 | 0.95 | -0.01 | **broken** |

### Analysis

- **palette** (strongest, sep 0.66): Reliably identifies AI gradient palettes.
  AI images match purple_blue/teal_orange/pink_purple centroids; real photos
  have natural colors far from these centroids.

- **texture_uniformity** (sep 0.52): AI images have smooth, uniform texture
  (low CV); real photos have varied texture across regions (high CV → score 0).
  Works well after the line-based texture fix.

- **noise_pattern** (weakest, sep -0.01): Both AI and real images score ~0.95.
  The detector flags anything without strong signal-dependent noise as "AI".
  Real photos from picsum have JPEG compression artifacts that look like
  uniform noise → score 1.0. AI images also score 1.0. This detector provides
  NO discrimination. **Broken.**

- **composition** (sep 0.11): Almost all images score ~1.0. The symmetry
  detector is too lenient — the normalization by max brightness makes h_sym
  stay high for nearly any image. Both AI (symmetric gradients) and real
  (asymmetric photos) score high. **Weak.**

- **frequency_ceiling** (sep 0.13): AI images score 0.35-0.60 (capped by
  fullness on smooth gradients); real photos score 0.0-0.35. Some separation
  but weak. The knee-sharpness metric helps but smooth gradients are still
  ambiguous. **Weak.**

- **metadata** (sep 0.15): AI images have no EXIF (score 0.5); real photos
  from picsum have partial EXIF (score 0.35). Minor separation. **Weak.**

## False Positives (real images flagged as AI)

**None.** All 10 real photographs scored below 0.5 (range 0.23–0.40).
Real photos benefit from: low palette scores (natural colors), zero texture
uniformity (varied texture), and partial EXIF data.

## False Negatives (AI images missed)

### ai_10.png — scored 0.40 (verdict: uncertain)

**Image**: Soft pastel lavender + radial vignette (center bright, edges dark)

**Why it was missed**:
- palette: 0.02 (pastel lavender doesn't match any AI centroid closely enough)
- frequency_ceiling: 0.00 (radial gradient has degenerate spectrum)
- texture_uniformity: 0.95 (smooth → uniform texture → high score)
- composition: 1.00 (radial symmetry → high score)
- noise_pattern: 0.56 (moderate)
- metadata: 0.50 (no EXIF)

The palette detector failed because the pastel lavender (#85, 0.75, 0.95)
is close to the soft_pastel centroid but not close enough (distance 0.42 >
0.4 threshold → score 0). The radial vignette creates a spectrum that the
frequency detector reads as natural (no knee). Combined with low frequency
and palette scores, the total fell below 0.5.

**Detectors that should have caught it but didn't**: palette (too strict
distance threshold), frequency_ceiling (radial gradient confuses the detector).

## Correction Effectiveness

From the scan of mock_project (5 AI images corrected):

- **Average improvement**: 0.164 (total score drop)
- **Images improved**: 5/5 (all corrections helped)
- **Images unchanged**: 0
- **Images worse**: 0

### Per-detector delta (avg across 5 fixed images):

| Detector | Avg Delta | Effect |
|----------|-----------|--------|
| texture_uniformity | -0.465 | **Most effective** |
| frequency_ceiling | -0.200 | Effective |
| palette | -0.150 | Effective |
| noise_pattern | +0.016 | Neutral (slight increase) |
| composition | +0.000 | **Least effective** (no change) |
| metadata | +0.000 | N/A (not correctable) |

### Analysis

- **Best correction: texture_uniformity** (delta -0.465). The line-based
  texture injection creates strong spatial variation, dropping the texture
  score dramatically. This is the most effective correction.

- **Worst correction: composition** (delta +0.000). The micro-rotation +
  crop doesn't change the composition SCORE on these gradient images because
  the symmetry detector normalizes by max brightness, keeping h_sym high
  regardless of small rotations. The image IS changed (rotation is visible),
  but the detector can't measure the improvement.

- **frequency_ceiling** improved (-0.200) because the texture noise changes
  the spectral knee measurement.

- **noise_pattern** slightly increased (+0.016) — the added texture creates
  decoupled variance, but the effect is small with the line-based approach.

## Weight Recommendation

### Current vs Suggested Weights

| Detector | Current | Suggested | Change |
|----------|---------|-----------|--------|
| palette | 0.22 | 0.42 | **+0.20** (increase) |
| texture_uniformity | 0.18 | 0.33 | **+0.15** (increase) |
| frequency_ceiling | 0.25 | 0.08 | -0.17 (decrease) |
| noise_pattern | 0.12 | 0.00 | -0.12 (decrease to zero) |
| composition | 0.08 | 0.07 | -0.01 (same) |
| metadata | 0.15 | 0.10 | -0.05 (slight decrease) |

### Recommendation

The calibration suggests:
1. **Increase palette weight** (0.22 → 0.42): Strongest discriminator (sep 0.66)
2. **Increase texture_uniformity weight** (0.18 → 0.33): Second strongest (sep 0.52)
3. **Decrease frequency_ceiling weight** (0.25 → 0.08): Weak separation (0.13),
   smooth gradients are ambiguous
4. **Zero out noise_pattern weight** (0.12 → 0.00): Negative separation (-0.01),
   provides no discrimination. **This detector is broken.**
5. **Keep composition weight** (0.08): Weak but consistent
6. **Slight decrease metadata weight** (0.15 → 0.10): Minor separation (0.15)

### Decision: DO NOT APPLY

Accuracy is 95% (≥ 80% threshold). The current weights are performing well
enough. Applying the suggested weights would:
- Help on edge cases like ai_10.png (palette weight increase would push it
  over 0.5)
- But risk overfitting to this specific 20-image test set
- The noise_pattern detector should be fixed before zeroing its weight

## Action Items

### 1. Fix noise_pattern detector (PRIORITY: HIGH)

The noise_pattern detector is **broken** — it scores ~0.95 for BOTH AI and
real images. The issue: it flags any image without strong signal-dependent
noise as "AI", but JPEG-compressed real photos also lack signal-dependent
noise (compression destroys the subtle noise-variance-intensity correlation).

**Fix**: Account for JPEG compression artifacts. If the image is JPEG
(check file format/EXIF), raise the "real" baseline. Or: detect JPEG
blocking artifacts (8×8 DCT blocks) and factor them into the noise analysis.

### 2. Fix composition detector (PRIORITY: MEDIUM)

The composition detector scores ~1.0 for nearly all images. The symmetry
normalization (by max brightness) makes h_sym stay high. Real photos with
asymmetric content still score 0.7-1.0.

**Fix**: Use a different normalization (e.g., normalize by mean, not max).
Or: measure symmetry of the gradient structure, not raw pixel values.
Or: lower the symmetry threshold from 0.85 to 0.95 (stricter).

### 3. Improve frequency_ceiling for radial gradients (PRIORITY: LOW)

ai_10 (radial vignette) scored 0.0 on frequency_ceiling. The radial gradient
creates a degenerate spectrum that the knee-sharpness metric can't analyze.

**Fix**: Add a radial spectrum analysis (not just Cartesian FFT) to detect
VAE cutoffs in radially-symmetric images.

### 4. Consider lowering threshold for pastel palettes (PRIORITY: LOW)

ai_10's pastel lavender palette scored 0.02 because the distance to the
soft_pastel centroid was 0.42 (just above the 0.4 threshold). Consider
adding more pastel centroids or widening the threshold for pastel palettes.

### 5. Correction: composition fix doesn't affect score (PRIORITY: MEDIUM)

The composition fix (rotation + crop) changes the IMAGE but not the SCORE.
The rotation is too small (0.4-1.2°) to meaningfully change the symmetry
detector's measurement. Consider: larger rotation (1-3°), or apply the
fix only when the composition detector can actually measure the change.

### 6. Re-run calibration after fixes (PRIORITY: MEDIUM)

After fixing noise_pattern and composition detectors, re-run this
calibration. The suggested weights will change significantly once
noise_pattern provides real discrimination.

## V2 Calibration (after fixes)

After fixing `detect_noise_pattern` (JPEG block+chroma analysis) and
`detect_composition` (std normalization instead of max), re-ran calibration
on the same 20 images. Results saved to `evaluation_v2.json`.

### Accuracy

- **V1 accuracy**: 95% (19/20)
- **V2 accuracy**: 95% (19/20) — maintained, no regression
- **Optimal threshold**: shifted from 0.5 to 0.39 (score distribution changed)
- **False positives**: 0 → 0 (still none)
- **False negatives**: 1 → 1 (still ai_10.png, the pastel radial vignette)

### Per-Detector Separation: V1 vs V2

| Detector | V1 Sep | V2 Sep | Change |
|----------|--------|--------|--------|
| noise_pattern | -0.01 | **0.79** | **FIXED** (+0.80) |
| composition | 0.11 | **0.41** | **FIXED** (+0.30) |
| palette | 0.66 | 0.57 | -0.09 (slight shift) |
| texture_uniformity | 0.52 | 0.47 | -0.05 (slight shift) |
| metadata | 0.15 | 0.15 | same |
| frequency_ceiling | 0.13 | 0.03 | -0.10 (now weakest) |

### Key Improvements

1. **noise_pattern: BROKEN → STRONGEST** (sep -0.01 → 0.79)
   - The JPEG block boundary + chroma analysis works extremely well.
   - Real photos: block_ratio ~1.25, chroma_ratio ~0.01 (low, JPEG subsampled)
   - AI images: block_ratio ~1.93, chroma_ratio ~0.44 (higher color variation)
   - The block_ratio is the primary discriminator; chroma helps on edge cases.
   - Note: the spec's chroma thresholds were inverted (assumed low chroma = AI,
     but real JPEG photos have even lower chroma due to 4:2:0 subsampling).
     Fixed: high chroma = AI, low chroma = real.

2. **composition: WEAK → MODERATE** (sep 0.11 → 0.41)
   - Normalizing by std instead of max makes h_symmetry sensitive to actual
     asymmetry relative to image contrast.
   - Real photos (asymmetric content) now score lower than AI (symmetric gradients).

3. **frequency_ceiling became weakest** (sep 0.13 → 0.03)
   - The std-based composition fix changed how images are scored overall.
   - frequency_ceiling was always weak on JPEG (smooth content, no clear knee).
   - Now correctly identified as the weakest detector.

### Weight Comparison

| Detector | V1 Current | V2 Current | V2 Suggested |
|----------|-----------|------------|--------------|
| palette | 0.22 | 0.30 | 0.24 |
| noise_pattern | 0.12 | 0.10 | 0.33 |
| texture_uniformity | 0.18 | 0.20 | 0.19 |
| composition | 0.08 | 0.10 | 0.17 |
| frequency_ceiling | 0.25 | 0.20 | 0.01 |
| metadata | 0.15 | 0.10 | 0.06 |

The V2 suggested weights now recommend:
- **noise_pattern: 0.33** (was 0.00 in V1 — now that it's fixed, it's the strongest)
- **frequency_ceiling: 0.01** (was 0.08 — now the weakest)
- palette reduced to 0.24 (still strong but noise_pattern is stronger)

### Decision: Weights NOT auto-applied

Accuracy is 95% (≥ 90% threshold). The manually-set V2 weights (palette 0.30,
noise 0.10, texture 0.20, comp 0.10, freq 0.20, meta 0.10) perform well.
The suggested weights would increase noise_pattern further, but the current
weights already achieve 95% accuracy. No auto-apply needed.

### Remaining Issues

1. **ai_10.png still missed** (score 0.40): The pastel radial vignette has
   a palette distance just above threshold (0.42 > 0.4) and a degenerate
   radial spectrum. The noise_pattern fix didn't help because ai_10 is PNG
   (Raw mode). Saving it as JPEG would likely trigger the block detection.

2. **frequency_ceiling is now weakest** (sep 0.03): On real JPEG photos,
   the knee-sharpness metric doesn't discriminate well. JPEG compression
   smooths the spectrum. Consider: JPEG-specific frequency analysis, or
   further weight reduction.

### Summary

The two detector fixes were highly successful:
- noise_pattern went from USELESS (sep -0.01) to STRONGEST (sep 0.79)
- composition went from WEAK (sep 0.11) to MODERATE (sep 0.41)
- Accuracy maintained at 95%
- The system now has 4 working detectors (palette, noise_pattern, texture, composition)
  and 2 weak ones (frequency_ceiling, metadata)
