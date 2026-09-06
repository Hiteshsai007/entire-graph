"""Graph CLI wrapper — the ONLY place that shells out to `entire`.

Records exact argv and cwd for every call. Prefers JSON output.
Respects PRD timeouts: 120s impact/index, 180s verify, 30s else.
Never fabricates missing graph fields.
"""

from __future__ import annotations


class GraphCLI:
    """Wrapper around entire graph CLI."""

    def __init__(self, repo: str):
        self.repo = repo
        raise NotImplementedError("GraphCLI — Phase 1 Step 5")
