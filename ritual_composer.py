"""
ritual_composer.py — composes living rituals from project content.

THE INNOVATION:
A website should not be a static encyclopedia. It should be a LIVING RITUAL
that changes with time, revealing content gradually.

The ritual composer:
  1. Analyzes the project content
  2. Determines the ritual structure
  3. Composes the ritual for the current moment

The ritual changes based on:
  - Time of day (morning, afternoon, evening, night)
  - Day of week
  - Lunar phase
  - Season

This makes the website feel ALIVE, not static.
"""

from datetime import datetime

# ============================================================
# TIME AWARENESS
# ============================================================

def get_time_phase(now=None):
    """Determine the phase of the day."""
    if now is None:
        now = datetime.now()
    hour = now.hour
    if 5 <= hour < 10:
        return "morning"
    elif 10 <= hour < 16:
        return "afternoon"
    elif 16 <= hour < 20:
        return "evening"
    else:
        return "night"

def get_ritual_tone(phase):
    """The ritual tone changes with the time of day."""
    tones = {
        "morning": {
            "opening": "הבוקר עלה. מה אתה מבקש היום?",
            "closing": "היום נפתח. לך אליו.",
            "mood": "fresh",
        },
        "afternoon": {
            "opening": "היום בעיצומו. עצור לרגע.",
            "closing": "היום ממשיך. אבל אתה כבר לא אותו דבר.",
            "mood": "grounded",
        },
        "evening": {
            "opening": "היום נסגר. מה נשאר?",
            "closing": "הערב יורד. קח איתך רק מה שצריך.",
            "mood": "reflective",
        },
        "night": {
            "opening": "הלילה. הזמן שבו הכל שקט.",
            "closing": "הלילה שומר. מחר יבוא.",
            "mood": "quiet",
        },
    }
    return tones.get(phase, tones["afternoon"])
# ============================================================
# RITUAL COMPOSITION
# ============================================================

def compose_ritual(content_items, now=None):
    """Compose a complete ritual from the project content.
    
    The ritual has 4 parts:
      1. Opening (based on time of day)
      2. The reading (one item, chosen by day)
      3. The whisper (one item, chosen by day)
      4. Closing (based on time of day)
    """
    if now is None:
        now = datetime.now()
    if content_items is None:
        content_items = []

    phase = get_time_phase(now)
    tone = get_ritual_tone(phase)

    # Day number for deterministic content selection
    day_number = now.timetuple().tm_yday

    # Select content items
    reading = None
    whisper = None
    if len(content_items) > 0:
        reading = content_items[day_number % len(content_items)]
    if len(content_items) > 1:
        whisper = content_items[(day_number + 1) % len(content_items)]

    return {
        "phase": phase,
        "mood": tone["mood"],
        "opening": tone["opening"],
        "reading": reading,
        "whisper": whisper,
        "closing": tone["closing"],
    }

def render_ritual(ritual):
    """Render the ritual as a sequence of moments."""
    moments = []
    moments.append({"type": "opening", "text": ritual["opening"], "mood": ritual["mood"]})
    if ritual["reading"]:
        moments.append({"type": "reading", "content": ritual["reading"], "mood": ritual["mood"]})
    if ritual["whisper"]:
        moments.append({"type": "whisper", "content": ritual["whisper"], "mood": ritual["mood"]})
    moments.append({"type": "closing", "text": ritual["closing"], "mood": ritual["mood"]})
    return moments