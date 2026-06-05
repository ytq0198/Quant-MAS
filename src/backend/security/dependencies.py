from __future__ import annotations

import os
from typing import Annotated, Callable

from fastapi import Depends, Header, HTTPException

from backend.security.api_keys import Principal, authenticate_api_key
from backend.security.roles import Role, has_required_role


def get_current_principal(
    x_quant_mas_key: Annotated[str | None, Header(alias="X-Quant-MAS-Key")] = None,
) -> Principal:
    """Return current caller principal from API key or open mode.

    从 API key 或 open mode 返回当前调用方身份。
    """
    principal = authenticate_api_key(
        x_quant_mas_key,
        configured_keys=os.getenv("QUANT_MAS_API_KEYS"),
        auth_mode=os.getenv("QUANT_MAS_AUTH_MODE", "open"),
    )
    if principal is None:
        raise HTTPException(status_code=401, detail="Missing or invalid Quant MAS API key.")
    return principal


def require_role(required_role: Role) -> Callable[[Principal], Principal]:
    """Create a FastAPI dependency requiring a role.

    创建要求指定角色的 FastAPI dependency。
    """

    def dependency(current: Annotated[Principal, Depends(get_current_principal)]) -> Principal:
        if not has_required_role(current.role, required_role):
            raise HTTPException(status_code=403, detail="Insufficient Quant MAS role.")
        return current

    return dependency
