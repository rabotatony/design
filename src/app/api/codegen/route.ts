import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

async function runCodegen(args: string[]): Promise<string> {
  const { stdout } = await execFileAsync("python3", args, {
    cwd: process.cwd(),
    maxBuffer: 50 * 1024 * 1024,
    env: { ...process.env, PYTHONPATH: process.cwd() },
  });
  return stdout.trim();
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    let out: string;
    if (body.design) {
      out = await runCodegen(["codegen.py", JSON.stringify({ design: body.design }), "--full"]);
    } else {
      const brief = body.brief || { project: "SaaS dashboard", feeling: "warm and precise" };
      out = await runCodegen(["codegen.py", "--brief", JSON.stringify(brief), "--full"]);
    }
    return NextResponse.json(JSON.parse(out));
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Codegen failed: ${msg}` }, { status: 500 });
  }
}
