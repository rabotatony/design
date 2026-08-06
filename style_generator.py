"""
style_generator.py — generates typography scale + spacing scale from a design language.

Extends design generation to include:
  1. Typography scale (font sizes, line heights, weights)
  2. Spacing scale (spacing increments)
  3. Border radius scale
  4. Shadow scale

The key: scales are derived from the design language's principles, not generic.
"""

# Typography scales derived from design principles.
TYPOGRAPHY_SCALES = {
    "wisdom": {
        "name": "contemplative-scale",
        "base_size": "18px",
        "scale_ratio": 1.25,
        "line_height": 1.8,
        "description": "Larger base size, generous line height for contemplative reading",
        "sizes": {
            "xs": "14px", "sm": "16px", "base": "18px",
            "lg": "22px", "xl": "28px", "2xl": "34px",
            "3xl": "42px", "4xl": "52px",
        },
    },
    "mystery": {
        "name": "veiled-scale",
        "base_size": "16px",
        "scale_ratio": 1.3,
        "line_height": 1.7,
        "description": "Moderate base size, dramatic scale ratio for reveals",
        "sizes": {
            "xs": "13px", "sm": "15px", "base": "16px",
            "lg": "21px", "xl": "27px", "2xl": "35px",
            "3xl": "45px", "4xl": "58px",
        },
    },
    "hierarchy": {
        "name": "descent-scale",
        "base_size": "16px",
        "scale_ratio": 1.333,
        "line_height": 1.6,
        "description": "Clear descending scale for hierarchy",
        "sizes": {
            "xs": "12px", "sm": "14px", "base": "16px",
            "lg": "21px", "xl": "28px", "2xl": "37px",
            "3xl": "49px", "4xl": "65px",
        },
    },
    "flow": {
        "name": "stream-scale",
        "base_size": "17px",
        "scale_ratio": 1.2,
        "line_height": 1.75,
        "description": "Flowing scale for continuous reading",
        "sizes": {
            "xs": "14px", "sm": "16px", "base": "17px",
            "lg": "20px", "xl": "24px", "2xl": "29px",
            "3xl": "35px", "4xl": "42px",
        },
    },
}

# Spacing scales derived from design principles.
SPACING_SCALES = {
    "wisdom": {
        "name": "contemplative-spacing",
        "base": "16px",
        "scale_ratio": 1.5,
        "description": "Generous spacing for contemplation",
        "sizes": {
            "xs": "8px", "sm": "12px", "base": "16px",
            "lg": "24px", "xl": "36px", "2xl": "54px",
            "3xl": "81px", "4xl": "121px",
        },
    },
    "mystery": {
        "name": "veiled-spacing",
        "base": "16px",
        "scale_ratio": 1.6,
        "description": "Dramatic spacing for reveals",
        "sizes": {
            "xs": "8px", "sm": "12px", "base": "16px",
            "lg": "26px", "xl": "41px", "2xl": "66px",
            "3xl": "105px", "4xl": "168px",
        },
    },
    "hierarchy": {
        "name": "descent-spacing",
        "base": "16px",
        "scale_ratio": 1.5,
        "description": "Clear descending spacing for hierarchy",
        "sizes": {
            "xs": "8px", "sm": "12px", "base": "16px",
            "lg": "24px", "xl": "36px", "2xl": "54px",
            "3xl": "81px", "4xl": "121px",
        },
    },
    "flow": {
        "name": "stream-spacing",
        "base": "16px",
        "scale_ratio": 1.4,
        "description": "Flowing spacing for continuous reading",
        "sizes": {
            "xs": "8px", "sm": "12px", "base": "16px",
            "lg": "22px", "xl": "31px", "2xl": "44px",
            "3xl": "61px", "4xl": "85px",
        },
    },
}


def derive_typography_scale(design_language):
    active_principles = design_language.get("active_principles", [])
    for principle in active_principles:
        if principle in TYPOGRAPHY_SCALES:
            return TYPOGRAPHY_SCALES[principle]
    return TYPOGRAPHY_SCALES.get("hierarchy", {})


def derive_spacing_scale(design_language):
    active_principles = design_language.get("active_principles", [])
    for principle in active_principles:
        if principle in SPACING_SCALES:
            return SPACING_SCALES[principle]
    return SPACING_SCALES.get("hierarchy", {})


def generate_typography_css(design_language):
    scale = derive_typography_scale(design_language)
    if not scale:
        return ""
    css_lines = [f"  /* Typography: {scale.get('description', '')} */"]
    for size_name, size_value in scale.get("sizes", {}).items():
        css_lines.append(f"  --text-{size_name}: {size_value};")
    css_lines.append(f"  --line-height: {scale.get('line_height', 1.6)};")
    return "\n".join(css_lines)


def generate_spacing_css(design_language):
    scale = derive_spacing_scale(design_language)
    if not scale:
        return ""
    css_lines = [f"  /* Spacing: {scale.get('description', '')} */"]
    for size_name, size_value in scale.get("sizes", {}).items():
        css_lines.append(f"  --space-{size_name}: {size_value};")
    return "\n".join(css_lines)


if __name__ == "__main__":
    design_language = {
        "active_principles": ["wisdom", "mystery", "hierarchy"],
    }
    print("Typography CSS:")
    print(generate_typography_css(design_language))
    print("\nSpacing CSS:")
    print(generate_spacing_css(design_language))
