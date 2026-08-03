import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

const SCRIPT = [
  "import sys, json, base64",
  "from codegen import generate_zip",
  "from designer import generate_design",
  "print(base64.b64encode(generate_zip(generate_design(json.loads(sys.argv[1])))).decode())",
].join("; ");

export async function GET(req: NextRequest) {
  try {
    const briefParam = req.nextUrl.searchParams.get("brief");
    const brief = briefParam
      ? JSON.parse(briefParam)
      : { project: "SaaS dashboard", feeling: "warm and precise" };
    const { stdout } = await execFileAsync("python3", ["-c", SCRIPT, JSON.stringify(brief)], {
      cwd: process.cwd(),
      maxBuffer: 50 * 1024 * 1024,
      env: { ...process.env, PYTHONPATH: process.cwd() },
    });
    const buf = Buffer.from(stdout.trim(), "base64");
    return new NextResponse(new Uint8Array(buf), {
      headers: {
        "Content-Type": "application/zip",
        "Content-Disposition": "attachment; filename=\"anti-ai-components.zip\"",
      },
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Download failed: ${msg}` }, { status: 500 });
  }
}
