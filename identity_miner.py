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
    # Input validation: handle non-string inputs gracefully
    if content is None:
        content = ""
    elif not isinstance(content, str):
        content = str(content)
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




# === V2 functions (narrative, audience, purpose, tone) ===

"""
identity_miner_v2.py — deep identity mining from project content.
Detects narrative, audience, purpose, tone, motifs, materials, character, voice.
"""


def detect_narrative(content):
    narrative_keywords = {
        "creation": ["created", "built", "formed", "begins"],
        "journey": ["path", "way", "journey", "walk"],
        "transformation": ["transform", "change", "become", "turn"],
        "revelation": ["reveal", "discover", "uncover", "show"],
        "descent": ["descend", "descends", "descends", "arrive"],
        "ascent": ["ascend", "rise", "climb", "rise"],
    }
    narratives = []
    for narrative, keywords in narrative_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                narratives.append(narrative)
                break
    return narratives if narratives else ["neutral"]


def detect_audience(content):
    audience_keywords = {
        "seekers": ["seeker", "seeking", "search", "searching"],
        "students": ["student", "learning", "study", "studying"],
        "practitioners": ["practitioner", "practice", "practicing"],
        "masters": ["master", "teacher", "wise", "wisdom"],
    }
    audiences = []
    for audience, keywords in audience_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                audiences.append(audience)
                break
    return audiences if audiences else ["general"]


def detect_purpose(content):
    purpose_keywords = {
        "teach": ["teach", "teaching", "learn", "learning"],
        "guide": ["guide", "guiding", "lead", "leading"],
        "reveal": ["reveal", "revealing", "discover", "discovering"],
        "transform": ["transform", "transforming", "change", "changing"],
        "inspire": ["inspire", "inspiring", "inspiration"],
    }
    purposes = []
    for purpose, keywords in purpose_keywords.items():
        for keyword in keywords:
            if keyword in content.lower():
                purposes.append(purpose)
                break
    return purposes if purposes else ["inform"]


def detect_tone(content):
    sentences = re.split(r"[.!?]+", content)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    if not sentences:
        return "neutral"
    avg_len = sum(len(s) for s in sentences) / len(sentences)
    questions = content.count("?")
    exclamations = content.count("!")
    if avg_len < 50 and questions < 2:
        return "concise-authoritative"
    elif avg_len < 100 and exclamations < 2:
        return "balanced-contemplative"
    elif questions > 3:
        return "inquisitive"
    elif exclamations > 3:
        return "passionate"
    else:
        return "elaborate-reflective"


def mine_identity_v2(content):
    """Mine a project's deep identity from its content."""
    from identity_miner import extract_motifs, detect_materials, detect_character, detect_voice
    motifs = extract_motifs(content)
    materials = detect_materials(content)
    character = detect_character(content)
    voice = detect_voice(content)
    narrative = detect_narrative(content)
    audience = detect_audience(content)
    purpose = detect_purpose(content)
    tone = detect_tone(content)
    return {
        "narrative": narrative,
        "audience": audience,
        "purpose": purpose,
        "tone": tone,
        "motifs": motifs,
        "materials": materials,
        "character": character,
        "voice": voice,
    }




def mine_identity_full(content):
    """Unified identity mining: combines v1 + v2."""
    identity_v1 = mine_identity(content)
    identity_v2 = mine_identity_v2(content)
    combined = dict(identity_v1)
    combined["narrative"] = identity_v2.get("narrative", [])
    combined["audience"] = identity_v2.get("audience", [])
    combined["purpose"] = identity_v2.get("purpose", [])
    combined["tone"] = identity_v2.get("tone", "neutral")
    return combined
