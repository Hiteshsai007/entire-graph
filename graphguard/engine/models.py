"""GraphGuard data models."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any


@dataclass
class NormalizedFacts:
    """Normalized facts extracted from graph impact output."""
    symbol: str
    is_public: bool
    direct_callers: int = 0
    transitive_callers: int = 0
    reachable_tests: int = 0
    cochange_files: int = 0
    direct_caller_names: list[str] = field(default_factory=list)
    transitive_caller_names: list[str] = field(default_factory=list)
    test_names: list[str] = field(default_factory=list)
    cochange_file_names: list[str] = field(default_factory=list)
    callees: list[str] = field(default_factory=list)
    type_consumers: list[str] = field(default_factory=list)
    siblings: list[str] = field(default_factory=list)
    file_path: str = ""
    line: int = 0
    blind_spots: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EvidenceTag:
    """A single evidence tag: graph_fact, derived, or historical."""
    tag: str  # "graph_fact" | "derived" | "historical"
    content: str
    file_line: str = ""  # e.g. "payments/api.py:5"
    argv: str = ""  # CLI command that produced this fact

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RankedTest:
    """A test ranked by graph reachability."""
    test_name: str
    score: int
    reason: str
    path: str  # e.g. "charge ←CALLS process_order ←TESTED_BY test_processor"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VerifyOutcome:
    """Result of a verification run."""
    status: str  # "Clean" | "Caught regression" | "Pre-existing" | "Contradicted"
    baseline_passed: bool | None = None
    post_edit_passed: bool | None = None
    baseline_output: str = ""
    post_edit_output: str = ""
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def render_text(self) -> str:
        lines = [f"Verification: {self.status}"]
        if self.baseline_passed is not None:
            lines.append(f"  Baseline: {'PASS' if self.baseline_passed else 'FAIL'}")
        if self.post_edit_passed is not None:
            lines.append(f"  Post-edit: {'PASS' if self.post_edit_passed else 'FAIL'}")
        if self.detail:
            lines.append(f"  Detail: {self.detail}")
        return "\n".join(lines)


@dataclass
class AnalysisReport:
    """Full analysis report for a symbol."""
    symbol: str
    repo: str
    tier: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    rule_id: str  # e.g. "H1"
    reason: str
    ranked_tests: list[RankedTest]
    evidence: list[EvidenceTag]
    facts: NormalizedFacts
    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verification: VerifyOutcome | None = None

    def to_dict(self) -> dict[str, Any]:
        d = {
            "report_id": self.report_id,
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "repo": self.repo,
            "tier": self.tier,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "ranked_tests": [t.to_dict() for t in self.ranked_tests],
            "evidence": [e.to_dict() for e in self.evidence],
            "facts": self.facts.to_dict(),
        }
        if self.verification is not None:
            d["verification"] = self.verification.to_dict()
        return d

    def render_text(self) -> str:
        lines = [
            f"═══ GraphGuard: {self.symbol} ═══",
            f"Risk: {self.tier} ({self.rule_id})",
            f"Reason: {self.reason}",
            "",
            "── Impact ──",
            f"  Direct callers: {self.facts.direct_callers} {self.facts.direct_caller_names}",
            f"  Transitive callers: {self.facts.transitive_callers} {self.facts.transitive_caller_names}",
            f"  Reachable tests: {self.facts.reachable_tests} {self.facts.test_names}",
            f"  Co-change files: {self.facts.cochange_files}",
            f"  File: {self.facts.file_path}:{self.facts.line}",
        ]
        if self.facts.blind_spots:
            lines.append(f"  ⚠ Blind spots: {', '.join(self.facts.blind_spots)}")

        lines.append("")
        lines.append("── Recommended Tests ──")
        for t in self.ranked_tests:
            lines.append(f"  [{t.score:3d}] {t.test_name}")
            lines.append(f"        {t.path}")

        lines.append("")
        lines.append("── Evidence (Why?) ──")
        for e in self.evidence:
            loc = f" @ {e.file_line}" if e.file_line else ""
            lines.append(f"  [{e.tag}]{loc} {e.content}")

        if self.verification:
            lines.append("")
            lines.append("── Prediction vs Outcome ──")
            lines.append(f"  {self.verification.render_text()}")

        return "\n".join(lines)

    def render_evidence_text(self) -> str:
        lines = [f"Evidence for {self.symbol} ({self.tier} via {self.rule_id}):"]
        for e in self.evidence:
            loc = f" @ {e.file_line}" if e.file_line else ""
            argv = f" (cmd: {e.argv})" if e.argv else ""
            lines.append(f"  [{e.tag}]{loc} {e.content}{argv}")
        return "\n".join(lines)
