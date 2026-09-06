"""The single subprocess boundary for Entire Graph commands."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence


class GraphCLIError(RuntimeError):
    """Base error for an Entire Graph invocation."""


class GraphCLIUnavailableError(GraphCLIError):
    """Raised when no Entire Graph executable can be located."""


class GraphCLICommandError(GraphCLIError):
    """Raised when Entire Graph returns a non-zero status."""


class GraphCLIOutputError(GraphCLIError):
    """Raised when Entire Graph does not return the expected JSON object."""


@dataclass(frozen=True)
class GraphCommandResult:
    """Structured result with the exact command provenance."""

    data: dict
    argv: tuple[str, ...]
    cwd: str

    @property
    def command_text(self) -> str:
        return shlex.join(self.argv)


class GraphCLI:
    """Run Entire Graph commands without fabricating structural facts."""

    def __init__(
        self,
        repo: str,
        command: Sequence[str] | None = None,
        timeout: int = 120,
        run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
    ):
        self.repo = str(Path(repo).resolve())
        self.command = tuple(command) if command else self._default_command()
        self.timeout = timeout
        self._run = run
        self.last_result: GraphCommandResult | None = None

    @staticmethod
    def _default_command() -> tuple[str, ...]:
        override = os.environ.get("GRAPHGUARD_ENTIRE_GRAPH_BIN")
        if override:
            return tuple(shlex.split(override))

        if shutil.which("entire"):
            return ("entire", "graph")
        if shutil.which("entire-graph"):
            return ("entire-graph",)

        checkout_binary = Path(__file__).resolve().parents[2] / "entire-graph"
        if checkout_binary.is_file() and os.access(checkout_binary, os.X_OK):
            return (str(checkout_binary),)

        raise GraphCLIUnavailableError(
            "Could not find Entire Graph. Install the Entire Graph plugin, add "
            "`entire-graph` to PATH, or set GRAPHGUARD_ENTIRE_GRAPH_BIN."
        )

    def impact(self, symbol: str, depth: int = 2) -> GraphCommandResult:
        """Return an Entire Graph impact report as JSON with command provenance."""
        argv = (
            *self.command,
            "impact",
            "--repo",
            self.repo,
            "--symbol",
            symbol,
            "--depth",
            str(depth),
            "--format",
            "json",
        )
        try:
            completed = self._run(
                list(argv),
                cwd=self.repo,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as exc:
            raise GraphCLICommandError(
                f"Entire Graph impact timed out after {self.timeout}s for {symbol!r}."
            ) from exc

        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
            raise GraphCLICommandError(f"Entire Graph impact failed: {detail}")

        try:
            data = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise GraphCLIOutputError(
                f"Entire Graph impact returned invalid JSON: {exc.msg}"
            ) from exc
        if not isinstance(data, dict):
            raise GraphCLIOutputError("Entire Graph impact must return a JSON object.")

        self.last_result = GraphCommandResult(data=data, argv=argv, cwd=self.repo)
        return self.last_result
