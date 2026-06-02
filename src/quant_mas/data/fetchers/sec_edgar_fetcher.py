"""SEC EDGAR JSON fetcher."""

from __future__ import annotations

import json
import urllib.request

from quant_mas.data.fetchers.base import resolve_env_value


def resolve_sec_edgar_user_agent(explicit: str | None = None) -> str:
    user_agent = resolve_env_value(
        explicit,
        "SEC_EDGAR_USER_AGENT",
        service_name="SEC EDGAR",
        cli_hint="--user-agent",
    )
    if "@" not in user_agent:
        raise ValueError(
            "SEC_EDGAR_USER_AGENT must include contact email, e.g. "
            "`YourName your@email.com`."
        )
    return user_agent


class SECEDGARFetcher:
    """Fetch SEC EDGAR company submissions and facts as parsed JSON."""

    def __init__(
        self,
        *,
        user_agent: str | None = None,
        request_timeout_seconds: float = 60.0,
    ) -> None:
        self.user_agent = resolve_sec_edgar_user_agent(user_agent)
        self.request_timeout_seconds = request_timeout_seconds

    def fetch_submissions(self, cik: str) -> dict:
        normalized = _normalize_cik(cik)
        url = f"https://data.sec.gov/submissions/CIK{normalized}.json"
        return self._get_json(url)

    def fetch_company_facts(self, cik: str) -> dict:
        normalized = _normalize_cik(cik)
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{normalized}.json"
        return self._get_json(url)

    def _get_json(self, url: str) -> dict:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": self.user_agent, "Accept": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.request_timeout_seconds) as response:
            return json.loads(response.read().decode("utf-8"))


def _normalize_cik(cik: str) -> str:
    text = str(cik).strip().lstrip("0")
    if not text.isdigit():
        raise ValueError("CIK must contain digits")
    return text.zfill(10)
