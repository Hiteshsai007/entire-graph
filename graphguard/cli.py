"""GraphGuard CLI."""

import argparse
import sys
from pathlib import Path
from graphguard.runner import analyze_symbol

def main():
    parser = argparse.ArgumentParser(description="GraphGuard Risk Analyzer")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    analyze_parser = subparsers.add_parser("analyze")
    analyze_parser.add_argument("symbol", help="Symbol to analyze")
    analyze_parser.add_argument("--repo", default=".", help="Repository root path")
    analyze_parser.add_argument("--verify", action="store_true", help="Run verification tests")
    
    args = parser.parse_args()
    
    if args.command == "analyze":
        try:
            repo_path = str(Path(args.repo).resolve())
            report = analyze_symbol(repo_path, args.symbol, args.verify)
            print(report.render_text())
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
