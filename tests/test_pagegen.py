import json
from pagegen import generate_page, generate_all_pages, CONCEPT_COPY


def test_generates_page_files():
    files = generate_page({"concept": "workbench"})
    assert len(files) == 2
    assert "page/landing-page.tsx" in files
    assert "page/content.json" in files
    assert "export default" in files["page/landing-page.tsx"]


def test_page_uses_tokens():
    files = generate_page({"concept": "clay"})
    page = files["page/landing-page.tsx"]
    assert "var(--color-" in page
    assert "var(--font-display)" in page
    assert "var(--radius-md)" in page


def test_copy_per_concept():
    import re
    headlines = set()
    for concept in CONCEPT_COPY:
        files = generate_page({"concept": concept})
        page = files["page/landing-page.tsx"]
        leftovers = re.findall(r"\{\{[A-Z0-9_]+\}\}", page)
        assert not leftovers, f"{concept}: leftover placeholders {leftovers}"
        headlines.add(CONCEPT_COPY[concept]["headline"])
    assert len(headlines) == 8  # every concept has a distinct headline


def test_tension_in_page():
    files = generate_page({"concept": "forge"})
    page = files["page/landing-page.tsx"]
    assert "2px solid var(--color-tension)" in page  # quote border
    assert "2px solid var(--color-accent)" in page   # highlighted pricing tier
    assert 'variant="tension"' in page               # tension Card in features


def test_content_json_valid():
    files = generate_page({"concept": "tide"})
    copy = json.loads(files["page/content.json"])
    for key in ("headline", "subtitle", "f1_title", "quote", "tier1", "cta_button"):
        assert key in copy and copy[key]


def test_brief_overrides_logo():
    files = generate_page({"concept": "vault"}, {"project": "Acme Dashboard"})
    assert "acme" in files["page/landing-page.tsx"]
    result = generate_all_pages({"concept": "vault"})
    assert result["file_count"] == 2
    assert result["total_lines"] > 100
