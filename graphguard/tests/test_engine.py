"""Tests for engine components using frozen testdata."""

import json
from pathlib import Path
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
    
    tier, rule_id, reason = classify(facts)
    assert tier == "HIGH"
    assert rule_id == "H1"
    
    ranked = rank_tests(facts, tier)
    assert len(ranked) > 0
    assert ranked[0].score == 100
    
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
