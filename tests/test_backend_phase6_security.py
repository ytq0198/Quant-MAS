import json

from backend.security.api_keys import authenticate_api_key, fingerprint_api_key, parse_api_keys
from backend.security.audit import append_audit_event
from backend.security.roles import Role, has_required_role


def test_parse_api_keys_maps_keys_to_roles_without_exposing_secret():
    mapping = parse_api_keys("viewer-secret:viewer,research-secret:researcher")

    assert mapping["viewer-secret"] == Role.VIEWER
    assert mapping["research-secret"] == Role.RESEARCHER


def test_authenticate_api_key_returns_role_and_fingerprint():
    principal = authenticate_api_key(
        "research-secret",
        configured_keys="research-secret:researcher",
        auth_mode="api_key",
    )

    assert principal.role == Role.RESEARCHER
    assert principal.key_fingerprint == fingerprint_api_key("research-secret")
    assert "research-secret" not in principal.key_fingerprint


def test_open_mode_returns_local_admin_principal():
    principal = authenticate_api_key(None, configured_keys="", auth_mode="open")

    assert principal.role == Role.ADMIN
    assert principal.auth_mode == "open"


def test_role_hierarchy_allows_researcher_for_viewer_but_not_reviewer():
    assert has_required_role(Role.RESEARCHER, Role.VIEWER) is True
    assert has_required_role(Role.RESEARCHER, Role.RESEARCHER) is True
    assert has_required_role(Role.RESEARCHER, Role.REVIEWER) is False


def test_append_audit_event_writes_jsonl_without_raw_key(tmp_path):
    audit_path = tmp_path / "backend_audit.jsonl"

    append_audit_event(
        audit_path,
        {
            "event_type": "api.request",
            "path": "/api/agents/run",
            "key_fingerprint": fingerprint_api_key("raw-secret"),
        },
    )

    raw = audit_path.read_text(encoding="utf-8")
    event = json.loads(raw)
    assert event["event_type"] == "api.request"
    assert "raw-secret" not in raw
