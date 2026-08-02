import os
import json
from pathlib import Path


def _root():
    return Path(__file__).resolve().parent.parent


def test_scan_project_script_exists():
    p = _root() / "scan_project.sh"
    assert p.exists(), f"{p} not found"
    assert os.access(p, os.X_OK), "scan_project.sh not executable"


def test_readme_exists():
    p = _root() / "README.md"
    assert p.exists(), "README.md not found"
    content = p.read_text()
    assert "# AI Image Detector" in content
    assert "## Quick Start" in content
    lines = content.splitlines()
    assert len(lines) < 150, f"README too long: {len(lines)} lines"


def test_pre_commit_hook_exists():
    p = _root() / "hooks" / "pre-commit-sample"
    assert p.exists(), "hooks/pre-commit-sample not found"
    assert os.access(p, os.X_OK), "pre-commit-sample not executable"


def test_npm_scripts_added():
    p = _root() / "package.json"
    assert p.exists(), "package.json not found"
    data = json.loads(p.read_text())
    scripts = data.get("scripts", {})
    assert "scan:ai" in scripts, "scan:ai missing"
    assert "scan:ai:fix" in scripts, "scan:ai:fix missing"
    assert "scan:ai:report" in scripts, "scan:ai:report missing"
    assert "scan:ai:all" in scripts, "scan:ai:all missing"
    assert "scan:ai:check" in scripts, "scan:ai:check missing"
