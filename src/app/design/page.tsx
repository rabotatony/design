"use client";

import { useState, useRef } from "react";

interface DesignData {
  design: {
    concept: string;
    palette: Record<string, string>;
    typography: {
      display: { family: string; weight: number; tracking: string };
      heading: { family: string; weight: number; tracking: string };
      body: { family: string; weight: number; tracking: string };
      mono: { family: string; weight: number; tracking: string };
      tension_rule: string;
    };
    spacing: { base: number; scale: number[]; tension: string; container: string };
    radius: { sm: number; md: number; lg: number; tension: string };
    effects: { shadow: string; grain: boolean; grain_amount: number; border_style: string; tension: string };
    anti_ai_validation: { palette_distance_from_ai: number; genericity_score: number; has_tension_element: boolean; has_concept: boolean; font_is_generic: boolean };
  };
  css: string;
  tailwind: string;
}

export default function DesignPage() {
  const [design, setDesign] = useState<DesignData | null>(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [brief, setBrief] = useState({ project: "fintech dashboard", feeling: "trustworthy but warm", audience: "freelancers" });
  const [constraints, setConstraints] = useState({ darkMode: true, rtl: false, mobile: true });
  const previewRef = useRef<HTMLDivElement>(null);

  const showToast = (msg: string) => { setToast(msg); setTimeout(() => setToast(null), 3000); };

  const generate = async () => {
    setLoading(true);
    try {
      const cons = Object.entries(constraints).filter(([_, v]) => v).map(([k]) => k === "darkMode" ? "dark mode" : k === "rtl" ? "hebrew RTL support" : "mobile-first");
      const res = await fetch("/api/design", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brief: { ...brief, constraints: cons } }),
      });
      if (!res.ok) throw new Error(await res.text());
      setDesign(await res.json());
    } catch (e) {
      showToast(`Failed: ${e instanceof Error ? e.message : "error"}`);
    } finally {
      setLoading(false);
    }
  };

  const copy = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    showToast(`${label} copied to clipboard`);
  };

  const p = design?.design.palette || {};
  const t = design?.design.typography;
  const r = design?.design.radius;
  const s = design?.design.spacing;
  const e = design?.design.effects;
  const cssVars = design ? `
    --c-primary:${p.primary};--c-secondary:${p.secondary};--c-accent:${p.accent};
    --c-tension:${p.tension};--c-surface:${p.surface};--c-surface-alt:${p.surface_alt};
    --c-text:${p.text};--c-text-muted:${p.text_muted};--c-border:${p.border};
    --c-success:${p.success};--c-warning:${p.warning};--c-error:${p.error};
    --f-display:'${t?.display.family}',sans-serif;--f-heading:'${t?.heading.family}',sans-serif;
    --f-body:'${t?.body.family}',sans-serif;--f-mono:'${t?.mono.family}',monospace;
    --r-sm:${r?.sm}px;--r-md:${r?.md}px;--r-lg:${r?.lg}px;
    --s-base:${s?.base}px;--shadow:${e?.shadow};
  ` : "";

  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="border-b border-border px-6 py-3 flex gap-6">
        <a href="/" className="text-sm text-muted-foreground hover:text-foreground">Detector</a>
        <a href="/design" className="text-sm font-bold text-foreground">Generator</a>
      </nav>
      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-[320px_1fr] gap-6">
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold">Design Generator</h1>
            <p className="text-sm text-muted-foreground mt-1">Generate a design system that doesn&apos;t look like AI</p>
          </div>
          <div className="space-y-3">
            <div>
              <label className="text-xs text-muted-foreground">Project</label>
              <input value={brief.project} onChange={(ev) => setBrief({ ...brief, project: ev.target.value })}
                className="w-full mt-1 px-3 py-2 bg-card border border-border rounded-lg text-sm" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Feeling</label>
              <input value={brief.feeling} onChange={(ev) => setBrief({ ...brief, feeling: ev.target.value })}
                className="w-full mt-1 px-3 py-2 bg-card border border-border rounded-lg text-sm" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Audience</label>
              <input value={brief.audience} onChange={(ev) => setBrief({ ...brief, audience: ev.target.value })}
                className="w-full mt-1 px-3 py-2 bg-card border border-border rounded-lg text-sm" />
            </div>
            <div className="flex flex-wrap gap-3 text-sm">
              {([["darkMode", "Dark mode"], ["rtl", "RTL"], ["mobile", "Mobile-first"]] as const).map(([k, label]) => (
                <label key={k} className="flex items-center gap-2">
                  <input type="checkbox" checked={constraints[k]} onChange={(ev) => setConstraints({ ...constraints, [k]: ev.target.checked })} />
                  {label}
                </label>
              ))}
            </div>
          </div>
          <button onClick={generate} disabled={loading}
            className="w-full px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium">
            {loading ? "Crafting design system..." : "Generate"}
          </button>
          {design && (
            <div className="space-y-2">
              <p className="text-xs text-muted-foreground">Export</p>
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => copy(design.css, "CSS")} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs hover:bg-muted">CSS</button>
                <button onClick={() => copy(design.tailwind, "Tailwind")} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs hover:bg-muted">Tailwind</button>
                <button onClick={() => copy(JSON.stringify(design.design, null, 2), "JSON")} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs hover:bg-muted">JSON</button>
                <button onClick={() => copy(design.css + "\n" + design.tailwind, "All")} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs hover:bg-muted">Copy All</button>
              </div>
            </div>
          )}
        </div>

        <div>
          {!design ? (
            <div className="border border-dashed border-border rounded-xl min-h-[400px] flex items-center justify-center text-muted-foreground text-sm">
              Enter a brief and click Generate to see a live design preview
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">Preview</span>
                <div className="flex gap-4 text-xs">
                  <span className="text-muted-foreground">Concept: <span className="text-foreground font-medium">{design.design.concept}</span></span>
                  <span className="text-muted-foreground">Genericity: <span className="text-green-500 font-mono">{design.design.anti_ai_validation.genericity_score}</span></span>
                </div>
              </div>
              <div ref={previewRef} style={{ cssText: cssVars, background: p.surface, color: p.text, fontFamily: `var(--f-body)`, borderRadius: r?.lg, padding: 32, border: `1px solid ${p.border}` }}>
                <link href={`https://fonts.googleapis.com/css2?family=${t?.display.family.replace(/ /g, "+")}&family=${t?.body.family.replace(/ /g, "+")}&family=${t?.mono.family.replace(/ /g, "+")}&display=swap`} rel="stylesheet" />
                {/* Nav */}
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: `${s?.base}px 0`, borderBottom: `1px solid ${p.border}`, marginBottom: 32 }}>
                  <span style={{ fontFamily: "var(--f-display)", fontWeight: t?.display.weight, color: p.primary, fontSize: 20, letterSpacing: t?.display.tracking }}>{design.design.concept}</span>
                  <div style={{ display: "flex", gap: 24, alignItems: "center" }}>
                    <span style={{ color: p.text_muted, fontSize: 14 }}>Features</span>
                    <span style={{ color: p.text_muted, fontSize: 14 }}>Pricing</span>
                    <span style={{ color: p.text_muted, fontSize: 14 }}>Docs</span>
                    <button style={{ background: p.accent, color: p.text, borderRadius: r?.sm, padding: "6px 16px", fontSize: 14, border: "none", cursor: "pointer" }}>Get Started</button>
                  </div>
                </div>
                {/* Hero */}
                <div style={{ marginBottom: 48 }}>
                  <h1 style={{ fontFamily: "var(--f-display)", fontWeight: t?.display.weight, fontSize: 40, letterSpacing: t?.display.tracking, margin: 0, marginBottom: 12 }}>{brief.project}</h1>
                  <p style={{ color: p.text_muted, fontSize: 16, maxWidth: 500, marginBottom: 24 }}>A design system crafted with deliberate tension — not another generic AI template.</p>
                  <div style={{ display: "flex", gap: 12 }}>
                    <button style={{ background: p.primary, color: p.text, borderRadius: r?.sm, padding: "10px 20px", fontSize: 14, border: "none", cursor: "pointer" }}>Primary Action</button>
                    <button style={{ background: "transparent", color: p.text, borderRadius: r?.sm, padding: "10px 20px", fontSize: 14, border: `1px solid ${p.border}`, cursor: "pointer" }}>Secondary</button>
                  </div>
                </div>
                {/* Cards */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 48 }}>
                  {["Precision", "Warmth", "Tension"].map((title, i) => (
                    <div key={i} style={{ background: p.surface_alt, borderRadius: r?.md, padding: 20, border: `${i === 2 ? 2 : 1}px solid ${p.border}` }}>
                      <h3 style={{ fontFamily: "var(--f-heading)", fontWeight: t?.heading.weight, fontSize: 18, margin: 0, marginBottom: 8 }}>{title}</h3>
                      <p style={{ color: p.text_muted, fontSize: 13, margin: 0 }}>{i === 2 ? "This card has 2px border — deliberate tension." : "Hand-crafted tokens, not algorithmic."}</p>
                    </div>
                  ))}
                </div>
                {/* Buttons */}
                <div style={{ display: "flex", gap: 8, marginBottom: 48, flexWrap: "wrap" }}>
                  <button style={{ background: p.primary, color: p.text, borderRadius: r?.sm, padding: "8px 16px", fontSize: 13, border: "none", cursor: "pointer" }}>Primary</button>
                  <button style={{ background: p.secondary, color: p.surface, borderRadius: r?.sm, padding: "8px 16px", fontSize: 13, border: "none", cursor: "pointer" }}>Secondary</button>
                  <button style={{ background: "transparent", color: p.text, borderRadius: r?.sm, padding: "8px 16px", fontSize: 13, border: `1px solid ${p.border}`, cursor: "pointer" }}>Ghost</button>
                  <button style={{ background: p.error, color: p.text, borderRadius: r?.sm, padding: "8px 16px", fontSize: 13, border: "none", cursor: "pointer" }}>Danger</button>
                </div>
                {/* Form */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 48 }}>
                  <input placeholder="Email" style={{ background: p.surface_alt, color: p.text, borderRadius: r?.sm, padding: "10px 14px", fontSize: 14, border: `1px solid ${p.border}`, outline: "none" }} />
                  <select style={{ background: p.surface_alt, color: p.text, borderRadius: r?.sm, padding: "10px 14px", fontSize: 14, border: `1px solid ${p.border}` }}>
                    <option>Option A</option><option>Option B</option>
                  </select>
                  <textarea placeholder="Message" style={{ background: p.surface_alt, color: p.text, borderRadius: r?.sm, padding: "10px 14px", fontSize: 14, border: `1px solid ${p.border}`, gridColumn: "1 / -1", minHeight: 60, resize: "vertical" }} />
                </div>
                {/* Alerts */}
                <div style={{ display: "flex", flexDirection: "column", gap: 8, marginBottom: 48 }}>
                  <div style={{ background: p.success, color: p.text, borderRadius: r?.sm, padding: "10px 14px", fontSize: 13, opacity: 0.8 }}>Success: Design saved.</div>
                  <div style={{ background: p.warning, color: p.surface, borderRadius: r?.sm, padding: "10px 14px", fontSize: 13, opacity: 0.8 }}>Warning: High saturation detected.</div>
                  <div style={{ background: p.error, color: p.text, borderRadius: r?.sm, padding: "10px 14px", fontSize: 13, opacity: 0.8 }}>Error: Generation failed.</div>
                </div>
                {/* Typography */}
                <div style={{ marginBottom: 48 }}>
                  <p style={{ fontFamily: "var(--f-display)", fontWeight: t?.display.weight, fontSize: 32, letterSpacing: t?.display.tracking, margin: 0 }}>Display</p>
                  <p style={{ fontFamily: "var(--f-heading)", fontWeight: t?.heading.weight, fontSize: 24, margin: "4px 0" }}>Heading</p>
                  <p style={{ fontFamily: "var(--f-body)", fontSize: 16, margin: "4px 0" }}>Body text — readable and warm.</p>
                  <p style={{ fontFamily: "var(--f-mono)", fontSize: 13, color: p.text_muted, margin: "4px 0" }}>const x = mono();</p>
                </div>
                {/* Spacing */}
                <div style={{ display: "flex", alignItems: "flex-end", gap: 4, height: 64 }}>
                  {s?.scale.map((sp) => (
                    <div key={sp} style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: 4 }}>
                      <div style={{ width: sp, height: sp, background: p.tension, borderRadius: 2 }} />
                      <span style={{ fontSize: 10, color: p.text_muted }}>{sp}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="mt-4 p-3 bg-card border border-border rounded-lg text-xs text-muted-foreground">
                <strong className="text-foreground">Tension:</strong> {t?.tension_rule}. {r?.tension}. {e?.tension}.
              </div>
            </div>
          )}
        </div>
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm z-50">{toast}</div>}
    </div>
  );
}
