import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_health_and_metrics_endpoints_are_available():
    client = TestClient(app)

    health = client.get("/api/health")
    metrics = client.get("/api/metrics/summary")

    assert health.status_code == 200
    assert metrics.status_code == 200
    assert health.json()["live_trading_enabled"] is False


def test_effective_config_redacts_api_keys(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "server-secret:admin")
    client = TestClient(app)

    response = client.get("/api/config/effective")

    assert response.status_code == 200
    assert "server-secret" not in str(response.json())


def test_recent_logs_endpoint_handles_missing_logs(monkeypatch, tmp_path):
    monkeypatch.setenv("QUANT_MAS_LOG_ROOT", str(tmp_path))
    client = TestClient(app)

    response = client.get("/api/logs/recent")

    assert response.status_code == 200
    assert response.json()["events"] == []
