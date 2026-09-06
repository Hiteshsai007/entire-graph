GraphGuard PRD — BTW Buildathon 2026 Track E2

Product: GraphGuard — evidence-backed change intelligence
Event: Sunday 6 Sep 2026 · Scaler, Bengaluru
Track: E2 — Build with Graph Intelligence
Repo model: Fork entireio/entire-graph NOW → Entire mirror India → clone from the mirror
Product path: graphguard/ inside that fork (do not edit the Graph analyzer)
Databricks award: optional after 13:30 IST; must not be able to kill the Entire score
Code freeze: treat 15:00 IST as deadline until a mentor says 16:00 out loud

How to use this file





Humans: execute SETUP, then the clock.



Claude Code: paste this entire file as the first message in a fresh session after SETUP steps 17–18 (init-agents + new session) and Checkpoint 1.



0. One-sentence product

A reviewer decision layer: CHANGE → Entire Graph impact → deterministic risk tier → ranked tests → verify baseline/post → Prediction vs Outcome (including Contradicted).

If Entire Graph is removed, GraphGuard cannot classify risk.
If Databricks is removed, the local UI still works.

Not building: chat UI, D3/force-directed graph, Maven live tests, Model Serving, LLM risk tiers, a second GraphGuard GitHub repo, edits to Entire Graph internals.



1. SETUP PLAYBOOK (do every step, in order)

Do not write graphguard/ product code until the Done-when list is checked.

A. Fork now (GitHub)





Open https://github.com/entireio/entire-graph



Fork to the team GitHub account



Do not fork cli, external-agents, skills, or hackathon-demo

B. Entire CLI + login





entire version (install Entire CLI if missing)



Sign in (entire auth / entire login — use whatever this install prints)

C. Mirror India (do not skip)





entire repo mirror create



Select your fork (<you>/entire-graph), not upstream entireio/entire-graph



Select India



Wait until status is ready

D. Clone from the mirror, not github.com





entire repo clone <india-mirror-url>



cd into that clone — this is the only working copy you submit from

E. Enable Checkpoints before any agent product work





entire enable -y --agent claude-code (or your agent name)



entire status — Checkpoints must be on

F. Graph plugin





entire plugin install graph



entire graph version



entire graph capabilities --json



entire graph init-agents --repo .



Close the agent. Start a fresh session in this repo. Required after init-agents.



entire graph index --repo .

G. Checkpoint 1 (plan, before product code)





Commit this PRD notes + BUILDATHON.md stub



Capture Entire Checkpoint 1 (paste §9.1)



Ask a mentor: submit 3:00 or 4:00? If unanswered, assume 3:00.

Done when





GitHub fork of entireio/entire-graph exists



Entire India mirror is ready



cwd is the mirror clone of our fork



entire status clean / Checkpoints on



entire graph version prints



init-agents done and this is a new agent session



Checkpoint 1 linked



3:00 vs 4:00 confirmed or we assume 3:00

Do not skip the India mirror. Do not code in a github.com clone of upstream.

While coding (every risky edit)

entire graph diff --base HEAD --head ./graphguard
entire graph impact --repo . --symbol <the symbol you will change> --depth 2

Open the file:line. Graph is evidence, not an oracle. If Graph says 0 callers and source has a call, believe source, record the miss, continue.

Push after every checkpoint commit so you are not stuck at 14:55.

Secrets: never in git, prompts, checkpoints, screenshots, or BUILDATHON.md.



2. Clock (IST, Sunday 6 Sep 2026)

Setup incomplete?              → SETUP PLAYBOOK
Graph CLI working?             → no  → fix plugin
Phase 1 HIGH + Why? + verify?  → no  → stay on Phase 1
Before 11:40?                  → finish UI, Checkpoint 2
12:00–13:30?                   → Curveball only (graph before edit)
13:30–14:15 + Curveball done?  → Databricks Delta → MLflow → App
Else                           → Checkpoint 4 + BUILDATHON.md + submit







IST



Block



Action



Forbidden





NOW if setup incomplete



A Setup



Fork now, mirror India, clone mirror, enable, graph, Checkpoint 1



Product code before CP1





setup done → 11:40



B Phase 1



Fixture, live impact on charge, engine, UI or HTML, verify + Contradicted



Databricks, Maven, analyzer edits





11:40–12:00



C Freeze



Checkpoint 2 + push



New features





12:00



D Noon



Stop. Close session. Receive Curveball.



Coding





12:00–13:30



E Curveball



Fresh session. Graph impact on this fork then smallest fix + one test. CP3



Databricks





13:30–14:15



F Databricks



Only if gate green: Delta → MLflow → App last



Graph/tests inside Databricks





14:15–15:00



G Close



Self entire graph diff, CP4, BUILDATHON.md, submit form



New features





15:00–17:00



Demo



Keep runnable. Demo owner talks



Edits

Databricks gate (all required): Phase 1 green, Curveball done, clock before 14:15. Earliest start 13:30. Hard stop 14:15.

If UI is not started by 11:20, ship a generated report.html instead of FastAPI polish.



3. Architecture

Reviewer
   └─ local UI :8765  (or report.html)
         └─ graphguard CLI (analyze / explain / verify)
               ├─ engine: risk.py + rank.py + evidence.py + thresholds.yaml
               ├─ store/local.py  (JSON SoR for the demo)
               └─ runner/graph_cli.py  ──only process that shells──► entire graph CLI
                                                                          │
                                                                          ▼
                                                              fixtures/demo-repo

Optional after 13:30: laptop HTTPS push → Databricks Delta + MLflow
                      Databricks App = read-only clone of the four panels





Graph produces facts. GraphGuard produces a decision. Databricks keeps receipts.



Never invent callers/callees/co-change/tests. Never let an LLM pick a tier.



4. Layout (create exactly this inside the fork)

entire-graph/                          ← OUR FORK (India mirror clone)
  BUILDATHON.md
  graphguard/
    README.md
    pyproject.toml
    thresholds.yaml                    ← judges will open this
    cli.py
    engine/
      normalize.py
      risk.py
      rank.py
      evidence.py
      models.py
    runner/
      graph_cli.py                     ← only subprocess to `entire`
      verify.py
    store/
      local.py
      databricks.py                    ← Phase 2 only; no-op if env missing
    web/
      app.py
      static/index.html
      static/app.js
      static/styles.css
    fixtures/demo-repo/
      payments/api.py                  ← charge()
      payments/processor.py            ← process_order() calls charge
      payments/notify.py               ← notify_and_bill() calls process_order
      payments/dynamic.py              ← getattr dispatch (graph-blind)
      payments/unrelated.py            ← health()
      tests/test_charge.py
      tests/test_processor.py
      tests/test_unrelated.py
    testdata/                          ← frozen JSON for unit tests
    tests/
    data/                              ← gitignore contents except .gitkeep

Do not modify Entire Graph plugin/analyzer source.



5. Fixture (live demo target)

Python, fast pytest. Not Maven.





charge is public; process_order is a direct caller; notify_and_bill is depth-2.



dispatch uses getattr so Graph will miss it → Contradicted demo.



health / test_unrelated have no path → not selected.

git init the fixture with two commits so entire graph diff --base/--head works.
Index: entire graph index --repo graphguard/fixtures/demo-repo
Default analyze: --repo graphguard/fixtures/demo-repo --symbol charge

Planted verify flow:





Baseline pytest of the three tests (pass)



Break charge in a way that also breaks dispatch("charge", …)



Post-edit verify: Caught regression and/or Contradicted. Show both.



6. Graph CLI wrapper

Only runner/graph_cli.py may shell out to entire. Record exact argv + cwd on every call.

entire graph capabilities --json
entire graph index --repo <repo>
entire graph diff --base <base> --head <head> --repo <repo>
entire graph commit [REV] --repo <repo>
entire graph impact --repo <repo> --symbol <NAME> --depth 2
entire graph neighbors --repo <repo> --symbol <NAME> --relation CALLS --direction in
entire graph def <NAME> --repo <repo>
entire graph verify --repo <repo> --test "<CMD>" --record-baseline <path>
entire graph verify --repo <repo> --test "<CMD>" --pre-edit-baseline <path>

Prefer --json / --format json. Timeouts: 120s impact/index, 180s verify, 30s else.
If Graph omits a field, store []. Never fabricate.



7. Risk engine (graphguard/thresholds.yaml — copy verbatim)

order: [CRITICAL, HIGH, MEDIUM, LOW]

CRITICAL:
  - id: C1
    when: is_public AND direct_callers >= 3 AND reachable_tests < 2
    reason: "public symbol with ≥3 direct callers and <2 reachable tests"
  - id: C2
    when: is_public AND reachable_tests == 0 AND direct_callers >= 1
    reason: "public symbol with callers and zero reachable tests"

HIGH:
  - id: H1
    when: is_public AND direct_callers >= 1 AND reachable_tests < 3
    reason: "public API with callers and thin test reachability"
  - id: H2
    when: direct_callers >= 2 AND transitive_callers >= 1
    reason: "≥2 direct callers and ≥1 transitive caller (depth 2)"
  - id: H3
    when: cochange_files >= 5 AND reachable_tests < 3
    reason: "high co-change (≥5) with thin tests"

MEDIUM:
  - id: M1
    when: direct_callers >= 1
    reason: "at least one direct caller"
  - id: M2
    when: cochange_files >= 3
    reason: "historical co-change ≥3 files"
  - id: M3
    when: reachable_tests == 0
    reason: "no reachable tests found"

LOW:
  - id: L1
    when: else
    reason: "internal or well-covered, no elevated signals"

Evaluate all rules; highest tier wins. Demo: charge → HIGH via H1. health → LOW.
is_public: name does not start with _ and file is not under tests/.
Always show blind spots: reflection/getattr, generated code, config wiring, inventory-only languages.
Unit-test the engine on frozen testdata so tests work without entire.



8. Ranking, evidence, verify, UI

Rank tests (stable sort): direct test of changed symbol (100); test of a direct caller (60); test of any HIGH/CRITICAL symbol (40); co-change with test file (10); else not selected (no graph path). Each selected row needs a path like charge ←CALLS process_order ←TESTED_BY test_processor.

Why? tags only:







tag



when





graph_fact



CLI result with file:line and argv





derived



fired rule id from thresholds.yaml





historical



Graph's own co-change count

Templates only. No LLM prose. Drop ungrounded rows.

Verify default cmd:

python -m pytest tests/test_charge.py tests/test_processor.py tests/test_unrelated.py -q

Baseline then post-edit. Outcomes: Clean / Caught regression / Pre-existing / Contradicted. Never hide Contradicted. Not Verified until both verifies ran.

CLI: analyze explain verify serve push-dbx
UI: one screen, four panels, 127.0.0.1:8765. Buttons: Analyze, Run tests, Run scenario: break_charge, Run scenario: contradict_dynamic. No login, no chat, no canvas.



9. Phase 1 build order (commit after each)





Scaffold + thresholds.yaml + models



Fixture + two git commits + fixture pytest; entire graph index on the fixture



testdata JSON



normalize + risk + tests



rank + evidence + tests



graph_cli + live analyze on charge → HIGH



verify + scenarios including Contradicted



UI or report.html



BUILDATHON.md → Checkpoint 2 candidate. Stop features.

Phase 1 green:

cd graphguard
python -m pytest -q
python -m graphguard.cli analyze --repo fixtures/demo-repo --symbol charge
python -m graphguard.cli serve



10. Curveball (12:00, fresh session)

Before any edit:

entire graph diff --base HEAD --head .
entire graph impact --repo . --symbol classify --depth 2
entire graph impact --repo . --symbol rank_tests --depth 2

Save JSON to graphguard/data/pre-curveball-impact.json.
Smallest change in one of {risk.py, rank.py, evidence.py, thresholds.yaml, verify.py} + one pytest. Checkpoint 3.



11. Databricks (13:30–14:15 only)

Same local JSON → Unity Catalog tables: impact_reports, impact_evidence, test_recommendations, verification_runs.
MLflow experiment graphguard (tier, timing, grounding_ok, outcome).
App last; drop if not up in 30 minutes.
Env never committed. Missing env → typed error; product still runs.
Never run entire graph or tests on Databricks compute.



12. BUILDATHON.md (repo root)

Must include: one-sentence summary; Track E2; fork + India mirror + clone-from-mirror + enable + graph plugin; architecture; Graph findings (fixture + self + final) verified at file:line; Curveball; four Checkpoint links; run instructions; Databricks URLs or "not deployed"; limitations. Never invent SHAs or URLs.



13. Checkpoint texts

9.1 / Checkpoint 1 (paste now)

GraphGuard is a reviewer decision layer on Entire Graph. We forked entireio/entire-graph, mirrored it on Entire India, cloned from the mirror, enabled Checkpoints, installed the graph plugin. Facts only from entire graph. Deterministic thresholds.yaml. Tests ranked by graph path. Product in graphguard/ of this fork. Demo fixtures/demo-repo. Databricks is a late push-out. Curveball: one of {risk, rank, evidence}.

Checkpoint 2 (pre-noon)

What works: analyze/verify/UI/tests. Exact demo command. Fixture outcomes actually seen (including Contradicted yes/no). Databricks not started. Do not add features after this commit.

Checkpoint 3

Constraint card. Pre-edit graph findings. Module changed. Proving test. Phase 1 loop intact.

Checkpoint 4

Final SHA. entire graph diff of this fork. Test results. Databricks URLs or not deployed. Known limits.



14. Demo script (3 minutes)





Analyze charge → HIGH badge + Why? tags + ranked tests



Run tests → Prediction vs Outcome



Show Contradicted (getattr) honestly



Open thresholds.yaml



If Databricks is up: same report_id in Delta; if not, skip without apology



15. Roles







Role



Name



Job





Submitter



_____



Form + remotes pushed





Demo owner



_____



3-minute script, local UI





Databricks owner



_____



Optional; screenshot fallback



16. Kill list

Wrong repo · skip India mirror · work in a github.com clone · product code before Checkpoint 1 · chat UI · D3 graph · Maven · Databricks before 13:30 · LLM risk tiers · Model Serving · rewriting Entire Graph · second product GitHub repo · secrets in git



17. Claude: first actions now

You do not research alternatives. You do not propose a different product.





If SETUP checkboxes are empty → SETUP PLAYBOOK. Fork now. Mirror India. Clone from mirror. Stop after init-agents for a fresh session.



If Checkpoint 1 is missing → commit plan, human confirms checkpoint.



Then Phase 1 §9 step 1. Create graphguard/. No Databricks.



Commit after each Phase 1 step.



At 11:40 freeze for Checkpoint 2.

Do not outline a new plan. Execute the current clock block.