"""Research interpretation agent."""

from __future__ import annotations

import json
import warnings
from dataclasses import asdict, dataclass
from typing import Any

from quant_mas.context import AgentContextBundle
from quant_mas.core import BaseAgent, LLMClient, Message, MockLLMClient, resolve_llm_client


RESEARCH_SYSTEM_PROMPT = """
You are a quantitative research assistant, not a trader.
You must not suggest live trading, broker instructions, orders, or target weights.
Separate Quant Engine facts from LLM inference. Metrics and artifacts are facts.
Use walk-forward OOS metrics as the paper-level evidence baseline; reference
baseline EXP-20260602-008 and OOS sharpe 0.586 when relevant.
Return JSON with keys: hypothesis, evidence_summary, suggested_experiments,
risks_and_caveats.
""".strip()


@dataclass(frozen=True)
class ResearchAgentOutput:
    """Structured ResearchAgent result."""

    hypothesis: str
    evidence_summary: str
    suggested_experiments: list[str]
    risks_and_caveats: str
    llm_provider: str
    context_snapshot: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ResearchAgentOutput":
        return cls(
            hypothesis=str(payload.get("hypothesis", "")),
            evidence_summary=str(payload.get("evidence_summary", "")),
            suggested_experiments=[
                str(item) for item in payload.get("suggested_experiments", [])
            ],
            risks_and_caveats=str(payload.get("risks_and_caveats", "")),
            llm_provider=str(payload.get("llm_provider", "mock")),
            context_snapshot=dict(payload.get("context_snapshot", {})),
        )


class ResearchAgent(BaseAgent):
    """Generate research hypotheses from a structured context bundle."""

    def __init__(
        self,
        llm_client: LLMClient | None = None,
        *,
        llm_provider: str | None = None,
        use_llm: bool = False,
        max_steps: int = 1,
    ) -> None:
        super().__init__(
            name="ResearchAgent",
            llm_client=llm_client
            or resolve_llm_client(provider=llm_provider, use_llm=use_llm),
            system_prompt=RESEARCH_SYSTEM_PROMPT,
            max_steps=max_steps,
        )

    def run_research(self, bundle: AgentContextBundle) -> ResearchAgentOutput:
        payload = {
            "instruction": "Analyze this context and return JSON only.",
            "context": bundle.to_dict(),
        }
        response_text = self._run_with_fallback(json.dumps(payload, ensure_ascii=False))
        parsed = _parse_json_object(response_text)
        provider = _provider_name(self.llm_client)
        if parsed is None:
            parsed = {
                "hypothesis": "Insufficient structured JSON from LLM; keep interpretation conservative.",
                "evidence_summary": response_text,
                "suggested_experiments": [
                    "Run walk-forward OOS validation and compare against baseline OOS sharpe 0.586.",
                    "Run feature ablation on the latest model or strategy experiment.",
                ],
                "risks_and_caveats": "LLM narrative is non-authoritative and cannot modify Quant Engine metrics.",
            }
        return ResearchAgentOutput(
            hypothesis=str(parsed.get("hypothesis", "")),
            evidence_summary=str(parsed.get("evidence_summary", "")),
            suggested_experiments=[
                str(item) for item in parsed.get("suggested_experiments", [])
            ],
            risks_and_caveats=str(parsed.get("risks_and_caveats", "")),
            llm_provider=provider,
            context_snapshot=_context_snapshot(bundle),
        )

    def step(self, *, step: int, **kwargs) -> Message:
        return self.llm_client.complete(self.history)

    def _run_with_fallback(self, prompt: str) -> str:
        try:
            return self.run(prompt)
        except Exception as exc:
            warnings.warn(
                f"ResearchAgent LLM call failed; falling back to MockLLMClient: {exc}",
                RuntimeWarning,
                stacklevel=2,
            )
            self.llm_client = MockLLMClient()
            self.history = []
            return self.run(prompt)


def _parse_json_object(text: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _provider_name(client: LLMClient) -> str:
    if hasattr(client, "provider"):
        return str(getattr(client, "provider"))
    if client.__class__.__name__ == "OpenAICompatibleLLMClient":
        return "openai_compatible"
    if client.__class__.__name__ == "LocalVLLMClient":
        return "local_vllm"
    return "mock"


def _context_snapshot(bundle: AgentContextBundle) -> dict[str, Any]:
    payload = bundle.to_dict()
    return {
        "task": payload["task"],
        "experiments": payload["experiments"],
        "baseline": payload["baseline"],
        "risk": payload["risk"],
        "rag_chunks": payload["rag_chunks"],
        "workflow": payload["workflow"],
        "baseline_ref": payload["baseline_ref"],
        "built_at": payload["built_at"],
    }
