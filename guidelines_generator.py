"""
guidelines_generator.py — generates design guidelines from a design language.

Design guidelines explain HOW to use the design system. They are DERIVED
from the design language's principles, patterns, and identity.

For example:
  - If the design has "mystery" principle, the guideline is "reveal, don't show"
  - If the design has "heat" principle, the guideline is "radiate from the center"
  - If the design has "growth" principle, the guideline is "let it grow"

The key: guidelines are derived from principles, not generic advice.
"""

# Design guidelines derived from design principles.
DESIGN_GUIDELINES = {
    "growth": {
        "name": "let-it-grow",
        "principles": [
            "Let content grow organically; don't force it into rigid structures",
            "Progressive disclosure: show less first, reveal more as the user engages",
            "Use organic, flowing transitions; avoid abrupt changes",
            "Let spacing breathe; don't cram elements together",
        ],
    },
    "branching": {
        "name": "tree-thinking",
        "principles": [
            "Think in hierarchies; every element has a parent and children",
            "Make parent-child relationships visually clear",
            "Use indentation and connecting lines to show hierarchy",
            "Let branches expand and collapse naturally",
        ],
    },
    "transformation": {
        "name": "embrace-change",
        "principles": [
            "Design for transformation; elements should change state gracefully",
            "Show before/after states clearly",
            "Use smooth morphing animations for state changes",
            "Provide visual feedback during every transformation",
        ],
    },
    "heat": {
        "name": "radiate-warmth",
        "principles": [
            "Radiate from a central focal point",
            "Use warm colors (oranges, reds, golds) for focal elements",
            "Add subtle glow to draw attention",
            "Use pulsing animations sparingly to suggest energy",
        ],
    },
    "flow": {
        "name": "go-with-the-flow",
        "principles": [
            "Let content flow continuously; avoid hard breaks",
            "Use wave-like, fluid spacing",
            "Use smooth scrolling and liquid animations",
            "Connect sections with flowing visual elements",
        ],
    },
    "depth": {
        "name": "think-in-layers",
        "principles": [
            "Think in layers; content exists at different depths",
            "Use parallax and elevation to suggest depth",
            "Use shadows to create a sense of depth",
            "Reveal deeper layers on interaction",
        ],
    },
    "hierarchy": {
        "name": "clear-descent",
        "principles": [
            "Establish clear vertical hierarchy",
            "Most important content at the top, largest and boldest",
            "Decrease size and weight as content descends",
            "Use clear section headers to mark hierarchy levels",
        ],
    },
    "balance": {
        "name": "find-equilibrium",
        "principles": [
            "Balance visual weight across the layout",
            "Use symmetric layouts for a sense of harmony",
            "Maintain equilibrium; avoid visual clutter",
            "Use harmonious spacing and proportions",
        ],
    },
    "mystery": {
        "name": "reveal-dont-show",
        "principles": [
            "Reveal, don't show; hide secondary content",
            "Use veils, overlays, and obscured elements",
            "Use slow fade-in animations for reveals",
            "Create a sense of discovery and exploration",
        ],
    },
    "revelation": {
        "name": "unfold-truth",
        "principles": [
            "Unfold content layer by layer",
            "Use peeling-back animations",
            "Reveal hidden content progressively",
            "Create a sense of discovery",
        ],
    },
    "wisdom": {
        "name": "layer-knowledge",
        "principles": [
            "Layer knowledge from surface to depth",
            "Use contemplative spacing and pacing",
            "Use classical, timeless typography",
            "Provide depth without overwhelming",
        ],
    },
    "light": {
        "name": "illuminate",
        "principles": [
            "Use light to draw attention to focal points",
            "Use illumination and glow effects",
            "Create contrast between light and dark",
            "Use dawning animations for reveals",
        ],
    },
    "creation": {
        "name": "let-it-emerge",
        "principles": [
            "Show emergence from a foundation",
            "Use building, accumulating animations",
            "Show crystallization and formation",
            "Create a sense of becoming",
        ],
    },
    "sacred": {
        "name": "honor-the-sacred",
        "principles": [
            "Use axial, processional layouts",
            "Use centered, reverent compositions",
            "Use processional spacing and pacing",
            "Create a sense of reverence and sacredness",
        ],
    },
}


def derive_guidelines(design_language):
    """Derive design guidelines from the design language's principles.
    Returns a dict of active guidelines with their principles.
    """
    active_principles = design_language.get("active_principles", [])
    active_guidelines = {}
    for principle in active_principles:
        if principle in DESIGN_GUIDELINES:
            active_guidelines[principle] = DESIGN_GUIDELINES[principle]
    return active_guidelines


if __name__ == "__main__":
    design_language = {
        "active_principles": ["mystery", "wisdom", "hierarchy"],
    }
    guidelines = derive_guidelines(design_language)
    for principle, guideline in guidelines.items():
        print(f"=== {principle}: {guideline['name']} ===")
        for principle_text in guideline["principles"]:
            print(f"    - {principle_text}")
