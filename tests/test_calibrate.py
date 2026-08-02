import os
import shutil
import random
import numpy as np
from PIL import Image
from calibrate import evaluate, apply_weights, compare
from detector import DETECTORS


def _make_ai_like(path):
    h, w = 128, 128
    t = np.linspace(0, 1, w)
    c1 = np.array([0.48, 0.18, 0.97])
    c2 = np.array([0.13, 0.59, 0.95])
    line = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    grad = np.broadcast_to(line[None, :, :], (h, w, 3)).copy()
    noise = np.random.normal(0, 0.02, (h, w, 3))
    a = (np.clip(grad + noise, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a).save(str(path))


def _make_natural(path):
    rng = np.random.default_rng(99)
    img = rng.random((128, 128, 3))
    img[:64, :64] *= 0.2
    Image.fromarray((img * 255).astype(np.uint8)).save(str(path))


def _build_dirs(tmp_path):
    random.seed(42)
    np.random.seed(42)
    ai_dir = tmp_path / "ai"
    hum_dir = tmp_path / "human"
    ai_dir.mkdir()
    hum_dir.mkdir()
    for i in range(5):
        _make_ai_like(ai_dir / f"ai{i}.png")
        _make_natural(hum_dir / f"h{i}.png")
    return str(ai_dir), str(hum_dir)


def test_evaluate_structure(tmp_path, capsys):
    ai_dir, hum_dir = _build_dirs(tmp_path)
    res = evaluate(ai_dir, hum_dir)
    capsys.readouterr()
    required = {"ai_images", "human_images", "accuracy", "threshold_used",
                "optimal_threshold", "false_positives", "false_negatives",
                "per_detector_accuracy", "suggested_weights", "weakest_detector",
                "strongest_detector"}
    assert set(res.keys()) >= required, set(res.keys()) ^ required
    assert 0 <= res["accuracy"] <= 1, res["accuracy"]
    assert 0.1 <= res["optimal_threshold"] <= 0.9, res["optimal_threshold"]
    assert set(res["per_detector_accuracy"].keys()) == set(DETECTORS.keys())
    assert abs(sum(res["suggested_weights"].values()) - 1.0) < 1e-6, res["suggested_weights"]
    assert res["weakest_detector"] in DETECTORS
    assert res["strongest_detector"] in DETECTORS


def test_evaluate_separation(tmp_path, capsys):
    ai_dir, hum_dir = _build_dirs(tmp_path)
    res = evaluate(ai_dir, hum_dir)
    capsys.readouterr()
    pd = res["per_detector_accuracy"]
    assert pd["palette"]["separation"] > 0.2, pd["palette"]
    assert pd["texture_uniformity"]["separation"] > 0.2, pd["texture_uniformity"]


def test_apply_weights(tmp_path):
    import calibrate
    det_path = os.path.join(os.path.dirname(calibrate.__file__), "detector.py")
    backup = tmp_path / "detector_backup.py"
    shutil.copy(det_path, str(backup))
    original_lines = open(det_path).read().splitlines()
    try:
        test_w = {
            "frequency_ceiling": 0.30, "noise_pattern": 0.15, "palette": 0.25,
            "composition": 0.03, "texture_uniformity": 0.12, "metadata": 0.15,
        }
        apply_weights(test_w)
        new_src = open(det_path).read()
        ns = {}
        import re
        m = re.search(r"WEIGHTS\s*=\s*\{(.*?)\}", new_src, re.DOTALL)
        for k, v in re.findall(r'"(\w+)":\s*([\d.]+)', m.group(1)):
            ns[k] = float(v)
        for k, v in test_w.items():
            assert abs(ns[k] - v) < 1e-6, (k, ns[k], v)
        import ast
        ast.parse(new_src)
        new_lines = new_src.splitlines()
        assert len(new_lines) == len(original_lines), "line count changed"
    finally:
        shutil.copy(str(backup), det_path)


def test_compare(tmp_path, capsys):
    random.seed(42)
    np.random.seed(42)
    before = tmp_path / "before"
    after = tmp_path / "after"
    before.mkdir()
    after.mkdir()
    import json
    from detector import analyze, correct
    for i in range(3):
        p = str(before / f"img{i}.png")
        _make_ai_like(p)
        d = analyze(p)
        jp = str(before / f"d{i}.json")
        with open(jp, "w") as f:
            json.dump(d, f)
        with __import__("contextlib").redirect_stdout(open(os.devnull, "w")):
            correct(p, jp, str(after / f"img{i}.png"))
    res = compare(str(before), str(after))
    capsys.readouterr()
    assert res["images_compared"] == 3, res["images_compared"]
    assert res["avg_improvement"] > 0, res["avg_improvement"]
    assert isinstance(res["best_correction"], str), res["best_correction"]
    for k in ("palette", "texture_uniformity", "composition"):
        assert k in res["per_detector_avg_delta"], res["per_detector_avg_delta"]


def test_evaluate_handles_empty_dir(tmp_path, capsys):
    empty = tmp_path / "empty"
    empty.mkdir()
    hum = tmp_path / "hum"
    hum.mkdir()
    _make_natural(hum / "h0.png")
    res = evaluate(str(empty), str(hum))
    capsys.readouterr()
    assert res["ai_images"] == 0, res["ai_images"]
    assert "accuracy" in res
