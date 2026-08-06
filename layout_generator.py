"""
layout_generator.py — generates actual HTML/CSS layouts from a design language.

This extends design generation beyond CSS custom properties to actual layouts.
The layout is DERIVED from the design language's principles, not picked from templates.

The key: the layout decisions are derived from the design language's principles.
For example, if the design language has "hierarchy" principle, the layout uses
a clear vertical hierarchy. If it has "mystery" principle, the layout uses
progressive revelation.
"""

# Layout templates derived from design principles.
# Each principle maps to a layout structure.
LAYOUT_TEMPLATES = {
    "hierarchy": {
        "structure": "vertical-stack",
        "description": "clear vertical hierarchy, top-down",
        "html": """
<div class="layout-hierarchy">
  <header class="level-1">
    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
  </header>
  <main class="level-2">
    <section class="content-block">
      {content}
    </section>
  </main>
  <footer class="level-3">
    {footer}
  </footer>
</div>
""",
        "css": """
.layout-hierarchy {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.level-1 {
  padding: var(--space-1) var(--space-2);
  text-align: center;
}
.level-2 {
  flex: 1;
  padding: var(--space-2);
  max-width: 800px;
  margin: 0 auto;
}
.level-3 {
  padding: var(--space-2);
  text-align: center;
}
""",
    },
    "mystery": {
        "structure": "progressive-reveal",
        "description": "progressive revelation, hidden depths",
        "html": """
<div class="layout-mystery">
  <div class="veil">
    <h1>{title}</h1>
    <p class="hint">{subtitle}</p>
  </div>
  <div class="reveal">
    <section class="hidden-content">
      {content}
    </section>
  </div>
</div>
""",
        "css": """
.layout-mystery {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.veil {
  padding: var(--space-1);
  text-align: center;
  opacity: 0.9;
}
.reveal {
  flex: 1;
  padding: var(--space-2);
  opacity: 0;
  transition: opacity 1s ease-in;
}
.reveal.visible {
  opacity: 1;
}
""",
    },
    "flow": {
        "structure": "continuous-flow",
        "description": "continuous, flowing, no hard breaks",
        "html": """
<div class="layout-flow">
  <div class="stream">
    <h1>{title}</h1>
    <div class="flow-content">
      {content}
    </div>
  </div>
</div>
""",
        "css": """
.layout-flow {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.stream {
  padding: var(--space-2);
  max-width: 700px;
  margin: 0 auto;
}
.flow-content {
  line-height: 1.8;
}
""",
    },
}


def derive_layout_structure(design_language):
    """Derive the layout structure from the design language's principles.
    Returns the layout template that best matches the active principles.
    """
    active_principles = design_language.get("active_principles", [])

    # Find the best matching layout template
    best_match = None
    best_score = 0
    for principle, template in LAYOUT_TEMPLATES.items():
        if principle in active_principles:
            best_match = template
            best_score += 1

    if best_match is None:
        # Default to hierarchy if no match
        best_match = LAYOUT_TEMPLATES["hierarchy"]

    return best_match


def generate_layout(design_language, content=None):
    """Generate an HTML/CSS layout from a design language.
    Returns (html, css) tuple.
    """
    content = content or {
        "title": "Title",
        "subtitle": "Subtitle",
        "content": "Content goes here",
        "footer": "Footer",
    }

    layout_template = derive_layout_structure(design_language)
    html = layout_template["html"].format(**content)
    css = layout_template["css"]

    return html, css


if __name__ == "__main__":
    # Test with a sample design language
    design_language = {
        "active_principles": ["hierarchy", "mystery"],
        "dimensions": {},
    }
    html, css = generate_layout(design_language)
    print("Generated HTML:")
    print(html)
    print("\nGenerated CSS:")
    print(css)
