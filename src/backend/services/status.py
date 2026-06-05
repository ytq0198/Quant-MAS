from __future__ import annotations

from typing import Any


def get_status_payload() -> dict[str, Any]:
    """Return the public v4 system status payload.

    返回 v4 系统状态公开载荷。
    """
    return {
        "project": "Quant MAS",
        "version": "v4",
        "description": (
            "Full-stack multi-agent quantitative research platform with "
            "deterministic quant pipelines, audited OOS evaluation, and "
            "human-reviewed workflows."
        ),
        "baselines": {
            "tests": "361 passed",
            "oos_experiment": "EXP-20260602-008",
            "oos_sharpe": 0.586,
        },
        "safety": {
            "live_trading": False,
            "principles": [
                "LLM agents do not place live orders.",
                "All trading candidates require backtesting, risk checks, audit logs, and human confirmation.",
                "Only audited walk-forward OOS metrics can support paper-grade conclusions.",
                "simulation.*, training.*, population.*, and audit.* metrics must not be mixed with oos.* metrics.",
            ],
        },
        "ui_modules": [
            "Dashboard",
            "Agent Console",
            "Tool Console",
            "Memory/RAG Search",
            "Backtest View",
            "Walk-forward OOS View",
            "Audit / Human Review",
            "Paper Export",
        ],
        "api": {
            "status": "/api/status",
            "docs": "/docs",
        },
    }
