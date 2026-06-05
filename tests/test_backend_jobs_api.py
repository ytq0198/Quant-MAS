import time

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_create_backtest_job_in_open_mode(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "open")
    client = TestClient(app)

    response = client.post(
        "/api/jobs",
        json={
            "type": "backtest",
            "params": {"experiment_name": "pytest_ui_backtest"},
            "summary": "pytest backtest job",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["source"] == "job_store"
    job_id = payload["job"]["job_id"]
    assert job_id.startswith("job-")


def test_job_lifecycle_reaches_terminal_state(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "open")
    client = TestClient(app)

    created = client.post(
        "/api/jobs",
        json={"type": "paper_export", "params": {}, "summary": "pytest export"},
    )
    job_id = created.json()["job"]["job_id"]

    terminal = {"completed", "failed"}
    status = "queued"
    for _ in range(40):
        detail = client.get(f"/api/jobs/{job_id}").json()
        status = detail["job"]["status"]
        if status in terminal:
            break
        time.sleep(0.05)

    assert status in terminal
    events = client.get(f"/api/jobs/{job_id}/events").json()
    assert events["events"]


def test_create_job_requires_researcher_in_api_key_mode(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "api_key")
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "viewer-secret:viewer,researcher-secret:researcher")
    client = TestClient(app)

    denied = client.post(
        "/api/jobs",
        json={"type": "backtest", "params": {}},
        headers={"X-Quant-MAS-Key": "viewer-secret"},
    )
    allowed = client.post(
        "/api/jobs",
        json={"type": "backtest", "params": {}},
        headers={"X-Quant-MAS-Key": "researcher-secret"},
    )

    assert denied.status_code == 403
    assert allowed.status_code == 200


def test_paper_export_endpoint_queues_job(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "open")
    client = TestClient(app)

    response = client.post("/api/artifacts/export", json={})

    assert response.status_code == 200
    assert response.json()["job"]["type"] == "paper_export"
