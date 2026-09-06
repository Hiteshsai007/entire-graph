"""GraphGuard CLI."""

import argparse
import sys
from pathlib import Path
from graphguard.runner import analyze_symbol
from graphguard.store.databricks import push_to_databricks
from graphguard.store.local import save_report

def main():
    parser = argparse.ArgumentParser(description="GraphGuard Risk Analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("symbol", help="Symbol to analyze")
    analyze_parser.add_argument("--repo", default=".", help="Repository root path")
    analyze_parser.add_argument("--verify", action="store_true", help="Run verification tests")

    export_parser = subparsers.add_parser(
        "export-databricks",
        help="Upload locally saved report JSON files to the configured Databricks volume",
    )
    export_parser.add_argument(
        "--data-dir",
        default=None,
        help="Directory containing report-*.json files (defaults to graphguard/data)",
    )
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        try:
            repo_path = str(Path(args.repo).resolve())
            report = analyze_symbol(repo_path, args.symbol, args.verify)
            print(report.render_text())
            print(f"Saved report: {save_report(report)}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if args.command == "export-databricks":
        try:
            result = push_to_databricks(args.data_dir)
            print(f"Uploaded {len(result.uploaded_files)} report(s) to {result.destination}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
