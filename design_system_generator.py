"""
design_system_generator.py — the unified end-to-end design generation system.

Connects all the pieces into a single system:
  content -> identity -> design language -> CSS + layouts + components

This is the complete design generation system. It takes a project's content
and generates a complete design system (CSS custom properties + layouts + components).

The key: the design is DERIVED from the project's identity, not picked from templates.
"""
import re
from collections import Counter


def mine_identity_from_content(content):
    """Mine a project's identity from its content."""
    words = re.findall(r"[\u0590-\u05FF\w]{3,}", content)
    word_counts = Counter(words)
    stop_words = {"של", "על", "את", "הוא", "היא", "הם", "לא", "כן", "אם", "כי",
                  "אבל", "או", "גם", "זה", "זאת", "אלה", "מה", "מי", "איך",
                  "the", "and", "for", "with", "that", "this", "from", "to"}
    meaningful = Counter({w: c for w, c in word_counts.items()
                          if w.lower() not in stop_words and c >= 2})
    motifs = [w for w, c in meaningful.most_common(5)]

    material_keywords = {
        "parchment": ["קלף", "דיו", "נייר", "parchment", "paper", "ink"],
        "forge": ["ברזל", "נפח", "מתכת", "forge", "metal", "iron"],
        "ocean": ["ים", "מים", "גלים", "ocean", "sea", "water"],
        "forest": ["יער", "עץ", "עצים", "forest", "tree", "wood"],
        "stone": ["אבן", "סלע", "stone", "rock"],
        "night": ["לילה", "חשך", "night", "dark"],
    }
    materials = []
    for material, keywords in material_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                materials.append(material)
                break

    character_keywords = {
        "mystical": ["מיסטיקה", "קבלה", "סוד", "mystical", "mystic", "kabbalah"],
        "industrial": ["תעשייה", "מכונה", "industrial", "machine", "factory"],
        "organic": ["טבע", "אורגני", "organic", "natural", "nature"],
        "scholarly": ["לימוד", "חכמה", "scholarly", "wisdom", "knowledge"],
        "sacred": ["קדוש", "sacred", "holy"],
    }
    character = "scholarly"
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


def generate_design_system(content):
    """Generate a complete design system from a project's content.
    Returns a dict with identity, design_language, css, layouts, components.
    """
    from design_language import derive_design_language
    from design_generator import generate_design_css
    from layout_generator import generate_layout
    from component_generator import generate_components
    from pattern_generator import derive_patterns

    # Step 1: mine identity
    identity = mine_identity_from_content(content)

    # Step 2: derive design language
    design_language = derive_design_language(identity)

    # Step 3: generate CSS custom properties
    design_css = generate_design_css(design_language)

    # Step 4: generate layouts
    layout_html, layout_css = generate_layout(design_language)

    # Step 5: generate components
    components = generate_components(design_language)

    # Step 6: derive design patterns
    patterns = derive_patterns(design_language)

    return {
        "identity": identity,
        "design_language": design_language,
        "css": design_css,
        "layout": {"html": layout_html, "css": layout_css},
        "components": components,
        "patterns": patterns,
    }


if __name__ == "__main__":
    content = """
    ספר יצירה אומר שהעולם נבנה משלוש אמות. אות אלף מים שין.
    הנתיב הראשון מכתר לחכמה. ספר יצירה פותח בה.
    עץ החיים הוא המבנה המארגן. האור יורד דרך הנתיבים.
    המיסטיקה מגלה את הסודות החבויים. הקבלה היא חכמה עתיקה.
    """
    system = generate_design_system(content)
    print("Identity:", system["identity"])
    print("\nActive principles:", system["design_language"]["active_principles"])
    print("\nGenerated CSS:")
    print(system["css"])
    print("\nGenerated layout HTML:")
    print(system["layout"]["html"])
    print("\nGenerated components:")
    for component_type, css in system["components"].items():
        print(f"  {component_type}: {len(css)} chars")
    print("\nGenerated patterns:")
    for principle, pattern in system["patterns"].items():
        print(f"  {principle}: {pattern['name']}")
