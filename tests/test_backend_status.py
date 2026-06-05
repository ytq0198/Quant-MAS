from backend.services.status import get_status_payload


def test_status_payload_exposes_v5_baseline_and_safety_boundary():
    payload = get_status_payload()

    assert payload["project"] == "Quant MAS"
    assert payload["version"] == "v5"
    assert payload["baselines"]["tests"] == "361 passed"
    assert payload["baselines"]["oos_experiment"] == "EXP-20260602-008"
    assert payload["baselines"]["oos_sharpe"] == 0.586
    assert payload["safety"]["live_trading"] is False
    assert "LLM agents do not place live orders." in payload["safety"]["principles"]
    assert "Dashboard" in payload["ui_modules"]
    assert "Observability" in payload["ui_modules"]
