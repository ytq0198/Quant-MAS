"""Core abstractions for Quant MAS."""

from quant_mas.core.agent import BaseAgent
from quant_mas.core.events import AgentEvent, AgentFinishEvent, ToolCallEvent
from quant_mas.core.llm import (
    LLMClient,
    LocalVLLMClient,
    MockLLMClient,
    OpenAICompatibleLLMClient,
    resolve_llm_client,
)
from quant_mas.core.message import Message

__all__ = [
    "AgentEvent",
    "AgentFinishEvent",
    "BaseAgent",
    "LLMClient",
    "LocalVLLMClient",
    "Message",
    "MockLLMClient",
    "OpenAICompatibleLLMClient",
    "ToolCallEvent",
    "resolve_llm_client",
]
