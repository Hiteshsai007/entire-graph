"""Rank tests by graph reachability."""

from __future__ import annotations
from graphguard.engine.models import NormalizedFacts, RankedTest

def rank_tests(facts: NormalizedFacts, tier: str) -> list[RankedTest]:
    """Rank tests by graph path score."""
    ranked = []
    seen = set()
    
    # Score only the exact reachability facts retained by normalize_impact.
    for test in facts.test_names:
        depth = facts.test_depths.get(test)
        if depth == 1 and test not in seen:
            path = f"{test} --CALLS--> {facts.symbol}"
            ranked.append(RankedTest(test_name=test, score=100, reason="direct graph caller", path=path))
            seen.add(test)

    # Depth-2 entries retain their graph-provided intermediate symbol in `via`.
    for test in facts.test_names:
        if test in seen:
            continue
        if facts.test_depths.get(test) == 2:
            via = facts.test_vias.get(test)
            path = (
                f"{test} --CALLS--> {via} --CALLS--> {facts.symbol}"
                if via
                else f"{test} --CALLS(depth=2)--> {facts.symbol}"
            )
            ranked.append(
                RankedTest(
                    test_name=test,
                    score=60,
                    reason="graph-reachable test at depth 2",
                    path=path,
                )
            )
            seen.add(test)
            
    # 4. Co-change with test file (10)
    for test_file in facts.cochange_file_names:
        if "test" in test_file:
            # Extract test name from file name roughly
            test = test_file.split("/")[-1].replace(".py", "")
            if test not in seen:
                path = f"{facts.symbol} ←CO_CHANGES_WITH {test_file}"
                ranked.append(RankedTest(test_name=test, score=10, reason="co-change with test file", path=path))
                seen.add(test)
                
    # Sort by score descending, then name, so equal graph paths are deterministic.
    ranked.sort(key=lambda x: (-x.score, x.test_name))
    return ranked
