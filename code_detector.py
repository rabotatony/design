"""
code_detector.py — detects AI-generation tells in TS/TSX code.
Completes the detection layer: images, text, collections, CSS, and now code.
Same architecture: independent detectors, weighted verdict, evidence.
"""
import re
import json


GENERIC_NAMES = {
    "data", "result", "results", "item", "items", "temp", "tmp", "val", "value",
    "obj", "arr", "res", "resp", "info", "element", "elem", "thing", "stuff",
    "handle", "process", "doIt", "myVar", "newData", "finalResult",
}

PLACEHOLDERS = re.compile(r"lorem|placeholder text|example text|your text here|dummy", re.I)
REDUNDANT_COMMENT = re.compile(r"this (function|component|hook|method|class)|this is a|here we|we (can |now )?(create|return|set|get|render|handle|update|check)", re.I)


def _strip_strings_and_comments(code):
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    code = re.sub(r"//[^\n]*", "", code)
    code = re.sub(r"(?:'[^']*')|(?:\"[^\"]*\")|(?:`[^`]*`)", "", code)
    return code


def detect_redundant_comments(code):
    lines = code.splitlines()
    n = max(1, len(lines))
    hits = 0
    examples = []
    for l in lines:
        s = l.strip()
        if s.startswith('//') or s.startswith('*') or s.startswith('/**'):
            if REDUNDANT_COMMENT.search(s):
                hits += 1
                if len(examples) < 3:
                    examples.append(s[:70])
    density = hits / (n / 100.0)
    score = min(1.0, density / 4.0)
    return {"score": round(score, 2), "detail": f"{hits} redundant comments / {n} lines",
            "examples": examples}


def detect_console_leftover(code):
    n = max(1, len(code.splitlines()))
    hits = len(re.findall(r"console\.(log|warn|error|debug|info)\(", code))
    density = hits / (n / 100.0)
    score = min(1.0, density / 3.0)
    return {"score": round(score, 2), "detail": f"{hits} console.* calls / {n} lines"}


def detect_todo_trails(code):
    n = max(1, len(code.splitlines()))
    hits = len(re.findall(r"\b(TODO|FIXME|HACK|XXX)\b", code))
    density = hits / (n / 100.0)
    score = min(1.0, density / 2.0)
    return {"score": round(score, 2), "detail": f"{hits} TODO/FIXME/HACK / {n} lines"}


def detect_generic_naming(code):
    body = _strip_strings_and_comments(code)
    declared = re.findall(r"(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", body)
    params = re.findall(r"\(([^)]*)\)\s*(?:=>|\{)", body)
    for p in params:
        for ident in re.findall(r"[A-Za-z_$][\w$]*", p):
            declared.append(ident)
    if not declared:
        return {"score": 0.0, "detail": "no declarations found"}
    generic = [d for d in declared if d in GENERIC_NAMES or d.lower() in GENERIC_NAMES]
    ratio = len(generic) / len(declared)
    score = min(1.0, ratio / 0.25)
    return {"score": round(score, 2),
            "detail": f"{len(generic)}/{len(declared)} generic identifiers"}


def detect_placeholders(code):
    hits = len(PLACEHOLDERS.findall(code))
    score = min(1.0, hits / 3.0)
    return {"score": round(score, 2), "detail": f"{hits} placeholder strings"}


WEIGHTS = {
    "redundant_comments": 0.30,
    "console_leftover": 0.20,
    "todo_trails": 0.15,
    "generic_naming": 0.25,
    "placeholders": 0.10,
}


def analyze_code(code, path=""):
    # Handle None input gracefully
    if code is None:
        code = ""
    detectors = {
        "redundant_comments": detect_redundant_comments(code),
        "console_leftover": detect_console_leftover(code),
        "todo_trails": detect_todo_trails(code),
        "generic_naming": detect_generic_naming(code),
        "placeholders": detect_placeholders(code),
    }
    total = round(sum(WEIGHTS[k] * detectors[k]["score"] for k in WEIGHTS), 2)
    verdict = "ai_likely" if total > 0.5 else "uncertain" if total > 0.25 else "human_likely"
    return {"path": path, "total_score": total, "verdict": verdict, "detectors": detectors}


def analyze_dir(paths):
    results = [analyze_code(open(p).read(), p) for p in paths]
    avg = round(sum(r["total_score"] for r in results) / max(1, len(results)), 2)
    return {"files": results, "avg_score": avg}


if __name__ == "__main__":
    import sys
    out = analyze_dir(sys.argv[1:])
    print(json.dumps(out, ensure_ascii=False, indent=1))