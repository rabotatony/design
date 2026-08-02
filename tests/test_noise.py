import numpy as np
from PIL import Image
from detector import detect_noise_pattern


def _save(arr, tmp_path):
    a = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a).save(str(tmp_path))
    return str(tmp_path)


def test_poisson_noise_is_real(tmp_path):
    rng = np.random.default_rng(1)
    base = np.tile(np.linspace(0.1, 0.9, 256), (256, 1))
    scaled = base * 200.0
    noisy = rng.poisson(scaled).astype(float) / 200.0
    p = _save(noisy, tmp_path / "poisson.png")
    res = detect_noise_pattern(p)
    assert res["score"] < 0.3, res


def test_uniform_gaussian_noise_is_ai(tmp_path):
    rng = np.random.default_rng(2)
    base = np.tile(np.linspace(0.1, 0.9, 256), (256, 1))
    noisy = np.clip(base + rng.normal(0, 0.05, base.shape), 0, 1)
    p = _save(noisy, tmp_path / "gaussian.png")
    res = detect_noise_pattern(p)
    assert res["score"] > 0.7, res


def test_jpeg_block_detection(tmp_path):
    h, w = 256, 256
    t = np.linspace(0, 1, w)
    c1 = np.array([0.48, 0.18, 0.97])
    c2 = np.array([0.13, 0.59, 0.95])
    line = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    grad = np.broadcast_to(line[None, :, :], (h, w, 3)).copy()
    arr = (np.clip(grad, 0, 1) * 255).astype(np.uint8)
    p = str(tmp_path / "gradient.jpg")
    Image.fromarray(arr).save(p, quality=85)
    res = detect_noise_pattern(p)
    assert "JPEG mode" in res["detail"], res["detail"]
    assert 0.0 <= res["score"] <= 1.0, res["score"]


def test_jpeg_chroma_analysis(tmp_path):
    h, w = 256, 256
    t = np.linspace(0, 1, w)
    c1 = np.array([0.48, 0.18, 0.97])
    c2 = np.array([0.13, 0.59, 0.95])
    line = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    img = np.broadcast_to(line[None, :, :], (h, w, 3)).copy()
    arr = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    p = str(tmp_path / "smooth.jpg")
    Image.fromarray(arr).save(p, quality=85)
    res = detect_noise_pattern(p)
    assert "chroma_ratio" in res["detail"], res["detail"]
    assert "JPEG mode" in res["detail"], res["detail"]


def test_png_uses_raw_mode(tmp_path):
    rng = np.random.default_rng(5)
    img = rng.random((256, 256, 3))
    arr = (img * 255).astype(np.uint8)
    p = str(tmp_path / "noise.png")
    Image.fromarray(arr).save(p)
    res = detect_noise_pattern(p)
    assert "Raw mode" in res["detail"], res["detail"]
