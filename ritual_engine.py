"""ritual_engine.py - the complete engine that powers the living website."""

from datetime import datetime


def select_content_by_moment(content_pool, now=None):
    """Select content based on the current moment."""
    if now is None:
        now = datetime.now()
    if content_pool is None or len(content_pool) == 0:
        return None
    hour = now.hour
    day = now.timetuple().tm_yday
    month = now.month
    seed = (day * 24 + hour) * 100 + month
    index = seed % len(content_pool)
    return content_pool[index]


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


def get_ritual_words(phase):
    """Get the ritual opening and closing words for the phase."""
    words = {
        "morning": (
            "The morning has risen. What do you seek today?",
            "The day opens. Go to it.",
        ),
        "afternoon": (
            "The day is in its fullness. Stop for a moment.",
            "The day continues. But you are no longer the same.",
        ),
        "evening": (
            "The day closes. What remains?",
            "The evening descends. Take only what you need.",
        ),
        "night": (
            "The night. The time when all is quiet.",
            "The night watches. Tomorrow will come.",
        ),
    }
    return words.get(phase, words["afternoon"])


def compose_complete_ritual(content_pool, now=None):
    """Compose a complete ritual for the current moment."""
    if now is None:
        now = datetime.now()

    phase = get_time_phase(now)
    opening, closing = get_ritual_words(phase)
    selected = select_content_by_moment(content_pool, now)

    return {
        "phase": phase,
        "opening": opening,
        "content": selected,
        "closing": closing,
    }