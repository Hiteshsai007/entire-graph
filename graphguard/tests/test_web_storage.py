"""API persistence behavior for browser-initiated analyses."""

from graphguard.web import app as web_app


def test_analyze_api_saves_report(monkeypatch, tmp_path):
    class Report:
        def to_dict(self):
            return {"symbol": "charge"}

    report = Report()
    saved = []
    monkeypatch.setattr(web_app, "analyze_symbol", lambda repo, symbol: report)
    monkeypatch.setattr(web_app, "save_report", saved.append)

    response = web_app.analyze(web_app.AnalyzeRequest(repo=str(tmp_path), symbol="charge"))

    assert response == {"symbol": "charge"}
    assert saved == [report]
