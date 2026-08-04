"""
tell_registry.py — the single source of truth for what makes a product look AI-built.

Every tell = a fingerprint of AVERAGING. Generative models optimize for "plausible
average good"; the tell is where the average shows through. Each tell carries:
  - signal : how to DETECT it (measurable)
  - counter: the OPPOSITE move that removes it (the "other layer")
  - weight : how strong a tell (0..1)

Two spaces:
  NEGATIVE SPACE ("not AI")  -> eliminate tells. Gets you to "not obviously AI".
  POSITIVE SPACE ("itself")  -> identity derived from the domain. Gets you to
                                "distinctively itself". This registry covers the
                                negative space + the identity-absence tells.
"""

# ─────────────────────────────────────────────────────────────────────────────
# COLOR
# ─────────────────────────────────────────────────────────────────────────────
COLOR = [
    {"id": "color.gradient_generic", "w": 0.9,
     "tell": "purple->blue / pink->orange / teal->purple gradients",
     "why": "the average of 'modern gradient' across training data",
     "signal": "2-stop linear-gradient whose hues fall in the 3 known AI bands",
     "counter": "single ink color, or a gradient derived from the domain's own material"},
    {"id": "color.aurora_bg", "w": 0.85,
     "tell": "soft aurora / rainbow blob backgrounds",
     "why": "diffusion 'ethereal background' mode",
     "signal": "large blurred multi-hue radial blobs behind hero",
     "counter": "one field of depth: parchment, night sky, or a real texture"},
    {"id": "color.neon_glow", "w": 0.7,
     "tell": "neon glow accents on dark UI",
     "why": "'futuristic' shortcut",
     "signal": "box-shadow with high-saturation low-lightness color",
     "counter": "candle-glow: warm low-saturation halo, or no glow at all"},
    {"id": "color.default_palette", "w": 0.8,
     "tell": "untouched Tailwind/Material default colors",
     "why": "never left the scaffold",
     "signal": "exact hex match to framework defaults (#3b82f6, #6366f1...)",
     "counter": "a palette mixed from the subject's real pigments"},
    {"id": "color.oversaturated", "w": 0.5,
     "tell": "everything at ~100% saturation",
     "why": "models push vibrance to look 'appealing'",
     "signal": "median accent saturation > 85%",
     "counter": "one saturated note in a field of muted ink"},
]

# ─────────────────────────────────────────────────────────────────────────────
# TYPOGRAPHY
# ─────────────────────────────────────────────────────────────────────────────
TYPO = [
    {"id": "type.font_generic", "w": 0.9,
     "tell": "Inter / Poppins / Montserrat / Roboto as the voice",
     "why": "the safe average of 'clean font'",
     "signal": "display font in the generic blocklist",
     "counter": "a typeface with a story, matched to the domain's era/texture"},
    {"id": "type.uniform_leading", "w": 0.6,
     "tell": "one line-height everywhere",
     "why": "a single default, never tuned",
     "signal": "all text nodes share identical line-height",
     "counter": "leading tuned per role: tight display, breathing body"},
    {"id": "type.no_optical", "w": 0.5,
     "tell": "no optical-size / no size-specific spacing",
     "why": "mathematical not optical alignment",
     "signal": "letter-spacing identical across all sizes",
     "counter": "letter-spacing opens as size shrinks; optical kerning pairs"},
    {"id": "type.system_only", "w": 0.55,
     "tell": "system font stack as the whole identity",
     "why": "no typographic decision was made",
     "signal": "font-family = system-ui with no loaded face",
     "counter": "load one characterful face and use it with intention"},
    {"id": "type.emoji_as_icon", "w": 0.5,
     "tell": "emoji as the icon system",
     "why": "fastest placeholder, never replaced",
     "signal": "emoji chars in feature/heading positions",
     "counter": "a drawn mark, or letterforms as glyphs"},
]

# ─────────────────────────────────────────────────────────────────────────────
# LAYOUT / STRUCTURE
# ─────────────────────────────────────────────────────────────────────────────
LAYOUT = [
    {"id": "layout.hero_formula", "w": 0.85,
     "tell": "centered heading + subtitle + 2 buttons, always",
     "why": "the modal hero across all landing pages",
     "signal": "hero = h1+p+button+button, text-align center",
     "counter": "an opening that behaves like the subject, not a template"},
    {"id": "layout.bento", "w": 0.7,
     "tell": "bento grid of equal rounded cards",
     "why": "the 2023-2025 'modern' layout average",
     "signal": "asymmetric-but-actually-uniform card grid",
     "counter": "one dominant gesture + subordinate details, like a manuscript page"},
    {"id": "layout.perfect_symmetry", "w": 0.7,
     "tell": "mirror symmetry on everything",
     "why": "symmetry is the loss-minimizing default",
     "signal": "horizontal flip similarity > 0.9 on hero/cards",
     "counter": "optical asymmetry: weight shifted to one side on purpose"},
    {"id": "layout.uniform_radius", "w": 0.8,
     "tell": "one border-radius on every element",
     "why": "a single variable, never differentiated",
     "signal": "all components share the same radius token",
     "counter": "radius hierarchy by role: amulet=round, card=soft, input=sharp"},
    {"id": "layout.equal_columns", "w": 0.6,
     "tell": "3 or 4 identical feature columns",
     "why": "the rule-of-three template",
     "signal": "N siblings with identical structure and near-identical width",
     "counter": "hierarchy: one leads, the rest serve; vary the rhythm"},
]

# ─────────────────────────────────────────────────────────────────────────────
# TEXTURE / MATERIAL / DEPTH
# ─────────────────────────────────────────────────────────────────────────────
TEXTURE = [
    {"id": "mat.no_grain", "w": 0.8,
     "tell": "perfectly clean flat surfaces, zero grain",
     "why": "models render idealized surfaces",
     "signal": "flat color fields with no noise/texture channel",
     "counter": "a faint grain or fiber at 2-4%: paper, linen, smoke"},
    {"id": "mat.flat_shadow", "w": 0.6,
     "tell": "one gray drop-shadow on everything",
     "why": "rgba(0,0,0,0.1) default",
     "signal": "single identical box-shadow across components",
     "counter": "shadow colored by the light source (warm candle, cool moon)"},
    {"id": "mat.glassmorphism", "w": 0.75,
     "tell": "frosted-glass translucent cards",
     "why": "a trend the model learned as 'premium'",
     "signal": "backdrop-filter: blur + translucent white",
     "counter": "opaque material with real depth: parchment on ink, or vice versa"},
    {"id": "mat.neumorphism", "w": 0.6,
     "tell": "soft dual-shadow extruded elements",
     "why": "another learned 'modern' trend",
     "signal": "two opposing soft shadows on same-bg elements",
     "counter": "committed surface, not an extrusion trick"},
]

# ─────────────────────────────────────────────────────────────────────────────
# COPY / TEXT
# ─────────────────────────────────────────────────────────────────────────────
COPY = [
    {"id": "copy.ai_vocab", "w": 0.9,
     "tell": "delve / tapestry / navigate / unlock / seamless / leverage / foster",
     "why": "LLM favorite tokens",
     "signal": "frequency of AI lexicon above threshold",
     "counter": "concrete domain words; the thing itself, named plainly"},
    {"id": "copy.parallel_bullets", "w": 0.8,
     "tell": "every bullet the same grammar + length",
     "why": "parallel completion is the easy path",
     "signal": "list items share POS-open and length within 15%",
     "counter": "vary the shape: one line, one clause, one image"},
    {"id": "copy.rule_of_three", "w": 0.7,
     "tell": "everything in threes",
     "why": "the most common rhetorical template",
     "signal": "triplets of adjectives/features/benefits",
     "counter": "one, or five, or an uneven honest number"},
    {"id": "copy.hedging", "w": 0.5,
     "tell": "'it's worth noting', 'it's important to'",
     "why": "safety-trained filler",
     "signal": "hedging phrase density",
     "counter": "say the thing directly"},
    {"id": "copy.no_specifics", "w": 0.85,
     "tell": "no numbers, no names, no dates, no place",
     "why": "averages contain no facts",
     "signal": "zero concrete entities per paragraph",
     "counter": "anchor with real specifics: a year, a source, a measured thing"},
    {"id": "copy.generic_valueprop", "w": 0.7,
     "tell": "'elevate your journey', 'empower your workflow'",
     "why": "interchangeable across all products",
     "signal": "value-prop passes the swap-test (fits any product)",
     "counter": "a claim only THIS product can make"},
]

# ─────────────────────────────────────────────────────────────────────────────
# CODE
# ─────────────────────────────────────────────────────────────────────────────
CODE = [
    {"id": "code.verbose_comments", "w": 0.6,
     "tell": "comments restating the obvious line",
     "why": "trained to be 'helpful'",
     "signal": "comment == paraphrase of the code it sits on",
     "counter": "comments only where intent isn't obvious; naming does the rest"},
    {"id": "code.generic_naming", "w": 0.5,
     "tell": "data/result/temp/handleThing everywhere",
     "why": "low-information defaults",
     "signal": "high ratio of generic identifiers",
     "counter": "names from the domain's own vocabulary"},
    {"id": "code.scaffold_structure", "w": 0.6,
     "tell": "untouched boilerplate folder/file layout",
     "why": "never reorganized for the actual problem",
     "signal": "exact match to framework scaffold tree",
     "counter": "structure shaped by the domain, not the template"},
    {"id": "code.todo_trails", "w": 0.4,
     "tell": "TODO/FIXME/placeholder comments left in",
     "why": "generation stopped before finishing",
     "signal": "TODO/FIXME/lorem density",
     "counter": "finished or removed; no loose threads"},
]

# ─────────────────────────────────────────────────────────────────────────────
# MOTION / INTERACTION
# ─────────────────────────────────────────────────────────────────────────────
MOTION = [
    {"id": "motion.uniform_easing", "w": 0.6,
     "tell": "one ease-in-out on every transition",
     "why": "single default, never tuned",
     "signal": "all animations share the same curve + duration",
     "counter": "an easing logic derived from the metaphor (breath, tide, flame)"},
    {"id": "motion.template_loading", "w": 0.5,
     "tell": "generic spinner/skeleton",
     "why": "default loading component",
     "signal": "standard spinner or skeleton blocks",
     "counter": "a loading gesture in-world (a candle lighting, a wheel turning)"},
    {"id": "motion.scale_hover", "w": 0.5,
     "tell": "every card scale-105 on hover",
     "why": "the one hover trick",
     "signal": "transform: scale on hover across all cards",
     "counter": "hover that reveals something about the object"},
]

# ─────────────────────────────────────────────────────────────────────────────
# UX / PRODUCT
# ─────────────────────────────────────────────────────────────────────────────
UX = [
    {"id": "ux.predictable_ia", "w": 0.6,
     "tell": "the standard SaaS sitemap (features/pricing/faq)",
     "why": "modal IA",
     "signal": "nav == the common template set",
     "counter": "IA organized by the user's actual ritual"},
    {"id": "ux.no_opinion", "w": 0.7,
     "tell": "every default is the safe middle",
     "why": "no stance was taken",
     "signal": "all settings/defaults are the median choice",
     "counter": "opinionated defaults that reflect a point of view"},
    {"id": "ux.cookie_onboarding", "w": 0.5,
     "tell": "generic 3-step onboarding carousel",
     "why": "the onboarding template",
     "signal": "carousel of 3 undifferentiated steps",
     "counter": "first-run that performs the product's core act immediately"},
]

# ─────────────────────────────────────────────────────────────────────────────
# IDENTITY-ABSENCE (the positive space, phrased as missing things)
# ─────────────────────────────────────────────────────────────────────────────
IDENTITY = [
    {"id": "id.no_domain_motif", "w": 0.9,
     "tell": "nothing derived from the subject's own structure",
     "why": "aesthetics imported, not grown from the domain",
     "signal": "no visual element traceable to the domain's geometry/text/ritual",
     "counter": "a motif extracted from the domain itself (for Shoshana: the Tree, "
               "the letters, the sefirot geometry, parchment-and-ink)"},
    {"id": "id.no_material_metaphor", "w": 0.7,
     "tell": "no physical material the UI 'is made of'",
     "why": "digital-generic, no substance",
     "signal": "no consistent material language (paper/ink/stone/light)",
     "counter": "commit to one material and let every surface obey it"},
    {"id": "id.no_signature_detail", "w": 0.8,
     "tell": "no single detail that only this product has",
     "why": "nothing was invented, everything chosen from the average",
     "signal": "every element exists in other products",
     "counter": "one signature gesture that becomes the brand's fingerprint"},
    {"id": "id.no_voice", "w": 0.7,
     "tell": "copy could be by anyone, for anything",
     "why": "no persona was committed to",
     "signal": "copy fails the voice-consistency test across pages",
     "counter": "a written voice with a register, and the discipline to keep it"},
]

REGISTRY = {
    "color": COLOR, "typography": TYPO, "layout": LAYOUT, "texture": TEXTURE,
    "copy": COPY, "code": CODE, "motion": MOTION, "ux": UX, "identity": IDENTITY,
}


def all_tells():
    out = []
    for layer, tells in REGISTRY.items():
        for t in tells:
            out.append({**t, "layer": layer})
    return out


def tells_by_layer(layer):
    return REGISTRY.get(layer, [])


def counters():
    """The full set of counter-moves: the generator's constraint checklist."""
    return [{"tell": t["id"], "do": t["counter"], "w": t["w"]}
            for t in all_tells()]


def top_tells(n=10):
    return sorted(all_tells(), key=lambda t: -t["w"])[:n]


def total_tells():
    return len(all_tells())


if __name__ == "__main__":
    tells = all_tells()
    print(f"registry: {len(tells)} tells across {len(REGISTRY)} layers")
    print("\nheaviest tells:")
    for t in top_tells(10):
        print(f"  {t['w']:.2f}  {t['id']:28s} {t['tell'][:50]}")
