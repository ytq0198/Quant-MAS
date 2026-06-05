from __future__ import annotations

import os
from typing import Any


def get_database_tables_status() -> dict[str, Any]:
    """Return optional database table readiness.

    返回可选数据库表准备状态。
    """
    mode = os.getenv("QUANT_MAS_STORAGE_MODE", "local_files")
    postgres_dsn = os.getenv("POSTGRES_DSN", "")
    if mode == "postgres" and not postgres_dsn:
        status = "not_configured"
    elif mode == "postgres":
        status = "configured_not_connected"
    else:
        status = "local_files"
    return {
        "mode": mode,
        "status": status,
        "required_for_tests": False,
        "tables": [
            "experiments",
            "experiment_metrics",
            "backtest_runs",
            "oos_runs",
            "risk_reviews",
            "audit_logs",
            "paper_artifacts",
        ],
        "notes": "Database tables are optional; local artifact mode remains the default.",
    }
