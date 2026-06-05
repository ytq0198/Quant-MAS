import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from backend.app import app


def test_database_tables_endpoint_is_fallback_safe():
    client = TestClient(app)

    response = client.get("/api/database/tables")

    assert response.status_code == 200
    assert response.json()["required_for_tests"] is False


def test_rag_documents_and_query_endpoints_are_fallback_safe():
    client = TestClient(app)

    docs_response = client.get("/api/rag/documents")
    query_response = client.get("/api/rag/query", params={"q": "OOS baseline"})

    assert docs_response.status_code == 200
    assert query_response.status_code == 200
    assert docs_response.json()["documents"]
    assert query_response.json()["results"]


def test_graph_relationships_endpoint_is_optional():
    client = TestClient(app)

    response = client.get("/api/graph/relationships")

    assert response.status_code == 200
    assert response.json()["required_for_tests"] is False
