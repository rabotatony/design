import numpy as np
from PIL import Image
from detector import detect_palette


def _save_rgb(arr, tmp_path):
    a = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a).save(str(tmp_path))
    return str(tmp_path)


def test_purple_blue_gradient_matches(tmp_path):
    c1 = np.array([0.48, 0.18, 0.97])
    c2 = np.array([0.13, 0.59, 0.95])
    t = np.linspace(0, 1, 256)
    line = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    img = np.tile(line[:, None, :], (1, 256, 1))
    p = _save_rgb(img, tmp_path / "gradient.png")
    res = detect_palette(p)
    assert res["score"] > 0.7, res


def test_random_palette_does_not_match(tmp_path):
    rng = np.random.default_rng(7)
    img = rng.random((256, 256, 3))
    p = _save_rgb(img, tmp_path / "random.png")
    res = detect_palette(p)
    assert res["score"] < 0.4, res
