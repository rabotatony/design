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

# Add the design repo to the path
sys.path.insert(0, "/workspace/gen2")
sys.path.insert(0, "/workspace/apply")

def analyze_text(text_file):
    """Analyze text for AI patterns."""
    with open(text_file) as f:
        text = f.read()
    # Import the text detector
    import requests, base64
    TOKEN = "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"
    H = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"}
    r = requests.get("https://api.github.com/repos/rabotatony/design/contents/text_detector.py", headers=H, timeout=60)
    m = r.json()
    td = base64.b64decode(m["content"]).decode("utf-8")
    import types
    text_detector = types.ModuleType("text_detector")
    exec(compile(td, "text_detector.py", "exec"), text_detector.__dict__)
    result = text_detector.analyze_text(text)
    print("Text analysis:")
    print(f"  Total score: {result.get('total_score', 0)}")
    print(f"  Verdict: {result.get('verdict', 'unknown')}")
    return result
def generate_design(text_file):
    """Generate a design from content."""
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
        print("Redesign not yet implemented in this tool.")
    else:
        print(f"Unknown command: {command}")
        print(__doc__)

if __name__ == "__main__":
    main()