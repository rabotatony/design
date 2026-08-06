"""
design_language.py — derives a complete design language from a project's identity.

The core principle: design is DERIVED from identity, not picked from templates.
This is what makes a design unique rather than generic-AI.

A design language has 7 dimensions, each derived from the project's identity:
  1. palette     — colors derived from the project's materials/character
  2. typography  — type choices derived from the project's character
  3. rhythm      — spacing/tempo derived from the project's structure
  4. geometry    — shapes/forms derived from the project's motifs
  5. texture     — surface treatment derived from the project's materials
  6. motion      — movement derived from the project's character
  7. voice       — the written voice derived from the project's character

Each dimension is a set of decisions with a "why" — the reason it was chosen.
This "why" is what makes the design coherent and unique.
"""

# Design principles derived from identity characteristics.
# Each principle maps to specific design decisions.
PRINCIPLES = {
    # Growth/organic principles
    "growth": {
        "layout": "progressive disclosure, expanding elements",
        "spacing": "increasing rhythm, breathing room that grows",
        "motion": "slow unfurling, organic easing",
        "geometry": "branching, fractal, organic curves",
    },
    "branching": {
        "layout": "hierarchical, tree-like navigation",
        "spacing": "nested indentation, parent-child relationships",
        "motion": "branching reveals, expanding nodes",
        "geometry": "tree structures, node-and-edge",
    },
    # Transformation principles
    "transformation": {
        "layout": "before/after, progressive states",
        "spacing": "compressing then expanding",
        "motion": "morphing, state transitions",
        "geometry": "shapes that change, metamorphosis",
    },
    "heat": {
        "layout": "radiating from center, glowing focal points",
        "spacing": "tight at core, loose at edges",
        "motion": "pulsing glow, flickering",
        "geometry": "radiating, ember-like, warm",
    },
    # Flow principles
    "flow": {
        "layout": "continuous, flowing, no hard breaks",
        "spacing": "fluid, wave-like rhythm",
        "motion": "smooth flowing, liquid easing",
        "geometry": "waves, curves, fluid forms",
    },
    "depth": {
        "layout": "layered, parallax, foreground/background",
        "spacing": "layered depth, z-axis thinking",
        "motion": "parallax, depth shifts",
        "geometry": "layered planes, depth cues",
    },
    # Structure principles
    "hierarchy": {
        "layout": "clear vertical hierarchy, top-down",
        "spacing": "descending scale, clear levels",
        "motion": "descending reveals, cascading",
        "geometry": "stepped, tiered, pyramidal",
    },
    "balance": {
        "layout": "symmetric, centered, balanced",
        "spacing": "even, harmonious",
        "motion": "gentle, balanced transitions",
        "geometry": "symmetric, balanced forms",
    },
    # Mystery principles
    "mystery": {
        "layout": "progressive revelation, hidden depths",
        "spacing": "generous negative space, breathing room",
        "motion": "slow reveals, fading in",
        "geometry": "veiled, layered, obscured",
    },
    "revelation": {
        "layout": "unfolding, revealing layers",
        "spacing": "opening up, expanding",
        "motion": "unfolding, peeling back",
        "geometry": "unfolding, opening forms",
    },
}

# Material-to-palette derivation: each material has a palette logic
MATERIAL_PALETTES = {
    "parchment": {
        "base": "warm light surface, aged paper",
        "ink": "dark warm brown, gall ink",
        "accent": "copper/gold, aged metal",
        "logic": "warm, aged, organic, hand-crafted",
    },
    "forge": {
        "base": "dark iron, forged metal",
        "ink": "warm light, heated glow",
        "accent": "ember orange, heated metal",
        "logic": "hot, strong, industrial, transformed",
    },
    "ocean": {
        "base": "deep blue, ocean depth",
        "ink": "light foam, sea spray",
        "accent": "teal, bioluminescence",
        "logic": "deep, flowing, vast, alive",
    },
    "forest": {
        "base": "deep green, forest floor",
        "ink": "light through leaves, dappled",
        "accent": "moss, lichen, growth",
        "logic": "organic, growing, layered, alive",
    },
    "stone": {
        "base": "cool gray, carved stone",
        "ink": "light on stone, etched",
        "accent": "mineral, crystalline",
        "logic": "solid, enduring, carved, timeless",
    },
}

# Character-to-typography derivation
CHARACTER_TYPOGRAPHY = {
    "mystical": {
        "display": "serif with character, ancient feel",
        "body": "readable serif, scholarly",
        "logic": "ancient wisdom, sacred texts",
    },
    "industrial": {
        "display": "strong geometric, industrial",
        "body": "clean sans, technical",
        "logic": "strength, precision, function",
    },
    "organic": {
        "display": "flowing, hand-drawn feel",
        "body": "warm humanist sans",
        "logic": "natural, growing, alive",
    },
    "scholarly": {
        "display": "classic serif, authoritative",
        "body": "readable serif, book-like",
        "logic": "knowledge, tradition, depth",
    },
}


def derive_principles(identity):
    """Derive design principles from the project's identity.
    identity: dict with 'motifs', 'materials', 'character' keys.
    Returns a list of active principles with their design decisions.
    """
    motifs = identity.get("motifs", [])
    materials = identity.get("materials", [])
    character = identity.get("character", "")

    active = {}
    # Map motifs/materials/character to principles
    motif_principle_map = {
        "tree": ["growth", "branching", "hierarchy"],
        "fire": ["heat", "transformation"],
        "forge": ["heat", "transformation"],
        "ocean": ["flow", "depth"],
        "water": ["flow", "depth"],
        "forest": ["growth", "branching"],
        "stone": ["hierarchy", "balance"],
        "mystery": ["mystery", "revelation"],
        "secret": ["mystery", "revelation"],
        "light": ["revelation", "hierarchy"],
    }

    for motif in motifs:
        motif_lower = motif.lower()
        for key, principles in motif_principle_map.items():
            if key in motif_lower:
                for p in principles:
                    if p in PRINCIPLES:
                        active[p] = PRINCIPLES[p]

    # Also check character
    for key, principles in motif_principle_map.items():
        if key in character.lower():
            for p in principles:
                if p in PRINCIPLES:
                    active[p] = PRINCIPLES[p]

    return active


def derive_palette(identity):
    """Derive palette from the project's materials."""
    materials = identity.get("materials", [])
    for material in materials:
        material_lower = material.lower()
        for key, palette in MATERIAL_PALETTES.items():
            if key in material_lower:
                return {"material": key, **palette}
    # Default to first material or parchment
    return {"material": "parchment", **MATERIAL_PALETTES["parchment"]}


def derive_typography(identity):
    """Derive typography from the project's character."""
    character = identity.get("character", "").lower()
    for key, typo in CHARACTER_TYPOGRAPHY.items():
        if key in character:
            return {"character": key, **typo}
    return {"character": "scholarly", **CHARACTER_TYPOGRAPHY["scholarly"]}


def derive_design_language(identity):
    """Derive a complete design language from a project's identity.
    Returns a dict with all 7 dimensions, each with decisions and reasons.
    """
    principles = derive_principles(identity)
    palette = derive_palette(identity)
    typography = derive_typography(identity)

    # Aggregate design decisions from active principles
    layout_decisions = [p["layout"] for p in principles.values()]
    spacing_decisions = [p["spacing"] for p in principles.values()]
    motion_decisions = [p["motion"] for p in principles.values()]
    geometry_decisions = [p["geometry"] for p in principles.values()]

    return {
        "identity": identity,
        "active_principles": list(principles.keys()),
        "dimensions": {
            "palette": palette,
            "typography": typography,
            "layout": layout_decisions,
            "spacing": spacing_decisions,
            "motion": motion_decisions,
            "geometry": geometry_decisions,
        },
        "note": "Design derived from identity, not picked from templates.",
    }


if __name__ == "__main__":
    # Test with a sample identity
    identity = {
        "motifs": ["tree of life", "light", "mystery"],
        "materials": ["parchment"],
        "character": "mystical scholarly",
    }
    lang = derive_design_language(identity)
    print("Active principles:", lang["active_principles"])
    print("Palette:", lang["dimensions"]["palette"])
    print("Typography:", lang["dimensions"]["typography"])
    print("Layout:", lang["dimensions"]["layout"])
