"use client";

import { useState, useCallback, useRef } from "react";

interface DetectorResult {
  score: number;
  detail: string;
}

interface Diagnosis {
  file?: string;
  total_score: number;
  verdict: string;
  detectors: Record<string, DetectorResult>;
}

interface ResultItem extends Diagnosis {
  filename: string;
  thumb: string;
  expanded: boolean;
  fixing: boolean;
  fixed?: boolean;
  fixedThumb?: string;
  afterScore?: number;
  improvement?: number;
  error?: string;
}

function scoreColor(s: number) {
  if (s < 0.4) return "#22c55e";
  if (s < 0.6) return "#eab308";
  return "#ef4444";
}

function verdictBadge(v: string) {
  const cls = v === "ai_likely" ? "bg-red-500/20 text-red-400" :
    v === "uncertain" ? "bg-yellow-500/20 text-yellow-400" :
    v === "human_likely" ? "bg-green-500/20 text-green-400" :
    "bg-muted text-muted-foreground";
  const label = v === "ai_likely" ? "AI Likely" : v === "uncertain" ? "Uncertain" : v === "human_likely" ? "Human Likely" : v;
  return { cls, label };
}

export default function Home() {
  const [results, setResults] = useState<ResultItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const fileMap = useRef<Map<string, File>>(new Map());

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  };

  const makeThumb = (file: File): Promise<string> =>
    new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.readAsDataURL(file);
    });

  const analyzeFiles = useCallback(async (files: File[]) => {
    if (!files.length) return;
    setLoading(true);
    try {
      const fd = new FormData();
      for (const f of files) {
        fd.append("files", f);
        fileMap.current.set(f.name, f);
      }
      const res = await fetch("/api/detect/batch", { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text());
      const data: Diagnosis[] = await res.json();
      const newItems: ResultItem[] = [];
      for (const d of data) {
        const file = fileMap.current.get(d.file || "");
        const thumb = file ? await makeThumb(file) : "";
        newItems.push({
          ...d,
          filename: d.file || "unknown",
          thumb,
          expanded: false,
          fixing: false,
        });
      }
      setResults((prev) => [...prev, ...newItems].sort((a, b) => b.total_score - a.total_score));
    } catch (e) {
      showToast(`Cannot analyze: ${e instanceof Error ? e.message : "Server error — make sure Python is installed"}`);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const files = Array.from(e.dataTransfer.files).filter((f) => f.type.startsWith("image/"));
    analyzeFiles(files);
  }, [analyzeFiles]);

  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    const files = Array.from(e.clipboardData.items)
      .filter((i) => i.type.startsWith("image/"))
      .map((i) => i.getAsFile())
      .filter(Boolean) as File[];
    if (files.length) analyzeFiles(files);
  }, [analyzeFiles]);

  const toggleExpand = (idx: number) => {
    setResults((prev) => prev.map((r, i) => (i === idx ? { ...r, expanded: !r.expanded } : r)));
  };

  const fixOne = async (idx: number) => {
    const item = results[idx];
    const file = fileMap.current.get(item.filename);
    if (!file) { showToast("Original file not found"); return; }
    setResults((prev) => prev.map((r, i) => (i === idx ? { ...r, fixing: true } : r)));
    try {
      const fd = new FormData();
      fd.append("file", file);
      const res = await fetch("/api/detect/fix", { method: "POST", body: fd });
      if (!res.ok) throw new Error(await res.text());
      const d = await res.json();
      setResults((prev) => prev.map((r, i) => i === idx ? {
        ...r, fixing: false, fixed: true,
        fixedThumb: d.fixed_image_base64 ? `data:image/png;base64,${d.fixed_image_base64}` : r.thumb,
        afterScore: d.after?.total_score ?? d.diagnosis_after?.total_score,
        improvement: d.improvement,
      } : r));
    } catch (e) {
      showToast(`Fix failed: ${e instanceof Error ? e.message : "error"}`);
      setResults((prev) => prev.map((r, i) => (i === idx ? { ...r, fixing: false } : r)));
    }
  };

  const fixAll = async () => {
    const toFix = results.filter((r) => r.total_score >= 0.6 && !r.fixed);
    if (!toFix.length) { showToast("No AI images to fix"); return; }
    for (const item of toFix) {
      const idx = results.indexOf(item);
      await fixOne(idx);
    }
  };

  const downloadReport = () => {
    const lines = ["# AI Detection Report", "", `Scanned: ${results.length} images`, ""];
    lines.push("| File | Score | Verdict |");
    lines.push("|------|-------|---------|");
    for (const r of results) {
      lines.push(`| ${r.filename} | ${r.total_score.toFixed(2)} | ${r.verdict} |`);
    }
    const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "ai-report.md";
    a.click();
  };

  const hasAI = results.some((r) => r.total_score >= 0.6);

  return (
    <div className="min-h-screen bg-background text-foreground" onPaste={handlePaste} tabIndex={0}>
      <div className="max-w-3xl mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-2xl font-bold">AI Image Detector</h1>
          <p className="text-sm text-muted-foreground mt-1">Drag images to detect AI-generated content</p>
        </header>

        <div
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleDrop}
          className={`min-h-[200px] flex flex-col items-center justify-center border-2 border-dashed rounded-xl cursor-pointer transition-colors p-8 ${
            dragOver ? "border-blue-500 bg-blue-500/5" : "border-border hover:border-blue-500/50"
          }`}
        >
          {loading ? (
            <div className="flex items-center gap-3">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-muted-foreground">Analyzing...</span>
            </div>
          ) : (
            <>
              <p className="text-foreground font-medium">Drop images here or click to browse</p>
              <p className="text-xs text-muted-foreground mt-2">Supports JPG, PNG, WebP • Multiple files OK</p>
            </>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            multiple
            className="hidden"
            onChange={(e) => {
              if (e.target.files) analyzeFiles(Array.from(e.target.files));
              e.target.value = "";
            }}
          />
        </div>

        {results.length > 0 && (
          <>
            <div className="flex gap-3 mt-6 flex-wrap">
              {hasAI && (
                <button
                  onClick={fixAll}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors"
                >
                  Fix All AI Images
                </button>
              )}
              <button
                onClick={downloadReport}
                className="px-4 py-2 bg-muted hover:bg-muted/80 text-foreground rounded-lg text-sm font-medium transition-colors"
              >
                Download Report
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
              {results.map((r, i) => {
                const col = scoreColor(r.total_score);
                const { cls, label } = verdictBadge(r.verdict);
                return (
                  <div key={i} className="bg-card border border-border rounded-xl p-4">
                    <div className="flex items-start gap-3">
                      <img src={r.thumb} alt="" className="w-20 h-20 rounded-lg object-cover flex-shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{r.filename}</p>
                        <div className="flex items-center gap-2 mt-2">
                          <div className="flex-1 h-2 rounded-full bg-muted overflow-hidden">
                            <div className="h-full rounded-full transition-all" style={{ width: `${r.total_score * 100}%`, background: col }} />
                          </div>
                          <span className="text-lg font-mono font-bold" style={{ color: col }}>{r.total_score.toFixed(2)}</span>
                        </div>
                        <span className={`inline-block rounded-full px-2 py-0.5 text-xs mt-2 ${cls}`}>{label}</span>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-3">
                      <button onClick={() => toggleExpand(i)} className="px-3 py-1.5 text-xs bg-muted hover:bg-muted/80 rounded-lg transition-colors">
                        Details
                      </button>
                      {r.total_score >= 0.4 && (
                        <button
                          onClick={() => fixOne(i)}
                          disabled={r.fixing}
                          className="px-3 py-1.5 text-xs bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
                        >
                          {r.fixing ? "Fixing..." : "Fix"}
                        </button>
                      )}
                      {r.fixed && r.fixedThumb && (
                        <a href={r.fixedThumb} download={`fixed_${r.filename}`} className="px-3 py-1.5 text-xs bg-muted hover:bg-muted/80 rounded-lg transition-colors">
                          Download
                        </a>
                      )}
                    </div>

                    {r.fixed && r.fixedThumb && (
                      <div className="flex gap-3 mt-4">
                        <div className="flex-1 text-center">
                          <img src={r.thumb} alt="before" className="w-full rounded-lg" />
                          <p className="text-xs text-muted-foreground mt-1">Before: {r.total_score.toFixed(2)}</p>
                        </div>
                        <div className="flex-1 text-center">
                          <img src={r.fixedThumb} alt="after" className="w-full rounded-lg" />
                          <p className="text-xs text-muted-foreground mt-1">After: {r.afterScore?.toFixed(2)}</p>
                        </div>
                        {r.improvement !== undefined && r.improvement > 0 && (
                          <span className="text-green-500 font-bold text-sm self-center">+{r.improvement.toFixed(2)}</span>
                        )}
                      </div>
                    )}

                    {r.expanded && r.detectors && (
                      <div className="mt-4 pt-4 border-t border-border space-y-2">
                        {Object.entries(r.detectors).map(([name, d]) => (
                          <div key={name}>
                            <div className="flex items-center gap-2 text-sm">
                              <span className="w-32 text-muted-foreground truncate">{name}</span>
                              <div className="flex-1 h-1.5 rounded-full bg-muted overflow-hidden">
                                <div className="h-full rounded-full" style={{ width: `${d.score * 100}%`, background: scoreColor(d.score) }} />
                              </div>
                              <span className={`w-8 text-right font-mono text-xs ${d.score > 0.5 ? "text-red-400" : ""}`}>{d.score.toFixed(2)}</span>
                            </div>
                            <p className="text-xs text-muted-foreground/60 ml-32 mt-0.5">{d.detail}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>

      {toast && (
        <div className="fixed bottom-4 right-4 bg-red-600 text-white px-4 py-3 rounded-lg text-sm z-50 max-w-sm">
          {toast}
        </div>
      )}
    </div>
  );
}
