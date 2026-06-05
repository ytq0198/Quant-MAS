from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends

from backend.security.api_keys import Principal
from backend.security.dependencies import get_current_principal

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/me")
def read_auth_me(
    principal: Annotated[Principal, Depends(get_current_principal)],
) -> dict[str, Any]:
    """Return current authentication principal.

    返回当前认证身份。
    """
    return {
        "auth_mode": principal.auth_mode,
        "role": principal.role.value,
        "key_fingerprint": principal.key_fingerprint,
    }


@router.post("/validate-key")
def validate_key(
    principal: Annotated[Principal, Depends(get_current_principal)],
) -> dict[str, Any]:
    """Validate current API key and role.

    验证当前 API key 和角色。
    """
    return {
        "valid": True,
        "auth_mode": principal.auth_mode,
        "role": principal.role.value,
        "key_fingerprint": principal.key_fingerprint,
    }
