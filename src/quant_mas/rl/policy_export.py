"""Export simulation-trained RL policies as StrategyCandidate records."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from quant_mas.research import StrategyCandidate, assert_no_oos_metrics
from quant_mas.rl.feature_policy import FeaturePolicyState
from quant_mas.rl.grpo_agent import PolicyState


def load_policy_state(path: str | Path) -> PolicyState | FeaturePolicyState:
    """Load a serialized M12 policy state."""
    payload = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if "feature_names" in payload:
        return FeaturePolicyState(
            feature_names=[str(value) for value in payload["feature_names"]],
            action_weights=[
                [float(item) for item in row]
                for row in payload["action_weights"]
            ],
            action_bias=[float(value) for value in payload["action_bias"]],
            step_count=int(payload.get("step_count", 0)),
            metadata=dict(payload.get("metadata", {})),
        )
    return PolicyState(
        action_logits=[float(value) for value in payload["action_logits"]],
        step_count=int(payload.get("step_count", 0)),
        metadata=dict(payload.get("metadata", {})),
    )


def load_training_metrics(path: str | Path) -> dict[str, Any]:
    """Load training metrics and reject OOS result fields."""
    metrics = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    _reject_oos_metrics(metrics)
    return metrics


def export_policy_candidate(
    *,
    policy_state_path: str | Path,
    metrics_path: str | Path,
    candidate_id: str | None = None,
    agent_type: str | None = None,
) -> StrategyCandidate:
    """Convert a policy checkpoint into a StrategyCandidate."""
    state_path = Path(policy_state_path).expanduser()
    state = load_policy_state(state_path)
    metrics = load_training_metrics(metrics_path)
    agent_id = str(state.metadata.get("agent_id") or "rl_policy")
    selected_candidate_id = candidate_id or f"rl_{_slug(agent_id)}_{state.step_count}"
    selection_metrics = _selection_metrics(metrics)
    assert_no_oos_metrics(selection_metrics)
    selected_agent_type = agent_type or _agent_type_for_state(state)
    return StrategyCandidate(
        candidate_id=selected_candidate_id,
        source="rl_training",
        agent_id=agent_id,
        agent_type=selected_agent_type,
        params=_params_for_state(state, state_path),
        selection_metrics=selection_metrics,
        artifacts={"policy_state": str(state_path), "training_metrics": str(Path(metrics_path).expanduser())},
        notes="Exported from M12 RL simulation; requires M11.7/M11.8 OOS validation.",
    )


def write_rl_candidates(
    candidates: list[StrategyCandidate],
    output_dir: str | Path,
) -> dict[str, str]:
    """Write RL candidates as JSON, CSV, and summary markdown."""
    if not candidates:
        raise ValueError("No RL candidates provided")
    target = Path(output_dir).expanduser()
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "candidates.json"
    csv_path = target / "candidates.csv"
    summary_path = target / "export_summary.md"
    json_path.write_text(
        json.dumps([candidate.to_dict() for candidate in candidates], indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    with csv_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "candidate_id",
                "agent_id",
                "agent_type",
                "training_policy_step_count",
                "simulation_sharpe_mean",
                "simulation_total_return_mean",
            ],
        )
        writer.writeheader()
        for candidate in candidates:
            writer.writerow(
                {
                    "candidate_id": candidate.candidate_id,
                    "agent_id": candidate.agent_id,
                    "agent_type": candidate.agent_type,
                    "training_policy_step_count": candidate.selection_metrics.get("training.policy_step_count"),
                    "simulation_sharpe_mean": candidate.selection_metrics.get("simulation.sharpe_mean"),
                    "simulation_total_return_mean": candidate.selection_metrics.get("simulation.total_return_mean"),
                }
            )
    summary_path.write_text(_summary_markdown(candidates), encoding="utf-8")
    return {
        "candidates_json": str(json_path),
        "candidates_csv": str(csv_path),
        "summary": str(summary_path),
    }


def _selection_metrics(metrics: dict[str, Any]) -> dict[str, Any]:
    selected: dict[str, Any] = {}
    for section in ("training", "simulation"):
        values = metrics.get(section, {})
        if isinstance(values, dict):
            for key, value in values.items():
                selected[f"{section}.{key}"] = value
    summary = metrics.get("summary", {})
    if isinstance(summary, dict):
        for key in ("algorithm", "baseline_experiment_id", "baseline_oos_sharpe"):
            if key in summary:
                selected[f"summary.{key}"] = summary[key]
    _reject_oos_metrics(selected)
    return selected


def _agent_type_for_state(state: PolicyState | FeaturePolicyState) -> str:
    if isinstance(state, FeaturePolicyState):
        return "feature_linear_policy"
    return "grpo_policy"


def _params_for_state(
    state: PolicyState | FeaturePolicyState,
    state_path: Path,
) -> dict[str, Any]:
    if isinstance(state, FeaturePolicyState):
        return {
            "policy_state_path": str(state_path),
            "policy_type": "feature_linear",
            "feature_names": list(state.feature_names),
            "action_weights": [list(row) for row in state.action_weights],
            "action_bias": list(state.action_bias),
            "step_count": int(state.step_count),
            "action_levels": [0.0, 0.25, 0.5, 1.0],
        }
    return {
        "policy_state_path": str(state_path),
        "policy_type": "logits",
        "action_logits": list(state.action_logits),
        "step_count": int(state.step_count),
        "action_policy": "discrete_logits",
        "action_levels": [0.0, 0.25, 0.5, 1.0],
    }


def _reject_oos_metrics(metrics: dict[str, Any]) -> None:
    for key, value in metrics.items():
        lowered = str(key).lower()
        if lowered == "oos" or lowered.startswith("oos."):
            raise ValueError("RL policy export must not include oos metrics")
        if isinstance(value, dict):
            _reject_oos_metrics(value)


def _summary_markdown(candidates: list[StrategyCandidate]) -> str:
    lines = [
        "# RL Policy Candidate Export",
        "",
        "**simulation_only:** true",
        "",
        "| Candidate | Agent | Type | Training Step | Simulation Sharpe Mean |",
        "|-----------|-------|------|---------------|------------------------|",
    ]
    for candidate in candidates:
        lines.append(
            "| {candidate} | {agent} | {agent_type} | {step} | {sharpe} |".format(
                candidate=candidate.candidate_id,
                agent=candidate.agent_id,
                agent_type=candidate.agent_type,
                step=candidate.selection_metrics.get("training.policy_step_count", ""),
                sharpe=candidate.selection_metrics.get("simulation.sharpe_mean", ""),
            )
        )
    lines.extend(
        [
            "",
            "These candidates were exported from simulation-only RL training.",
            "Walk-forward OOS validation must use M11.7/M11.8 scripts.",
            "",
        ]
    )
    return "\n".join(lines)


def _slug(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in str(value)).strip("_")
