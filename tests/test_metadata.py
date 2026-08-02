import numpy as np
from PIL import Image, ExifTags
from detector import detect_metadata, analyze, WEIGHTS


def _save_jpeg_with_exif(path, exif_dict):
    img = Image.fromarray(np.full((64, 64, 3), 128, np.uint8))
    exif = img.getexif()
    for k, v in exif_dict.items():
        exif[k] = v
    img.save(str(path), exif=exif.tobytes())
    return str(path)


def test_ai_software_tag(tmp_path):
    p = _save_jpeg_with_exif(tmp_path / "sd.jpg", {305: "Stable Diffusion XL"})
    res = detect_metadata(p)
    assert res["score"] == 1.0, res
    assert "Stable Diffusion" in res["detail"], res


def test_full_camera_exif(tmp_path):
    p = _save_jpeg_with_exif(tmp_path / "cam.jpg", {
        271: "Canon", 272: "EOS R5", 37386: 50,
        33434: (1, 200), 33437: 2.8,
    })
    res = detect_metadata(p)
    assert res["score"] == 0.0, res


def test_no_exif(tmp_path):
    img = Image.fromarray(np.full((64, 64, 3), 128, np.uint8))
    p = str(tmp_path / "plain.png")
    img.save(p)
    res = detect_metadata(p)
    assert res["score"] == 0.5, res
    assert "No EXIF" in res["detail"], res


def test_partial_exif(tmp_path):
    p = _save_jpeg_with_exif(tmp_path / "par.jpg", {271: "Nikon", 272: "D850"})
    res = detect_metadata(p)
    assert res["score"] == 0.2, res


def test_corrupt_metadata(tmp_path):
    img = Image.fromarray(np.full((64, 64, 3), 128, np.uint8))
    exif = img.getexif()
    exif[305] = "Stable Diffusion XL"
    p = str(tmp_path / "corrupt.jpg")
    img.save(p, exif=exif.tobytes())
    data = bytearray(open(p, "rb").read())
    for i in range(len(data) - 10):
        if data[i] == 0xFF and data[i + 1] == 0xE1 and data[i + 4:i + 10] == b"Exif\x00\x00":
            for j in range(i + 10, min(i + 60, len(data))):
                data[j] = 0xFF if j % 2 else 0x00
            break
    open(p, "wb").write(data)
    res = detect_metadata(p)
    assert res["score"] == 0.3, res


def test_metadata_in_analyze(tmp_path):
    p = _save_jpeg_with_exif(tmp_path / "sd.jpg", {305: "Stable Diffusion XL"})
    result = analyze(p)
    assert "metadata" in result["detectors"], "metadata key missing"
    assert result["detectors"]["metadata"]["score"] == 1.0, result["detectors"]["metadata"]
    expected = sum(WEIGHTS[n] * result["detectors"][n]["score"] for n in WEIGHTS)
    assert abs(result["total_score"] - round(expected, 2)) < 0.02, (result["total_score"], expected)


def test_weights_sum_to_one():
    assert len(WEIGHTS) == 6, WEIGHTS
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, sum(WEIGHTS.values())
