"""Databricks store — Phase 2 only. No-op if env missing."""

from __future__ import annotations

import os


def push_to_databricks():
    """Push local reports to Databricks Delta + MLflow.

    Requires DATABRICKS_HOST and DATABRICKS_TOKEN env vars.
    Phase 2 only — not implemented until after 13:30 IST.
    """
    host = os.environ.get("DATABRICKS_HOST")
    token = os.environ.get("DATABRICKS_TOKEN")
    if not host or not token:
        raise EnvironmentError(
            "DATABRICKS_HOST and DATABRICKS_TOKEN must be set. "
            "Databricks integration is Phase 2 only."
        )
    # Phase 2 implementation goes here
    raise NotImplementedError("Databricks push not yet implemented (Phase 2)")
