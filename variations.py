import sys
import json
import zlib
import random

from designer import (
    FEELING_MAP, CONCEPT_PALETTES, generate_palette, generate_typography,
    generate_system, validate_design, _shift_hue,
)

# variations.py — N genuinely distinct design directions from one brief.
# Different concepts give different palettes, fonts and tension rules;
# hue offsets separate directions that share a feeling family.
# Deterministic: seeded per concept (crc32), same brief -> same directions.

ALTERNATES = ["workbench", "clay", "caliper", "tide", "forge", "vault", "craft", "ember"]
HUE_OFFSETS = [0, 15, -15, 30]
DOMAIN_MAP = {"fintech": "vault", "finance": "vault", "tech": "caliper", "health": "tide",
              "food": "clay", "art": "craft", "game": "forge", "education": "workbench"}


def candidate_concepts(brief):
    feeling = str(brief.get("feeling") or "").lower()
    project = str(brief.get("project") or "").lower()
    candidates = []
    for keyword, concepts in FEELING_MAP.items():
        if keyword in feeling:
            for c in concepts:
                if c in CONCEPT_PALETTES and c not in candidates:
                    candidates.append(c)
    for word, concept in DOMAIN_MAP.items():
        if word in project and concept not in candidates:
            candidates.append(concept)
    for alt in ALTERNATES:
        if alt not in candidates:
            candidates.append(alt)
    return candidates


def generate_design_for_concept(brief, concept, hue_shift=0):
    random.seed(zlib.crc32(concept.encode()) % 100000)
    palette = generate_palette(concept, brief)
    if hue_shift:
        for k in ("primary", "accent", "tension"):
            palette[k] = _shift_hue(palette[k], hue_shift)
    typography = generate_typography(concept, brief)
    system = generate_system(concept, brief)
    design = {
        "concept": concept,
        "palette": palette,
        "typography": typography,
        "spacing": system["spacing"],
        "radius": system["radius"],
        "effects": system["effects"],
    }
    validation = validate_design(design)
    attempts = 0
    while validation["genericity_score"] > 0.4 and attempts < 3:
        for k in ("primary", "accent", "tension"):
            palette[k] = _shift_hue(palette[k], 20)
        validation = validate_design(design)
        attempts += 1
    design["anti_ai_validation"] = validation
    return design


def generate_variations(brief, count=3):
    candidates = candidate_concepts(brief)
    variations = []
    for i, concept in enumerate(candidates[:count]):
        design = generate_design_for_concept(brief, concept, HUE_OFFSETS[i % len(HUE_OFFSETS)])
        variations.append({
            "index": i,
            "concept": concept,
            "genericity": design["anti_ai_validation"]["genericity_score"],
            "colors": {k: design["palette"][k] for k in ("primary", "secondary", "accent", "tension", "surface")},
            "display_font": design["typography"]["display"]["family"],
            "tension_rule": design["typography"]["tension_rule"],
            "design": design,
        })
    return variations


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: variations.py \'{"project": "...", "feeling": "..."}\' [count]')
        sys.exit(1)
    brief = json.loads(sys.argv[1])
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    result = generate_variations(brief, count)
    slim = [{k: v for k, v in item.items() if k != "design"} for item in result]
    print(json.dumps(slim, indent=2))
