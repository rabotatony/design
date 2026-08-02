# AI Image Detector

A Python tool that scans images for AI-generation signatures (frequency ceilings,
AI palettes, uniform texture, JPEG block artifacts) and optionally corrects them.
Built to keep AI-generated assets out of design projects.

## Quick Start

```bash
# Scan a single image
python3 detector.py image.jpg

# Scan a directory, fix AI images, write report
python3 detector.py ./images --scan --fix --report report.md
```

## Web App

```bash
python3 server.py
# Open http://localhost:8765
```

Drag & drop images, see scores, click Fix, download corrected images.
No build tools — vanilla JS frontend served by FastAPI.

## How It Works

Six detectors run on each image, each returns a 0–1 score:

1. **frequency_ceiling** — FFT knee sharpness; AI images have a spectral cutoff.
2. **noise_pattern** — JPEG: 8×8 block energy + chroma noise. PNG: intensity-variance correlation.
3. **palette** — KMeans color clusters vs known AI gradient centroids.
4. **composition** — symmetry (std-normalized) + center/edge brightness ratio.
5. **texture_uniformity** — Laplacian variance CV across 64×64 blocks.
6. **metadata** — EXIF camera data vs AI software tags (Stable Diffusion, etc.).

Total score = weighted average. Verdict: `ai_likely` (>0.6), `uncertain` (0.4–0.6), `human_likely` (<0.4).

## Corrections

Applied only to detectors scoring > 0.5:

- **fix_palette** — hue shift 8–15°, saturation reduction 5–10%.
- **fix_texture** — spatially-varying line texture via 4×4 multiplier grid.
- **fix_composition** — asymmetric crop + micro-rotation (0.4–1.2°).

## CLI Reference

| Command | Action |
|---------|--------|
| `python3 detector.py <image>` | Print diagnosis JSON |
| `python3 detector.py <image> --fix` | Correct single image, print before/after |
| `python3 detector.py <image> --fix -o out.png` | Correct to custom path |
| `python3 detector.py <dir> --scan` | Scan directory, print JSON summary |
| `python3 detector.py <dir> --scan --fix` | Scan + fix all AI images |
| `python3 detector.py <dir> --scan --report r.md` | Scan + write markdown report |
| `python3 calibrate.py evaluate <ai_dir> <real_dir>` | Calibrate on labeled data |
| `python3 calibrate.py evaluate <ai> <real> --apply` | Calibrate + update weights |
| `python3 calibrate.py compare <before> <after>` | Measure correction effectiveness |
| `bash scan_project.sh` | Scan parent project dirs |

## Calibration

```bash
# Put known-AI images in ai/, known-real in real/
python3 calibrate.py evaluate ai/ real/
# Accuracy, per-detector separation, suggested weights printed as JSON
```

## Integration

npm scripts (in parent `package.json`):

```bash
npm run scan:ai        # scan public/
npm run scan:ai:fix    # scan + fix
npm run scan:ai:all    # scan all project dirs
npm run scan:ai:check  # exit 1 if AI detected (CI/pre-commit)
```

Pre-commit hook (blocks AI image commits):

```bash
cp ai-detector/hooks/pre-commit-sample .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Accuracy

95% on 20 real+AI images (10 picsum photos, 10 synthetic AI).
See `test_data/FINDINGS.md` for full calibration report.

Known limitation: pastel radial vignettes can score below threshold (1 false negative).

## Development

```bash
pytest tests/ -v          # 45 tests
python3 calibrate.py evaluate test_data/ai test_data/real
```

```
detector.py       # 6 detectors + corrections + CLI
calibrate.py      # evaluate / apply_weights / compare
tests/            # 45 tests
test_data/        # calibration data + FINDINGS.md
scan_project.sh   # project scanner
hooks/            # pre-commit sample
```
