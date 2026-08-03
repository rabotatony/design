import io
import json
import zipfile
from pipeline import run_pipeline, package_zip

BRIEF = {"project": "fintech dashboard for freelancers",
         "feeling": "trustworthy but warm",
         "audience": "freelance designers 25-40"}


def test_pipeline_structure():
    result = run_pipeline(BRIEF)
    for key in ("brief", "concept", "steps", "design", "files", "file_count",
                "total_lines", "zip_base64", "all_passed", "total_duration_ms"):
        assert key in result, f"missing key {key}"
    assert len(result["steps"]) == 5
    assert result["file_count"] == 12


def test_pipeline_steps_pass():
    result = run_pipeline(BRIEF)
    for step in result["steps"]:
        assert step["status"] == "pass", f"step {step['step']} failed: {step['detail']}"
        assert step["duration_ms"] >= 0
    assert result["all_passed"] is True


def test_pipeline_genericity_passes():
    result = run_pipeline(BRIEF)
    v = result["design"]["anti_ai_validation"]
    assert v["genericity_score"] < 0.4


def test_pipeline_zip_contains_design_components_and_page():
    result = run_pipeline(BRIEF)
    zb = base64_decode(result["zip_base64"])
    zf = zipfile.ZipFile(io.BytesIO(zb))
    names = zf.namelist()
    assert "design.json" in names
    assert any("tokens.css" in n for n in names)
    assert any("Button.tsx" in n for n in names)
    assert "page/landing-page.tsx" in names
    assert "page/content.json" in names
    assert len(names) == 13  # design.json + 10 components + 2 page files
    design_in_zip = json.loads(zf.read("design.json"))
    assert design_in_zip["concept"] == result["concept"]


def test_package_zip_roundtrip():
    result = run_pipeline(BRIEF)
    zb = package_zip(result["design"], result["files"])
    zf = zipfile.ZipFile(io.BytesIO(zb))
    assert len(zf.namelist()) == 13


def base64_decode(s):
    import base64
    return base64.b64decode(s)
