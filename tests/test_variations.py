from variations import generate_variations, generate_design_for_concept, candidate_concepts

BRIEF = {"project": "fintech dashboard for freelancers",
         "feeling": "trustworthy but warm"}


def test_generates_three_variations():
    result = generate_variations(BRIEF)
    assert len(result) == 3
    concepts = [v["concept"] for v in result]
    assert len(set(concepts)) == 3


def test_variations_distinct():
    result = generate_variations(BRIEF)
    primaries = [v["colors"]["primary"] for v in result]
    assert len(set(primaries)) == 3
    fonts = [v["display_font"] for v in result]
    assert len(set(fonts)) >= 2


def test_variations_pass_genericity():
    result = generate_variations(BRIEF)
    for v in result:
        assert v["genericity"] < 0.5, f'{v["concept"]}: {v["genericity"]}'


def test_fallback_concepts():
    result = generate_variations({"project": "unknown thing"})
    assert len(result) == 3
    assert len(set(v["concept"] for v in result)) == 3


def test_forced_concept():
    design = generate_design_for_concept(BRIEF, "forge")
    assert design["concept"] == "forge"
    assert "palette" in design and "typography" in design


def test_deterministic():
    a = generate_variations(BRIEF)
    b = generate_variations(BRIEF)
    assert [v["colors"]["primary"] for v in a] == [v["colors"]["primary"] for v in b]
    assert [v["concept"] for v in a] == [v["concept"] for v in b]


def test_candidates_exclude_unknown_concepts():
    from designer import CONCEPT_PALETTES
    candidates = candidate_concepts(BRIEF)
    for c in candidates:
        assert c in CONCEPT_PALETTES
