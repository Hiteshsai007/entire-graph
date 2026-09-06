"""Unrelated health check — no path to charge().

GraphGuard should not select test_unrelated as a recommended test for charge.
"""


def health() -> dict:
    """Health check endpoint. Has no path to charge()."""
    return {"status": "ok", "service": "payments"}
