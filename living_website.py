"""
living_website.py — makes the website ALIVE with lunar and seasonal awareness.

THE INNOVATION:
A mysticism website should be connected to the actual cosmos.
The lunar phase, the season, the day of week — these should affect
what the website shows and how it feels.

This is what makes a website feel HUMAN and ALIVE, not static and AI.
"""

from datetime import datetime
import math

# ============================================================
# LUNAR PHASE
# ============================================================

def get_lunar_phase(now=None):
    """Calculate the current lunar phase (0-1, where 0=new moon, 0.5=full moon)."""
    if now is None:
        now = datetime.now()
    # Synodic month is ~29.53 days
    # Reference new moon: January 6, 2000
    ref = datetime(2000, 1, 6, 18, 14)
    days = (now - ref).total_seconds() / 86400
    phase = (days % 29.53) / 29.53
    return phase

def get_lunar_phase_name(phase):
    """Get the name of the lunar phase."""
    if phase < 0.0625:
        return "מולד"  # New moon
    elif phase < 0.1875:
        return "סהר מתמלא"  # Waxing crescent
    elif phase < 0.3125:
        return "רבע ראשון"  # First quarter
    elif phase < 0.4375:
        return "סהר מתמלא"  # Waxing gibbous
    elif phase < 0.5625:
        return "מלא"  # Full moon
    elif phase < 0.6875:
        return "סהר מתמעט"  # Waning gibbous
    elif phase < 0.8125:
        return "רבע אחרון"  # Last quarter
    else:
        return "סהר מתמעט"  # Waning crescent

def get_lunar_ritual_tone(phase):
    """The ritual tone changes with the lunar phase."""
    if phase < 0.25:
        return {"mood": "beginning", "theme": "זמן לזרוע. מה אתה רוצה שיתחיל?"}
    elif phase < 0.5:
        return {"mood": "growing", "theme": "הדבר גדל. תן לו מקום."}
    elif phase < 0.75:
        return {"mood": "full", "theme": "השיא. מה אתה רואה עכשיו?"}
    else:
        return {"mood": "releasing", "theme": "זמן לשחרר. מה כבר לא צריך?"}
# ============================================================
# SEASONAL AWARENESS
# ============================================================

def get_season(now=None):
    """Get the current season."""
    if now is None:
        now = datetime.now()
    month = now.month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        return "winter"

def get_seasonal_tone(season):
    """The ritual tone changes with the season."""
    tones = {
        "spring": {"mood": "renewal", "theme": "משהו חדש מתחיל. מה נולד?"},
        "summer": {"mood": "fullness", "theme": "הכל פורח. מה אתה עושה עם השפע?"},
        "autumn": {"mood": "harvest", "theme": "זמן לאסוף. מה הבשיל?"},
        "winter": {"mood": "rest", "theme": "זמן לנוח. מה מחכה מתחת לפני השטח?"},
    }
    return tones.get(season, tones["summer"])

# ============================================================
# COMPLETE LIVING WEBSITE STATE
# ============================================================

def get_living_state(now=None):
    """Get the complete living state of the website.
    
    This combines:
      - Time of day (morning, afternoon, evening, night)
      - Lunar phase (new, waxing, full, waning)
      - Season (spring, summer, autumn, winter)
    
    The website uses this state to determine what to show.
    """
    from ritual_composer import get_time_phase, get_ritual_tone
    if now is None:
        now = datetime.now()

    phase = get_time_phase(now)
    time_tone = get_ritual_tone(phase)

    lunar_phase = get_lunar_phase(now)
    lunar_name = get_lunar_phase_name(lunar_phase)
    lunar_tone = get_lunar_ritual_tone(lunar_phase)

    season = get_season(now)
    seasonal_tone = get_seasonal_tone(season)

    return {
        "time_phase": phase,
        "time_tone": time_tone,
        "lunar_phase": lunar_phase,
        "lunar_name": lunar_name,
        "lunar_tone": lunar_tone,
        "season": season,
        "seasonal_tone": seasonal_tone,
    }