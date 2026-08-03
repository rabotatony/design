import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

const SCRIPT = [
  "import sys, json",
  "from apply import apply_to_globals_css",
  "from designer import generate_design",
  "payload = json.loads(sys.argv[1])",
  "design = payload.get('design') or generate_design(payload.get('brief') or {})",
  "css, report = apply_to_globals_css(payload['css'], design)",
  "print(json.dumps({'css': css, 'report': report, 'design': design}))",
].join("\n");

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    if (!body.css) {
      return NextResponse.json({ error: "css is required" }, { status: 400 });
    }
    const { stdout } = await execFileAsync(
      "python3",
      ["-c", SCRIPT, JSON.stringify({ css: body.css, brief: body.brief, design: body.design })],
      {
        cwd: process.cwd(),
        maxBuffer: 50 * 1024 * 1024,
        env: { ...process.env, PYTHONPATH: process.cwd() },
      }
    );
    return NextResponse.json(JSON.parse(stdout.trim()));
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Apply failed: ${msg}` }, { status: 500 });
  }
}
