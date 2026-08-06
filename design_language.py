"""
design_language.py — derives a complete design language from a project's identity.

The core principle: design is DERIVED from identity, not picked from templates.
This is what makes a design unique rather than generic-AI.
"""

PRINCIPLES = {
    "growth": {"layout": "progressive disclosure, expanding elements", "spacing": "increasing rhythm, breathing room that grows", "motion": "slow unfurling, organic easing", "geometry": "branching, fractal, organic curves"},
    "branching": {"layout": "hierarchical, tree-like navigation", "spacing": "nested indentation, parent-child relationships", "motion": "branching reveals, expanding nodes", "geometry": "tree structures, node-and-edge"},
    "transformation": {"layout": "before/after, progressive states", "spacing": "compressing then expanding", "motion": "morphing, state transitions", "geometry": "shapes that change, metamorphosis"},
    "heat": {"layout": "radiating from center, glowing focal points", "spacing": "tight at core, loose at edges", "motion": "pulsing glow, flickering", "geometry": "radiating, ember-like, warm"},
    "flow": {"layout": "continuous, flowing, no hard breaks", "spacing": "fluid, wave-like rhythm", "motion": "smooth flowing, liquid easing", "geometry": "waves, curves, fluid forms"},
    "depth": {"layout": "layered, parallax, foreground/background", "spacing": "layered depth, z-axis thinking", "motion": "parallax, depth shifts", "geometry": "layered planes, depth cues"},
    "hierarchy": {"layout": "clear vertical hierarchy, top-down", "spacing": "descending scale, clear levels", "motion": "descending reveals, cascading", "geometry": "stepped, tiered, pyramidal"},
    "balance": {"layout": "symmetric, centered, balanced", "spacing": "even, harmonious", "motion": "gentle, balanced transitions", "geometry": "symmetric, balanced forms"},
    "mystery": {"layout": "progressive revelation, hidden depths", "spacing": "generous negative space, breathing room", "motion": "slow reveals, fading in", "geometry": "veiled, layered, obscured"},
    "revelation": {"layout": "unfolding, revealing layers", "spacing": "opening up, expanding", "motion": "unfolding, peeling back", "geometry": "unfolding, opening forms"},
    "wisdom": {"layout": "layered knowledge, progressive depth", "spacing": "generous, contemplative", "motion": "slow, deliberate, thoughtful", "geometry": "structured, classical, timeless"},
    "light": {"layout": "radiating, illuminated focal points", "spacing": "expanding outward from light source", "motion": "gentle illumination, dawning", "geometry": "radiating, luminous, glowing"},
    "creation": {"layout": "emergent, building up from foundation", "spacing": "building, accumulating", "motion": "emergent, building, forming", "geometry": "forming, emerging, crystallizing"},
    "sacred": {"layout": "centered, axial, processional", "spacing": "generous, reverent, processional", "motion": "slow, reverent, processional", "geometry": "axial, processional, sacred geometry"},
}

MATERIAL_PALETTES = {
    "parchment": {"base": "warm light surface, aged paper", "ink": "dark warm brown, gall ink", "accent": "copper/gold, aged metal", "logic": "warm, aged, organic, hand-crafted"},
    "forge": {"base": "dark iron, forged metal", "ink": "warm light, heated glow", "accent": "ember orange, heated metal", "logic": "hot, strong, industrial, transformed"},
    "ocean": {"base": "deep blue, ocean depth", "ink": "light foam, sea spray", "accent": "teal, bioluminescence", "logic": "deep, flowing, vast, alive"},
    "forest": {"base": "deep green, forest floor", "ink": "light through leaves, dappled", "accent": "moss, lichen, growth", "logic": "organic, growing, layered, alive"},
    "stone": {"base": "cool gray, carved stone", "ink": "light on stone, etched", "accent": "mineral, crystalline", "logic": "solid, enduring, carved, timeless"},
    "night": {"base": "deep night, dark sky", "ink": "starlight, pale glow", "accent": "silver, moonlight", "logic": "dark, mysterious, celestial, quiet"},
}

CHARACTER_TYPOGRAPHY = {
    "mystical": {"display": "serif with character, ancient feel", "body": "readable serif, scholarly", "logic": "ancient wisdom, sacred texts"},
    "industrial": {"display": "strong geometric, industrial", "body": "clean sans, technical", "logic": "strength, precision, function"},
    "organic": {"display": "flowing, hand-drawn feel", "body": "warm humanist sans", "logic": "natural, growing, alive"},
    "scholarly": {"display": "classic serif, authoritative", "body": "readable serif, book-like", "logic": "knowledge, tradition, depth"},
    "sacred": {"display": "ancient serif, sacred feel", "body": "readable serif, reverent", "logic": "sacred texts, ancient wisdom"},
}

MOTIF_PRINCIPLE_MAP = {
    "tree": ["growth", "branching", "hierarchy"], "fire": ["heat", "transformation"],
    "forge": ["heat", "transformation"], "ocean": ["flow", "depth"], "water": ["flow", "depth"],
    "forest": ["growth", "branching"], "stone": ["hierarchy", "balance"],
    "mystery": ["mystery", "revelation"], "secret": ["mystery", "revelation"],
    "light": ["light", "revelation"], "wisdom": ["wisdom", "hierarchy"],
    "creation": ["creation", "growth"], "sacred": ["sacred", "hierarchy"],
    "book": ["wisdom", "revelation"], "path": ["flow", "revelation"],
    "עץ": ["growth", "branching", "hierarchy"], "חיים": ["growth", "light"],
    "אור": ["light", "revelation"], "ספר": ["wisdom", "revelation"],
    "יצירה": ["creation", "growth"], "מים": ["flow", "depth"], "אש": ["heat", "transformation"],
    "עץ חיים": ["growth", "branching", "hierarchy"], "קבלה": ["mystery", "wisdom", "sacred"],
    "מיסטיקה": ["mystery", "revelation"], "סוד": ["mystery", "revelation"],
    "חכמה": ["wisdom", "hierarchy"], "קדוש": ["sacred", "hierarchy"], "נתיב": ["flow", "revelation"],
    "נשמה": ["light", "revelation"],
}


def derive_principles(identity):
    motifs = identity.get("motifs", [])
    materials = identity.get("materials", [])
    character = identity.get("character", "")
    active = {}
    for motif in motifs:
        motif_lower = motif.lower()
        for key, principles in MOTIF_PRINCIPLE_MAP.items():
            if key in motif_lower:
                for p in principles:
                    if p in PRINCIPLES:
                        active[p] = PRINCIPLES[p]
    for material in materials:
        material_lower = material.lower()
        for key, principles in MOTIF_PRINCIPLE_MAP.items():
            if key in material_lower:
                for p in principles:
                    if p in PRINCIPLES:
                        active[p] = PRINCIPLES[p]
    for key, principles in MOTIF_PRINCIPLE_MAP.items():
        if key in character.lower():
            for p in principles:
                if p in PRINCIPLES:
                    active[p] = PRINCIPLES[p]
    return active


def derive_palette(identity):
    materials = identity.get("materials", [])
    for material in materials:
        material_lower = material.lower()
        for key, palette in MATERIAL_PALETTES.items():
            if key in material_lower:
                return {"material": key, **palette}
    return {"material": "parchment", **MATERIAL_PALETTES["parchment"]}


def derive_typography(identity):
    character = identity.get("character", "").lower()
    for key, typo in CHARACTER_TYPOGRAPHY.items():
        if key in character:
            return {"character": key, **typo}
    return {"character": "scholarly", **CHARACTER_TYPOGRAPHY["scholarly"]}


def derive_design_language(identity):
    principles = derive_principles(identity)
    palette = derive_palette(identity)
    typography = derive_typography(identity)
    layout_decisions = [p["layout"] for p in principles.values()]
    spacing_decisions = [p["spacing"] for p in principles.values()]
    motion_decisions = [p["motion"] for p in principles.values()]
    geometry_decisions = [p["geometry"] for p in principles.values()]
    return {
        "identity": identity,
        "active_principles": list(principles.keys()),
        "dimensions": {
            "palette": palette, "typography": typography,
            "layout": layout_decisions, "spacing": spacing_decisions,
            "motion": motion_decisions, "geometry": geometry_decisions,
        },
        "note": "Design derived from identity, not picked from templates.",
    }


if __name__ == "__main__":
    identity = {
        "motifs": ["ספר", "יצירה", "עץ", "חיים", "אור"],
        "materials": ["parchment"],
        "character": "mystical scholarly sacred",
    }
    lang = derive_design_language(identity)
    print("Active principles:", lang["active_principles"])
    print("Palette:", lang["dimensions"]["palette"])
    print("Typography:", lang["dimensions"]["typography"])
    print("Layout:", lang["dimensions"]["layout"])
