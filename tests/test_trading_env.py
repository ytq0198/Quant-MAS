from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import math
import pandas as pd
import pytest

from quant_mas.rl import (
    BuyAndHoldPolicy,
    MLCopyPolicy,
    RandomPolicy,
    TradingEnv,
    TradingEnvConfig,
    build_synthetic_ml_signals,
    build_synthetic_ohlcv,
)


def test_trading_env_config_validates_action_levels() -> None:
    with pytest.raises(ValueError, match="sorted"):
        TradingEnvConfig(action_levels=(0.0, 1.0, 0.5))
    with pytest.raises(ValueError, match="long-only"):
        TradingEnvConfig(action_levels=(-0.1, 0.0, 1.0))


def test_reset_returns_observation_and_info() -> None:
    env = TradingEnv(build_synthetic_ohlcv(8), config=TradingEnvConfig())

    observation, info = env.reset(seed=7)

    assert env.observation_dim == len(observation)
    assert set(observation) == {"position_weight", "last_return", "rolling_vol_5", "volume", "close"}
    assert "date" in info


def test_step_advances_date_without_overflow() -> None:
    env = TradingEnv(build_synthetic_ohlcv(5), config=TradingEnvConfig())
    _, info = env.reset()

    result = env.step(0)

    assert result.info["date"] != info["date"]
    assert result.terminated is False


def test_last_step_terminates() -> None:
    env = TradingEnv(build_synthetic_ohlcv(3), config=TradingEnvConfig())
    env.reset()

    first = env.step(0)
    second = env.step(0)

    assert first.terminated is False
    assert second.terminated is True


def test_next_bar_execution_sets_position_to_action_level() -> None:
    config = TradingEnvConfig(action_levels=(0.0, 0.25, 0.5, 1.0))
    env = TradingEnv(build_synthetic_ohlcv(8), config=config)
    env.reset()

    result = env.step(2)

    assert result.info["target_weight"] == pytest.approx(0.5)
    assert result.info["position_weight"] == pytest.approx(0.5)


def test_observation_uses_current_not_future_close() -> None:
    data = build_synthetic_ohlcv(6)
    env = TradingEnv(data, config=TradingEnvConfig())
    observation, _ = env.reset()

    assert observation["close"] == pytest.approx(float(data.iloc[0]["close"]))
    assert observation["close"] != pytest.approx(float(data.iloc[1]["close"]))


def test_reward_is_finite_and_deterministic() -> None:
    data = build_synthetic_ohlcv(8)
    env_a = TradingEnv(data, config=TradingEnvConfig())
    env_b = TradingEnv(data, config=TradingEnvConfig())
    env_a.reset(seed=42)
    env_b.reset(seed=42)

    reward_a = env_a.step(1).reward
    reward_b = env_b.step(1).reward

    assert math.isfinite(reward_a)
    assert reward_a == pytest.approx(reward_b)


def test_episode_summary_contains_metrics() -> None:
    env = TradingEnv(build_synthetic_ohlcv(8), config=TradingEnvConfig())
    env.reset()
    while True:
        result = env.step(1)
        if result.terminated or result.truncated:
            break

    summary = env.render_episode_summary()

    assert "total_return" in summary
    assert "max_drawdown" in summary
    assert summary["simulation_only"] is True


def test_buy_and_hold_policy_chooses_max_long_action() -> None:
    policy = BuyAndHoldPolicy(action_space_n=4)

    assert policy.act({}, {}) == 3


def test_random_policy_seed_is_reproducible() -> None:
    first = RandomPolicy(4, seed=123)
    second = RandomPolicy(4, seed=123)

    assert [first.act({}, {}) for _ in range(5)] == [second.act({}, {}) for _ in range(5)]


def test_ml_copy_policy_aligns_by_date() -> None:
    data = build_synthetic_ohlcv(5)
    signals = build_synthetic_ml_signals(data, weight=0.5)
    config = TradingEnvConfig(action_levels=(0.0, 0.25, 0.5, 1.0))
    policy = MLCopyPolicy(signals, config=config)

    action = policy.act({}, {"date": str(pd.to_datetime(data.iloc[0]["date"]))})

    assert action == 2


def test_run_rl_baseline_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_rl_baseline.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--policy" in result.stdout


def test_run_rl_baseline_dry_run(tmp_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_rl_baseline.py",
            "--config",
            "configs/rl.yaml",
            "--policy",
            "random",
            "--dry-run",
            "--output-dir",
            str(tmp_path / "rl"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    metrics = json.loads((tmp_path / "rl" / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["simulation_only"] is True
    assert "simulation.sharpe" in metrics
