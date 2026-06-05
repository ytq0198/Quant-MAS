from __future__ import annotations

from typing import Any


def get_graph_relationships() -> dict[str, Any]:
    """Return optional graph relationship fixture.

    返回可选图谱关系夹具。
    """
    return {
        "source": "fallback_graph",
        "required_for_tests": False,
        "relationships": [
            {"source": "ResearchAgent", "relation": "calls", "target": "BacktestTool"},
            {"source": "EXP-20260602-008", "relation": "evaluated_by", "target": "Walk-forward OOS"},
            {"source": "PaperArtifact", "relation": "summarizes", "target": "Experiment"},
        ],
    }
