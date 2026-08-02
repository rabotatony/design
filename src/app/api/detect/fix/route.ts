import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";
import { writeFile, readFile, unlink, mkdir } from "fs/promises";
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
  const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const inFile = path.join(tmpDir, `in-${id}${ext}`);
  const outFile = path.join(tmpDir, `out-${id}${ext}`);
  try {
    await writeFile(inFile, new Uint8Array(await file.arrayBuffer()));
    const script = `from detector import process; import json; r=process('${inFile}','${outFile}'); print(json.dumps(r))`;
    const { stdout } = await execFileAsync("python3", ["-c", script], {
      cwd: process.cwd(),
      maxBuffer: 10 * 1024 * 1024,
    });
    const report = JSON.parse(stdout.trim().split("\n").pop()!);
    let fixedBase64 = "";
    try {
      const fixedData = await readFile(outFile);
      fixedBase64 = Buffer.from(fixedData).toString("base64");
    } catch {}
    return NextResponse.json({ ...report, fixed_image_base64: fixedBase64 });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Fix failed: ${msg}` }, { status: 500 });
  } finally {
    try { await unlink(inFile); } catch {}
    try { await unlink(outFile); } catch {}
  }
}
