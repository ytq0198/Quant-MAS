from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    """Supported lightweight RBAC roles.

    支持的轻量 RBAC 角色。
    """

    VIEWER = "viewer"
    RESEARCHER = "researcher"
    REVIEWER = "reviewer"
    ADMIN = "admin"


_ROLE_LEVELS: dict[Role, int] = {
    Role.VIEWER: 10,
    Role.RESEARCHER: 20,
    Role.REVIEWER: 30,
    Role.ADMIN: 40,
}


def parse_role(value: str | None) -> Role:
    """Parse a role string with viewer fallback.

    解析角色字符串，默认回退到 viewer。
    """
    if not value:
        return Role.VIEWER
    try:
        return Role(value.strip().lower())
    except ValueError:
        return Role.VIEWER


def has_required_role(actual: Role, required: Role) -> bool:
    """Return whether actual role satisfies required role.

    返回实际角色是否满足所需角色。
    """
    return _ROLE_LEVELS[actual] >= _ROLE_LEVELS[required]
