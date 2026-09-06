"""FastAPI app for GraphGuard."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import os
import sys

# Add parent directory to path to allow absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from graphguard.runner import analyze_symbol
from graphguard.store.local import save_report

app = FastAPI(title="GraphGuard API")

# Serve static files
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class AnalyzeRequest(BaseModel):
    repo: str
    symbol: str

@app.get("/")
def read_root():
    return FileResponse(str(static_dir / "index.html"))

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        repo_path = str(Path(req.repo).resolve())
        report = analyze_symbol(repo_path, req.symbol)
        save_report(report)
        return report.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
