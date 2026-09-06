"""Tests for process_order() — tests a direct caller of charge."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from payments.processor import process_order


def test_process_order_success():
    result = process_order("order-1", "cust-1", 99.99)
    assert result["status"] == "processed"
    assert result["order_id"] == "order-1"
    assert result["receipt"]["amount"] == 99.99


def test_process_order_missing_order_id():
    try:
        process_order("", "cust-1", 50.0)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "order" in str(e).lower()
