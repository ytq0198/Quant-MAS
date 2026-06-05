from backend.services.config_status import get_effective_config
from backend.services.health import get_deep_health, get_health
from backend.services.logs import get_recent_logs
from backend.services.metrics import get_metrics_summary


def test_health_reports_research_api_without_live_trading():
    payload = get_health()

    assert payload["status"] == "ok"
    assert payload["live_trading_enabled"] is False


def test_deep_health_includes_optional_components():
    payload = get_deep_health()

    component_names = {item["name"] for item in payload["components"]}
    assert {"backend", "artifact_root", "database_optional", "rag_optional"}.issubset(component_names)


def test_metrics_summary_is_fallback_safe():
    payload = get_metrics_summary()

    assert payload["source"] == "fallback_metrics"
    assert payload["counters"]["protected_routes"] >= 2


def test_recent_logs_handles_missing_log_dir(tmp_path):
    payload = get_recent_logs(log_root=tmp_path)

    assert payload["source"] == "fallback_empty"
    assert payload["events"] == []


def test_effective_config_redacts_secrets(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "secret-value")
    monkeypatch.setenv("QUANT_MAS_API_KEYS", "raw-key:admin")

    payload = get_effective_config()
    raw = str(payload)

    assert "secret-value" not in raw
    assert "raw-key" not in raw
    assert payload["auth_mode"] in {"open", "api_key"}
    assert "env" in payload
    assert payload["env"] == payload["values"]
