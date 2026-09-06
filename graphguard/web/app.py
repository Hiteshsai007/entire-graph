"""FastAPI app for GraphGuard."""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import json
import os
import sys

# Add parent directory to path to allow absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from graphguard.runner import analyze_symbol
from graphguard.engine.evidence import build_evidence
from graphguard.engine.normalize import normalize_impact
from graphguard.engine.models import AnalysisReport
from graphguard.engine.rank import rank_tests
from graphguard.engine.risk import classify
from graphguard.runner.graph_cli import GraphCLIUnavailableError
from graphguard.store.local import save_report

app = FastAPI(title="GraphGuard API")

# Serve static files
static_dir = Path(__file__).parent / "static"
demo_impact_path = Path(__file__).parents[1] / "testdata" / "impact_charge.json"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

class AnalyzeRequest(BaseModel):
    repo: str
    symbol: str

@app.get("/")
def read_root():
    return FileResponse(str(static_dir / "index.html"))


def hosted_demo_report(symbol: str) -> AnalysisReport:
    """Build a clearly-labelled report from the checked-in demo graph snapshot."""
    if symbol != "charge":
        raise HTTPException(
            status_code=422,
            detail="The hosted demo includes the `charge` fixture only. Run GraphGuard locally to analyze your own repository.",
        )

    raw_impact = json.loads(demo_impact_path.read_text())
    facts = normalize_impact(raw_impact, symbol)
    tier, rule_id, reason = classify(facts)
    return AnalysisReport(
        symbol=symbol,
        repo="graphguard/fixtures/demo-repo (hosted fixture)",
        tier=tier,
        rule_id=rule_id,
        reason=reason,
        facts=facts,
        ranked_tests=rank_tests(facts, tier),
        evidence=build_evidence(
            facts,
            tier,
            rule_id,
            reason,
            ["checked-in Entire Graph impact snapshot: graphguard/testdata/impact_charge.json"],
        ),
    )

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    try:
        repo_path = str(Path(req.repo).resolve())
        is_hosted = os.getenv("VERCEL") == "1"
        try:
            report = analyze_symbol(repo_path, req.symbol)
        except GraphCLIUnavailableError:
            if not is_hosted:
                raise
            report = hosted_demo_report(req.symbol)

        # Vercel functions have an ephemeral, read-only application bundle. The
        # hosted demo never pretends that a report was durably stored.
        if not is_hosted:
            save_report(report)
        response = report.to_dict()
        if is_hosted:
            response["demo_notice"] = (
                "Hosted demo: this result is generated from the checked-in `charge` "
                "Entire Graph impact snapshot. Analyze your own repository locally."
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
