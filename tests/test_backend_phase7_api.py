import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_review_queue_and_jobs_are_readable_in_open_mode(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "open")
    client = TestClient(app)

    review_response = client.get("/api/review/queue")
    jobs_response = client.get("/api/jobs")

    assert review_response.status_code == 200
    assert jobs_response.status_code == 200
    assert review_response.json()["reviews"]
    assert jobs_response.json()["jobs"]


def test_review_decision_requires_reviewer_in_api_key_mode(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_AUTH_MODE", "api_key")
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "viewer-secret:viewer,reviewer-secret:reviewer")
    client = TestClient(app)

    denied = client.post("/api/review/review-demo-001/approve", headers={"X-Quant-MAS-Key": "viewer-secret"})
    allowed = client.post("/api/review/review-demo-001/approve", headers={"X-Quant-MAS-Key": "reviewer-secret"})

    assert denied.status_code == 403
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "approved"


def test_job_detail_endpoint_returns_fallback_job():
    client = TestClient(app)

    response = client.get("/api/jobs/job-demo-001")

    assert response.status_code == 200
    assert response.json()["job"]["job_id"] == "job-demo-001"
