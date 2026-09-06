# GraphGuard — Evidence-Backed Change Intelligence

**Track:** E2 — Build with Graph Intelligence
**Event:** BTW Buildathon 2026, Sunday 6 Sep, Scaler Bengaluru

## One-Sentence Summary

GraphGuard is a reviewer decision layer that uses Entire Graph's structural facts
to deterministically classify change risk, rank tests by graph reachability,
and verify predictions against real test outcomes — including honestly reporting
when dynamic dispatch contradicts graph-derived expectations.

## Setup

1. Forked `entireio/entire-graph` → `Hiteshsai007/entire-graph`
2. Entire India mirror: _(pending confirmation)_
3. Cloned from mirror
4. Checkpoints enabled (`entire status`)
5. Graph plugin installed (`entire graph version`)
6. `entire graph init-agents --repo .` completed
7. Fresh agent session started

## Architecture

See `GRAPHGAURD_CLAUDE.md` §3.

## Graph Findings

_(To be filled after Phase 1 implementation)_

## Curveball

Pre-edit baseline saved to `graphguard/data/pre-curveball-impact.json`: `classify`
was ambiguous with the analyzer's Groovy scanner, while `rank_tests` has two
direct callers and three transitive callers. The supplied `diff --head .` form
is not supported by this CLI, so the clean pre-edit baseline records `HEAD`
against `HEAD`.

Curveball change: `graphguard/engine/rank.py` now breaks equal test scores by
test name, keeping recommendations deterministic when graph entry order differs.
Proving test: `test_rank_tests_breaks_equal_scores_by_test_name`.

## Checkpoints

1. **Checkpoint 1:** Plan committed.
2. **Checkpoint 2:** What works: analyze/verify/UI/tests. Exact demo command. Fixture outcomes actually seen (including Contradicted yes/no). Databricks not started. Do not add features after this commit.
3. **Checkpoint 3:** Deterministic equal-score ranking tie-break in `rank.py`, proven by `test_rank_tests_breaks_equal_scores_by_test_name`.
4. **Checkpoint 4:** _(final)_

## Run Instructions

```bash
cd graphguard
python -m pytest -q
python -m graphguard.cli analyze --repo fixtures/demo-repo --symbol charge
python -m graphguard.cli serve
```

## Databricks

Not deployed.

## Limitations

- Graph cannot see `getattr`/dynamic dispatch → reported as Contradicted
- Inventory-only languages have no semantic relations
- Co-change data depends on git history depth in the fixture
