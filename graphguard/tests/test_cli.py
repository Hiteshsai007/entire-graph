"""Tests for GraphGuard's local persistence and Databricks export commands."""

from __future__ import annotations

import sys
from types import SimpleNamespace

from graphguard import cli


def test_analyze_saves_the_generated_report(monkeypatch, tmp_path, capsys):
    class Report:
        def render_text(self):
            return "HIGH risk"

    report = Report()
    saved_path = tmp_path / "report-charge.json"
    observed = {}

    def fake_analyze(repo, symbol, verify):
        observed.update(repo=repo, symbol=symbol, verify=verify)
        return report

    monkeypatch.setattr(cli, "analyze_symbol", fake_analyze)
    monkeypatch.setattr(cli, "save_report", lambda value: saved_path)
    monkeypatch.setattr(sys, "argv", ["graphguard", "analyze", "charge", "--repo", str(tmp_path)])

    cli.main()

    assert observed == {"repo": str(tmp_path.resolve()), "symbol": "charge", "verify": False}
    assert capsys.readouterr().out == f"HIGH risk\nSaved report: {saved_path}\n"


def test_export_databricks_uses_default_report_directory(monkeypatch, capsys):
    result = SimpleNamespace(
        destination="/Volumes/workspace/graphguard/input/graphguard/reports",
        uploaded_files=("report-charge.json",),
    )
    monkeypatch.setattr(cli, "push_to_databricks", lambda data_dir: result)
    monkeypatch.setattr(sys, "argv", ["graphguard", "export-databricks"])

    cli.main()

    assert capsys.readouterr().out == (
        "Uploaded 1 report(s) to /Volumes/workspace/graphguard/input/graphguard/reports\n"
    )
