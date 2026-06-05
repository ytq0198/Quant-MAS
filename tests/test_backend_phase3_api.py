import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_backtest_endpoint_returns_summary_payload():
    client = TestClient(app)

    response = client.get("/api/backtests/demo-backtest")

    assert response.status_code == 200
    assert response.json()["metric_family"] == "backtest.summary"


def test_oos_endpoint_returns_paper_grade_baseline_payload():
    client = TestClient(app)

    response = client.get("/api/oos/EXP-20260602-008")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_oos"] is True
    assert payload["sharpe"] == 0.586


def test_risk_endpoint_returns_review_required_payload():
    client = TestClient(app)

    response = client.get("/api/risk/demo-risk")

    assert response.status_code == 200
    assert response.json()["human_confirmation_required"] is True
