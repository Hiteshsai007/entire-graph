"""Core runner that ties GraphGuard together."""

import subprocess
import sys
from graphguard.engine.models import AnalysisReport, VerifyOutcome
from graphguard.engine.normalize import normalize_impact
from graphguard.engine.risk import classify
from graphguard.engine.rank import rank_tests
from graphguard.engine.evidence import build_evidence
from graphguard.runner.graph_cli import GraphCLI

def run_impact(repo: str, symbol: str) -> tuple[dict, str]:
    """Run entire-graph impact and return parsed JSON and the raw CLI command."""
    result = GraphCLI(repo).impact(symbol)
    return result.data, result.command_text

def run_verify(repo: str, tests: list[str]) -> bool:
    """Run pytest on the given tests. Returns True if passed, False otherwise."""
    if not tests:
        return True
    
    # We run pytest on the specific tests inside the repo
    cmd = [sys.executable, "-m", "pytest"]
    
    # Instead of passing specific test nodes (which requires exact paths),
    # we just pass the test names using -k for the demo.
    k_arg = " or ".join(tests)
    cmd.extend(["-k", k_arg])
    
    result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    return result.returncode == 0

def analyze_symbol(repo: str, symbol: str, verify: bool = False) -> AnalysisReport:
    """Analyze a symbol end-to-end."""
    
    # 1. Run impact
    raw_data, cmd_str = run_impact(repo, symbol)
    
    # 2. Normalize
    facts = normalize_impact(raw_data, symbol)
    
    # 3. Classify risk
    tier, rule_id, reason = classify(facts)
    
    # 4. Rank tests
    ranked = rank_tests(facts, tier)
    
    # 5. Build evidence
    evidence = build_evidence(facts, tier, rule_id, reason, [cmd_str])
    
    report = AnalysisReport(
        symbol=symbol,
        repo=repo,
        tier=tier,
        rule_id=rule_id,
        reason=reason,
        ranked_tests=ranked,
        evidence=evidence,
        facts=facts
    )
    
    if verify:
        # Just a placeholder verify logic for the basic analyze.
        # In the demo, the verify script will do before/after.
        test_names = [t.test_name for t in ranked]
        passed = run_verify(repo, test_names)
        report.verification = VerifyOutcome(
            status="Clean" if passed else "Regression Detected",
            baseline_passed=passed
        )
        
    return report
