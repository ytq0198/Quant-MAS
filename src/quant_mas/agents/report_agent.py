"""Report agent."""

from __future__ import annotations

import json
from typing import Any

from quant_mas.core import BaseAgent, LLMClient, Message


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
    ) -> str:
        payload = {
            "title": title,
            "metrics": metrics,
            "notes": notes,
        }
        return self.run(json.dumps(payload, ensure_ascii=False))

    def step(self, *, step: int, **kwargs) -> Message:
        return self.llm_client.complete(self.history)

