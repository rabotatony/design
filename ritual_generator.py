"""
ritual_generator.py — transforms over-comprehensive AI projects into rituals.

THE CORE INSIGHT:
AI generates comprehensiveness (everything, all at once).
Humans generate focus (one thing, deeply).

The fix: find the ONE THING that matters, build a ritual around it.
"""

def detect_overcomprehensiveness(chapters_or_sections):
    """Detect if a project tries to cover too much."""
    if chapters_or_sections is None:
        chapters_or_sections = []
    n = len(chapters_or_sections)
    if n > 20:
        return {"severity": "extreme", "count": n,
                "diagnosis": "The project is an encyclopedia, not an experience.",
                "fix": "Show ONE thing at a time. Build a ritual."}
    elif n > 8:
        return {"severity": "high", "count": n,
                "diagnosis": "The project shows too much at once.",
                "fix": "Reduce to the essential few. Add breathing room."}
    return {"severity": "ok", "count": n}

def find_the_one_thing(content_items):
    """Find the ONE thing that should be the focus.
    
    Heuristic: the one thing is usually the thing that:
    - Brings people back (daily/recurring)
    - Has the most emotional resonance
    - Is the simplest to understand
    """
    if not content_items:
        return None
    # For a mysticism project, the one thing is the DAILY READING
    # It brings people back every day. It is personal. It is simple.
    daily_items = [item for item in content_items if "daily" in str(item).lower() or "today" in str(item).lower()]
    if daily_items:
        return {"one_thing": daily_items[0], "type": "daily_reading"}
    # Fallback: the first item
    return {"one_thing": content_items[0], "type": "primary"}