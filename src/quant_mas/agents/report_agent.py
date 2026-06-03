"""Report agent."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from quant_mas.core import BaseAgent, LLMClient, Message


@dataclass(frozen=True)
class ReportResult:
    """Structured report output preserving Quant Engine facts."""

    metrics: dict[str, Any]
    narrative: str | None
    facts_markdown: str


class ReportAgent(BaseAgent):
    """Generate concise research/backtest reports through an LLM boundary."""

    def __init__(self, llm_client: LLMClient, *, max_steps: int = 1) -> None:
        super().__init__(
            name="ReportAgent",
            llm_client=llm_client,
            system_prompt=(
                "You are a quantitative research report agent. Summarize metrics, "
                "risks, and next steps. Do not recommend live trading."
            ),
            max_steps=max_steps,
        )

    def generate_report(
        self,
        *,
        title: str,
        metrics: dict[str, Any],
        notes: str = "",
        use_llm: bool = False,
        return_result: bool = False,
    ) -> str | ReportResult:
        metrics_copy = deepcopy(metrics)
        facts_markdown = _facts_markdown(title=title, metrics=metrics_copy, notes=notes)
        payload = {
            "title": title,
            "metrics": metrics_copy,
            "notes": notes,
            "instruction": (
                "Summarize only provided metrics and notes. Do not invent metrics, "
                "orders, target weights, or live trading actions."
            ),
        }
        narrative = self.run(json.dumps(payload, ensure_ascii=False)) if use_llm or not return_result else None
        if return_result:
            return ReportResult(
                metrics=metrics_copy,
                narrative=narrative,
                facts_markdown=facts_markdown,
            )
        return narrative or facts_markdown

    def step(self, *, step: int, **kwargs) -> Message:
        return self.llm_client.complete(self.history)


def _facts_markdown(*, title: str, metrics: dict[str, Any], notes: str) -> str:
    lines = [f"# {title}", "", "## Metrics"]
    for key in sorted(metrics):
        lines.append(f"- {key}: {metrics[key]}")
    if notes:
        lines.extend(["", "## Notes", notes])
    return "\n".join(lines)
