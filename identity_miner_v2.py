"""
identity_miner_v2.py — deep identity mining from project content.
Detects narrative, audience, purpose, tone, motifs, materials, character, voice.
"""
import re
from collections import Counter


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


if __name__ == "__main__":
    content = """
    The book of creation says the world was built from three elements.
    The first path descends from crown to wisdom. The light descends through the paths.
    The mystic reveals the hidden secrets. The ancient wisdom teaches the seeker.
    """
    identity = mine_identity_v2(content)
    print("Deep Identity:", identity)
