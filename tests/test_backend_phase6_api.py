import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_auth_me_reports_open_mode_by_default(monkeypatch):
    monkeypatch.delenv("QUANT_MAS_AUTH_MODE", raising=False)
    monkeypatch.delenv("QUANT_MAS_API_KEYS", raising=False)
    client = TestClient(app)

    response = client.get("/api/auth/me")

    assert response.status_code == 200
    payload = response.json()
    assert payload["auth_mode"] == "open"
    assert payload["role"] == "admin"


def test_agent_run_requires_researcher_in_api_key_mode(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "api_key")
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "viewer-secret:viewer,research-secret:researcher")
    client = TestClient(app)

    missing = client.post("/api/agents/run", json={"agent": "ResearchAgent", "task": "test"})
    denied = client.post(
        "/api/agents/run",
        headers={"X-Quant-MAS-Key": "viewer-secret"},
        json={"agent": "ResearchAgent", "task": "test"},
    )
    allowed = client.post(
        "/api/agents/run",
        headers={"X-Quant-MAS-Key": "research-secret"},
        json={"agent": "ResearchAgent", "task": "test"},
    )

    assert missing.status_code == 401
    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["live_trading_enabled"] is False


def test_audit_logs_require_reviewer_in_api_key_mode(monkeypatch, tmp_path):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "api_key")
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "viewer-secret:viewer,reviewer-secret:reviewer")
    monkeypatch.setenv("QUANT_MAS_ARTIFACT_ROOT", str(tmp_path))
    client = TestClient(app)

    denied = client.get("/api/audit/logs", headers={"X-Quant-MAS-Key": "viewer-secret"})
    allowed = client.get("/api/audit/logs", headers={"X-Quant-MAS-Key": "reviewer-secret"})

    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_auth_validate_key_returns_role(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "api_key")
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "admin-secret:admin")
    client = TestClient(app)

    response = client.post("/api/auth/validate-key", headers={"X-Quant-MAS-Key": "admin-secret"})

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_agent_run_writes_audit_event_without_raw_key(monkeypatch, tmp_path):
    audit_path = tmp_path / "backend_audit.jsonl"
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "api_key")
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "research-secret:researcher")
    monkeypatch.setenv("QUANT_MAS_AUDIT_WRITE_PATH", str(audit_path))
    client = TestClient(app)

    response = client.post(
        "/api/agents/run",
        headers={"X-Quant-MAS-Key": "research-secret"},
        json={"agent": "ResearchAgent", "task": "Summarize OOS baseline"},
    )

    assert response.status_code == 200
    raw = audit_path.read_text(encoding="utf-8")
    assert "agent.run" in raw
    assert "ResearchAgent" in raw
    assert "research-secret" not in raw
