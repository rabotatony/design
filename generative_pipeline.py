"""
generative_pipeline.py - Unified generative design pipeline.
Connects: identity mining -> generative design -> CSS generation.
This is a COMPLETE, TRULY GENERATIVE design system.
"""
import sys
sys.path.insert(0, "/workspace/gen2")
from generative_design import generate_design_from_identity, generate_color_harmony

def generate_css_from_design(design):
    """Generate CSS custom properties from a generative design."""
    palette = design["palette"]
    typography = design["typography"]
    spacing = design["spacing"]
    css_lines = []
    css_lines.append(":root {")
    css_lines.append("  /* Palette (generated from color theory) */")
    css_lines.append("  --surface-base: " + palette["base"] + ";")
    for i, color in enumerate(palette["surface_colors"]):
        css_lines.append("  --surface-" + str(i) + ": " + color + ";")
    harmony = palette["harmony"]
    if "analogous" in harmony:
        css_lines.append("  --accent: " + harmony["analogous"][-1] + ";")
    css_lines.append("")
    css_lines.append("  /* Typography (generated from mathematical ratios) */")
    for i, size in enumerate(typography["sizes"]):
        css_lines.append("  --text-" + str(i) + ": " + str(size) + "px;")
    css_lines.append("  --line-height: " + str(typography["line_height"]) + ";")
    css_lines.append("")
    css_lines.append("  /* Spacing (generated from mathematical ratios) */")
    for i, sp in enumerate(spacing["spacings"]):
        css_lines.append("  --space-" + str(i) + ": " + str(sp) + "px;")
    css_lines.append("}")
    return "\n".join(css_lines)
def run_generative_pipeline(content, identity_miner=None):
    """Run the complete generative design pipeline.
    content -> identity -> generative design -> CSS.
    """
    if identity_miner is None:
        from identity_miner import mine_identity
        identity = mine_identity(content)
    else:
        identity = identity_miner(content)
    design = generate_design_from_identity(identity)
    css = generate_css_from_design(design)
    return {
        "identity": identity,
        "design": design,
        "css": css,
    }

if __name__ == "__main__":
    content = """
    The book of creation says the world was built from three elements.
    The mystic reveals the hidden secrets. The ancient wisdom teaches the seeker.
    The parchment holds the sacred text. The candle illuminates the path.
    """
    result = run_generative_pipeline(content)
    print("Identity:", result["identity"])
    print()
    print("Generated CSS:")
    print(result["css"])