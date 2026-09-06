"""GraphGuard CLI — analyze / explain / verify / serve / push-dbx."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="graphguard",
        description="Evidence-backed change intelligence powered by Entire Graph",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # analyze
    p_analyze = sub.add_parser("analyze", help="Analyze a symbol for change risk")
    p_analyze.add_argument("--repo", required=True, help="Path to the target repo")
    p_analyze.add_argument("--symbol", required=True, help="Symbol name to analyze")
    p_analyze.add_argument("--depth", type=int, default=2, help="Transitive depth")
    p_analyze.add_argument("--json", action="store_true", help="JSON output")

    # explain
    p_explain = sub.add_parser("explain", help="Show evidence for a risk classification")
    p_explain.add_argument("--repo", required=True)
    p_explain.add_argument("--symbol", required=True)

    # verify
    p_verify = sub.add_parser("verify", help="Run baseline + post-edit verification")
    p_verify.add_argument("--repo", required=True)
    p_verify.add_argument("--symbol", required=True)
    p_verify.add_argument("--test-cmd", default=None, help="Override test command")
    p_verify.add_argument("--scenario", default=None,
                          choices=["break_charge", "contradict_dynamic"],
                          help="Run a built-in scenario")

    # serve
    p_serve = sub.add_parser("serve", help="Start local UI on :8765")
    p_serve.add_argument("--port", type=int, default=8765)
    p_serve.add_argument("--host", default="127.0.0.1")

    # push-dbx
    p_push = sub.add_parser("push-dbx", help="Push results to Databricks (Phase 2)")

    args = parser.parse_args()

    if args.command == "analyze":
        from graphguard.runner.graph_cli import GraphCLI
        from graphguard.engine.normalize import normalize_impact
        from graphguard.engine.risk import classify
        from graphguard.engine.rank import rank_tests
        from graphguard.engine.evidence import build_evidence
        from graphguard.engine.models import AnalysisReport
        from graphguard.store.local import save_report
        import json

        graph = GraphCLI(repo=args.repo)
        raw_impact = graph.impact(symbol=args.symbol, depth=args.depth)
        facts = normalize_impact(raw_impact, symbol=args.symbol)
        tier, rule_id, reason = classify(facts)
        ranked = rank_tests(facts, tier)
        evidence = build_evidence(facts, tier, rule_id, reason, graph.last_calls())
        report = AnalysisReport(
            symbol=args.symbol,
            repo=args.repo,
            tier=tier,
            rule_id=rule_id,
            reason=reason,
            ranked_tests=ranked,
            evidence=evidence,
            facts=facts,
        )
        save_report(report)
        if args.json:
            print(json.dumps(report.to_dict(), indent=2))
        else:
            print(report.render_text())

    elif args.command == "explain":
        from graphguard.store.local import load_latest_report
        report = load_latest_report(args.symbol)
        if report is None:
            print(f"No report found for {args.symbol}. Run analyze first.", file=sys.stderr)
            sys.exit(1)
        print(report.render_evidence_text())

    elif args.command == "verify":
        from graphguard.runner.verify import run_verify
        result = run_verify(
            repo=args.repo,
            symbol=args.symbol,
            test_cmd=args.test_cmd,
            scenario=args.scenario,
        )
        print(result.render_text())

    elif args.command == "serve":
        from graphguard.web.app import create_app
        import uvicorn
        app = create_app()
        print(f"GraphGuard UI → http://{args.host}:{args.port}")
        uvicorn.run(app, host=args.host, port=args.port)

    elif args.command == "push-dbx":
        try:
            from graphguard.store.databricks import push_to_databricks
            push_to_databricks()
        except ImportError:
            print("Databricks dependencies not installed. Install with: pip install -e '.[databricks]'",
                  file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Databricks push failed: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
