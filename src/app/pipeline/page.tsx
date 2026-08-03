"use client";

import { useState } from "react";

interface Step {
  step: number;
  name: string;
  status: string;
  detail: string;
  duration_ms: number;
}

interface Variation {
  index: number;
  concept: string;
  genericity: number;
  colors: Record<string, string>;
  display_font: string;
  tension_rule: string;
}

interface PipelineResult {
  concept: string;
  steps: Step[];
  design: {
    palette: Record<string, string>;
    typography: Record<string, { family: string; weight: number; tracking: string }>;
    spacing: { tension?: string };
    radius: { sm?: number; md?: number; tension?: string };
    effects: { tension?: string };
    anti_ai_validation: { genericity_score: number; has_tension_element: boolean };
  };
  files: Record<string, string>;
  file_count: number;
  total_lines: number;
  zip_base64: string;
  all_passed: boolean;
  total_duration_ms: number;
}

export default function PipelinePage() {
  const [brief, setBrief] = useState({ project: "", feeling: "", audience: "" });
  const [running, setRunning] = useState(false);
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [visibleSteps, setVisibleSteps] = useState(0);
  const [toast, setToast] = useState<string | null>(null);
  const [activeFile, setActiveFile] = useState("tokens.css");
  const [showFiles, setShowFiles] = useState(false);
  const [directions, setDirections] = useState<Variation[] | null>(null);
  const [chosenConcept, setChosenConcept] = useState<string | null>(null);
  const [exploring, setExploring] = useState(false);

  const showToast = (m: string) => {
    setToast(m);
    setTimeout(() => setToast(null), 4000);
  };

  const explore = async () => {
    setExploring(true);
    try {
      const res = await fetch("/api/variations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brief, count: 3 }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setDirections(data.variations);
      setChosenConcept(null);
    } catch (err) {
      showToast(`Variations failed: ${err instanceof Error ? err.message : "error"}`);
    } finally {
      setExploring(false);
    }
  };

  const run = async () => {
    setRunning(true);
    setResult(null);
    setVisibleSteps(0);
    setShowFiles(false);
    try {
      const res = await fetch("/api/pipeline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ brief, concept: chosenConcept ?? undefined }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
      for (let i = 1; i <= data.steps.length; i++) {
        setTimeout(() => setVisibleSteps(i), i * 350);
      }
    } catch (err) {
      showToast(`Pipeline failed: ${err instanceof Error ? err.message : "error"}`);
    } finally {
      setRunning(false);
    }
  };

  const downloadZip = () => {
    if (!result?.zip_base64) { showToast("Run the pipeline first"); return; }
    const bytes = atob(result.zip_base64);
    const buf = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) buf[i] = bytes.charCodeAt(i);
    const a = document.createElement("a");
    a.href = URL.createObjectURL(new Blob([buf], { type: "application/zip" }));
    a.download = `pipeline-${result.concept}.zip`;
    a.click();
    URL.revokeObjectURL(a.href);
    showToast("Complete package downloaded");
  };

  const d = result?.design;
  const pal = d?.palette;
  const typ = d?.typography;
  const fontUrl = typ
    ? "https://fonts.googleapis.com/css2?" +
      [...new Set([typ.display.family, typ.body.family])]
        .map((f) => `family=${f.replace(/ /g, "+")}:wght@400;500;600;700`).join("&") +
      "&display=swap"
    : "";

  return (
    <div className="min-h-screen bg-background text-foreground">
      {result && <link rel="stylesheet" href={fontUrl} />}
      <nav className="border-b border-border px-6 py-3 flex gap-6">
        <a href="/" className="text-sm text-muted-foreground hover:text-foreground">Detector</a>
        <a href="/design" className="text-sm text-muted-foreground hover:text-foreground">Generator</a>
        <a href="/redesign" className="text-sm text-muted-foreground hover:text-foreground">Redesign</a>
        <a href="/pipeline" className="text-sm font-bold text-foreground">Pipeline</a>
        <a href="/apply" className="text-sm text-muted-foreground hover:text-foreground">Apply</a>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-6">
        <div className="space-y-4">
          <div>
            <h1 className="text-2xl font-bold">The Full Pipeline</h1>
            <p className="text-sm text-muted-foreground mt-1">One brief in. Complete human-looking design system out.</p>
          </div>

          <div className="space-y-3 bg-card border border-border rounded-lg p-4">
            <div>
              <label className="text-xs text-muted-foreground">Project</label>
              <input value={brief.project} onChange={(e) => setBrief({ ...brief, project: e.target.value })}
                placeholder="fintech dashboard for freelancers"
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Feeling</label>
              <input value={brief.feeling} onChange={(e) => setBrief({ ...brief, feeling: e.target.value })}
                placeholder="trustworthy but warm"
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm mt-1" />
            </div>
            <div>
              <label className="text-xs text-muted-foreground">Audience</label>
              <input value={brief.audience} onChange={(e) => setBrief({ ...brief, audience: e.target.value })}
                placeholder="freelance designers, 25-40"
                className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm mt-1" />
            </div>
            <button onClick={run} disabled={running}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-md py-2.5 text-sm font-medium">
              {running ? "Running pipeline..." : "Run Pipeline"}
            </button>
          </div>

          <div className="bg-card border border-border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div>
                <p className="text-sm font-medium">Design Directions</p>
                <p className="text-xs text-muted-foreground">3 distinct concepts — pick one or run default</p>
              </div>
              <button onClick={explore} disabled={exploring}
                className="px-3 py-1.5 bg-card border border-border hover:bg-muted disabled:opacity-50 rounded-lg text-xs">
                {exploring ? "Exploring..." : "Explore"}
              </button>
            </div>
            {chosenConcept && (
              <p className="text-xs text-green-500 mb-2">Will run with: {chosenConcept}</p>
            )}
            {directions && (
              <div className="space-y-2">
                {directions.map((v) => (
                  <button
                    key={v.concept}
                    onClick={() => setChosenConcept(chosenConcept === v.concept ? null : v.concept)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${chosenConcept === v.concept ? "border-blue-500 bg-blue-500/10" : "border-border hover:bg-muted"}`}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm font-medium">{v.concept}</span>
                      <span className="text-[10px] font-mono text-green-500">genericity {v.genericity}</span>
                    </div>
                    <div className="flex gap-1 mb-1.5">
                      {Object.values(v.colors).map((c, i) => (
                        <span key={i} className="w-5 h-5 rounded-full border border-border" style={{ background: c }} />
                      ))}
                    </div>
                    <p className="text-[10px] text-muted-foreground">{v.display_font} · {v.tension_rule}</p>
                  </button>
                ))}
              </div>
            )}
          </div>

          {result && (
            <div className="bg-card border border-border rounded-lg p-4 space-y-3">
              {result.steps.map((s, i) => (
                <div key={s.step} className={`flex items-start gap-3 transition-opacity duration-300 ${i < visibleSteps ? "opacity-100" : "opacity-0"}`}>
                  <span className={`mt-0.5 text-sm ${s.status === "pass" ? "text-green-500" : "text-red-500"}`}>
                    {s.status === "pass" ? "✓" : "✗"}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">{s.name}</p>
                    <p className="text-xs text-muted-foreground truncate">{s.detail}</p>
                  </div>
                  <span className="text-xs text-muted-foreground font-mono">{s.duration_ms}ms</span>
                </div>
              ))}
              {visibleSteps >= result.steps.length && (
                <div className="pt-2 border-t border-border flex items-center justify-between">
                  <span className={`text-xs font-medium ${result.all_passed ? "text-green-500" : "text-red-500"}`}>
                    {result.all_passed ? "All steps passed" : "Some steps failed"}
                  </span>
                  <span className="text-xs text-muted-foreground font-mono">{result.total_duration_ms}ms total</span>
                </div>
              )}
            </div>
          )}

          {result && (
            <button onClick={downloadZip}
              className="w-full bg-card border border-border hover:bg-muted rounded-md py-2.5 text-sm font-medium">
              Download Complete Package (ZIP)
            </button>
          )}
        </div>

        <div>
          {!result && (
            <div className="h-full min-h-[400px] border border-dashed border-border rounded-lg flex items-center justify-center text-sm text-muted-foreground">
              {running ? "Running 5 steps: concept → design → validation → components → page..." : "Run the pipeline to see the result"}
            </div>
          )}

          {result && d && pal && typ && (
            <div className="space-y-4">
              <div className="rounded-lg overflow-hidden border border-border"
                style={{ background: pal.surface, color: pal.text, fontFamily: `'${typ.body.family}', sans-serif` }}>
                <div className="flex items-center gap-6 px-6 py-4 flex-wrap" style={{ borderBottom: `1px solid ${pal.border}` }}>
                  <span style={{ fontFamily: `'${typ.display.family}', sans-serif`, color: pal.primary, fontSize: 18, fontWeight: 500 }}>
                    {brief.project.split(" ")[0] || "acme"}
                  </span>
                  <span className="flex gap-4 flex-1 text-sm" style={{ color: pal.text_muted }}>
                    <span>product</span><span>pricing</span><span>docs</span>
                  </span>
                  <span className="text-xs px-3 py-1.5 rounded font-medium"
                    style={{ background: pal.accent, color: pal.surface, borderRadius: d.radius.sm }}>
                    start
                  </span>
                </div>
                <div style={{ paddingTop: 64, paddingBottom: 40, paddingLeft: 32, paddingRight: 40 }}>
                  <h2 style={{ fontFamily: `'${typ.display.family}', sans-serif`, fontSize: 40, fontWeight: 500, letterSpacing: typ.display.tracking, margin: 0 }}>
                    built like a workshop
                  </h2>
                  <p className="text-base mt-3 mb-6" style={{ color: pal.text_muted, maxWidth: 480 }}>
                    Concept &quot;{result.concept}&quot; — deliberate tension, asymmetric spacing, split radius.
                  </p>
                  <div className="flex gap-3 flex-wrap">
                    <span className="text-sm px-5 py-2.5 font-medium" style={{ background: pal.primary, color: pal.surface, borderRadius: d.radius.sm }}>
                      get started
                    </span>
                    <span className="text-sm px-5 py-2.5" style={{ border: `1px solid ${pal.secondary}`, color: pal.secondary, borderRadius: d.radius.sm }}>
                      read more
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 px-8 pb-8">
                  {[0, 1, 2].map((i) => (
                    <div key={i} style={{ background: pal.surface, border: `${i === 1 ? 2 : 1}px solid ${i === 1 ? pal.tension : pal.border}`, borderRadius: d.radius.md, padding: 20 }}>
                      <p className="text-sm font-semibold mb-2" style={{ fontFamily: `'${typ.display.family}', sans-serif` }}>
                        {["default card", "tension card", "with footer"][i]}
                      </p>
                      <p className="text-xs" style={{ color: pal.text_muted }}>
                        {i === 1 ? "The one 2px border in the system." : "Cards and buttons use different radius."}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-card border border-border rounded-lg p-4">
                  <p className="text-xs text-muted-foreground mb-2">Palette</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(pal).slice(0, 8).map(([k, v]) => (
                      <div key={k} className="flex items-center gap-1.5">
                        <span className="w-4 h-4 rounded-full border border-border" style={{ background: v }} />
                        <span className="text-[10px] text-muted-foreground font-mono">{k}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="bg-card border border-border rounded-lg p-4">
                  <p className="text-xs text-muted-foreground mb-2">Validation</p>
                  <p className="text-sm">genericity: <span className="font-mono font-bold text-green-500">{d.anti_ai_validation.genericity_score}</span></p>
                  <p className="text-sm">tension: <span className="font-mono font-bold text-green-500">{d.anti_ai_validation.has_tension_element ? "present" : "missing"}</span></p>
                  <p className="text-xs text-muted-foreground mt-1">{result.file_count} files · {result.total_lines} lines</p>
                </div>
              </div>

              <div className="bg-card border border-border rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">Generated Files</p>
                  <button onClick={() => setShowFiles(!showFiles)} className="text-xs text-blue-500 hover:underline">
                    {showFiles ? "Hide code" : "View code"}
                  </button>
                </div>
                {showFiles && (
                  <div>
                    <div className="flex flex-wrap gap-1 mb-2">
                      {Object.keys(result.files).map((name) => (
                        <button key={name} onClick={() => setActiveFile(name)}
                          className={`px-2 py-1 rounded text-[11px] font-mono ${activeFile === name ? "bg-blue-600 text-white" : "bg-muted text-muted-foreground hover:text-foreground"}`}>
                          {name.split("/").pop()}
                        </button>
                      ))}
                    </div>
                    <pre className="bg-background border border-border rounded-lg p-3 text-[11px] leading-relaxed overflow-auto max-h-[400px] font-mono">
                      {result.files[activeFile]}
                    </pre>
                  </div>
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
