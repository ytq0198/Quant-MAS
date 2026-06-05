import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_experiments_endpoint_is_fallback_safe(monkeypatch, tmp_path):
    monkeypatch.setenv("QUANT_MAS_ARTIFACT_ROOT", str(tmp_path))
    client = TestClient(app)

    response = client.get("/api/experiments")

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "fallback_baseline"
    assert payload["experiments"][0]["experiment_id"] == "EXP-20260602-008"


def test_paper_artifacts_endpoint_is_fallback_safe(monkeypatch, tmp_path):
    monkeypatch.setenv("QUANT_MAS_ARTIFACT_ROOT", str(tmp_path))
    client = TestClient(app)

    response = client.get("/api/artifacts/paper")

    assert response.status_code == 200
    assert response.json()["source"] == "fallback_empty"


def test_audit_logs_endpoint_is_fallback_safe(monkeypatch, tmp_path):
    monkeypatch.setenv("QUANT_MAS_ARTIFACT_ROOT", str(tmp_path))
    client = TestClient(app)

    response = client.get("/api/audit/logs")

    assert response.status_code == 200
    assert response.json()["source"] == "fallback_empty"
