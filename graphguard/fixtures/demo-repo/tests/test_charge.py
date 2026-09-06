"""Tests for charge() — direct test of the target symbol."""

import sys
import os

# Add demo-repo to path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from payments.api import charge


def test_charge_success():
    result = charge("cust-1", 50.0)
    assert result["status"] == "charged"
    assert result["amount"] == 50.0
    assert result["customer_id"] == "cust-1"


def test_charge_negative_amount():
    try:
        charge("cust-1", -10.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "positive" in str(e).lower()


def test_charge_empty_customer():
    try:
        charge("", 10.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "customer" in str(e).lower()
