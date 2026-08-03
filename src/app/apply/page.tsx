"use client";

import { useState } from "react";

interface Change {
  var: string;
  from: string;
  to: string;
  token?: string;
}

interface ApplyResult {
  css: string;
  report: {
    concept: string;
    variables_changed: number;
    changes: Change[];
    notes: string[];
  };
  design: {
    concept: string;
    palette: Record<string, string>;
    typography: Record<string, { family: string }>;
  };
}

export default function ApplyPage() {
  const [cssInput, setCssInput] = useState("");
  const [brief, setBrief] = useState({ project: "", feeling: "" });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ApplyResult | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [view, setView] = useState<"changes" | "css">("changes");

  const showToast = (m: string) => {
    setToast(m);
    setTimeout(() => setToast(null), 4000);
  };

  const apply = async () => {
    if (!cssInput.trim()) {
      showToast("Paste your globals.css first");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/apply", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ css: cssInput, brief }),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
      setView("changes");
    } catch (err) {
      showToast(`Apply failed: ${err instanceof Error ? err.message : "error"}`);
    } finally {
      setLoading(false);
    }
  };

  const copyCss = () => {
    if (!result) return;
    navigator.clipboard.writeText(result.css);
    showToast("Redesigned CSS copied");
  };

  const downloadCss = () => {
    if (!result) return;
    const blob = new Blob([result.css], { type: "text/css" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "globals.redesigned.css";
    a.click();
    URL.revokeObjectURL(a.href);
    showToast("globals.redesigned.css downloaded");
  };

  return (
    <div className="min-h-screen bg-background text-foreground">
      <nav className="border-b border-border px-6 py-3 flex gap-6">
        <a href="/" className="text-sm text-muted-foreground hover:text-foreground">Detector</a>
        <a href="/design" className="text-sm text-muted-foreground hover:text-foreground">Generator</a>
        <a href="/redesign" className="text-sm text-muted-foreground hover:text-foreground">Redesign</a>
        <a href="/pipeline" className="text-sm text-muted-foreground hover:text-foreground">Pipeline</a>
        <a href="/apply" className="text-sm font-bold text-foreground">Apply</a>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-6">
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold">Apply to Project</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Paste a project&apos;s globals.css. Get it redesigned with a human-looking design system.
            </p>
          </div>

          <div className="space-y-3 bg-card border border-border rounded-lg p-4">
            <div>
              <label className="text-xs text-muted-foreground">Project (optional)</label>
              <input value={brief.project} onChange={(e) => setBrief({ ...brief, project: e.target.value })}
                placeholder="what is this project?"
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Feeling (optional)</label>
              <input value={brief.feeling} onChange={(e) => setBrief({ ...brief, feeling: e.target.value })}
                placeholder="trustworthy, warm, precise..."
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">globals.css content</label>
              <textarea value={cssInput} onChange={(e) => setCssInput(e.target.value)}
                placeholder={`:root {\n  --background: oklch(1 0 0);\n  --primary: oklch(0.205 0 0);\n  ...\n}`}
                spellCheck={false}
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-xs font-mono mt-1 h-72 resize-y" />
            </div>
            <button onClick={apply} disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-md py-2.5 text-sm font-medium">
              {loading ? "Redesigning..." : "Apply Design"}
            </button>
          </div>
        </div>

        <div>
          {!result && (
            <div className="h-full min-h-[400px] border border-dashed border-border rounded-lg flex items-center justify-center text-sm text-muted-foreground px-8 text-center">
              Works with shadcn globals.css — oklch (Tailwind 4), HSL triplets (legacy), or hex.
              Only known variables change; charts, sidebar and custom vars stay untouched.
            </div>
          )}

          {result && (
            <div className="space-y-4">
              <div className="bg-card border border-border rounded-lg p-4">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div>
                    <p className="text-sm font-medium">
                      Concept: <span className="font-bold">{result.report.concept}</span>
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {result.report.variables_changed} variables replaced
                    </p>
                  </div>
                  <div className="flex gap-1">
                    {Object.entries(result.design.palette).slice(0, 8).map(([k, v]) => (
                      <span key={k} title={k} className="w-6 h-6 rounded-full border border-border" style={{ background: v }} />
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-card border border-border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex gap-2">
                    <button onClick={() => setView("changes")}
                      className={`px-3 py-1.5 rounded-lg text-xs ${view === "changes" ? "bg-blue-600 text-white" : "bg-muted text-muted-foreground"}`}>
                      Changes ({result.report.changes.length})
                    </button>
                    <button onClick={() => setView("css")}
                      className={`px-3 py-1.5 rounded-lg text-xs ${view === "css" ? "bg-blue-600 text-white" : "bg-muted text-muted-foreground"}`}>
                      Full CSS
                    </button>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={copyCss} className="px-3 py-1.5 bg-muted hover:bg-muted/70 rounded-lg text-xs">Copy CSS</button>
                    <button onClick={downloadCss} className="px-3 py-1.5 bg-muted hover:bg-muted/70 rounded-lg text-xs">Download</button>
                  </div>
                </div>

                {view === "changes" ? (
                  <div className="space-y-1.5 max-h-[480px] overflow-auto">
                    {result.report.changes.map((c, i) => (
                      <div key={i} className="flex items-center gap-2 text-xs font-mono bg-background border border-border rounded px-2 py-1.5">
                        <span className="text-foreground font-semibold w-44 shrink-0 truncate">{c.var}</span>
                        <span className="text-muted-foreground truncate flex-1">{c.from}</span>
                        <span className="text-muted-foreground">→</span>
                        <span className="text-green-500 truncate flex-1">{c.to}</span>
                      </div>
                    ))}
                    {result.report.notes.map((n, i) => (
                      <p key={i} className="text-[11px] text-muted-foreground pt-1">• {n}</p>
                    ))}
                  </div>
                ) : (
                  <pre className="bg-background border border-border rounded-lg p-3 text-[11px] leading-relaxed overflow-auto max-h-[480px] font-mono">
                    {result.css}
                  </pre>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {toast && (
        <div className="fixed bottom-4 right-4 bg-card border border-border rounded-lg px-4 py-3 text-sm shadow-lg">
          {toast}
        </div>
      )}
    </div>
  );
}
