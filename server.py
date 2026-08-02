import os
import io
import json
import base64
import tempfile
import zipfile
import contextlib
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from detector import analyze, process

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
MAX_SIZE = 50 * 1024 * 1024


def _save_tmp(upload):
    data = upload.file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(413, "File exceeds 50MB limit")
    suffix = os.path.splitext(upload.filename)[1] or ".png"
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, "wb") as f:
        f.write(data)
    return path

def _analyze_quiet(path):
    with contextlib.redirect_stdout(open(os.devnull, "w")):
        return analyze(path)

def _process_quiet(path, out):
    with contextlib.redirect_stdout(open(os.devnull, "w")):
        return process(path, out)


@app.get("/")
def index():
    return FileResponse(os.path.join(os.path.dirname(__file__), "static", "index.html"))

@app.post("/api/analyze")
async def api_analyze(file: UploadFile = File(...)):
    path = _save_tmp(file)
    try: return _analyze_quiet(path)
    finally: os.unlink(path)


@app.post("/api/fix")
async def api_fix(file: UploadFile = File(...)):
    path = _save_tmp(file)
    try:
        before = _analyze_quiet(path)
        if before["total_score"] < 0.4:
            with open(path, "rb") as f: b64 = base64.b64encode(f.read()).decode()
            return {"diagnosis_before": before, "diagnosis_after": before, "improvement": 0,
                    "image_base64": b64, "message": "human_likely, no correction needed"}
        fd, out = tempfile.mkstemp(suffix=os.path.splitext(path)[1]); os.close(fd)
        report = _process_quiet(path, out); after = _analyze_quiet(out)
        with open(out, "rb") as f: b64 = base64.b64encode(f.read()).decode()
        os.unlink(out)
        return {"diagnosis_before": before, "diagnosis_after": after,
                "improvement": report["improvement"], "image_base64": b64}
    finally: os.unlink(path)


def _thumb(path, size=60):
    from PIL import Image as PImage
    img = PImage.open(path).convert("RGB"); img.thumbnail((size, size))
    buf = io.BytesIO(); img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@app.post("/api/batch")
async def api_batch(files: list[UploadFile] = File(...)):
    results = []
    for f in files:
        path = _save_tmp(f)
        try:
            d = _analyze_quiet(path)
            d["thumb"] = "data:image/png;base64," + _thumb(path)
        except Exception as e:
            d = {"file": f.filename, "error": str(e), "total_score": 0, "verdict": "error"}
        finally:
            os.unlink(path)
        d["file"] = f.filename
        results.append(d)
    return sorted(results, key=lambda r: r.get("total_score", 0), reverse=True)


@app.post("/api/batch/fix")
async def api_batch_fix(files: list[UploadFile] = File(...)):
    buf = io.BytesIO()
    summary = {"total": 0, "fixed": 0, "skipped": 0}
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            path = _save_tmp(f)
            try:
                before = _analyze_quiet(path)
                summary["total"] += 1
                if before["total_score"] < 0.4:
                    summary["skipped"] += 1
                    zf.write(path, f.filename)
                    continue
                fd, out = tempfile.mkstemp(suffix=os.path.splitext(path)[1])
                os.close(fd)
                _process_quiet(path, out)
                zf.write(out, f"fixed_{f.filename}")
                os.unlink(out)
                summary["fixed"] += 1
            finally:
                os.unlink(path)
    buf.seek(0)
    return Response(content=buf.read(), media_type="application/zip",
                    headers={"X-Summary": json.dumps(summary), "Content-Disposition": "attachment; filename=fixed_images.zip"})


if __name__ == "__main__":
    import uvicorn
    print("Open http://localhost:8765")
    uvicorn.run(app, host="0.0.0.0", port=8765)