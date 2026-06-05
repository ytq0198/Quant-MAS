from __future__ import annotations

import hashlib
from dataclasses import dataclass

from backend.security.roles import Role, parse_role


@dataclass(frozen=True)
class Principal:
    """Authenticated caller metadata.

    已认证调用方元数据。
    """

    role: Role
    auth_mode: str
    key_fingerprint: str | None = None


def parse_api_keys(configured_keys: str | None) -> dict[str, Role]:
    """Parse QUANT_MAS_API_KEYS style key-role config.

    解析 QUANT_MAS_API_KEYS 风格的 key-role 配置。
    """
    mapping: dict[str, Role] = {}
    for item in (configured_keys or "").split(","):
        if not item.strip() or ":" not in item:
            continue
        key, role = item.split(":", 1)
        key = key.strip()
        if key:
            mapping[key] = parse_role(role)
    return mapping


def fingerprint_api_key(api_key: str) -> str:
    """Return a safe API key fingerprint.

    返回安全的 API key 指纹。
    """
    digest = hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:12]
    return f"sha256:{digest}"


def authenticate_api_key(
    api_key: str | None,
    *,
    configured_keys: str | None,
    auth_mode: str | None,
) -> Principal | None:
    """Authenticate an API key or return open-mode admin principal.

    认证 API key，或返回 open mode 的 admin principal。
    """
    mode = (auth_mode or "open").strip().lower()
    if mode == "open":
        return Principal(role=Role.ADMIN, auth_mode="open", key_fingerprint=None)

    mapping = parse_api_keys(configured_keys)
    if not api_key or api_key not in mapping:
        return None
    return Principal(
        role=mapping[api_key],
        auth_mode="api_key",
        key_fingerprint=fingerprint_api_key(api_key),
    )
