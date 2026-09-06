"""End-to-end demo script for verification."""

import sys
from pathlib import Path
from graphguard.runner import analyze_symbol
from graphguard.verify import verify_symbol_changes

def break_charge():
    """Simulate a developer breaking the charge method signature."""
    repo = Path(__file__).parent / "fixtures" / "demo-repo"
    api_file = repo / "payments" / "api.py"
    
    with open(api_file) as f:
        content = f.read()
        
    # Introduce a breaking change: rename 'amount' to 'amount_cents'
    content = content.replace("amount: float", "amount_cents: int")
    content = content.replace("if amount <= 0:", "if amount_cents <= 0:")
    content = content.replace("return True", "return amount_cents > 0")
    
    with open(api_file, "w") as f:
        f.write(content)

def restore_charge():
    """Restore the charge method signature."""
    repo = Path(__file__).parent / "fixtures" / "demo-repo"
    api_file = repo / "payments" / "api.py"
    
    with open(api_file) as f:
        content = f.read()
        
    content = content.replace("amount_cents: int", "amount: float")
    content = content.replace("if amount_cents <= 0:", "if amount <= 0:")
    content = content.replace("return amount_cents > 0", "return True")
    
    with open(api_file, "w") as f:
        f.write(content)

def main():
    repo_path = str((Path(__file__).parent / "fixtures" / "demo-repo").resolve())
    
    print("Running GraphGuard analysis on 'charge'...")
    report = analyze_symbol(repo_path, "charge")
    print(report.render_text())
    
    print("\n--- Starting Verification Demo ---")
    
    # Ensure clean state
    restore_charge()
    
    outcome = verify_symbol_changes(
        repo=repo_path,
        tests=report.ranked_tests,
        edit_callback=break_charge
    )
    
    report.verification = outcome
    print("\n" + report.verification.render_text())
    
    # Restore after demo
    restore_charge()

if __name__ == "__main__":
    main()
