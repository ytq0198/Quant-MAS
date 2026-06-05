from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


REQUIRED_DOCS = [
    "docs/v5_enterprise_overview.md",
    "docs/api_reference.md",
    "docs/security_model.md",
    "docs/metric_family_policy.md",
    "docs/demo_script.md",
    "docs/server_deployment.md",
    "docs/server_env.md",
    "docs/release_checklist.md",
]


def test_enterprise_docs_exist_and_are_bilingual():
    for relative_path in REQUIRED_DOCS:
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert " / " in text
        assert re.search(r"[\u4e00-\u9fff]", text)


def test_api_reference_contains_phase9_observability_routes():
    text = (ROOT / "docs/api_reference.md").read_text(encoding="utf-8")

    for route in [
        "/api/health",
        "/api/health/deep",
        "/api/metrics/summary",
        "/api/logs/recent",
        "/api/config/effective",
    ]:
        assert route in text


def test_enterprise_docs_do_not_contain_forbidden_promises():
    forbidden_terms = [
        "稳赚",
        "保本",
        "收益承诺",
        "实盘承诺",
        "guaranteed profit",
        "guaranteed return",
        "live order placement",
    ]

    combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in REQUIRED_DOCS).lower()

    for term in forbidden_terms:
        assert term.lower() not in combined
