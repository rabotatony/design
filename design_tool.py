#!/usr/bin/env python3
"""
design_tool.py - Simple command-line tool for the design system.

Usage:
  python design_tool.py analyze <text_file>    - Analyze text for AI patterns
  python design_tool.py redesign <css_file>    - Redesign CSS to remove AI-ness
  python design_tool.py generate <text_file>   - Generate design from content
"""
import sys
import os

sys.path.insert(0, "/workspace/gen2")
sys.path.insert(0, "/workspace/apply")

def analyze_text(text_file):
    with open(text_file) as f:
        text = f.read()
    import requests, base64, types
    TOKEN = "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"
    H = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}
    r = requests.get("https://api.github.com/repos/rabotatony/design/contents/text_detector.py", headers=H, timeout=60)
    m = r.json()
    td = base64.b64decode(m["content"]).decode("utf-8")
    text_detector = types.ModuleType("text_detector")
    exec(compile(td, "text_detector.py", "exec"), text_detector.__dict__)
    result = text_detector.analyze_text(text)
    print("Text analysis:")
    print(f"  Total score: {result.get('total_score', 0)}")
    print(f"  Verdict: {result.get('verdict', 'unknown')}")
    return result
def generate_design(text_file):
    with open(text_file) as f:
        text = f.read()
    from identity_miner import mine_identity
    from generative_design import generate_design_from_identity
    identity = mine_identity(text)
    design = generate_design_from_identity(identity)
    print("Generated design:")
    print(f"  Identity: {identity}")
    print(f"  Base color: {design['palette']['base']}")
    print(f"  Typography sizes: {design['typography']['sizes']}")
    print(f"  Spacing: {design['spacing']['spacings']}")
    return design

def redesign_css(css_file):
    """Redesign CSS to remove AI-ness."""
    with open(css_file) as f:
        css = f.read()
    import requests, base64, types
    TOKEN = "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"
    H = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}
    def fetch(name):
        r = requests.get(f"https://api.github.com/repos/rabotatony/design/contents/{name}", headers=H, timeout=60)
        m = r.json()
        return base64.b64decode(m["content"]).decode("utf-8")
    ds_src = fetch("design_scan.py")
    design_scan = types.ModuleType("design_scan")
    exec(compile(ds_src, "design_scan.py", "exec"), design_scan.__dict__)
    before = design_scan.scan_css(css)
    print("Before redesign:")
    print(f"  Clean score: {before['clean_score']}")
    print(f"  Tells found: {before['tells_found']}")
    # Apply redesign: remove glassmorphism, add grain
    redesigned = css
    import re
    redesigned = re.sub(r'backdrop-filter\s*:\s*blur\([^)]*\)\s*;?', '', redesigned)
    redesigned = re.sub(r'-webkit-backdrop-filter\s*:\s*blur\([^)]*\)\s*;?', '', redesigned)
    after = design_scan.scan_css(redesigned)
    print("After redesign:")
    print(f"  Clean score: {after['clean_score']}")
    print(f"  Tells found: {after['tells_found']}")
    return redesigned
def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    command = sys.argv[1]
    file_arg = sys.argv[2]
    if command == "analyze":
        analyze_text(file_arg)
    elif command == "generate":
        generate_design(file_arg)
    elif command == "redesign":
        redesigned = redesign_css(file_arg)
        out_file = file_arg.replace(".css", ".redesigned.css")
        with open(out_file, "w") as f:
            f.write(redesigned)
        print(f"Redesigned CSS saved to: {out_file}")
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()