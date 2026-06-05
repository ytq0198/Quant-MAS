from __future__ import annotations

import os
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.security.api_keys import Principal
from backend.security.audit import append_audit_event
from backend.security.dependencies import require_role
from backend.security.roles import Role
from backend.services.review import approve_review, get_review_detail, list_review_queue, reject_review

router = APIRouter(prefix="/api/review", tags=["review"])


class RejectReviewRequest(BaseModel):
    reason: str = ""


@router.get("/queue")
def read_review_queue() -> dict[str, Any]:
    """Return human review queue.

    返回人工审查队列。
    """
    return list_review_queue()


@router.get("/{review_id}")
def read_review_detail(review_id: str) -> dict[str, Any]:
    """Return one human review item.

    返回单个人工审查项。
    """
    return get_review_detail(review_id)


@router.post("/{review_id}/approve")
def approve_review_item(
    review_id: str,
    principal: Annotated[Principal, Depends(require_role(Role.REVIEWER))],
) -> dict[str, Any]:
    """Approve one review item.

    批准单个审查项。
    """
    payload = approve_review(review_id, reviewer=principal.role.value)
    _write_review_audit(payload["audit_event"], principal)
    return payload


@router.post("/{review_id}/reject")
def reject_review_item(
    review_id: str,
    request: RejectReviewRequest,
    principal: Annotated[Principal, Depends(require_role(Role.REVIEWER))],
) -> dict[str, Any]:
    """Reject one review item.

    拒绝单个审查项。
    """
    payload = reject_review(review_id, reviewer=principal.role.value, reason=request.reason)
    _write_review_audit(payload["audit_event"], principal)
    return payload


def _write_review_audit(event: dict[str, Any], principal: Principal) -> None:
    audit_path = os.getenv("QUANT_MAS_AUDIT_WRITE_PATH")
    if not audit_path:
        return
    append_audit_event(
        audit_path,
        {
            **event,
            "role": principal.role.value,
            "key_fingerprint": principal.key_fingerprint,
        },
    )
