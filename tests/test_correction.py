import os
import json
import random
import numpy as np
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from detector import analyze, correct, fix_texture, fix_composition


def _save_rgb(arr, path):
    a = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a).save(path)
    return path


def _make_ai_like(path):
    h, w = 256, 256
    t = np.linspace(0, 1, w)
    c1 = np.array([0.48, 0.18, 0.97])
    c2 = np.array([0.13, 0.59, 0.95])
    line = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    grad = np.broadcast_to(line[None, :, :], (h, w, 3)).copy()
    return _save_rgb(grad, path)


def _make_natural(path):
    rng = np.random.default_rng(99)
    img = rng.random((256, 256, 3))
    img[:128, :128] *= 0.2
    return _save_rgb(img, path)


def _diag_json(img_path, json_path):
    res = analyze(img_path)
    with open(json_path, "w") as f:
        json.dump(res, f)
    return res


def test_correction_lowers_score_and_keeps_ssim(tmp_path):
    random.seed(0)
    np.random.seed(0)
    img_path = str(tmp_path / "ai.png")
    diag_path = str(tmp_path / "diag.json")
    out_path = str(tmp_path / "fixed.png")
    _make_ai_like(img_path)
    before = _diag_json(img_path, diag_path)

    summary = correct(img_path, diag_path, out_path)
    assert os.path.exists(out_path)
    assert summary["count"] >= 1

    after = analyze(out_path)
    drop = before["total_score"] - after["total_score"]
    assert drop >= 0.10 - 1e-6, f"score drop too small: {drop} (before={before['total_score']}, after={after['total_score']})"

    orig = np.asarray(Image.open(img_path).convert("RGB"))
    fixed = np.asarray(Image.open(out_path).convert("RGB"))
    if orig.shape != fixed.shape:
        fixed = np.asarray(
            Image.open(out_path).convert("RGB").resize((orig.shape[1], orig.shape[0]), Image.BILINEAR)
        )
    s = ssim(orig, fixed, channel_axis=2)
    assert s > 0.82, f"SSIM too low: {s}"

    tex_before = before["detectors"]["texture_uniformity"]["score"]
    tex_after = after["detectors"]["texture_uniformity"]["score"]
    assert tex_after < tex_before, f"texture not improved: {tex_before} -> {tex_after}"

    comp_before = before["detectors"]["composition"]["score"]
    comp_after = after["detectors"]["composition"]["score"]
    assert comp_after <= comp_before, f"composition increased: {comp_before} -> {comp_after}"


def test_correction_tiny_image_no_crash(tmp_path):
    img_path = str(tmp_path / "tiny.png")
    diag_path = str(tmp_path / "diag.json")
    out_path = str(tmp_path / "out.png")
    Image.fromarray(np.random.randint(0, 255, (1, 1, 3), np.uint8)).save(img_path)
    _diag_json(img_path, diag_path)
    summary = correct(img_path, diag_path, out_path)
    assert os.path.exists(out_path)
    arr = np.asarray(Image.open(out_path).convert("RGB"))
    assert arr.shape[0] >= 1 and arr.shape[1] >= 1


def test_no_corrections_when_all_low(tmp_path):
    img_path = str(tmp_path / "natural.png")
    diag_path = str(tmp_path / "diag.json")
    out_path = str(tmp_path / "out.png")
    _make_natural(img_path)
    before = _diag_json(img_path, diag_path)
    for name in ("palette", "texture_uniformity", "composition"):
        assert before["detectors"][name]["score"] < 0.5, (name, before["detectors"][name])

    summary = correct(img_path, diag_path, out_path)
    assert summary["count"] == 0

    orig = np.asarray(Image.open(img_path).convert("RGB"))
    fixed = np.asarray(Image.open(out_path).convert("RGB"))
    assert orig.shape == fixed.shape
    assert np.array_equal(orig, fixed), "output differs from input when no corrections applied"


def test_texture_fix_creates_variation(tmp_path):
    random.seed(42)
    np.random.seed(42)
    from scipy.ndimage import laplace
    h, w = 256, 256
    t = np.linspace(0, 1, w)
    line = np.array([0.48, 0.18, 0.97])[None, :] * (1 - t[:, None]) + np.array([0.13, 0.59, 0.95])[None, :] * t[:, None]
    grad = np.broadcast_to(line[None, :, :], (h, w, 3)).copy()
    arr = (np.clip(grad, 0, 1) * 255).astype(np.uint8)
    fixed, ok = fix_texture(arr, 1.0)
    assert ok
    gray = np.asarray(Image.fromarray(fixed).convert("L"), dtype=float) / 255.0
    lap = laplace(gray)
    vs = np.array([lap[i:i + 64, j:j + 64].var() for i in range(0, h - 63, 64) for j in range(0, w - 63, 64)])
    cv = vs.std() / (vs.mean() + 1e-6)
    assert cv > 0.3, f"CV too low: {cv}"


def test_composition_fix_rotation(tmp_path):
    random.seed(42)
    np.random.seed(42)
    h, w = 256, 256
    half = np.random.randint(0, 255, (h, w // 2, 3), np.uint8)
    img = np.concatenate([half, half[:, ::-1]], axis=1)
    fixed, ok = fix_composition(img, 1.0)
    assert ok
    assert not np.array_equal(img, fixed), "output identical to input"
    assert abs(fixed.shape[0] - h) <= 30, f"height changed too much: {fixed.shape[0]} vs {h}"
    assert abs(fixed.shape[1] - w) <= 30, f"width changed too much: {fixed.shape[1]} vs {w}"
