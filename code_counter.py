"""
code_counter.py — the counter-layer for code_detector.

Applies the SAFE mechanical counters (remove redundant comments, strip debug
console.log/info/debug) and flags the tells that need a human (TODO trails,
generic naming, placeholders). Renaming identifiers or resolving TODOs changes
behavior/semantics, so those are reported, not auto-fixed.
"""
import re

REDUNDANT_COMMENT = re.compile(
    r"this (function|component|hook|method|class)|this is a|here we|we (can |now )?"
    r"(create|return|set|get|render|handle|update|check)", re.I)
DEBUG_CONSOLE = re.compile(r"^\s*console\.(log|info|debug)\([^\n]*\)\s*;?\s*$")
GENERIC_NAMES = {"data","result","results","item","items","temp","tmp","val","value",
                 "obj","arr","res","resp","info","element","elem","handle","process",
                 "event","events","props","state","render","content","contents",
                 "list","lists","object","objects","thing","things","stuff","newdata","finalresult","myvar"}


def remove_redundant_comments(code):
    out, removed = [], 0
    for line in code.splitlines():
        s = line.strip()
        if (s.startswith("//")) and REDUNDANT_COMMENT.search(s):
            removed += 1
            continue
        out.append(line)
    return "\n".join(out), removed


def remove_debug_console(code):
    out, removed = [], 0
    for line in code.splitlines():
        if DEBUG_CONSOLE.match(line):
            removed += 1
            continue
        out.append(line)
    return "\n".join(out), removed


def flag_human_review(code):
    todos = len(re.findall(r"\b(TODO|FIXME|HACK|XXX)\b", code))
    body = re.sub(r'"[^"]*"', "", re.sub(r"//[^\n]*", "", code))
    declared = re.findall(r"(?:const|let|var|function)\s+([A-Za-z_$][\w$]*)", body)
    generic = [d for d in declared if d.lower() in GENERIC_NAMES]
    return {
        "todo_trails": todos,
        "generic_identifiers": sorted(set(generic))[:12],
        "note": "TODO trails and identifier renames change behavior/semantics; a human must decide.",
    }


def clean_code(code):
    """Apply safe counters + report. Returns (cleaned_code, report)."""
    before_lines = len(code.splitlines())
    code2, rm_comments = remove_redundant_comments(code)
    code3, rm_console = remove_debug_console(code2)
    review = flag_human_review(code3)
    report = {
        "removed_redundant_comments": rm_comments,
        "removed_debug_console": rm_console,
        "lines": {"before": before_lines, "after": len(code3.splitlines())},
        "needs_human_review": review,
    }
    return code3, report
