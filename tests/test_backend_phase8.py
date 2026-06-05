from backend.services.graph import get_graph_relationships
from backend.services.rag import list_rag_documents, query_rag
from backend.services.storage_status import get_database_tables_status


def test_database_tables_status_is_optional_without_real_db(monkeypatch):
    monkeypatch.setenv("QUANT_MAS_STORAGE_MODE", "postgres")
    monkeypatch.delenv("POSTGRES_DSN", raising=False)

    payload = get_database_tables_status()

    assert payload["mode"] == "postgres"
    assert payload["status"] == "not_configured"
    assert payload["required_for_tests"] is False


def test_rag_documents_fallback_lists_research_docs():
    payload = list_rag_documents()

    assert payload["source"] == "fallback_documents"
    assert payload["documents"]
    assert any("research" in item["type"] for item in payload["documents"])


def test_rag_query_fallback_is_metric_safe():
    payload = query_rag("OOS baseline")

    assert payload["source"] == "fallback_rag"
    assert payload["query"] == "OOS baseline"
    assert payload["results"]
    assert "oos.*" in payload["safety_notes"][0]


def test_graph_relationships_are_optional_fixture():
    payload = get_graph_relationships()

    assert payload["source"] == "fallback_graph"
    assert payload["relationships"]
    assert payload["required_for_tests"] is False
