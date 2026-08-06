"""
design_pipeline.py — the full design generation pipeline.

Connects the three engines:
  1. identity mining   (dna_miner)      — extract the project's identity
  2. design language   (design_language) — derive a design language from identity
  3. design generation (design_generator) — generate actual CSS from the design language

This is the complete pipeline: content -> identity -> design language -> design.
"""
import re


def mine_identity_from_content(content):
    """Mine a project's identity from its content.
    Extracts motifs, materials, and character from the text.
    Returns an identity dict.
    """
    # Extract motifs: recurring meaningful words/concepts
    # This is a simplified version; a real implementation would use deeper NLP
    words = re.findall(r"[\u0590-\u05FF\w]{3,}", content)
    from collections import Counter
    word_counts = Counter(words)
    # Filter to meaningful words (not stop words)
    stop_words = {"של", "על", "את", "הוא", "היא", "הם", "לא", "כן", "אם", "כי",
                  "אבל", "או", "גם", "זה", "זאת", "אלה", "מה", "מי", "איך",
                  "the", "and", "for", "with", "that", "this", "from", "to"}
    meaningful = Counter({w: c for w, c in word_counts.items() if w.lower() not in stop_words and c >= 2})
    motifs = [w for w, c in meaningful.most_common(5)]

    # Detect materials from keywords
    material_keywords = {
        "parchment": ["קלף", "דיו", "נייר", "parchment", "paper", "ink"],
        "forge": ["ברזל", "נפח", "מתכת", "forge", "metal", "iron"],
        "ocean": ["ים", "מים", "גלים", "ocean", "sea", "water"],
        "forest": ["יער", "עץ", "עצים", "forest", "tree", "wood"],
        "stone": ["אבן", "סלע", "stone", "rock"],
    }
    materials = []
    for material, keywords in material_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                materials.append(material)
                break

    # Detect character from keywords
    character_keywords = {
        "mystical": ["מיסטיקה", "קבלה", "סוד", "mystical", "mystic", "kabbalah"],
        "industrial": ["תעשייה", "מכונה", "industrial", "machine", "factory"],
        "organic": ["טבע", "אורגני", "organic", "natural", "nature"],
        "scholarly": ["לימוד", "חכמה", "scholarly", "wisdom", "knowledge"],
    }
    character = "scholarly"  # default
    for char, keywords in character_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                character = char
                break

    return {
        "motifs": motifs,
        "materials": materials if materials else ["parchment"],
        "character": character,
    }


def generate_design_from_content(content):
    """Generate a complete design from a project's content.
    Full pipeline: content -> identity -> design language -> design.
    Returns (design_css, design_language, identity).
    """
    from design_language import derive_design_language
    from design_generator import generate_design_css

    # Step 1: mine identity
    identity = mine_identity_from_content(content)

    # Step 2: derive design language
    design_language = derive_design_language(identity)

    # Step 3: generate design
    design_css = generate_design_css(design_language)

    return design_css, design_language, identity


if __name__ == "__main__":
    # Test with sample content (Shoshana-like)
    content = """
    ספר יצירה אומר שהעולם נבנה משלוש אמות. אות אלף מים שין.
    הנתיב הראשון מכתר לחכמה. ספר יצירה פותח בה.
    עץ החיים הוא המבנה המארגן. האור יורד דרך הנתיבים.
    המיסטיקה מגלה את הסודות החבויים. הקבלה היא חכמה עתיקה.
    """
    css, lang, identity = generate_design_from_content(content)
    print("Identity:", identity)
    print("\nActive principles:", lang["active_principles"])
    print("\nGenerated CSS:")
    print(css)
