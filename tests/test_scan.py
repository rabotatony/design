import os
import random
import numpy as np
from PIL import Image
from detector import scan, report


def _make_ai_like(path):
    h, w = 128, 128
    t = np.linspace(0, 1, w)
    c1 = np.array([0.48, 0.18, 0.97])
    c2 = np.array([0.13, 0.59, 0.95])
    line = c1[None, :] * (1 - t[:, None]) + c2[None, :] * t[:, None]
    grad = np.broadcast_to(line[None, :, :], (h, w, 3)).copy()
    Image.fromarray((np.clip(grad, 0, 1) * 255).astype(np.uint8)).save(path)


def _make_natural(path):
    rng = np.random.default_rng(99)
    img = rng.random((128, 128, 3))
    img[:64, :64] *= 0.2
    Image.fromarray((img * 255).astype(np.uint8)).save(path)


def _build_tree(root):
    random.seed(42)
    np.random.seed(42)
    sub = root / "sub"
    sub.mkdir(parents=True, exist_ok=True)
    _make_ai_like(str(root / "ai1.png"))
    _make_ai_like(str(root / "ai2.png"))
    _make_natural(str(root / "nat.png"))
    (root / "fake.png").write_bytes(b"not an image")
    _make_ai_like(str(sub / "ai3.png"))


def test_scan_finds_all_images(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    _build_tree(root)
    res = scan(str(root))
    captured = capsys.readouterr()
    import json
    parsed = json.loads(captured.out)
    assert parsed["total_images"] == 4, f"expected 4, got {parsed['total_images']}"
    assert any("fake.png" in e for e in res["errors"]), res["errors"]
    scores = [r["score"] for r in res["results"]]
    assert scores == sorted(scores, reverse=True), "results not sorted by score desc"


def test_scan_scores_correct(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    _build_tree(root)
    res = scan(str(root))
    capsys.readouterr()
    ai_scores = [r["score"] for r in res["results"] if r["file"].startswith("ai") or "ai" in r["file"]]
    nat = [r for r in res["results"] if r["file"] == "nat.png"][0]
    assert all(s > 0.6 for s in ai_scores), ai_scores
    assert nat["score"] < 0.4, nat


def test_scan_fix_creates_outputs(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    _build_tree(root)
    res = scan(str(root), fix=True)
    capsys.readouterr()
    ai_files = ["ai1.png", "ai2.png", "sub/ai3.png"]
    for f in ai_files:
        fixed = root / f.replace(".png", "_fixed.png")
        assert fixed.exists(), f"missing {fixed}"
    nat_fixed = root / "nat_fixed.png"
    assert not nat_fixed.exists(), "natural image should not be fixed"
    fixed_count = sum(1 for r in res["results"] if r["fixed"])
    assert res["fixed"] == fixed_count, (res["fixed"], fixed_count)


def test_scan_fix_output_dir(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    _build_tree(root)
    out_dir = tmp_path / "fixed_out"
    res = scan(str(root), fix=True, output_dir=str(out_dir))
    capsys.readouterr()
    assert (out_dir / "ai1_fixed.png").exists()
    assert (out_dir / "ai2_fixed.png").exists()
    assert (out_dir / "sub" / "ai3_fixed.png").exists()
    assert not (root / "ai1_fixed.png").exists(), "no _fixed next to original"
    assert not (root / "ai2_fixed.png").exists()
    assert not (root / "sub" / "ai3_fixed.png").exists()


def test_report_markdown(tmp_path, capsys):
    root = tmp_path / "project"
    root.mkdir()
    _build_tree(root)
    res = scan(str(root))
    capsys.readouterr()
    md_path = str(tmp_path / "report.md")
    ret = report(res, md_path)
    assert ret == md_path
    assert os.path.exists(md_path)
    content = open(md_path).read()
    assert "# AI Detection Report" in content
    assert "Needs Attention" in content
    assert "Uncertain" in content
    assert "ai1.png" in content
    assert "fake.png" in content and "Errors" in content
