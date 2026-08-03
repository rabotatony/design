import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

export async function POST(req: NextRequest) {
  const body = await req.json();
  const brief = body.brief || "";
  try {
    let inputDesign: Record<string, unknown>;
    if (body.css) {
      const { stdout } = await execFileAsync("python3", ["-c", `
import json; from redesigner import parse_css, redesign
d = parse_css(${JSON.stringify(body.css)})
if d is None: print(json.dumps({"error": "No valid CSS variables found"}))
else: print(json.dumps(redesign(d, ${JSON.stringify(brief)})))
`], { cwd: process.cwd(), maxBuffer: 10 * 1024 * 1024, env: { ...process.env, PYTHONPATH: process.cwd() } });
      const result = JSON.parse(stdout.trim());
      if (result.error) return NextResponse.json(result, { status: 400 });
      return NextResponse.json(result);
    }
    inputDesign = body.design || body;
    const briefArg = brief || "";
    const { stdout } = await execFileAsync("python3", [
      "-c", `import json,sys; from redesigner import redesign; r=redesign(json.loads(sys.argv[1]), sys.argv[2] if len(sys.argv)>2 and sys.argv[2] else None); print(json.dumps(r))`,
      JSON.stringify(inputDesign), briefArg,
    ], { cwd: process.cwd(), maxBuffer: 10 * 1024 * 1024, env: { ...process.env, PYTHONPATH: process.cwd() } });
    return NextResponse.json(JSON.parse(stdout.trim()));
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Redesign failed: ${msg}` }, { status: 500 });
  }
}
