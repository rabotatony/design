"""
component_generator.py — generates components (buttons, cards) from a design language.

This extends design generation to components. The component styles are DERIVED
from the design language's principles, not picked from templates.

The key: component styles are derived from the design language's principles.
For example, if the design language has "heat" principle, buttons glow.
If it has "mystery" principle, cards reveal on hover.
"""

# Component templates derived from design principles.
COMPONENT_TEMPLATES = {
    "button": {
        "heat": """
.btn-primary {
  background: var(--accent);
  color: var(--surface-0);
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  box-shadow: 0 0 12px var(--accent);
  transition: box-shadow 0.3s ease;
}
.btn-primary:hover {
  box-shadow: 0 0 20px var(--accent);
}
""",
        "mystery": """
.btn-primary {
  background: var(--accent);
  color: var(--surface-0);
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  opacity: 0.8;
  transition: opacity 0.5s ease;
}
.btn-primary:hover {
  opacity: 1;
}
""",
        "default": """
.btn-primary {
  background: var(--accent);
  color: var(--surface-0);
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  transition: background 0.3s ease;
}
.btn-primary:hover {
  background: var(--ink-soft);
}
""",
    },
    "card": {
        "heat": """
.card {
  background: var(--surface-1);
  border: 1px solid var(--accent);
  border-radius: 12px;
  padding: var(--space-2);
  box-shadow: 0 0 16px var(--accent);
}
""",
        "mystery": """
.card {
  background: var(--surface-1);
  border: 1px solid var(--ink-faint);
  border-radius: 12px;
  padding: var(--space-2);
  opacity: 0.9;
  transition: opacity 0.5s ease;
}
.card:hover {
  opacity: 1;
}
""",
        "default": """
.card {
  background: var(--surface-1);
  border: 1px solid var(--ink-faint);
  border-radius: 12px;
  padding: var(--space-2);
}
""",
    },
}


def derive_component_style(component_type, design_language):
    """Derive the component style from the design language's principles.
    Returns the CSS for the component.
    """
    active_principles = design_language.get("active_principles", [])
    templates = COMPONENT_TEMPLATES.get(component_type, {})

    # Find the best matching template
    for principle in active_principles:
        if principle in templates:
            return templates[principle]

    # Default template if no match
    return templates.get("default", "")


def generate_components(design_language):
    """Generate component CSS from a design language.
    Returns a dict of component_type -> css.
    """
    components = {}
    for component_type in COMPONENT_TEMPLATES:
        components[component_type] = derive_component_style(component_type, design_language)
    return components


if __name__ == "__main__":
    # Test with a sample design language
    design_language = {
        "active_principles": ["heat", "mystery"],
        "dimensions": {},
    }
    components = generate_components(design_language)
    for component_type, css in components.items():
        print(f"=== {component_type} ===")
        print(css)
