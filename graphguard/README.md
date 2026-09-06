# GraphGuard

Evidence-backed change intelligence powered by [Entire Graph](https://github.com/entireio/entire-graph).

## What It Does

1. **Analyze** — Run `entire graph impact` on a symbol; classify risk deterministically via `thresholds.yaml`.
2. **Explain** — Show *why* with graph-grounded evidence tags (`graph_fact`, `derived`, `historical`).
3. **Rank Tests** — Order tests by graph reachability (direct test → caller test → co-change).
4. **Verify** — Run baseline + post-edit tests; report Clean / Caught regression / Pre-existing / Contradicted.

## Quick Start

```bash
cd graphguard
pip install -e ".[dev]"
python -m pytest -q
python -m graphguard.cli analyze --repo fixtures/demo-repo --symbol charge
python -m graphguard.cli serve
```

Open http://127.0.0.1:8765

## Architecture

```
Reviewer
   └─ local UI :8765 (or report.html)
         └─ graphguard CLI (analyze / explain / verify)
               ├─ engine: risk.py + rank.py + evidence.py + thresholds.yaml
               ├─ store/local.py  (JSON SoR for the demo)
               └─ runner/graph_cli.py ── shells ──► entire graph CLI
                                                        │
                                                        ▼
                                            fixtures/demo-repo
```

## Risk Tiers

Deterministic. See `thresholds.yaml`. No LLM in the loop.

## Limitations

- `getattr` / dynamic dispatch is invisible to the graph → reported as **Contradicted**
- Co-change data requires git history
- Inventory-only languages have no semantic relations
