# GraphGuard - Evidence-Backed Change Intelligence

## One-sentence summary

GraphGuard turns Entire Graph impact evidence into a deterministic change-risk decision, ranked test plan, and reviewable explanation while explicitly marking incomplete structural evidence as provisional.

## Problem, intended user, and why it matters

Reviewers and coding agents need to decide what a change can break before they run an expensive or incomplete test suite. A raw dependency graph does not tell a reviewer which tests matter, how confident to be, or when static analysis is incomplete. GraphGuard gives developers reviewing an API or implementation change a small, inspectable risk assessment with a concrete verification path.

## Selected Entire track and why Entire is essential

**Track 2 - Build with Graph Intelligence.** Entire Graph is the factual input to the product: impact supplies callers, reachable tests, file location, co-change information, and machine-readable partial-failure signals. GraphGuard normalizes that evidence, applies deterministic risk thresholds, ranks tests, and shows the exact graph command behind each finding. Without the graph, the product has no structural basis for its recommendation.

## Architecture and main workflow

~~~text
Reviewer or API client
  -> GraphGuard CLI / FastAPI UI
  -> Entire Graph impact JSON
  -> normalized facts + deterministic risk classification + ranked tests
  -> saved local report-*.json artifact
  -> optional Unity Catalog Volume staging
  -> Databricks notebook: Delta tables + MLflow run metrics
~~~

The local JSON report is the system of record for the demo. No LLM assigns a risk tier. Databricks is an optional analytics and demonstration layer; it does not replace the local decision workflow.

## Entire Graph findings and verification

Entire Graph v0.4.0 is installed and activated for this checkout. The following evidence was verified against source, tests, and a live local run:

- Graph search for “GraphGuard Databricks report export and notebook materialization” located **push_to_databricks** in graphguard/store/databricks.py and its focused staging tests.
- Impact analysis for **push_to_databricks** found the CLI and two Databricks tests as direct callers, plus graphguard/README.md as its only historical co-change partner. The focused test suite covers those call sites.
- A live analysis of **charge** classified it as **HIGH (H1)**, ranked five reachable tests, and saved a report-*.json artifact. The FastAPI endpoint returned the same graph-backed report and persisted an artifact.
- python3 -m pytest -q graphguard/tests is the regression suite for risk classification, partial graph evidence, the browser UI, report persistence, and Databricks staging.

Graph results are evidence rather than an oracle. GraphGuard does not present dynamic dispatch, reflection, generated code, or a machine-readable partial failure as a complete relationship fact.

## Noon Curveball: what changed and how we adapted

The response is the explicit **Graph is Evidence, Not an Oracle** behavior. The invalidated assumption was that every relationship from Entire Graph impact was complete enough to drive a decision. The implementation now carries confirmed or partial analysis status, labels partial output as incomplete evidence, keeps its risk classification provisional, and requires source or test verification before relationship counts or test recommendations are used.

graphguard/testdata/impact_partial.json represents a dynamic-dispatch partial failure. test_partial_impact_requires_verification_without_changing_confirmed_behavior proves the partial-evidence labels and verification requirement, while test_charge_high_risk proves that confirmed-output behavior remains intact. The deterministic equal-score tie break in graphguard/engine/rank.py, covered by test_rank_tests_breaks_equal_scores_by_test_name, ensures recommendations remain stable when graph entry ordering varies.

## Checkpoint links and what each checkpoint proves

The historical Git commits below are useful code milestones, but they are **not being misrepresented as Entire Checkpoints**:

1. [Planning milestone](https://github.com/Hiteshsai007/entire-graph/commit/5eef99ebefc97b0fd664807cffcb3077733c5847)
2. [Analysis, verification, and UI baseline](https://github.com/Hiteshsai007/entire-graph/commit/ee48e87c5f2272a97e7e09df239ff086e41a682b)
3. [Deterministic ranking milestone](https://github.com/Hiteshsai007/entire-graph/commit/02652f1746de852d7978da5e021022b888395ada)
4. [Merged release-readiness documentation](https://github.com/Hiteshsai007/entire-graph/commit/4164859)

In this checkout, the seven reviewed Entire lifecycle hooks are trusted and Entire is enabled. A genuine final verification checkpoint must be attached to the final commit and its link included in the submission. The required pre-noon, Curveball, and final checkpoint records cannot be truthfully backfilled if they were not captured during the event; use entire checkpoint list and verify each link before submission.

## Setup, run, and test instructions

~~~bash
# From the repository root.
python3 -m pip install -e "./graphguard[dev]"
entire plugin install graph
entire graph version
entire graph init-agents --repo .

# Run the full regression suite and a live graph-backed analysis.
python3 -m pytest -q graphguard/tests
python3 -m graphguard.cli analyze charge --repo graphguard/fixtures/demo-repo

# Start the local product.
python3 -m uvicorn graphguard.web.app:app --host 127.0.0.1 --port 8765
~~~

Open http://127.0.0.1:8765/, choose a repository and symbol, then inspect the risk tier, evidence, and ranked tests. A successful CLI or UI analysis saves a local report-*.json file under graphguard/data/; those generated artifacts are intentionally not committed.

## Databricks use, data sources, and limitations

### Verified workspace resources

- Unity Catalog schema: workspace.graphguard
- Managed Volume: /Volumes/workspace/graphguard/input
- Workspace resource: [GraphGuard input volume](https://dbc-ddd40b1f-5e3d.cloud.databricks.com/explore/data/volumes/workspace/graphguard/input?o=7474658491693886)
- Repository notebook: graphguard/notebooks/databricks_export.py

The staging command uploads only local report-*.json artifacts to /Volumes/workspace/graphguard/input/graphguard/reports. The notebook reads those files, materializes impact_reports, impact_evidence, test_recommendations, and verification_runs Delta tables under workspace.graphguard, and records metrics in the /Shared/graphguard MLflow experiment.

### Data provenance and responsible use

The demo reports are generated from the repository's synthetic graphguard/fixtures/demo-repo code and its local Entire Graph output. They contain source paths, symbol names, deterministic risk facts, and test names; they are not customer, company, credential, or personal data. Do not upload confidential repositories or include tokens in code, screenshots, prompts, checkpoints, or this document.

### Reproduce the live export

Generate a Databricks personal access token in the workspace and keep it only in the terminal session. Never commit or paste it into this repository.

~~~bash
python3 -m pip install -e "./graphguard[databricks]"
export DATABRICKS_HOST="https://dbc-ddd40b1f-5e3d.cloud.databricks.com"
export DATABRICKS_TOKEN="<personal-access-token>"
export DATABRICKS_CATALOG="workspace"
export DATABRICKS_SCHEMA="graphguard"
export DATABRICKS_VOLUME="input"

python3 -m graphguard.cli analyze charge --repo graphguard/fixtures/demo-repo
python3 -m graphguard.cli export-databricks
~~~

Then import graphguard/notebooks/databricks_export.py into the same Databricks workspace and run it from a Databricks notebook with available serverless compute. Verify the four Delta tables, the MLflow metrics, and the Volume file list. The resource provisioning and local staging path are verified; the final credentialed upload and notebook run must be demonstrated before claiming a complete Databricks integration.

## Known limitations and next steps

- Static analysis cannot fully resolve dynamic dispatch, reflection, or generated code; GraphGuard marks that evidence as partial and requires verification.
- Co-change evidence depends on locally available Git history.
- Databricks Free Edition is serverless and quota-limited. Preserve a screenshot or recording after a successful live export as a fallback demo asset.
- The final submission must reference a pushed final commit, genuine Entire Checkpoint links, final semantic-diff evidence, and a live Databricks result if entering the Databricks award category.
