"""
pattern_generator.py — generates design PATTERNS from a design language.

Design patterns are recurring design decisions that make a design system
coherent and unique. They are DERIVED from the design language's principles.

For example:
  - If the design has "mystery" principle, the pattern is "progressive disclosure"
  - If the design has "heat" principle, the pattern is "radiating focus"
  - If the design has "growth" principle, the pattern is "expanding hierarchy"

The key: patterns are derived from principles, not picked from templates.
"""

# Design patterns derived from design principles.
DESIGN_PATTERNS = {
    "growth": {
        "name": "expanding-hierarchy",
        "description": "Elements grow and expand as the user progresses",
        "rules": [
            "Use progressive disclosure: show less first, reveal more on interaction",
            "Increase spacing as content becomes more important",
            "Use organic easing curves (ease-in-out) for expansions",
            "Scale elements up slightly on hover to suggest growth",
        ],
    },
    "branching": {
        "name": "tree-navigation",
        "description": "Navigation follows a tree-like structure",
        "rules": [
            "Use hierarchical navigation with clear parent-child relationships",
            "Indent child elements to show hierarchy",
            "Use connecting lines or branches to show relationships",
            "Collapse/expand branches on interaction",
        ],
    },
    "transformation": {
        "name": "state-morphing",
        "description": "Elements transform between states",
        "rules": [
            "Use smooth transitions between states",
            "Show before/after states clearly",
            "Use morphing animations for state changes",
            "Provide visual feedback during transformation",
        ],
    },
    "heat": {
        "name": "radiating-focus",
        "description": "Focus radiates from a central point",
        "rules": [
            "Use a central focal point that radiates attention",
            "Use warm colors (oranges, reds) for focal elements",
            "Add subtle glow effects to focal elements",
            "Use pulsing animations to suggest heat/energy",
        ],
    },
    "flow": {
        "name": "continuous-stream",
        "description": "Content flows continuously without hard breaks",
        "rules": [
            "Avoid hard section breaks; use gradual transitions",
            "Use flowing, wave-like spacing",
            "Use smooth scrolling and liquid animations",
            "Connect sections with flowing visual elements",
        ],
    },
    "depth": {
        "name": "layered-reality",
        "description": "Content exists in layers with depth",
        "rules": [
            "Use layered elements with clear z-axis",
            "Use parallax scrolling for depth",
            "Use shadows and elevation to suggest depth",
            "Reveal deeper layers on interaction",
        ],
    },
    "hierarchy": {
        "name": "clear-descent",
        "description": "Clear vertical hierarchy from top to bottom",
        "rules": [
            "Use clear vertical hierarchy with descending importance",
            "Use larger, bolder elements at the top",
            "Decrease size and weight as content descends",
            "Use clear section headers to mark hierarchy levels",
        ],
    },
    "balance": {
        "name": "harmonious-equilibrium",
        "description": "Elements are balanced and harmonious",
        "rules": [
            "Use symmetric layouts for balance",
            "Balance visual weight across the layout",
            "Use harmonious spacing and proportions",
            "Avoid visual clutter; maintain equilibrium",
        ],
    },
    "mystery": {
        "name": "progressive-revelation",
        "description": "Content is revealed progressively",
        "rules": [
            "Hide secondary content; reveal on interaction",
            "Use veils, overlays, and obscured elements",
            "Use slow fade-in animations for reveals",
            "Create a sense of discovery and exploration",
        ],
    },
    "revelation": {
        "name": "unfolding-truth",
        "description": "Truth unfolds layer by layer",
        "rules": [
            "Unfold content layer by layer",
            "Use peeling-back animations",
            "Reveal hidden content progressively",
            "Create a sense of discovery",
        ],
    },
    "wisdom": {
        "name": "layered-knowledge",
        "description": "Knowledge is layered and deep",
        "rules": [
            "Layer knowledge from surface to depth",
            "Use contemplative spacing and pacing",
            "Use classical, timeless typography",
            "Provide depth without overwhelming",
        ],
    },
    "light": {
        "name": "illuminated-focus",
        "description": "Light illuminates the focal point",
        "rules": [
            "Use light to draw attention to focal points",
            "Use illumination and glow effects",
            "Create contrast between light and dark",
            "Use dawning animations for reveals",
        ],
    },
    "creation": {
        "name": "emergent-formation",
        "description": "Things emerge and form from foundation",
        "rules": [
            "Show emergence from a foundation",
            "Use building, accumulating animations",
            "Show crystallization and formation",
            "Create a sense of becoming",
        ],
    },
    "sacred": {
        "name": "processional-axis",
        "description": "Sacred, processional, axial",
        "rules": [
            "Use axial, processional layouts",
            "Use centered, reverent compositions",
            "Use processional spacing and pacing",
            "Create a sense of reverence and sacredness",
        ],
    },
}


def derive_patterns(design_language):
    """Derive design patterns from the design language's principles.
    Returns a dict of active patterns with their rules.
    """
    active_principles = design_language.get("active_principles", [])
    active_patterns = {}
    for principle in active_principles:
        if principle in DESIGN_PATTERNS:
            active_patterns[principle] = DESIGN_PATTERNS[principle]
    return active_patterns


if __name__ == "__main__":
    design_language = {
        "active_principles": ["mystery", "wisdom", "hierarchy"],
    }
    patterns = derive_patterns(design_language)
    for principle, pattern in patterns.items():
        print(f"=== {principle}: {pattern['name']} ===")
        print(f"  {pattern['description']}")
        for rule in pattern["rules"]:
            print(f"    - {rule}")
