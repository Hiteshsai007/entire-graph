"""Build evidence tags from graph facts."""

from __future__ import annotations
from graphguard.engine.models import NormalizedFacts, EvidenceTag

def build_evidence(facts: NormalizedFacts, tier: str, rule_id: str, reason: str, cli_calls: list) -> list[EvidenceTag]:
    """Build evidence tags (graph_fact, derived, historical)."""
    evidence = []
    
    # 1. Structural evidence. Partial analyzer output is explicitly not a
    # confirmed graph fact, even if it contains some resolved relationships.
    for call in cli_calls:
        if "impact" in call:
            if facts.analysis_status == "partial":
                evidence.append(EvidenceTag(
                    tag="incomplete_graph_evidence",
                    content="Graph analysis is partial; relationship counts and test reachability are not complete.",
                    file_line=f"{facts.file_path}:{facts.line}",
                    argv=call,
                ))
            else:
                evidence.append(EvidenceTag(
                    tag="graph_fact",
                    content=f"Impact analysis found {facts.raw_direct_callers} direct, {facts.raw_transitive_callers} transitive callers.",
                    file_line=f"{facts.file_path}:{facts.line}",
                    argv=call
                ))
            break
    
    # 2. derived
    # Fired rule id from thresholds.yaml
    evidence.append(EvidenceTag(
        tag="derived",
        content=(
            f"Provisional classification: {tier} because {reason}"
            if facts.analysis_status == "partial"
            else f"Classified as {tier} because {reason}"
        ),
        file_line=f"thresholds.yaml:{rule_id}"
    ))

    if facts.analysis_status == "partial":
        evidence.append(EvidenceTag(
            tag="verification_required",
            content="Verify affected source and run relevant tests before relying on this risk tier or test ranking.",
        ))
    
    # 3. historical
    # Graph's own co-change count
    if facts.cochange_files > 0:
        evidence.append(EvidenceTag(
            tag="historical",
            content=f"Historically co-changes with {facts.cochange_files} files.",
            file_line=""
        ))
        
    return evidence
