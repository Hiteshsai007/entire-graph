"""Deterministic risk classification from thresholds.yaml."""

from __future__ import annotations
import yaml
from pathlib import Path
from graphguard.engine.models import NormalizedFacts

def load_thresholds():
    p = Path(__file__).parent.parent / "thresholds.yaml"
    with open(p) as f:
        return yaml.safe_load(f)

def evaluate_condition(when: str, facts: NormalizedFacts) -> bool:
    if when == "else":
        return True
        
    parts = when.split(" AND ")
    for part in parts:
        part = part.strip()
        if part == "is_public":
            if not facts.is_public: return False
        elif ">=" in part:
            field, val = part.split(">=")
            field = field.strip()
            val = int(val.strip())
            if getattr(facts, field) < val: return False
        elif "<" in part:
            field, val = part.split("<")
            field = field.strip()
            val = int(val.strip())
            if getattr(facts, field) >= val: return False
        elif "==" in part:
            field, val = part.split("==")
            field = field.strip()
            val = int(val.strip())
            if getattr(facts, field) != val: return False
    return True

def classify(facts: NormalizedFacts) -> tuple[str, str, str]:
    """Classify risk tier from NormalizedFacts.
    Returns (tier, rule_id, reason).
    """
    thresholds = load_thresholds()
    order = thresholds.get("order", [])
    
    for tier in order:
        rules = thresholds.get(tier, [])
        for rule in rules:
            if evaluate_condition(rule["when"], facts):
                return tier, rule["id"], rule["reason"]
                
    return "LOW", "L1", "internal or well-covered, no elevated signals"
