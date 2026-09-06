"""Tests for engine components using frozen testdata."""

import json
from pathlib import Path
from graphguard.engine.models import AnalysisReport, NormalizedFacts
from graphguard.engine.normalize import normalize_impact
from graphguard.engine.risk import classify
from graphguard.engine.rank import rank_tests
from graphguard.engine.evidence import build_evidence

TESTDATA_DIR = Path(__file__).parent.parent / "testdata"

def test_charge_high_risk():
    with open(TESTDATA_DIR / "impact_charge.json") as f:
        raw = json.load(f)
        
    facts = normalize_impact(raw, "charge")
    assert facts.symbol == "charge"
    assert facts.is_public is True
    assert facts.direct_callers == 1
    assert facts.transitive_callers == 1
    assert facts.raw_direct_callers == 4
    assert facts.raw_transitive_callers == 3
    assert facts.test_depths["test_charge_success"] == 1
    assert facts.test_vias["test_process_order_success"] == "process_order"
    
    tier, rule_id, reason = classify(facts)
    assert tier == "HIGH"
    assert rule_id == "H1"
    
    ranked = rank_tests(facts, tier)
    assert len(ranked) > 0
    assert ranked[0].score == 100
    depth_two = next(test for test in ranked if test.test_name == "test_process_order_success")
    assert depth_two.path == "test_process_order_success --CALLS--> process_order --CALLS--> charge"
    
    evidence = build_evidence(facts, tier, rule_id, reason, ["entire graph impact --repo . --symbol charge"])
    assert len(evidence) == 2
    assert evidence[0].tag == "graph_fact"
    assert evidence[1].tag == "derived"

def test_health_low_risk():
    with open(TESTDATA_DIR / "impact_health.json") as f:
        raw = json.load(f)
        
    facts = normalize_impact(raw, "health")
    assert facts.symbol == "health"
    assert facts.is_public is True
    assert facts.direct_callers == 0
    assert facts.raw_direct_callers == 1
    
    tier, rule_id, reason = classify(facts)
    assert tier == "LOW"
    assert rule_id == "L1"


def test_rank_tests_breaks_equal_scores_by_test_name():
    facts = NormalizedFacts(
        symbol="charge",
        is_public=True,
        test_names=["test_zebra", "test_alpha"],
        test_depths={"test_zebra": 1, "test_alpha": 1},
        direct_caller_names=["test_zebra", "test_alpha"],
    )

    ranked = rank_tests(facts, "HIGH")

    assert [test.test_name for test in ranked] == ["test_alpha", "test_zebra"]


def test_partial_impact_requires_verification_without_changing_confirmed_behavior():
    with open(TESTDATA_DIR / "impact_partial.json") as f:
        raw = json.load(f)

    facts = normalize_impact(raw, "dynamic_charge")
    tier, rule_id, reason = classify(facts)
    evidence = build_evidence(
        facts, tier, rule_id, reason,
        ["entire graph impact --repo . --symbol dynamic_charge"],
    )

    assert facts.analysis_status == "partial"
    assert "partial failure: E_DYNAMIC_DISPATCH" in facts.analysis_limitations
    assert facts.direct_callers == 0
    assert [tag.tag for tag in evidence] == [
        "incomplete_graph_evidence", "derived", "verification_required",
    ]
    assert evidence[1].content.startswith("Provisional classification:")

    report = AnalysisReport(
        symbol="dynamic_charge",
        repo="fixtures/partial-repo",
        tier=tier,
        rule_id=rule_id,
        reason=reason,
        ranked_tests=[],
        evidence=evidence,
        facts=facts,
    )
    assert "Analysis: PARTIAL" in report.render_text()
