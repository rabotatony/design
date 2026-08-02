import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";
import { writeFile, unlink, mkdir } from "fs/promises";
import path from "path";
import os from "os";

const execFileAsync = promisify(execFile);

async function analyzeFile(file: File): Promise<Record<string, unknown>> {
  const tmpDir = path.join(os.tmpdir(), "ai-detector");
  await mkdir(tmpDir, { recursive: true });
  const ext = path.extname(file.name) || ".png";
  const tmpFile = path.join(tmpDir, `batch-${Date.now()}-${Math.random().toString(36).slice(2)}${ext}`);
  try {
    await writeFile(tmpFile, new Uint8Array(await file.arrayBuffer()));
    const { stdout } = await execFileAsync("python3", ["detector.py", tmpFile], {
      cwd: process.cwd(),
      maxBuffer: 10 * 1024 * 1024,
    });
    const result = JSON.parse(stdout);
    result.file = file.name;
    return result;
  } finally {
    try { await unlink(tmpFile); } catch {}
  }
}

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const files = formData.getAll("files") as File[];
  if (!files.length) {
    return NextResponse.json({ error: "No files provided" }, { status: 400 });
  }
  const results: Record<string, unknown>[] = [];
  for (const file of files) {
    if (file.size > 50 * 1024 * 1024) {
      results.push({ file: file.name, error: "File exceeds 50MB", total_score: 0, verdict: "error" });
      continue;
    }
    try {
      results.push(await analyzeFile(file));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : String(err);
      results.push({ file: file.name, error: msg, total_score: 0, verdict: "error" });
    }
  }
  results.sort((a, b) => ((b.total_score as number) || 0) - ((a.total_score as number) || 0));
  return NextResponse.json(results);
}
