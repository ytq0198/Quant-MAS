"""Gymnasium-like trading environment for simulation-only RL experiments."""

from __future__ import annotations

from typing import Any

import pandas as pd

from quant_mas.risk import RiskLimits, check_position_limits
from quant_mas.rl.env_schema import RewardConfig, StepResult, TradingEnvConfig
from quant_mas.rl.reward import compute_episode_metrics, compute_step_reward


REQUIRED_COLUMNS = {"date", "open", "high", "low", "close", "volume"}


class TradingEnv:
    """Long-only discrete target-weight environment.

    Observation at bar i uses current and historical values only. Action chosen
    at bar i is executed at bar i+1 open, and reward uses i -> i+1 return.
    """

    def __init__(
        self,
        market_data: pd.DataFrame,
        *,
        config: TradingEnvConfig | None = None,
        reward_config: RewardConfig | None = None,
        symbol: str | None = None,
        risk_limits: RiskLimits | None = None,
    ) -> None:
        self.config = config or TradingEnvConfig()
        self.reward_config = reward_config or RewardConfig()
        self.risk_limits = risk_limits or RiskLimits(max_position_weight=1.0)
        self.symbol = symbol
        self.market_data = _prepare_market_data(market_data, symbol=symbol)
        self._index = 0
        self._position_weight = 0.0
        self._equity = self.config.initial_cash
        self._running_max = self.config.initial_cash
        self._equity_curve: list[float] = []
        self._turnover_sum = 0.0
        self._steps = 0
        self._terminated = False

    @property
    def action_space_n(self) -> int:
        return len(self.config.action_levels)

    @property
    def observation_dim(self) -> int:
        return len(self._observation())

    def reset(self, *, seed: int | None = None) -> tuple[dict[str, float], dict[str, Any]]:
        self._index = 0
        self._position_weight = 0.0
        self._equity = self.config.initial_cash
        self._running_max = self.config.initial_cash
        self._equity_curve = [self._equity]
        self._turnover_sum = 0.0
        self._steps = 0
        self._terminated = False
        return self._observation(), {"date": str(self.market_data.iloc[0]["date"]), "seed": seed}

    def step(self, action_index: int) -> StepResult:
        if self._terminated:
            raise RuntimeError("Episode is terminated. Call reset() before stepping again.")
        if self._index >= len(self.market_data) - 1:
            self._terminated = True
            return StepResult(self._observation(), 0.0, True, False, self._info())

        requested_weight = self.config.validate_action_index(action_index)
        target_weight, risk_info = self._risk_adjust_weight(requested_weight)
        current = self.market_data.iloc[self._index]
        next_bar = self.market_data.iloc[self._index + 1]
        prev_equity = self._equity
        turnover = abs(target_weight - self._position_weight)
        execution_cost = self._execution_cost(prev_equity, turnover)
        market_return = float(next_bar["open"] / current["close"] - 1.0)
        self._equity = prev_equity * (1.0 + target_weight * market_return) - execution_cost
        self._position_weight = target_weight
        self._running_max = max(self._running_max, self._equity)
        drawdown = self._equity / self._running_max - 1.0
        self._turnover_sum += turnover
        self._index += 1
        self._steps += 1
        self._equity_curve.append(self._equity)

        terminated = self._index >= len(self.market_data) - 1
        truncated = self.config.max_steps is not None and self._steps >= self.config.max_steps
        self._terminated = terminated or truncated
        reward = compute_step_reward(
            prev_equity=prev_equity,
            equity=self._equity,
            turnover=turnover,
            drawdown=drawdown,
            cost=execution_cost / prev_equity,
            config=self.reward_config,
        )
        info = self._info()
        info.update(
            {
                "requested_weight": requested_weight,
                "target_weight": target_weight,
                "turnover": turnover,
                "market_return": market_return,
                "execution_cost": execution_cost,
                "drawdown": drawdown,
                "risk": risk_info,
                "simulation_only": True,
            }
        )
        return StepResult(self._observation(), reward, terminated, truncated, info)

    def render_episode_summary(self) -> dict[str, float | bool]:
        metrics = compute_episode_metrics(
            pd.Series(self._equity_curve, dtype=float),
            turnover_sum=self._turnover_sum,
        )
        return {**metrics, "simulation_only": True}

    def _risk_adjust_weight(self, requested_weight: float) -> tuple[float, dict[str, Any]]:
        targets = pd.DataFrame(
            [{"symbol": self._symbol_name(), "target_weight": requested_weight}]
        )
        decision = check_position_limits(targets, self.risk_limits, clip=True)
        adjusted = float(decision.adjusted_targets["target_weight"].iloc[0])
        return adjusted, {
            "status": decision.status,
            "approved": decision.approved,
            "violations": decision.violations,
        }

    def _execution_cost(self, equity: float, turnover: float) -> float:
        commission = equity * turnover * self.config.commission_rate
        slippage = equity * turnover * (self.config.slippage_bps / 10_000.0)
        return float(commission + slippage)

    def _observation(self) -> dict[str, float]:
        row = self.market_data.iloc[self._index]
        start = max(0, self._index - 4)
        history = self.market_data.iloc[start : self._index + 1]
        last_return = 0.0
        if self._index > 0:
            prev_close = float(self.market_data.iloc[self._index - 1]["close"])
            last_return = float(row["close"] / prev_close - 1.0)
        rolling_vol = float(history["close"].pct_change().dropna().std(ddof=0) or 0.0)
        return {
            "position_weight": float(self._position_weight),
            "last_return": last_return,
            "rolling_vol_5": rolling_vol,
            "volume": float(row["volume"]),
            "close": float(row["close"]),
        }

    def _info(self) -> dict[str, Any]:
        row = self.market_data.iloc[self._index]
        return {
            "date": str(row["date"]),
            "step": self._steps,
            "equity": float(self._equity),
            "position_weight": float(self._position_weight),
        }

    def _symbol_name(self) -> str:
        if "symbol" in self.market_data.columns:
            return str(self.market_data.iloc[0]["symbol"])
        return self.symbol or "SYN"


def _prepare_market_data(frame: pd.DataFrame, *, symbol: str | None) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"market_data missing columns: {sorted(missing)}")
    data = frame.copy()
    if symbol is not None:
        if "symbol" not in data.columns:
            raise ValueError("symbol filter requires symbol column")
        data = data[data["symbol"].astype(str) == symbol]
    if data.empty:
        raise ValueError("market_data is empty")
    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date").reset_index(drop=True)
    if len(data) < 2:
        raise ValueError("market_data must contain at least two bars")
    return data
