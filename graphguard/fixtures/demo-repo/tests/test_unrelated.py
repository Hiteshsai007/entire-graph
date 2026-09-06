"""Tests for health() — unrelated, no path to charge()."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from payments.unrelated import health


def test_health():
    result = health()
    assert result["status"] == "ok"
    assert result["service"] == "payments"
