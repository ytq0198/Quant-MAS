from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def list_review_queue() -> dict[str, Any]:
    """Return fallback human review queue.

    返回回退人工审查队列。
    """
    return {"source": "fallback_review_queue", "reviews": [_fallback_review_item()]}


def get_review_detail(review_id: str) -> dict[str, Any]:
    """Return one fallback review item.

    返回单个回退审查项。
    """
    item = _fallback_review_item()
    if review_id != item["review_id"]:
        return {"source": "fallback_review_queue", "review": None, "message": "Review item not found."}
    return {"source": "fallback_review_queue", "review": item}


def approve_review(review_id: str, reviewer: str) -> dict[str, Any]:
    """Approve a review item without enabling live trading.

    批准审查项，但不启用实盘交易。
    """
    return _decision_payload(review_id, reviewer, "approved")


def reject_review(review_id: str, reviewer: str, reason: str = "") -> dict[str, Any]:
    """Reject a review item with an optional reason.

    拒绝审查项，可附带原因。
    """
    payload = _decision_payload(review_id, reviewer, "rejected")
    payload["reason"] = reason
    payload["audit_event"]["reason"] = reason
    return payload


def _fallback_review_item() -> dict[str, Any]:
    return {
        "review_id": "review-demo-001",
        "experiment_id": "EXP-20260602-008",
        "candidate_type": "paper_claim",
        "status": "pending",
        "metric_family": "oos",
        "human_confirmation_required": True,
        "required_gates": ["backtest", "risk_check", "audit_log", "human_confirmation"],
        "created_at": "2026-06-05T00:00:00Z",
        "summary": "Review OOS baseline claim before paper-grade presentation.",
        "live_trading_enabled": False,
    }


def _decision_payload(review_id: str, reviewer: str, status: str) -> dict[str, Any]:
    event_type = f"review.{status}"
    return {
        "review_id": review_id,
        "status": status,
        "reviewer": reviewer,
        "live_trading_enabled": False,
        "decided_at": datetime.now(UTC).isoformat(),
        "audit_event": {
            "event_type": event_type,
            "review_id": review_id,
            "reviewer": reviewer,
            "status": status,
            "live_trading_enabled": False,
        },
    }
