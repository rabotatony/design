import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom
from detector import detect_frequency_ceiling


def _save(arr, tmp_path):
    a = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a).save(str(tmp_path))
    return str(tmp_path)


def _lowpass_ai(size=256, cutoff=70, seed=42):
    rng = np.random.default_rng(seed)
    base = rng.random((size, size))
    f = np.fft.fftshift(np.fft.fft2(base))
    yy, xx = np.mgrid[0:size, 0:size]
    rad = np.sqrt((yy - size / 2) ** 2 + (xx - size / 2) ** 2)
    mask = 1.0 / (1.0 + (rad / cutoff) ** 8)
    f = f * mask
    f = np.fft.ifftshift(f)
    img = np.real(np.fft.ifft2(f))
    img = (img - img.min()) / (img.max() - img.min() + 1e-10)
    return img


def _natural_noise(size=256, seed=0):
    rng = np.random.default_rng(seed)
    img = rng.random((size, size))
    return gaussian_filter(img, sigma=0.5)


def _perlin_like(size=256, seed=1):
    rng = np.random.default_rng(seed)
    perlin = np.zeros((size, size))
    for oct_i, sc in enumerate([64, 32, 16, 8]):
        nn = size // sc + 2
        g = rng.random((nn, nn))
        z = zoom(g, sc, order=1)[:size, :size]
        perlin += z * (0.5 ** oct_i)
    perlin = (perlin - perlin.min()) / (perlin.max() - perlin.min() + 1e-10)
    return perlin


def test_frequency_ceiling_detected(tmp_path):
    img = _lowpass_ai()
    p = _save(img, tmp_path / "ceiling.png")
    res = detect_frequency_ceiling(p)
    assert res["score"] > 0.7, res


def test_no_frequency_ceiling(tmp_path):
    img = _natural_noise()
    p = _save(img, tmp_path / "noise.png")
    res = detect_frequency_ceiling(p)
    assert res["score"] < 0.3, res


def test_does_not_crash_on_tiny(tmp_path):
    img = np.array([[0.5]])
    p = _save(img, tmp_path / "tiny.png")
    res = detect_frequency_ceiling(p)
    assert "score" in res
    assert "detail" in res


def test_real_photo_spectrum(tmp_path):
    img = _perlin_like()
    p = _save(img, tmp_path / "perlin.png")
    res = detect_frequency_ceiling(p)
    assert res["score"] < 0.4, res


def test_pure_gradient(tmp_path):
    x = np.linspace(0, 1, 256)
    X, Y = np.meshgrid(x, x)
    img = X
    p = _save(img, tmp_path / "gradient.png")
    res = detect_frequency_ceiling(p)
    assert 0.3 <= res["score"] <= 0.8, res


def test_calibration_improvement(tmp_path, capsys):
    import json
    from calibrate import evaluate
    ai_dir = tmp_path / "ai"
    nat_dir = tmp_path / "nat"
    ai_dir.mkdir()
    nat_dir.mkdir()
    np.random.seed(42)
    for i in range(5):
        _save(_lowpass_ai(seed=42 + i), ai_dir / f"ai{i}.png")
        _save(_natural_noise(seed=i), nat_dir / f"n{i}.png")
    res = evaluate(str(ai_dir), str(nat_dir))
    capsys.readouterr()
    sep = res["per_detector_accuracy"]["frequency_ceiling"]["separation"]
    print(f"\n# frequency_ceiling separation after fix: {sep} (was 0.0)")
    assert sep > 0.3, f"separation {sep} not > 0.3"
