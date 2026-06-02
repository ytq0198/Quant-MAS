"""Vector-light backtest engine with next-bar execution."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quant_mas.backtest.costs import CommissionModel, SlippageModel
from quant_mas.backtest.metrics import calculate_metrics
from quant_mas.data import validate_ohlcv
from quant_mas.strategies import Strategy


@dataclass(frozen=True)
class BacktestResult:
    equity_curve: pd.DataFrame
    trades: pd.DataFrame
    metrics: dict


class BacktestEngine:
    """Run a simple long-only backtest with next-bar execution."""

    def __init__(
        self,
        strategy: Strategy,
        initial_cash: float = 100_000.0,
        commission_model: CommissionModel | None = None,
        slippage_model: SlippageModel | None = None,
    ) -> None:
        if initial_cash <= 0:
            raise ValueError("initial_cash must be positive")
        self.strategy = strategy
        self.initial_cash = initial_cash
        self.commission_model = commission_model or CommissionModel()
        self.slippage_model = slippage_model or SlippageModel()

    def run(self, data: pd.DataFrame) -> BacktestResult:
        market_data = validate_ohlcv(data)
        signals = self.strategy.generate_signals(market_data)
        self._validate_signals(signals)

        frames = []
        trades = []
        portfolio_equity = self.initial_cash
        symbol_count = market_data["symbol"].nunique()
        capital_per_symbol = self.initial_cash / symbol_count

        for symbol, symbol_data in market_data.groupby("symbol", sort=True):
            symbol_signals = signals[signals["symbol"] == symbol]
            equity, symbol_trades = self._run_symbol(
                symbol_data.sort_values("date").reset_index(drop=True),
                symbol_signals.sort_values("date").reset_index(drop=True),
                capital_per_symbol,
            )
            frames.append(equity)
            trades.extend(symbol_trades)

        combined = self._combine_equity(frames)
        if not combined.empty:
            scale = portfolio_equity / combined["equity"].iloc[0]
            combined["equity"] = combined["equity"] * scale
            combined["returns"] = combined["equity"].pct_change().fillna(0.0)

        trades_frame = pd.DataFrame(
            trades,
            columns=[
                "date",
                "symbol",
                "side",
                "quantity",
                "price",
                "trade_value",
                "commission",
            ],
        )
        return BacktestResult(
            equity_curve=combined,
            trades=trades_frame,
            metrics=calculate_metrics(combined),
        )

    def _run_symbol(
        self,
        data: pd.DataFrame,
        signals: pd.DataFrame,
        initial_cash: float,
    ) -> tuple[pd.DataFrame, list[dict]]:
        merged = data.merge(
            signals.loc[:, ["date", "symbol", "target_weight"]],
            on=["date", "symbol"],
            how="left",
        )
        merged["target_weight"] = merged["target_weight"].fillna(0.0)
        merged["execution_weight"] = merged["target_weight"].shift(1).fillna(0.0)

        cash = initial_cash
        shares = 0.0
        equity_rows = []
        trades = []

        for row in merged.itertuples(index=False):
            pre_trade_equity = cash + shares * row.open
            target_value = pre_trade_equity * row.execution_weight
            current_value = shares * row.open
            trade_value = target_value - current_value

            if abs(trade_value) > 1e-12:
                side = "buy" if trade_value > 0 else "sell"
                execution_price = self.slippage_model.adjust_price(float(row.open), side)
                quantity = trade_value / execution_price
                actual_trade_value = quantity * execution_price
                commission = self.commission_model.calculate(actual_trade_value)
                cash -= actual_trade_value + commission
                shares += quantity
                trades.append(
                    {
                        "date": row.date,
                        "symbol": row.symbol,
                        "side": side,
                        "quantity": quantity,
                        "price": execution_price,
                        "trade_value": actual_trade_value,
                        "commission": commission,
                    }
                )

            equity = cash + shares * row.close
            equity_rows.append(
                {
                    "date": row.date,
                    "symbol": row.symbol,
                    "equity": equity,
                    "cash": cash,
                    "shares": shares,
                    "close": row.close,
                    "target_weight": row.target_weight,
                    "execution_weight": row.execution_weight,
                }
            )

        equity_frame = pd.DataFrame(equity_rows)
        equity_frame["returns"] = equity_frame["equity"].pct_change().fillna(0.0)
        return equity_frame, trades

    @staticmethod
    def _combine_equity(frames: list[pd.DataFrame]) -> pd.DataFrame:
        if not frames:
            return pd.DataFrame(columns=["date", "equity", "returns"])
        combined = (
            pd.concat(frames, ignore_index=True)
            .groupby("date", as_index=False)["equity"]
            .sum()
            .sort_values("date")
            .reset_index(drop=True)
        )
        combined["returns"] = combined["equity"].pct_change().fillna(0.0)
        return combined

    @staticmethod
    def _validate_signals(signals: pd.DataFrame) -> None:
        required = {"date", "symbol", "target_weight"}
        missing = required.difference(signals.columns)
        if missing:
            raise ValueError(f"Strategy signals missing columns: {sorted(missing)}")
        if signals.duplicated(["date", "symbol"]).any():
            raise ValueError("Strategy signals contain duplicate date/symbol rows")

