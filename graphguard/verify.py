"""Stateful verification logic for GraphGuard.

Baseline tests -> Wait for edit/Perform edit -> Post-edit tests -> Result
"""

import subprocess
import time
from typing import Callable
from graphguard.engine.models import RankedTest, VerifyOutcome

def verify_symbol_changes(repo: str, tests: list[RankedTest], edit_callback: Callable[[], None]) -> VerifyOutcome:
    """Run baseline tests, trigger edit, run post-edit tests, compute outcome."""
    
    test_names = [t.test_name for t in tests]
    
    if not test_names:
        return VerifyOutcome(status="No tests to run")
        
    cmd = ["python3", "-m", "pytest", "-v"]
    k_arg = " or ".join(test_names)
    cmd.extend(["-k", k_arg])
    
    print(f"Running baseline tests: {k_arg}")
    baseline_result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    baseline_passed = baseline_result.returncode == 0
    
    print("Applying edit...")
    edit_callback()
    
    print("Running post-edit tests...")
    post_edit_result = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
    post_edit_passed = post_edit_result.returncode == 0
    
    if not baseline_passed:
        status = "Pre-existing"
        detail = "Tests failed before edits were made."
    elif baseline_passed and post_edit_passed:
        status = "Contradicted"
        detail = "Tests passed after edit. Graph analysis might have blind spots (e.g., dynamic dispatch)."
    else:
        status = "Caught regression"
        detail = "Tests caught the breaking change!"
        
    return VerifyOutcome(
        status=status,
        baseline_passed=baseline_passed,
        post_edit_passed=post_edit_passed,
        baseline_output=baseline_result.stdout,
        post_edit_output=post_edit_result.stdout,
        detail=detail
    )
