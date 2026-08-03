import sys
import io
import time
import json
import base64
import zipfile

from designer import generate_design, extract_concept
from codegen import generate_all

# pipeline.py — the full automation: brief -> concept -> validated design ->
# component library -> packaged ZIP. One call, four measured steps.


def _step(n, name, status, detail, started):
    return {
        "step": n, "name": name, "status": status,
        "detail": detail, "duration_ms": round((time.time() - started) * 1000, 1),
    }


def package_zip(design, files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("design.json", json.dumps(design, indent=2))
        for name, content in files.items():
            zf.writestr("anti-ai-components/" + name, content)
    return buf.getvalue()


def run_pipeline(brief):
    total_start = time.time()
    steps = []

    # Step 1: concept extraction
    t0 = time.time()
    concept = extract_concept(brief)
    steps.append(_step(1, "Concept extraction", "pass", "concept: " + concept, t0))

    # Step 2: design system + anti-AI validation
    t0 = time.time()
    design = generate_design(brief)
    v = design["anti_ai_validation"]
    passed = v["genericity_score"] < 0.4
    detail = (str(len(design["palette"])) + " colors, genericity "
              + str(v["genericity_score"]) + " -> " + ("PASS" if passed else "FAIL"))
    steps.append(_step(2, "Design system + validation", "pass" if passed else "fail", detail, t0))

    # Step 3: component library
    t0 = time.time()
    codegen_result = generate_all(design)
    detail = str(codegen_result["file_count"]) + " files, " + str(codegen_result["total_lines"]) + " lines"
    steps.append(_step(3, "Component library", "pass", detail, t0))

    # Step 4: package
    t0 = time.time()
    zb = package_zip(design, codegen_result["files"])
    size_kb = round(len(zb) / 1024, 1)
    steps.append(_step(4, "Package", "pass", "ZIP " + str(size_kb) + " KB", t0))

    return {
        "brief": brief,
        "concept": concept,
        "steps": steps,
        "design": design,
        "files": codegen_result["files"],
        "file_count": codegen_result["file_count"],
        "total_lines": codegen_result["total_lines"],
        "zip_base64": base64.b64encode(zb).decode("ascii"),
        "all_passed": all(s["status"] == "pass" for s in steps),
        "total_duration_ms": round((time.time() - total_start) * 1000, 1),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: pipeline.py \'{"project": "...", "feeling": "..."}\' [--full]')
        sys.exit(1)
    brief = json.loads(sys.argv[1])
    result = run_pipeline(brief)
    if "--full" not in sys.argv:
        result = {k: v for k, v in result.items() if k not in ("zip_base64", "files")}
    print(json.dumps(result, indent=2))
