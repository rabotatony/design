import sys
import io
import re
import json
import base64
import zipfile

# codegen.py — turns a design system (from designer.py or redesigner.py)
# into a ready-to-use React component library.
# Components consume CSS variables from tokens.css — no Tailwind at runtime.
# Tension is baked into the code: buttons --radius-sm vs cards --radius-md,
# asymmetric section spacing, one 2px-border Card variant.

BUTTON_TSX = 'import type { CSSProperties, ReactNode } from "react";\n\ntype Variant = "primary" | "secondary" | "ghost" | "danger";\n\n// Tension: buttons use --radius-sm while cards use --radius-md. Deliberately different.\nexport default function Button({\n  variant = "primary",\n  children,\n  onClick,\n  type = "button",\n}: {\n  variant?: Variant;\n  children: ReactNode;\n  onClick?: () => void;\n  type?: "button" | "submit";\n}) {\n  const variants: Record<Variant, CSSProperties> = {\n    primary: {\n      background: "var(--color-primary)",\n      color: "var(--color-surface)",\n      border: "1px solid var(--color-primary)",\n    },\n    secondary: {\n      background: "transparent",\n      color: "var(--color-secondary)",\n      border: "1px solid var(--color-secondary)",\n    },\n    ghost: {\n      background: "transparent",\n      color: "var(--color-text-muted)",\n      border: "1px solid transparent",\n    },\n    danger: {\n      background: "var(--color-error)",\n      color: "#FFFFFF",\n      border: "1px solid var(--color-error)",\n    },\n  };\n  return (\n    <button\n      type={type}\n      onClick={onClick}\n      style={{\n        fontFamily: "var(--font-body)",\n        fontSize: 14,\n        fontWeight: 600,\n        padding: "10px 20px",\n        borderRadius: "var(--radius-sm)",\n        cursor: "pointer",\n        ...variants[variant],\n      }}\n    >\n      {children}\n    </button>\n  );\n}\n'

CARD_TSX = 'import type { CSSProperties, ReactNode } from "react";\n\n// Tension: variant="tension" renders the one 2px border in the system.\nexport default function Card({\n  title,\n  children,\n  footer,\n  variant = "default",\n}: {\n  title?: string;\n  children: ReactNode;\n  footer?: ReactNode;\n  variant?: "default" | "tension";\n}) {\n  const style: CSSProperties = {\n    background: "var(--color-surface)",\n    border: (variant === "tension" ? "2px" : "1px") + " solid var(--color-border)",\n    borderRadius: "var(--radius-md)",\n    padding: "var(--space-24)",\n    boxShadow: "var(--shadow)",\n  };\n  return (\n    <div style={style}>\n      {title && (\n        <h3\n          style={{\n            fontFamily: "var(--font-heading)",\n            color: "var(--color-text)",\n            fontSize: 17,\n            marginTop: 0,\n            marginBottom: "var(--space-12)",\n          }}\n        >\n          {title}\n        </h3>\n      )}\n      <div\n        style={{\n          fontFamily: "var(--font-body)",\n          color: "var(--color-text-muted)",\n          fontSize: 14,\n          lineHeight: 1.5,\n        }}\n      >\n        {children}\n      </div>\n      {footer && <div style={{ marginTop: "var(--space-16)" }}>{footer}</div>}\n    </div>\n  );\n}\n'

INPUT_TSX = 'import type { CSSProperties } from "react";\n\n// Form controls: text input, textarea, select. Error state uses --color-error.\nexport default function Input({\n  label,\n  error,\n  type = "text",\n  placeholder,\n  as = "input",\n  options,\n  value,\n  onChange,\n}: {\n  label?: string;\n  error?: string;\n  type?: string;\n  placeholder?: string;\n  as?: "input" | "textarea" | "select";\n  options?: string[];\n  value?: string;\n  onChange?: (v: string) => void;\n}) {\n  const base: CSSProperties = {\n    width: "100%",\n    boxSizing: "border-box",\n    background: "var(--color-surface-alt)",\n    border: error ? "1px solid var(--color-error)" : "1px solid var(--color-border)",\n    borderRadius: "var(--radius-sm)",\n    color: "var(--color-text)",\n    fontFamily: "var(--font-body)",\n    fontSize: 14,\n    padding: "10px 12px",\n    outline: "none",\n  };\n  const labelStyle: CSSProperties = {\n    display: "block", fontFamily: "var(--font-body)", fontSize: 12,\n    color: "var(--color-text-muted)", marginBottom: 6,\n  };\n  const handle = (e: { target: { value: string } }) => onChange && onChange(e.target.value);\n  return (\n    <label style={{ display: "block" }}>\n      {label && <span style={labelStyle}>{label}</span>}\n      {as === "textarea" ? (\n        <textarea style={{ ...base, minHeight: 96 }} placeholder={placeholder} value={value} onChange={handle} />\n      ) : as === "select" ? (\n        <select style={base} value={value} onChange={handle}>\n          {(options || []).map((o) => (\n            <option key={o} value={o}>{o}</option>\n          ))}\n        </select>\n      ) : (\n        <input style={base} type={type} placeholder={placeholder} value={value} onChange={handle} />\n      )}\n      {error && (\n        <span style={{ display: "block", fontSize: 12, fontFamily: "var(--font-body)", color: "var(--color-error)", marginTop: 4 }}>\n          {error}\n        </span>\n      )}\n    </label>\n  );\n}\n'

ALERT_TSX = 'import type { ReactNode } from "react";\n\nconst COLORS = {\n  success: "var(--color-success)",\n  warning: "var(--color-warning)",\n  error: "var(--color-error)",\n};\n\nexport default function Alert({\n  variant = "success",\n  children,\n  onClose,\n}: {\n  variant?: "success" | "warning" | "error";\n  children: ReactNode;\n  onClose?: () => void;\n}) {\n  return (\n    <div\n      role="alert"\n      style={{\n        display: "flex",\n        alignItems: "center",\n        gap: 12,\n        background: "var(--color-surface-alt)",\n        border: "1px solid " + COLORS[variant],\n        borderLeft: "4px solid " + COLORS[variant],\n        borderRadius: "var(--radius-sm)",\n        padding: "12px 16px",\n        fontFamily: "var(--font-body)",\n        fontSize: 14,\n        color: "var(--color-text)",\n      }}\n    >\n      <span style={{ flex: 1 }}>{children}</span>\n      {onClose && (\n        <button\n          onClick={onClose}\n          aria-label="dismiss"\n          style={{\n            background: "transparent",\n            border: "none",\n            color: "var(--color-text-muted)",\n            cursor: "pointer",\n            fontSize: 16,\n          }}\n        >\n          ×\n        </button>\n      )}\n    </div>\n  );\n}\n'

NAV_TSX = '// Nav: logo + links + CTA. Display font on logo, accent on CTA.\nexport default function Nav({\n  logo,\n  links,\n  cta,\n  onCta,\n}: {\n  logo: string;\n  links: { label: string; href: string }[];\n  cta?: string;\n  onCta?: () => void;\n}) {\n  return (\n    <nav\n      style={{\n        display: "flex",\n        alignItems: "center",\n        gap: 24,\n        flexWrap: "wrap",\n        padding: "16px 24px",\n        background: "var(--color-surface)",\n        borderBottom: "1px solid var(--color-border)",\n      }}\n    >\n      <span\n        style={{\n          fontFamily: "var(--font-display)",\n          fontSize: 18,\n          fontWeight: 500,\n          letterSpacing: "var(--tracking-display)",\n          color: "var(--color-primary)",\n        }}\n      >\n        {logo}\n      </span>\n      <span style={{ display: "flex", gap: 20, flex: 1, flexWrap: "wrap" }}>\n        {links.map((l) => (\n          <a\n            key={l.href}\n            href={l.href}\n            style={{ fontFamily: "var(--font-body)", fontSize: 14, color: "var(--color-text-muted)", textDecoration: "none" }}\n          >\n            {l.label}\n          </a>\n        ))}\n      </span>\n      {cta && (\n        <button\n          onClick={onCta}\n          style={{\n            background: "var(--color-accent)",\n            color: "var(--color-surface)",\n            border: "none",\n            borderRadius: "var(--radius-sm)",\n            padding: "8px 16px",\n            fontFamily: "var(--font-body)",\n            fontSize: 13,\n            fontWeight: 600,\n            cursor: "pointer",\n          }}\n        >\n          {cta}\n        </button>\n      )}\n    </nav>\n  );\n}\n'

HERO_TSX = 'import Button from "./Button";\n\n// Tension: asymmetric vertical spacing (--section-top differs from --section-bottom).\nexport default function Hero({\n  title,\n  subtitle,\n  primaryCta,\n  secondaryCta,\n  onPrimary,\n  onSecondary,\n}: {\n  title: string;\n  subtitle: string;\n  primaryCta?: string;\n  secondaryCta?: string;\n  onPrimary?: () => void;\n  onSecondary?: () => void;\n}) {\n  return (\n    <section\n      style={{\n        paddingTop: "var(--section-top)",\n        paddingBottom: "var(--section-bottom)",\n        paddingLeft: 24,\n        paddingRight: 32,\n        maxWidth: 1200,\n        margin: "0 auto",\n      }}\n    >\n      <h1\n        style={{\n          fontFamily: "var(--font-display)",\n          fontWeight: 500,\n          fontSize: 48,\n          letterSpacing: "var(--tracking-display)",\n          color: "var(--color-text)",\n          marginTop: 0,\n          marginBottom: 16,\n        }}\n      >\n        {title}\n      </h1>\n      <p\n        style={{\n          fontFamily: "var(--font-body)",\n          fontSize: 17,\n          color: "var(--color-text-muted)",\n          maxWidth: 560,\n          marginBottom: 32,\n        }}\n      >\n        {subtitle}\n      </p>\n      <span style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>\n        {primaryCta && <Button onClick={onPrimary}>{primaryCta}</Button>}\n        {secondaryCta && (\n          <Button variant="secondary" onClick={onSecondary}>\n            {secondaryCta}\n          </Button>\n        )}\n      </span>\n    </section>\n  );\n}\n'

SHOWCASE_TSX = 'import Nav from "./components/Nav";\nimport Hero from "./components/Hero";\nimport Card from "./components/Card";\nimport Button from "./components/Button";\nimport Input from "./components/Input";\nimport Alert from "./components/Alert";\n\n// Showcase: every component and variant on one page.\n// Import tokens.css once in your root layout before mounting this.\nexport default function Showcase() {\n  return (\n    <div style={{ background: "var(--color-surface)", minHeight: "100vh", color: "var(--color-text)" }}>\n      <Nav\n        logo="acme"\n        links={[\n          { label: "product", href: "#" },\n          { label: "pricing", href: "#" },\n          { label: "docs", href: "#" },\n        ]}\n        cta="start"\n      />\n      <Hero\n        title="built like a workshop, not a template"\n        subtitle="A design system with deliberate tension: asymmetric section spacing, split radius, one loud border."\n        primaryCta="get started"\n        secondaryCta="read more"\n      />\n      <section style={{ maxWidth: 1200, margin: "0 auto", padding: "0 24px 64px" }}>\n        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16 }}>\n          <Card title="default card">Body copy with muted color and a 1px border.</Card>\n          <Card title="tension card" variant="tension">\n            This one carries the 2px border — the deliberate break in the system.\n          </Card>\n          <Card title="with footer" footer={<Button variant="secondary">action</Button>}>\n            Cards and buttons use different radius on purpose.\n          </Card>\n        </div>\n        <div style={{ display: "flex", gap: 12, margin: "32px 0", flexWrap: "wrap" }}>\n          <Button>primary</Button>\n          <Button variant="secondary">secondary</Button>\n          <Button variant="ghost">ghost</Button>\n          <Button variant="danger">danger</Button>\n        </div>\n        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: 16, marginBottom: 32 }}>\n          <Input label="name" placeholder="your name" />\n          <Input label="email" type="email" placeholder="you@studio.com" error="required" />\n          <Input label="plan" as="select" options={["solo", "team", "studio"]} />\n        </div>\n        <div style={{ display: "grid", gap: 12 }}>\n          <Alert variant="success">saved. everything synced.</Alert>\n          <Alert variant="warning">storage almost full.</Alert>\n          <Alert variant="error">deploy failed — check logs.</Alert>\n        </div>\n      </section>\n    </div>\n  );\n}\n'



FALLBACK = {
    "concept": "craft",
    "palette": {
        "primary": "#5B4A3F", "secondary": "#E8DCC8", "accent": "#6B4423",
        "tension": "#556B2F", "surface": "#181512", "surface_alt": "#201C18",
        "text": "#DCD5C8", "text_muted": "#9B9488", "border": "#2A2520",
        "success": "#4A7C59", "warning": "#B8860B", "error": "#A63D40",
    },
    "typography": {
        "display": {"family": "Bitter", "weight": 500, "tracking": "-0.02em"},
        "heading": {"family": "Bitter", "weight": 600, "tracking": "-0.01em"},
        "body": {"family": "Work Sans", "weight": 400, "tracking": "0.01em"},
        "mono": {"family": "Space Mono", "weight": 400, "tracking": "0.02em"},
        "tension_rule": "body uses 15px, headings 17px",
    },
    "spacing": {
        "base": 8, "scale": [4, 8, 12, 16, 24, 32, 48, 64, 96],
        "tension": "section spacing asymmetric: 80px top, 48px bottom",
        "container": "max-width 1200px, padding-left 24px, padding-right 32px",
    },
    "radius": {"sm": 6, "md": 10, "lg": 14, "tension": "cards use 10px, buttons use 6px"},
    "effects": {
        "shadow": "0 1px 3px rgba(0,0,0,0.4)", "grain": True, "grain_amount": 0.03,
        "border_style": "1px solid", "tension": "one element uses 2px border instead of 1px",
    },
}


def _norm(design):
    merged = {}
    merged["concept"] = design.get("concept") or FALLBACK["concept"]
    for key in ("palette", "typography", "spacing", "radius", "effects"):
        base = dict(FALLBACK[key])
        incoming = design.get(key)
        if isinstance(incoming, dict):
            base.update(incoming)
        merged[key] = base
    return merged


def _section_spacing(design):
    tension = str(design["spacing"].get("tension", ""))
    nums = re.findall(r"(\d+)px", tension)
    if len(nums) >= 2:
        return int(nums[0]), int(nums[1])
    return 64, 64


def _font_url(design):
    fams = []
    for role in ("display", "heading", "body", "mono"):
        fam = design["typography"][role]["family"]
        if fam not in fams:
            fams.append(fam)
    parts = ["family=" + str(f).replace(" ", "+") + ":wght@400;500;600;700" for f in fams]
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"


def gen_tokens_css(design):
    d = _norm(design)
    top, bottom = _section_spacing(d)
    lines = ["@import url('" + _font_url(d) + "');"]
    lines.append("/* Generated by Anti-AI Design System - concept: " + d["concept"] + " */")
    lines.append(":root {")
    for key, val in d["palette"].items():
        lines.append("  --color-" + key.replace("_", "-") + ": " + str(val) + ";")
    for role in ("display", "heading", "body", "mono"):
        t = d["typography"][role]
        lines.append("  --font-" + role + ": '" + str(t["family"]) + "', sans-serif;")
        lines.append("  --tracking-" + role + ": " + str(t.get("tracking", "0em")) + ";")
    for key, val in d["radius"].items():
        if isinstance(val, (int, float)):
            lines.append("  --radius-" + key + ": " + str(val) + "px;")
    lines.append("  --spacing-base: " + str(d["spacing"]["base"]) + "px;")
    for s in d["spacing"]["scale"]:
        lines.append("  --space-" + str(s) + ": " + str(s) + "px;")
    lines.append("  --section-top: " + str(top) + "px;")
    lines.append("  --section-bottom: " + str(bottom) + "px;")
    lines.append("  --shadow: " + str(d["effects"]["shadow"]) + ";")
    lines.append("}")
    if d["effects"].get("grain"):
        grain_svg = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
                     "width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence "
                     "type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E"
                     "%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)'/%3E%3C/svg%3E")
        lines.append(".grain-overlay { position: relative; }")
        lines.append(".grain-overlay::after {")
        lines.append("  content: ''; position: absolute; inset: 0; pointer-events: none;")
        lines.append("  opacity: " + str(d["effects"].get("grain_amount", 0.03)) + ";")
        lines.append("  background-image: url(\"" + grain_svg + "\");")
        lines.append("}")
    return "\n".join(lines)


def gen_tailwind_extend(design):
    d = _norm(design)
    cfg = {
        "colors": {k: str(v) for k, v in d["palette"].items()},
        "fontFamily": {r: [d["typography"][r]["family"], "sans-serif"]
                       for r in ("display", "heading", "body", "mono")},
        "borderRadius": {k: str(v) + "px" for k, v in d["radius"].items()
                         if isinstance(v, (int, float))},
        "spacing": {str(s): str(s) + "px" for s in d["spacing"]["scale"]},
        "boxShadow": {"subtle": str(d["effects"]["shadow"])},
    }
    header = "// Generated by Anti-AI Design System - concept: " + d["concept"] + "\n"
    header += "// Usage: paste the export below into your tailwind.config.js theme.extend\n"
    return header + "module.exports = " + json.dumps(cfg, indent=2) + ";\n"


def gen_readme(design):
    d = _norm(design)
    fam = {r: d["typography"][r]["family"] for r in ("display", "body", "mono")}
    lines = [
        "# Anti-AI Component Library",
        "",
        "Concept: **" + d["concept"] + "** - generated with deliberate tension so it reads human, not templated.",
        "",
        "## Components",
        "",
        "| File | What it is |",
        "| --- | --- |",
        "| Button.tsx | primary / secondary / ghost / danger, uses --radius-sm |",
        "| Card.tsx | default + tension variant (the one 2px border) |",
        "| Input.tsx | text input, textarea, select, with label + error |",
        "| Alert.tsx | success / warning / error, dismissible |",
        "| Nav.tsx | logo + links + accent CTA |",
        "| Hero.tsx | headline + subtitle + CTAs, asymmetric section spacing |",
        "| showcase.tsx | all components on one page |",
        "",
        "## Install",
        "",
        "1. Import `tokens.css` once in your root layout.",
        "2. Copy `components/` into your project.",
        "3. Render `<Showcase />` to see everything.",
        "",
        "## Fonts",
        "",
        "- Display/heading: " + str(fam["display"]),
        "- Body: " + str(fam["body"]),
        "- Mono: " + str(fam["mono"]),
        "- Loaded automatically via the Google Fonts @import in tokens.css",
        "",
        "## Built-in tension",
        "",
        "- " + str(d["radius"].get("tension", "cards and buttons use different radius")),
        "- " + str(d["spacing"].get("tension", "asymmetric section spacing")),
        "- " + str(d["effects"].get("tension", "one element uses a 2px border")),
        "- Typography rule: " + str(d["typography"].get("tension_rule", "n/a")),
        "",
        "Generated by the Anti-AI Design System. Do not remove the tension -",
        "it is what keeps this from looking like a template.",
    ]
    return "\n".join(lines)



def generate_components(design):
    d = _norm(design)
    return {
        "tokens.css": gen_tokens_css(d),
        "tailwind.extend.js": gen_tailwind_extend(d),
        "components/Button.tsx": BUTTON_TSX,
        "components/Card.tsx": CARD_TSX,
        "components/Input.tsx": INPUT_TSX,
        "components/Alert.tsx": ALERT_TSX,
        "components/Nav.tsx": NAV_TSX,
        "components/Hero.tsx": HERO_TSX,
        "showcase.tsx": SHOWCASE_TSX,
        "README.md": gen_readme(d),
    }


def generate_zip(design):
    files = generate_components(design)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr("anti-ai-components/" + name, content)
    return buf.getvalue()


def generate_all(design):
    files = generate_components(design)
    total_lines = sum(len(c.splitlines()) for c in files.values())
    return {
        "concept": _norm(design)["concept"],
        "files": files,
        "file_count": len(files),
        "total_lines": total_lines,
        "zip_base64": base64.b64encode(generate_zip(design)).decode("ascii"),
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage: codegen.py \'{"design": {...}}\' | --brief \'{"project": "...", "feeling": "..."}\' [--zip out.zip] [--full]')
        sys.exit(1)
    if sys.argv[1] == "--brief":
        from designer import generate_design
        design = generate_design(json.loads(sys.argv[2]))
    else:
        payload = json.loads(sys.argv[1])
        design = payload.get("design", payload)
    if "--zip" in sys.argv:
        out = sys.argv[sys.argv.index("--zip") + 1]
        with open(out, "wb") as f:
            f.write(generate_zip(design))
        print("wrote " + out)
    else:
        result = generate_all(design)
        if "--full" in sys.argv:
            print(json.dumps(result))
        else:
            print(json.dumps({k: v for k, v in result.items() if k != "zip_base64"}, indent=2))
