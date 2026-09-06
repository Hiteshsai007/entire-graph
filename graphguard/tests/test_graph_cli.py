"""Tests for the portable Entire Graph subprocess boundary."""

from __future__ import annotations

import subprocess

import pytest

from graphguard.runner.graph_cli import GraphCLI, GraphCLICommandError, GraphCLIOutputError


def test_impact_records_exact_command_and_cwd(tmp_path):
    observed = {}

    def fake_run(argv, **kwargs):
        observed["argv"] = argv
        observed["kwargs"] = kwargs
        return subprocess.CompletedProcess(argv, 0, stdout='{"focus": {"name": "charge"}}', stderr="")

    result = GraphCLI(str(tmp_path), command=("entire", "graph"), run=fake_run).impact("charge")

    assert result.data["focus"]["name"] == "charge"
    assert result.argv == (
        "entire", "graph", "impact", "--repo", str(tmp_path), "--symbol", "charge",
        "--depth", "2", "--format", "json",
    )
    assert result.cwd == str(tmp_path)
    assert observed["argv"] == list(result.argv)
    assert observed["kwargs"]["cwd"] == str(tmp_path)


def test_impact_surfaces_graph_command_failure(tmp_path):
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 2, stdout="", stderr="symbol not found")

    client = GraphCLI(str(tmp_path), command=("entire", "graph"), run=fake_run)

    with pytest.raises(GraphCLICommandError, match="symbol not found"):
        client.impact("missing")


def test_impact_rejects_non_json_output(tmp_path):
    def fake_run(argv, **kwargs):
        return subprocess.CompletedProcess(argv, 0, stdout="not json", stderr="")

    client = GraphCLI(str(tmp_path), command=("entire", "graph"), run=fake_run)

    with pytest.raises(GraphCLIOutputError, match="invalid JSON"):
        client.impact("charge")
