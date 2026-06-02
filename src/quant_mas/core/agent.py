"""Base agent implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from quant_mas.core.llm import LLMClient
from quant_mas.core.message import Message


class BaseAgent(ABC):
    """Base class for bounded-step agents."""

    def __init__(
        self,
        name: str,
        llm_client: LLMClient,
        *,
        system_prompt: str = "",
        max_steps: int = 4,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        self.name = name
        self.llm_client = llm_client
        self.system_prompt = system_prompt
        self.max_steps = max_steps
        self.history: list[Message] = []
        if system_prompt:
            self.history.append(Message(role="system", content=system_prompt))

    def run(self, input_text: str, **kwargs) -> str:
        """Run one bounded agent turn."""
        self.history.append(Message(role="user", content=input_text))
        for step in range(self.max_steps):
            response = self.step(step=step, **kwargs)
            self.history.append(response)
            if self.is_finished(response, step=step):
                return response.content
        raise RuntimeError(f"{self.name} exceeded max_steps={self.max_steps}")

    @abstractmethod
    def step(self, *, step: int, **kwargs) -> Message:
        """Execute a single agent step."""

    def is_finished(self, response: Message, *, step: int) -> bool:
        return True

