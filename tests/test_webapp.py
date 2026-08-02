import os
from pathlib import Path
from fastapi.testclient import TestClient
import numpy as np
from PIL import Image
import io


def _root():
    return Path(__file__).resolve().parent.parent


def _make_img_bytes(seed=0, size=64):
    rng = np.random.default_rng(seed)
    arr = rng.integers(0, 255, (size, size, 3), dtype=np.uint8)
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_server_imports():
    import server
    client = TestClient(server.app)
    res = client.get("/")
    assert res.status_code == 200
    assert "AI Image Detector" in res.text


def test_api_analyze():
    import server
    client = TestClient(server.app)
    buf = _make_img_bytes()
    res = client.post("/api/analyze", files={"file": ("test.png", buf, "image/png")})
    assert res.status_code == 200
    d = res.json()
    assert "total_score" in d
    assert "detectors" in d
    assert len(d["detectors"]) == 6


def test_api_batch():
    import server
    client = TestClient(server.app)
    buf1 = _make_img_bytes(1)
    buf2 = _make_img_bytes(2)
    res = client.post("/api/batch", files=[
        ("files", ("a.png", buf1, "image/png")),
        ("files", ("b.png", buf2, "image/png")),
    ])
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert "thumb" in data[0]
    scores = [r["total_score"] for r in data]
    assert scores == sorted(scores, reverse=True)


def test_static_index_exists():
    p = _root() / "static" / "index.html"
    assert p.exists(), "static/index.html not found"
    content = p.read_text()
    assert "AI Image Detector" in content
    lines = content.splitlines()
    assert len(lines) < 500, f"index.html too long: {len(lines)} lines"


def test_server_under_120_lines():
    p = _root() / "server.py"
    lines = p.read_text().splitlines()
    assert len(lines) <= 120, f"server.py too long: {len(lines)} lines"
