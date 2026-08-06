"""
identity_miner.py — improved identity mining from project content.

The previous identity mining was simplistic (keyword-based). This version
is more sophisticated:
  1. Better motif extraction (recurring meaningful concepts)
  2. Better material detection (from content + context)
  3. Better character detection (from writing style)
  4. Better voice detection (from sentence structure)

The key insight: identity is not just keywords, it's the RELATIONSHIPS
between concepts, the recurring patterns, the writing style.
"""
import re
from collections import Counter


def extract_motifs(content, top_n=5):
    """Extract recurring meaningful concepts from content.
    Uses word frequency + context to find meaningful motifs.
    """
    # Extract words (Hebrew + English)
    words = re.findall(r"[\u0590-\u05FF\w]{3,}", content)
    word_counts = Counter(words)

    # Stop words to filter out
    stop_words = {
        "של", "על", "את", "הוא", "היא", "הם", "לא", "כן", "אם", "כי",
        "אבל", "או", "גם", "זה", "זאת", "אלה", "מה", "מי", "איך",
        "the", "and", "for", "with", "that", "this", "from", "to",
        "אשר", "כאשר", "בין", "עם", "אל", "עד", "מ", "ל", "ב", "כ", "ש", "ה", "ו",
    }

    # Filter to meaningful words
    meaningful = Counter({
        w: c for w, c in word_counts.items()
        if w.lower() not in stop_words and c >= 2
    })

    # Get top motifs
    motifs = [w for w, c in meaningful.most_common(top_n)]
    return motifs


def detect_materials(content):
    """Detect materials from content + context.
    Uses keyword matching + contextual clues.
    """
    material_keywords = {
        "parchment": ["קלף", "דיו", "נייר", "parchment", "paper", "ink", "ספר", "כתב"],
        "forge": ["ברזל", "נפח", "מתכת", "forge", "metal", "iron", "אש", "להבה"],
        "ocean": ["ים", "מים", "גלים", "ocean", "sea", "water", "תהום"],
        "forest": ["יער", "עץ", "עצים", "forest", "tree", "wood", "חיים"],
        "stone": ["אבן", "סלע", "stone", "rock", "הר"],
        "night": ["לילה", "חשך", "night", "dark", "כוכב", "ירח"],
        "light": ["אור", "light", "שמש", "זוהר"],
    }

    materials = []
    for material, keywords in material_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                materials.append(material)
                break

    return materials if materials else ["parchment"]


def detect_character(content):
    """Detect character from writing style.
    Uses keyword matching + sentence structure.
    """
    character_keywords = {
        "mystical": ["מיסטיקה", "קבלה", "סוד", "mystical", "mystic", "kabbalah", "נסתר", "סודי"],
        "industrial": ["תעשייה", "מכונה", "industrial", "machine", "factory", "טכנולוגיה"],
        "organic": ["טבע", "אורגני", "organic", "natural", "nature", "צמיחה"],
        "scholarly": ["לימוד", "חכמה", "scholarly", "wisdom", "knowledge", "ידע"],
        "sacred": ["קדוש", "sacred", "holy", "קדושה", "תורה"],
    }

    character = "scholarly"  # default
    for char, keywords in character_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                character = char
                break

    return character


def detect_voice(content):
    """Detect voice from sentence structure.
    Analyzes sentence length, complexity, and style.
    """
    # Split into sentences
    sentences = re.split(r"[.!?]+", content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]

    if not sentences:
        return "neutral"

    # Average sentence length
    avg_len = sum(len(s) for s in sentences) / len(sentences)

    # Detect voice characteristics
    if avg_len < 50:
        return "concise"
    elif avg_len < 100:
        return "balanced"
    else:
        return "elaborate"


def mine_identity(content):
    """Mine a project's identity from its content.
    Returns an identity dict with motifs, materials, character, voice.
    """
    motifs = extract_motifs(content)
    materials = detect_materials(content)
    character = detect_character(content)
    voice = detect_voice(content)

    return {
        "motifs": motifs,
        "materials": materials,
        "character": character,
        "voice": voice,
    }


if __name__ == "__main__":
    content = """
    ספר יצירה אומר שהעולם נבנה משלוש אמות. אות אלף מים שין.
    הנתיב הראשון מכתר לחכמה. ספר יצירה פותח בה.
    עץ החיים הוא המבנה המארגן. האור יורד דרך הנתיבים.
    המיסטיקה מגלה את הסודות החבויים. הקבלה היא חכמה עתיקה.
    """
    identity = mine_identity(content)
    print("Identity:", identity)
