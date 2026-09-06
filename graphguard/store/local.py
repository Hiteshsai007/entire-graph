"""Local JSON store — system of record for the demo."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphguard.engine.models import AnalysisReport

_STORE_DIR = Path(__file__).resolve().parent.parent / "data"


def _ensure_store():
    _STORE_DIR.mkdir(parents=True, exist_ok=True)


def save_report(report: AnalysisReport) -> Path:
    """Save an analysis report as JSON. Returns the file path."""
    _ensure_store()
    path = _STORE_DIR / f"report-{report.symbol}-{report.report_id[:8]}.json"
    with open(path, "w") as f:
        json.dump(report.to_dict(), f, indent=2)
    return path


def load_latest_report(symbol: str) -> AnalysisReport | None:
    """Load the most recent report for a symbol."""
    from graphguard.engine.models import (
        AnalysisReport, NormalizedFacts, EvidenceTag, RankedTest, VerifyOutcome,
    )
    _ensure_store()
    candidates = sorted(
        _STORE_DIR.glob(f"report-{symbol}-*.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return None
    with open(candidates[0]) as f:
        d = json.load(f)
    facts = NormalizedFacts(**d["facts"])
    ranked = [RankedTest(**t) for t in d.get("ranked_tests", [])]
    evidence = [EvidenceTag(**e) for e in d.get("evidence", [])]
    verification = None
    if d.get("verification"):
        verification = VerifyOutcome(**d["verification"])
    return AnalysisReport(
        symbol=d["symbol"],
        repo=d["repo"],
        tier=d["tier"],
        rule_id=d["rule_id"],
        reason=d["reason"],
        ranked_tests=ranked,
        evidence=evidence,
        facts=facts,
        report_id=d["report_id"],
        timestamp=d["timestamp"],
        verification=verification,
    )


def list_reports() -> list[dict]:
    """List all stored reports as dicts."""
    _ensure_store()
    reports = []
    for path in sorted(_STORE_DIR.glob("report-*.json"), key=lambda p: p.stat().st_mtime, reverse=True):
        with open(path) as f:
            reports.append(json.load(f))
    return reports
