"use client";

import { useState } from "react";

interface Problem {
  element: string;
  issue: string;
  severity: "high" | "medium" | "low";
}

interface RedesignResult {
  original: { colors: Record<string, string>; fonts: Record<string, string>; effects?: string[]; radius?: string };
  diagnosis: { genericity_score: number; problems: Problem[]; verdict: string };
  redesigned: { colors: Record<string, string>; fonts: Record<string, string>; radius: { cards: string; buttons: string }; effects: string[]; tension_elements: string[] };
  css_variables: string;
  changes_summary: string[];
  improvement: { genericity_before: number; genericity_after: number; delta: number };
}

const SAMPLE = `:root {
  --primary: #7B2FF7;
  --secondary: #2196F3;
  --bg: #FFFFFF;
  --text: #1A1A1A;
  --accent: #FF6B9D;
  --font-heading: 'Poppins';
  --font-body: 'Inter';
  --radius: 12px;
}`;

function Swatch({ color, size = 28 }: { color: string; size?: number }) {
  return <div style={{ width: size, height: size, borderRadius: "50%", background: color, border: "1px solid #333" }} />;
}

export default function RedesignPage() {
  const [input, setInput] = useState("");
  const [brief, setBrief] = useState("");
  const [result, setResult] = useState<RedesignResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (m: string) => { setToast(m); setTimeout(() => setToast(null), 3000); };

  const analyze = async () => {
    setLoading(true);
    try {
      const payload = input.includes("{") && input.includes("}")
        ? { design: JSON.parse(input), brief }
        : { css: input, brief };
      const res = await fetch("/api/redesign", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (e) {
      showToast(`Failed: ${e instanceof Error ? e.message : "error"}`);
    } finally {
      setLoading(false);
    }
  };

  const severityIcon = (s: string) => s === "high" ? "🔴" : s === "medium" ? "🟡" : "🟢";
  const oldColors = result?.original.colors || {};
  const newColors = result?.redesigned.colors || {};
  const oldFonts = result?.original.fonts || {};
  const newFonts = result?.redesigned.fonts || {};

  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="border-b border-border px-6 py-3 flex gap-6">
        <a href="/" className="text-sm text-muted-foreground hover:text-foreground">Detector</a>
        <a href="/design" className="text-sm text-muted-foreground hover:text-foreground">Generator</a>
        <a href="/redesign" className="text-sm font-bold text-foreground">Redesign</a>
        <a href="/pipeline" className="text-sm text-muted-foreground hover:text-foreground">Pipeline</a>
        <a href="/apply" className="text-sm text-muted-foreground hover:text-foreground">Apply</a>
      </nav>
      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold">Project Redesigner</h1>
            <p className="text-sm text-muted-foreground mt-1">Paste your design. Get back one that looks human.</p>
          </div>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Paste CSS or design JSON here..."
            className="w-full h-64 px-3 py-2 bg-card border border-border rounded-lg text-xs font-mono resize-none"
          />
          <button onClick={() => setInput(SAMPLE)} className="text-xs text-blue-500 hover:underline">Use sample</button>
          <div>
            <label className="text-xs text-muted-foreground">Brief hint (optional)</label>
            <input value={brief} onChange={(e) => setBrief(e.target.value)} placeholder="fintech dashboard" className="w-full mt-1 px-3 py-2 bg-card border border-border rounded-lg text-sm" />
          </div>
          <button onClick={analyze} disabled={loading || !input} className="w-full px-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg text-sm font-medium">
            {loading ? "Analyzing..." : "Analyze & Redesign"}
          </button>
        </div>

        <div>
          {!result ? (
            <div className="border border-dashed border-border rounded-xl min-h-[400px] flex items-center justify-center text-muted-foreground text-sm">
              Paste a design and click Analyze to see diagnosis and redesign
            </div>
          ) : (
            <div className="space-y-6">
              {/* Diagnosis */}
              <div className="bg-card border border-border rounded-xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs uppercase tracking-wider text-muted-foreground">Diagnosis</span>
                  <span className="text-sm font-mono">{result.diagnosis.genericity_score.toFixed(2)}</span>
                </div>
                <div className="h-2 rounded-full bg-muted overflow-hidden mb-4">
                  <div className="h-full rounded-full" style={{ width: `${result.diagnosis.genericity_score * 100}%`, background: result.diagnosis.genericity_score > 0.5 ? "#ef4444" : "#22c55e" }} />
                </div>
                <div className="space-y-1">
                  {result.diagnosis.problems.map((p, i) => (
                    <div key={i} className="text-sm flex items-start gap-2">
                      <span>{severityIcon(p.severity)}</span>
                      <span className="text-muted-foreground"><span className="text-foreground">{p.element}:</span> {p.issue}</span>
                    </div>
                  ))}
                  {result.diagnosis.problems.length === 0 && <p className="text-sm text-muted-foreground">No generic patterns detected.</p>}
                </div>
              </div>

              {/* Before/After */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-card rounded-xl p-4" style={{ border: "1px solid #ef4444" }}>
                  <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3">Before</p>
                  <div className="flex gap-2 mb-3">
                    {Object.values(oldColors).slice(0, 5).map((c, i) => <Swatch key={i} color={c} />)}
                  </div>
                  <p className="text-sm font-mono">{oldFonts.heading || "—"} / {oldFonts.body || "—"}</p>
                  <p className="text-xs text-muted-foreground mt-1">Effects: {result.original.effects?.join(", ") || "none"}</p>
                  <p className="text-xs text-muted-foreground">Radius: {result.original.radius || "—"}</p>
                  <p className="text-xs text-red-400 mt-2">Score: {result.improvement.genericity_before.toFixed(2)}</p>
                </div>
                <div className="bg-card rounded-xl p-4" style={{ border: "1px solid #22c55e" }}>
                  <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3">After</p>
                  <div className="flex gap-2 mb-3">
                    {["primary", "secondary", "accent", "tension", "surface"].map((k) => newColors[k] && <Swatch key={k} color={newColors[k]} />)}
                  </div>
                  <p className="text-sm font-mono">{newFonts.heading} / {newFonts.body}</p>
                  <p className="text-xs text-muted-foreground mt-1">Effects: {result.redesigned.effects.join(", ")}</p>
                  <p className="text-xs text-muted-foreground">Radius: {result.redesigned.radius.cards} / {result.redesigned.radius.buttons}</p>
                  <p className="text-xs text-green-400 mt-2">Score: {result.improvement.genericity_after.toFixed(2)}</p>
                </div>
              </div>

              {/* Changes */}
              <div className="bg-card border border-border rounded-xl p-4">
                <p className="text-xs uppercase tracking-wider text-muted-foreground mb-2">Changes</p>
                <ul className="space-y-1">
                  {result.changes_summary.map((c, i) => (
                    <li key={i} className="text-sm text-muted-foreground">• {c}</li>
                  ))}
                </ul>
              </div>

              {/* Export */}
              <div className="flex gap-2 flex-wrap">
                <button onClick={() => { navigator.clipboard.writeText(result.css_variables); showToast("CSS copied"); }} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs hover:bg-muted">Copy CSS</button>
                <button onClick={() => { navigator.clipboard.writeText(JSON.stringify(result.redesigned, null, 2)); showToast("JSON copied"); }} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs hover:bg-muted">Copy JSON</button>
                <button onClick={() => {
                  const blob = new Blob([JSON.stringify(result, null, 2)], { type: "application/json" });
                  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = "redesign.json"; a.click();
                }} className="px-3 py-1.5 bg-card border border-border rounded-lg text-xs hover:bg-muted">Download All</button>
              </div>
            </div>
          )}
        </div>
      </div>
      {toast && <div className="fixed bottom-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm z-50">{toast}</div>}
    </div>
  );
}
