import os
import random
import subprocess
import sys
import numpy as np
from PIL import Image
from detector import process


def _make_ai_like(path):
    h, w = 256, 256
    t = np.linspace(0, 1, w)
    c1 = np.array([0.48, 0.18, 0.97])
    c2 = np.array([0.13, 0.59, 0.95])
    line = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    grad = np.broadcast_to(line[None, :, :], (h, w, 3)).copy()
    a = (np.clip(grad, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a).save(path)


def _make_natural(path):
    rng = np.random.default_rng(99)
    img = rng.random((256, 256, 3))
    img[:128, :128] *= 0.2
    Image.fromarray((img * 255).astype(np.uint8)).save(path)


def test_process_ai_image(tmp_path):
    random.seed(42)
    np.random.seed(42)
    img_path = str(tmp_path / "ai.png")
    out_path = str(tmp_path / "fixed.png")
    _make_ai_like(img_path)

    report = process(img_path, out_path)

    assert os.path.exists(out_path), "output file not created"
    assert report["improvement"] > 0, f"improvement not positive: {report['improvement']}"
    for key in ("input", "output", "before", "after", "improvement", "corrections_applied", "per_detector"):
        assert key in report, f"missing key: {key}"
    assert set(report["per_detector"].keys()) == {
        "frequency_ceiling", "noise_pattern", "palette", "composition", "texture_uniformity"
    }
    for name, d in report["per_detector"].items():
        assert set(d.keys()) == {"before", "after", "delta"}, (name, d)


def test_process_human_image(tmp_path, capsys):
    random.seed(42)
    np.random.seed(42)
    img_path = str(tmp_path / "nat.png")
    out_path = str(tmp_path / "fixed.png")
    _make_natural(img_path)

    result = process(img_path, out_path)

    captured = capsys.readouterr()
    assert "no correction needed" in captured.out
    assert not os.path.exists(out_path), "output file should not exist for human image"
    assert result["total_score"] < 0.4, result["total_score"]


def test_process_cli_fix_flag(tmp_path):
    random.seed(42)
    np.random.seed(42)
    img_path = str(tmp_path / "test_img.jpg")
    _make_ai_like(img_path)

    result = subprocess.run(
        [sys.executable, "detector.py", img_path, "--fix"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "improvement" in result.stdout, result.stdout
    fixed = img_path.replace(".jpg", "_fixed.jpg")
    assert os.path.exists(fixed), "default _fixed file not created"


def test_process_custom_output(tmp_path):
    random.seed(42)
    np.random.seed(42)
    img_path = str(tmp_path / "test_img.jpg")
    custom = str(tmp_path / "custom_out.png")
    _make_ai_like(img_path)

    result = subprocess.run(
        [sys.executable, "detector.py", img_path, "--fix", "-o", custom],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    assert os.path.exists(custom), "custom output not created"
    default_fixed = img_path.replace(".jpg", "_fixed.jpg")
    assert not os.path.exists(default_fixed), "default _fixed should not exist when -o given"
