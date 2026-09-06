"""Tests for portable stateful verification."""

from __future__ import annotations

import subprocess
import sys

from graphguard.engine.models import RankedTest
from graphguard.runner import run_verify
from graphguard.verify import verify_symbol_changes


def test_verify_uses_the_active_python_interpreter(monkeypatch, tmp_path):
    commands = []
    outcomes = iter([0, 1])

    def fake_run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, next(outcomes), stdout="output", stderr="")

    monkeypatch.setattr("graphguard.verify.subprocess.run", fake_run)

    outcome = verify_symbol_changes(
        str(tmp_path),
        [RankedTest("test_charge", 100, "direct graph caller", "test_charge --CALLS--> charge")],
        lambda: None,
    )

    assert outcome.status == "Caught regression"
    assert commands == [
        [sys.executable, "-m", "pytest", "-v", "-k", "test_charge"],
        [sys.executable, "-m", "pytest", "-v", "-k", "test_charge"],
    ]


def test_runner_verify_uses_the_active_python_interpreter(monkeypatch, tmp_path):
    commands = []

    def fake_run(command, **kwargs):
        commands.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("graphguard.runner.subprocess.run", fake_run)

    assert run_verify(str(tmp_path), ["test_charge"])
    assert commands == [[sys.executable, "-m", "pytest", "-k", "test_charge"]]
