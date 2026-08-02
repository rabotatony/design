import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";
import { writeFile, unlink, mkdir } from "fs/promises";
import path from "path";
import os from "os";

const execFileAsync = promisify(execFile);

export async function POST(req: NextRequest) {
  const formData = await req.formData();
  const file = formData.get("file") as File | null;
  if (!file) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }
  if (file.size > 50 * 1024 * 1024) {
    return NextResponse.json({ error: "File exceeds 50MB limit" }, { status: 413 });
  }
  const tmpDir = path.join(os.tmpdir(), "ai-detector");
  await mkdir(tmpDir, { recursive: true });
  const ext = path.extname(file.name) || ".png";
  const tmpFile = path.join(tmpDir, `upload-${Date.now()}-${Math.random().toString(36).slice(2)}${ext}`);
  try {
    const bytes = new Uint8Array(await file.arrayBuffer());
    await writeFile(tmpFile, bytes);
    const { stdout } = await execFileAsync("python3", ["detector.py", tmpFile], {
      cwd: process.cwd(),
      maxBuffer: 10 * 1024 * 1024,
    });
    const result = JSON.parse(stdout);
    return NextResponse.json(result);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Cannot analyze: ${msg}` }, { status: 500 });
  } finally {
    try { await unlink(tmpFile); } catch {}
  }
}
