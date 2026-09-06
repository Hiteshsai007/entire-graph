"""Normalize raw graph impact JSON into NormalizedFacts."""

from __future__ import annotations

from graphguard.engine.models import NormalizedFacts


def normalize_impact(raw: dict, symbol: str) -> NormalizedFacts:
    """Convert raw entire graph impact JSON into NormalizedFacts.

    Implemented in Phase 1 Step 4.
    """
    raise NotImplementedError("normalize_impact — Phase 1 Step 4")
