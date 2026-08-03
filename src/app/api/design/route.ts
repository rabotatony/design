import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

async function runDesigner(briefJson: string, flag?: string): Promise<string> {
  const args = flag ? ["designer.py", briefJson, flag] : ["designer.py", briefJson];
  const { stdout } = await execFileAsync("python3", args, {
    cwd: process.cwd(),
    maxBuffer: 10 * 1024 * 1024,
    env: { ...process.env, PYTHONPATH: process.cwd() },
  });
  return stdout.trim();
}

export async function GET() {
  const brief = { project: "SaaS dashboard", feeling: "warm and precise", audience: "developers" };
  return POST(NextRequest ? new NextRequest("http://localhost/api/design", {
    method: "POST",
    body: JSON.stringify({ brief }),
    headers: { "Content-Type": "application/json" },
  }) : null as never);
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const brief = body.brief || body;
  const briefJson = JSON.stringify(brief);
  try {
    const [designOut, cssOut, tailwindOut] = await Promise.all([
      runDesigner(briefJson),
      runDesigner(briefJson, "--css"),
      runDesigner(briefJson, "--tailwind"),
    ]);
    const design = JSON.parse(designOut);
    return NextResponse.json({
      design,
      css: cssOut,
      tailwind: tailwindOut,
    });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Design generation failed: ${msg}` }, { status: 500 });
  }
}
