import { NextRequest, NextResponse } from "next/server";
import { execFile } from "child_process";
import { promisify } from "util";

const execFileAsync = promisify(execFile);

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const brief = body.brief || { project: "SaaS dashboard", feeling: "warm and precise" };
    const count = Math.min(Math.max(parseInt(String(body.count || 3), 10) || 3, 1), 5);
    const { stdout } = await execFileAsync(
      "python3",
      ["variations.py", JSON.stringify(brief), String(count)],
      {
        cwd: process.cwd(),
        maxBuffer: 50 * 1024 * 1024,
        env: { ...process.env, PYTHONPATH: process.cwd() },
      }
    );
    return NextResponse.json({ variations: JSON.parse(stdout.trim()) });
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: `Variations failed: ${msg}` }, { status: 500 });
  }
}
