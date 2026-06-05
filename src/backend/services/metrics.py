from __future__ import annotations

from typing import Any


def get_metrics_summary() -> dict[str, Any]:
    """Return lightweight fallback metrics summary.

    返回轻量回退指标摘要。
    """
    return {
        "source": "fallback_metrics",
        "research_only": True,
        "live_trading_enabled": False,
        "counters": {
            "api_groups": 15,
            "protected_routes": 2,
            "fallback_safe_services": 10,
        },
        "gauges": {
            "oos_sharpe_baseline": 0.586,
            "oos_window_count": 19,
        },
        "notes": [
            "Prometheus/Grafana are not required for Phase 9.",
            "No live-trading metric is exposed.",
        ],
    }
