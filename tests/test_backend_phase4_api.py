import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_database_status_endpoint_returns_optional_backends():
    client = TestClient(app)

    response = client.get("/api/database/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "optional"
    assert payload["default_backend"] == "local_files"


def test_deployment_status_endpoint_returns_artifacts():
    client = TestClient(app)

    response = client.get("/api/deployment/status")

    assert response.status_code == 200
    payload = response.json()
    assert "Dockerfile.backend" in payload["artifacts"]
    assert payload["safety"]["live_trading_enabled"] is False
