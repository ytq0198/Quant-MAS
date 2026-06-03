"""Run a simulation-only RL baseline episode."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

from quant_mas.rl import (
    RewardConfig,
    TradingEnv,
    TradingEnvConfig,
    build_policy,
    build_synthetic_ohlcv,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run simulation-only RL baseline.")
    parser.add_argument("--config", default="configs/rl.yaml")
    parser.add_argument("--policy", choices=["random", "buy_hold", "ml_copy"])
    parser.add_argument("--market-data-path")
    parser.add_argument("--signals-path")
    parser.add_argument("--output-dir")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        config = _load_yaml(args.config)
        env_config = TradingEnvConfig.from_dict(config)
        reward_config = RewardConfig.from_dict(config)
        paths = config.get("paths", {})
        policy_config = config.get("policy", {})
        experiment = config.get("experiment", {})
        policy_name = args.policy or policy_config.get("name", "random")
        seed = args.seed if args.seed is not None else int(experiment.get("seed", 42))
        market_path = Path(args.market_data_path or paths.get("market_data", "")).expanduser()
        signals_path = args.signals_path or paths.get("signals")
        output_dir = Path(args.output_dir or paths.get("output_dir", "outputs/rl_baseline")).expanduser()
        market_data = _load_market_data(market_path, dry_run=args.dry_run)
        signals = _load_signals(signals_path)
        env = TradingEnv(market_data, config=env_config, reward_config=reward_config)
        policy = build_policy(policy_name, config=env_config, signals=signals, seed=seed)
        observation, info = env.reset(seed=seed)
        rewards: list[float] = []
        while True:
            action = policy.act(observation, info)
            result = env.step(action)
            rewards.append(result.reward)
            observation = result.observation
            info = result.info
            if result.terminated or result.truncated:
                break
        summary = env.render_episode_summary()
        metrics = {
            "simulation.total_return": summary["total_return"],
            "simulation.sharpe": summary["sharpe"],
            "simulation.max_drawdown": summary["max_drawdown"],
            "simulation.reward_sum": float(sum(rewards)),
            "simulation_only": True,
            "policy": policy_name,
        }
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (output_dir / "episode_summary.json").write_text(
            json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        (output_dir / "summary.md").write_text(
            _summary_markdown(policy_name=policy_name, metrics=metrics, summary=summary),
            encoding="utf-8",
        )
        print(json.dumps({"metrics": metrics, "output_dir": str(output_dir)}, indent=2))
        return 0
    except Exception as exc:
        print(f"[rl-baseline] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_yaml(path: str | Path) -> dict:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _load_market_data(path: Path, *, dry_run: bool) -> pd.DataFrame:
    if path and path.exists():
        return pd.read_parquet(path)
    if dry_run:
        return build_synthetic_ohlcv(n_bars=32, symbol="SYN")
    raise FileNotFoundError(f"market data not found: {path}. Use --dry-run for synthetic data.")


def _load_signals(path: str | None) -> pd.DataFrame | None:
    if not path:
        return None
    signal_path = Path(path).expanduser()
    if not signal_path.exists():
        raise FileNotFoundError(f"signals not found: {signal_path}")
    return pd.read_parquet(signal_path)


def _summary_markdown(*, policy_name: str, metrics: dict, summary: dict) -> str:
    return "\n".join(
        [
            "# RL Baseline Simulation",
            "",
            "**simulation_only:** true",
            "",
            f"- policy: {policy_name}",
            f"- simulation.total_return: {metrics['simulation.total_return']}",
            f"- simulation.sharpe: {metrics['simulation.sharpe']}",
            f"- simulation.max_drawdown: {metrics['simulation.max_drawdown']}",
            f"- final_equity: {summary['final_equity']}",
            "",
            "This is a simulation-only auxiliary experiment. It is not a live trading system.",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
