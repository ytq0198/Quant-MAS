import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_status_endpoint_returns_v5_payload():
    client = TestClient(app)

    response = client.get("/api/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["project"] == "Quant MAS"
    assert payload["version"] == "v5"
    assert payload["safety"]["live_trading"] is False
