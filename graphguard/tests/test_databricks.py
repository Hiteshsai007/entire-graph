"""Tests for the optional Databricks staging integration."""

from __future__ import annotations

import json

import pytest

from graphguard.store.databricks import (
    DatabricksConfig,
    DatabricksConfigurationError,
    DatabricksIntegrationError,
    push_to_databricks,
)


def test_config_requires_all_environment_values(monkeypatch):
    for name in (
        "DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_CATALOG",
        "DATABRICKS_SCHEMA", "DATABRICKS_VOLUME",
    ):
        monkeypatch.delenv(name, raising=False)

    with pytest.raises(DatabricksConfigurationError, match="DATABRICKS_HOST"):
        DatabricksConfig.from_env()


def test_push_uploads_only_graphguard_report_files(tmp_path):
    (tmp_path / "report-charge.json").write_text(json.dumps({"symbol": "charge"}))
    (tmp_path / "not-a-report.json").write_text("{}")
    calls = []

    class Files:
        def create_directory(self, path):
            calls.append(("directory", path))

        def upload_from(self, destination, source, overwrite):
            calls.append(("upload", destination, source, overwrite))

    class Client:
        files = Files()

    config = DatabricksConfig("https://example.cloud.databricks.com", "token", "main", "graphguard", "input")
    result = push_to_databricks(tmp_path, config=config, client=Client())

    assert result.destination == "/Volumes/main/graphguard/input/graphguard/reports"
    assert result.uploaded_files == ("/Volumes/main/graphguard/input/graphguard/reports/report-charge.json",)
    assert calls[0] == ("directory", result.destination)
    assert calls[1][0:2] == ("upload", result.uploaded_files[0])


def test_push_requires_local_report_artifacts(tmp_path):
    config = DatabricksConfig("https://example.cloud.databricks.com", "token", "main", "graphguard", "input")

    with pytest.raises(DatabricksIntegrationError, match="No GraphGuard report"):
        push_to_databricks(tmp_path, config=config, client=object())
