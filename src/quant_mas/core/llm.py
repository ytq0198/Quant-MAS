"""LLM client boundary."""

from __future__ import annotations

import json
import os
import warnings
from abc import ABC, abstractmethod
from collections.abc import Sequence
from urllib import error, request

from quant_mas.core.message import Message
from quant_mas.utils.env import load_repo_dotenv


class LLMClient(ABC):
    """Abstract chat-completion client."""

    @abstractmethod
    def complete(self, messages: Sequence[Message], **kwargs) -> Message:
        """Return an assistant message."""


class MockLLMClient(LLMClient):
    """Deterministic LLM client for tests and offline development."""

    def __init__(self, responses: Sequence[str] | None = None) -> None:
        self.responses = list(responses or [])
        self.calls: list[list[Message]] = []

    def complete(self, messages: Sequence[Message], **kwargs) -> Message:
        self.calls.append(list(messages))
        if self.responses:
            content = self.responses.pop(0)
        else:
            latest_user = next(
                (message.content for message in reversed(messages) if message.role == "user"),
                "",
            )
            content = f"Mock response: {latest_user}"
        return Message(role="assistant", content=content)


class OpenAICompatibleLLMClient(LLMClient):
    """Chat completions via an OpenAI-compatible HTTP API."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float = 60,
    ) -> None:
        if not base_url:
            raise ValueError("LLM base_url is required")
        if not api_key:
            raise ValueError("LLM API key is required")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout_seconds = timeout_seconds

    def complete(self, messages: Sequence[Message], **kwargs) -> Message:
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": [message.to_dict() for message in messages],
            "temperature": kwargs.get("temperature", 0.2),
        }
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=data,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            raise RuntimeError(
                f"LLM request failed with HTTP {exc.code}; check provider settings."
            ) from exc
        except error.URLError as exc:
            raise RuntimeError("LLM request failed; check network and provider settings.") from exc
        parsed = json.loads(raw)
        try:
            content = parsed["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("LLM response did not match chat/completions format") from exc
        return Message(
            role="assistant",
            content=str(content),
            metadata={"provider": "openai_compatible", "model": payload["model"]},
        )


def resolve_llm_client(
    *,
    provider: str | None = None,
    use_llm: bool = False,
) -> LLMClient:
    """Resolve an LLM client from env; offline-safe by default."""
    load_repo_dotenv()
    selected = (provider or os.getenv("LLM_PROVIDER") or "mock").strip().lower()
    if not use_llm or selected == "mock":
        return MockLLMClient()
    if selected != "openai_compatible":
        raise ValueError("Unknown LLM provider. Use mock or openai_compatible.")
    api_key = os.getenv("LLM_API_KEY", "")
    if not api_key:
        warnings.warn(
            "LLM_API_KEY is not set; falling back to MockLLMClient.",
            RuntimeWarning,
            stacklevel=2,
        )
        return MockLLMClient()
    return OpenAICompatibleLLMClient(
        base_url=os.getenv("LLM_BASE_URL", "https://api.deepseek.com"),
        api_key=api_key,
        model=os.getenv("LLM_MODEL", "deepseek-chat"),
        timeout_seconds=float(os.getenv("LLM_TIMEOUT_SECONDS", "60")),
    )
