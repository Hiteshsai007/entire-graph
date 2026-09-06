# GraphGuard — Evidence-Backed Change Intelligence

**Track:** E2 — Build with Graph Intelligence
**Event:** BTW Buildathon 2026, Sunday 6 Sep, Scaler Bengaluru

## One-Sentence Summary

GraphGuard is a reviewer decision layer that uses Entire Graph's structural facts
to deterministically classify change risk, rank tests by graph reachability,
and verify predictions against real test outcomes — including honestly reporting
when dynamic dispatch contradicts graph-derived expectations.

## Setup

1. GraphGuard Checkpoints 1–3 and Databricks export staging were merged into [`Hiteshsai007/entire-graph`](https://github.com/Hiteshsai007/entire-graph) `main` at [`f3196af`](https://github.com/Hiteshsai007/entire-graph/commit/f3196af).
2. Entire India mirror: **not configured or verified in this checkout**. Do not claim that this checkout was cloned from a mirror until its URL and push are confirmed.
3. The local GraphGuard tests were run from the repository root with the project test suite.
4. A local Entire Graph executable is required for a live analysis; configure `entire`, `entire-graph`, or `GRAPHGUARD_ENTIRE_GRAPH_BIN`.

## Architecture

```
Reviewer → local FastAPI UI / CLI → GraphGuard engine
                                  → Entire Graph impact facts
                                  → deterministic risk + ranked tests + evidence
```

The local JSON store remains the demo source of record. No LLM assigns risk tiers.

## Graph Findings

Verified against frozen `impact_charge.json` by `graphguard/tests/test_engine.py`:

- `charge` is public and classifies as **HIGH** via deterministic rule `H1`.
- The normalized facts contain one direct and one transitive caller; the direct test recommendation scores `100`.
- `test_process_order_success` preserves the graph path through `process_order` to `charge`.

These are fixture-backed unit-test findings. A live `entire graph impact` demonstration still requires an installed Entire Graph executable.

## Curveball

Pre-edit baseline saved to `graphguard/data/pre-curveball-impact.json`: `classify`
was ambiguous with the analyzer's Groovy scanner, while `rank_tests` has two
direct callers and three transitive callers. The supplied `diff --head .` form
is not supported by this CLI, so the clean pre-edit baseline records `HEAD`
against `HEAD`.

Curveball change: `graphguard/engine/rank.py` now breaks equal test scores by
test name, keeping recommendations deterministic when graph entry order differs.
Proving test: `test_rank_tests_breaks_equal_scores_by_test_name`.

## Noon Curveball - Track 2: Graph is Evidence, Not an Oracle

**Invalidated assumption:** every relationship returned by `entire graph impact`
could be presented as complete. Dynamic dispatch, reflection, generated code, or
machine-readable partial failures can leave the structural picture incomplete.

**Impact analysis before edit:** `analyze_symbol` consumes impact output through
`normalize_impact`, then passes the facts to deterministic classification, test
ranking, evidence rendering, CLI output, and the FastAPI UI.

**Revised design:** impact output now carries an explicit `confirmed` or `partial`
analysis status. Fully resolved output retains its existing graph facts and
deterministic risk tier. Partial output is labeled as incomplete graph evidence,
its tier is provisional, and the UI/CLI require source or test verification before
relying on relationship counts or ranked tests.

**Proof:** `graphguard/testdata/impact_partial.json` represents a dynamic-dispatch
partial failure. `test_partial_impact_requires_verification_without_changing_confirmed_behavior`
checks the incomplete-evidence and verification-required labels; the existing
`test_charge_high_risk` preserves confirmed-output behavior.

## Checkpoints

1. **Checkpoint 1:** [Plan committed](https://github.com/Hiteshsai007/entire-graph/commit/5eef99ebefc97b0fd664807cffcb3077733c5847).
2. **Checkpoint 2:** [Analyze/verify/UI/tests baseline](https://github.com/Hiteshsai007/entire-graph/commit/ee48e87c5f2272a97e7e09df239ff086e41a682b).
3. **Checkpoint 3:** [Deterministic equal-score ranking tie-break](https://github.com/Hiteshsai007/entire-graph/commit/02652f1746de852d7978da5e021022b888395ada), proven by `test_rank_tests_breaks_equal_scores_by_test_name`.
4. **Checkpoint 4:** Release verification recorded against merged `main` [`f3196af`](https://github.com/Hiteshsai007/entire-graph/commit/f3196af): `python3 -m pytest -q graphguard/tests` → **11 passed**.

## Run Instructions

```bash
python -m pip install -e "./graphguard[dev]"
python -m pytest -q graphguard/tests
python -m graphguard.cli analyze charge --repo graphguard/fixtures/demo-repo
python -m uvicorn graphguard.web.app:app --host 127.0.0.1 --port 8765
```

For a live analysis, make the Entire Graph command available as `entire`, `entire-graph`, or set `GRAPHGUARD_ENTIRE_GRAPH_BIN` before running the CLI or submitting a UI analysis.

## Databricks

Export staging is merged: local GraphGuard JSON can be staged for the Databricks notebook, which materializes the four Unity Catalog tables and MLflow metrics. No Databricks workspace or app URL is configured or deployed for this release.

## Limitations

- Graph cannot see `getattr`/dynamic dispatch → reported as Contradicted
- Inventory-only languages have no semantic relations
- Co-change data depends on git history depth in the fixture
- The release environment used for this record has no Entire Graph executable, so the live UI/CLI analysis was not asserted here; its portable command-resolution behavior is covered by unit tests.
- The Entire India mirror has not been configured in this checkout, so its push status cannot be confirmed.
