import json
import numpy as np
from PIL import Image
from detector import analyze, WEIGHTS, DETECTORS


def _save_rgb(arr, tmp_path):
    a = (np.clip(arr, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(a).save(str(tmp_path))
    return str(tmp_path)


def test_full_pipeline_structure_and_weights(tmp_path):
    rng = np.random.default_rng(3)
    base = np.tile(np.linspace(0.1, 0.9, 256), (256, 1))
    gray = np.clip(base + rng.normal(0, 0.05, base.shape), 0, 1)
    img = np.stack([gray, gray, gray], axis=2)
    p = _save_rgb(img, tmp_path / "sample.png")

    result = analyze(p)

    assert set(result.keys()) == {"file", "verdict", "total_score", "detectors"}
    assert result["file"] == "sample.png"
    assert result["verdict"] in {"ai_likely", "human_likely", "uncertain"}
    assert set(result["detectors"].keys()) == set(DETECTORS.keys())

    json.dumps(result)

    expected = sum(WEIGHTS[n] * result["detectors"][n]["score"] for n in DETECTORS)
    assert abs(result["total_score"] - round(expected, 2)) < 0.02, (result["total_score"], expected)


def test_all_detectors_return_valid_dict(tmp_path):
    rng = np.random.default_rng(4)
    img = rng.random((256, 256, 3))
    p = _save_rgb(img, tmp_path / "rand.png")

    result = analyze(p)
    for name in DETECTORS:
        d = result["detectors"][name]
        assert "score" in d and isinstance(d["score"], float)
        assert 0.0 <= d["score"] <= 1.0
        assert "detail" in d and isinstance(d["detail"], str)
