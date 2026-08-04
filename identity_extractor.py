"""
identity_extractor.py — the POSITIVE space engine.

Eliminating tells gets a product to "not obviously AI". That is necessary but
not sufficient. To be "distinctively itself", the design must be GROWN from the
domain's own structure, not imported from an aesthetic library.

A DomainDNA has five roots. Every one must be traceable to the subject itself:
  motif     — the domain's own geometry/structure, as the organizing principle
  material  — the physical substance the UI is "made of"
  signature — the ONE gesture only this product has
  voice     — the written register, kept with discipline
  palette   — WHERE color comes from (its source), not which hex values
"""

import json

SCHEMA = ["motif", "material", "signature", "voice", "palette_logic",
          "hierarchy_logic", "rhythm_logic"]


def shoshana_dna():
    """Domain DNA for Shoshana, derived from Kabbalah's own structure."""
    return {
        "domain": "shoshana",
        "motif": (
            "The Tree of Life (עץ החיים) as layout logic, not decoration: "
            "content emanates top-down like the sefirot — source above, "
            "manifestation below. 22 paths = 22 cards is already in the data; "
            "the UI should make that correspondence visible."
        ),
        "material": (
            "Parchment and ink by day; night sky and candlelight by night. "
            "Gold only where something is holy — never as decoration."
        ),
        "signature": (
            "The rose (שושנה) as the single brand gesture: five petals as the "
            "organizing count, and the daily reading 'opens' like a petal "
            "unfolding — the one interaction no other product has."
        ),
        "voice": (
            "Quiet scholar, first person plural. Short declarative sentences. "
            "Sources named plainly (sifra, year, place). Never sells, never "
            "exclaims. The register of someone who has read the text."
        ),
        "palette_logic": (
            "Color from the materials: parchment (#e8dfc8 family), gall-ink "
            "(#14110d family), and one copper note (#8a5a2b) that reads as "
            "aged metal, not accent. Tradition/element colors stay semantic."
        ),
        "hierarchy_logic": (
            "Emanation, not grid: each section flows from the one above it; "
            "the eye descends the tree. No equal columns of features."
        ),
        "rhythm_logic": (
            "Breath rhythm (the existing BreathMoment) sets motion timing: "
            "4-7-8. Transitions inhale/exhale, never snap, never bounce."
        ),
    }


def validate_dna(dna):
    """A DNA is valid only if every root is present, specific, and non-generic."""
    problems = []
    for key in SCHEMA:
        if key not in dna or not str(dna[key]).strip():
            problems.append(f"missing root: {key}")
    # anti-generic: DNA must not contain AI-tell words as its own substance
    generic = ["modern", "clean", "minimal", "sleek", "seamless", "elevate",
               "cutting-edge", "user-friendly", "innovative"]
    blob = " ".join(str(dna[k]) for k in SCHEMA if k in dna).lower()
    hits = [g for g in generic if g in blob]
    if hits:
        problems.append(f"generic words in DNA: {hits}")
    return {"valid": not problems, "problems": problems}


if __name__ == "__main__":
    dna = shoshana_dna()
    v = validate_dna(dna)
    print(json.dumps({"validation": v}, ensure_ascii=False))
    print("\nSHOSHANA DNA:")
    for k in SCHEMA:
        print(f"  [{k}]\n    {dna[k][:160]}")
