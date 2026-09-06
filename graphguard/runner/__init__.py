"""Core runner that ties GraphGuard together."""

import json
import subprocess
from pathlib import Path
from graphguard.engine.models import AnalysisReport, VerifyOutcome
from graphguard.engine.normalize import normalize_impact
from graphguard.engine.risk import classify
from graphguard.engine.rank import rank_tests
from graphguard.engine.evidence import build_evidence

def run_impact(repo: str, symbol: str) -> tuple[dict, str]:
    """Run entire-graph impact and return parsed JSON and the raw CLI command."""
    # Assuming entire-graph is in the PATH or we use the specific path for the buildathon
    eg_bin = "/Users/tarun.n/BTW/entire-graph/entire-graph"
    cmd = [eg_bin, "impact", "--repo", repo, "--symbol", symbol, "--depth", "2", "--format", "json"]
    cmd_str = " ".join(cmd)
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # We might get multiple JSON objects if the symbol is ambiguous, 
    # but for GraphGuard demo we assume unambiguous or we pick the first valid output.
    # The output might have a warning on stderr and JSON on stdout.
    
    if result.returncode != 0:
        # If it failed, try to parse what we have, otherwise raise
        try:
            return json.loads(result.stdout), cmd_str
        except json.JSONDecodeError:
            raise RuntimeError(f"entire-graph failed: {result.stderr}")
            
    try:
        # If there are multiple lines (ndjson), take the last one or the one that has "focus"
        lines = result.stdout.strip().split("\n")
        data = None
        for line in lines:
            try:
                parsed = json.loads(line)
                if "focus" in parsed:
                    data = parsed
                    break
            except:
                pass
        if data:
            return data, cmd_str
        return json.loads(result.stdout), cmd_str
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse entire-graph output: {e}\nSTDOUT: {result.stdout}")

def run_verify(repo: str, tests: list[str]) -> bool:
    """Run pytest on the given tests. Returns True if passed, False otherwise."""
    if not tests:
        return True
    
    # We run pytest on the specific tests inside the repo
    cmd = ["python3", "-m", "pytest"]
    
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
