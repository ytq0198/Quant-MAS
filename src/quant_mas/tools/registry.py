"""Tool registry."""

from __future__ import annotations

from collections.abc import Iterable

from quant_mas.tools.base import BaseTool


class ToolRegistry:
    """Register and retrieve tools by unique name."""

    def __init__(self, tools: Iterable[BaseTool] | None = None) -> None:
        self._tools: dict[str, BaseTool] = {}
        for tool in tools or ():
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool not found: {name}") from exc

    def list(self) -> list[BaseTool]:
        return list(self._tools.values())

    def names(self) -> list[str]:
        return sorted(self._tools)

