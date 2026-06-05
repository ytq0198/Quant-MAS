from backend.services.backtests import get_backtest_summary
from backend.services.oos import get_oos_summary
from backend.services.risk import get_risk_summary


def test_backtest_summary_is_research_only_and_not_oos():
    summary = get_backtest_summary("demo-backtest")

    assert summary["id"] == "demo-backtest"
    assert summary["metric_family"] == "backtest.summary"
    assert summary["is_oos"] is False
    assert summary["research_only"] is True
    assert "not financial advice" in summary["disclaimer"].lower()


def test_oos_summary_returns_verified_baseline_windows():
    summary = get_oos_summary("EXP-20260602-008")

    assert summary["id"] == "EXP-20260602-008"
    assert summary["metric_family"] == "oos"
    assert summary["is_oos"] is True
    assert summary["sharpe"] == 0.586
    assert summary["window_count"] == 19
    assert summary["paper_grade"] is True


def test_risk_summary_requires_human_confirmation():
    summary = get_risk_summary("demo-risk")

    assert summary["id"] == "demo-risk"
    assert summary["status"] == "review_required"
    assert summary["live_trading_enabled"] is False
    assert summary["human_confirmation_required"] is True
    assert "audit log" in " ".join(summary["required_gates"]).lower()
