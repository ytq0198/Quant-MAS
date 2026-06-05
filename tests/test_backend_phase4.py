from backend.services.database import get_database_status
from backend.services.deployment import get_deployment_status


def test_database_status_lists_optional_storage_backends():
    status = get_database_status()

    backend_names = {backend["name"] for backend in status["backends"]}
    assert {"local_files", "sqlite", "postgres", "pgvector", "neo4j"}.issubset(backend_names)
    assert status["mode"] == "optional"
    assert status["default_backend"] == "local_files"
    assert all("required_for_tests" in backend for backend in status["backends"])


def test_deployment_status_documents_local_and_server_paths():
    status = get_deployment_status()

    assert status["phase"] == "v4-phase-4"
    assert status["frontend"]["dev_url"] == "http://127.0.0.1:5173"
    assert status["backend"]["dev_url"] == "http://127.0.0.1:8000"
    assert status["safety"]["live_trading_enabled"] is False
    assert "docker-compose.yml" in status["artifacts"]
