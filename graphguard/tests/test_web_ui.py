"""Regression tests for the GraphGuard browser UI contract."""

from pathlib import Path


INDEX_HTML = (
    Path(__file__).resolve().parents[1] / "web" / "static" / "index.html"
)


def test_blank_repository_path_shows_validation_error() -> None:
    page = INDEX_HTML.read_text()

    assert "const repo = document.getElementById('repo').value.trim();" in page
    assert "if (!repo) {\n                errorEl.innerText = 'Repository path is required.';" in page
    assert "errorEl.style.display = 'block';" in page
