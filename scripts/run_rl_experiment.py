"""Run a simulation-only RL training experiment."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from quant_mas.memory import ExperimentMemory
from quant_mas.rl import (
    GRPOPolicyAgent,
    RLTrainingLoop,
    RewardConfig,
    TradingEnv,
    TradingEnvConfig,
    build_synthetic_ohlcv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run simulation-only RL training.")
    parser.add_argument("--config", default="configs/rl_training.yaml")
    parser.add_argument("--algorithm", choices=["grpo", "ppo"])
    parser.add_argument("--market-data-path")
    parser.add_argument("--max-steps", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--output-dir")
    parser.add_argument("--memory-path")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    return parser


def run_rl_experiment(
    *,
    config_path: str | Path = "configs/rl_training.yaml",
    algorithm: str | None = None,
    market_data_path: str | Path | None = None,
    max_steps: int | None = None,
    seed: int | None = None,
    output_dir: str | Path | None = None,
    memory_path: str | Path | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    config = _load_yaml(config_path)
    training_config = config.setdefault("rl_training", {})
    if algorithm is not None:
        training_config["algorithm"] = algorithm
    selected_seed = int(seed if seed is not None else training_config.get("seed", 42))
    selected_max_steps = int(max_steps if max_steps is not None else training_config.get("max_steps", 10))
    n_groups = int(training_config.get("n_groups", 2))
    rollouts_per_group = int(training_config.get("rollouts_per_group", 2))

    env_config = TradingEnvConfig.from_dict(config.get("env", {}))
    reward_config = RewardConfig.from_dict(config.get("reward", {}))
    market_data = _load_market_data(
        market_data_path or config.get("paths", {}).get("market_data"),
        dry_run=dry_run,
    )
    env = TradingEnv(market_data, config=env_config, reward_config=reward_config)
    policy = GRPOPolicyAgent(
        agent_id="grpo_policy_001",
        action_space_n=env.action_space_n,
        seed=selected_seed,
    )
    loop = RLTrainingLoop(env=env, policy=policy, config=config)
    result = loop.run(
        max_steps=selected_max_steps,
        n_groups=n_groups,
        rollouts_per_group=rollouts_per_group,
        seed=selected_seed,
    )
    artifacts: dict[str, str] = {}
    experiment_id: str | None = None
    if not dry_run:
        experiment = config.get("experiment", {})
        name = experiment.get("name", "rl_training_grpo_001")
        target_dir = Path(
            output_dir or config.get("paths", {}).get("output_dir", "outputs/rl_training")
        ).expanduser() / str(name)
        artifacts = loop.save_checkpoint(target_dir, result)
        memory = ExperimentMemory(
            memory_path
            or experiment.get("memory_path")
            or target_dir.parent / "experiments.json"
        )
        record = memory.add(
            name=name,
            metrics=result.metrics,
            artifacts=artifacts,
            params={
                "family": experiment.get("family", "rl_training"),
                "config": config,
                "market_data_path": str(market_data_path) if market_data_path else None,
            },
            notes="Simulation-only RL training. OOS validation must use M11.7/M11.8.",
        )
        experiment_id = record.experiment_id

    return {
        "algorithm": result.algorithm,
        "metrics": result.metrics,
        "policy_state": {
            "action_logits": result.policy_state.action_logits,
            "step_count": result.policy_state.step_count,
            "metadata": result.policy_state.metadata,
        },
        "artifacts": artifacts,
        "experiment_id": experiment_id,
        "dry_run": dry_run,
    }


def main() -> int:
    _configure_stdout()
    args = build_parser().parse_args()
    try:
        result = run_rl_experiment(
            config_path=args.config,
            algorithm=args.algorithm,
            market_data_path=args.market_data_path,
            max_steps=args.max_steps,
            seed=args.seed,
            output_dir=args.output_dir,
            memory_path=args.memory_path,
            dry_run=args.dry_run,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"[rl-training] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_yaml(path: str | Path) -> dict[str, Any]:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _load_market_data(path: str | Path | None, *, dry_run: bool) -> pd.DataFrame:
    if path:
        market_path = Path(path).expanduser()
        if market_path.exists():
            return pd.read_parquet(market_path)
    if dry_run or path is None:
        return build_synthetic_ohlcv(n_bars=40, symbol="SYN")
    raise FileNotFoundError(f"market data not found: {path}. Use --dry-run for synthetic data.")


def _configure_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


if __name__ == "__main__":
    raise SystemExit(main())
