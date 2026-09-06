"""Deterministic risk classification from thresholds.yaml."""

from __future__ import annotations


def classify(facts) -> tuple[str, str, str]:
    """Classify risk tier from NormalizedFacts.

    Returns (tier, rule_id, reason).
    Implemented in Phase 1 Step 4.
    """
    raise NotImplementedError("classify — Phase 1 Step 4")
