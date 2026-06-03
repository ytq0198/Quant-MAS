"""Merge text-derived signals into feature tables."""

from __future__ import annotations

import pandas as pd


def merge_text_signals_into_features(
    features: pd.DataFrame,
    signals: pd.DataFrame,
    *,
    on: tuple[str, str] = ("date", "symbol"),
    signal_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Left join text signals and reject duplicate or future-leaking rows.

    Text signals are ordinary feature columns for downstream deterministic
    training and walk-forward evaluation. They do not replace Quant Engine
    metrics and must not contain labels, future returns, or trading orders.
    """
    date_col, symbol_col = on
    _require_columns(features, [date_col, symbol_col], "features")
    _require_columns(signals, [date_col, symbol_col], "signals")
    feature_frame = features.copy()
    signal_frame = _wide_signal_frame(signals, date_col=date_col, symbol_col=symbol_col)
    feature_frame[date_col] = pd.to_datetime(feature_frame[date_col])
    signal_frame[date_col] = pd.to_datetime(signal_frame[date_col])
    if signal_columns is not None:
        _require_columns(signal_frame, [*on, *signal_columns], "signals")
        signal_frame = signal_frame[[*on, *signal_columns]]
    _reject_duplicate_keys(signal_frame, [date_col, symbol_col])
    assert_no_future_text_leakage(feature_frame, signal_frame, on=on)
    rows_before = len(feature_frame)
    merged = feature_frame.merge(signal_frame, how="left", on=list(on), validate="many_to_one")
    if len(merged) != rows_before:
        raise ValueError("Text signal merge changed row count; check duplicate keys")
    return merged


def assert_no_future_text_leakage(
    features: pd.DataFrame,
    signals: pd.DataFrame,
    *,
    on: tuple[str, str] = ("date", "symbol"),
) -> None:
    """Assert each signal date is not after its matched feature bar date."""
    date_col, symbol_col = on
    feature_keys = features[[date_col, symbol_col]].copy()
    signal_keys = signals[[date_col, symbol_col]].copy()
    feature_keys[date_col] = pd.to_datetime(feature_keys[date_col])
    signal_keys[date_col] = pd.to_datetime(signal_keys[date_col])
    merged = signal_keys.merge(
        feature_keys,
        on=[date_col, symbol_col],
        how="left",
        indicator=True,
    )
    unmatched = merged[merged["_merge"] == "left_only"]
    if not unmatched.empty:
        earliest_by_symbol = feature_keys.groupby(symbol_col)[date_col].min()
        for _, row in unmatched.iterrows():
            symbol = row[symbol_col]
            signal_date = row[date_col]
            if symbol in earliest_by_symbol and signal_date > earliest_by_symbol[symbol]:
                raise ValueError(
                    "Future text leakage detected: signal date has no matching historical bar"
                )


def _wide_signal_frame(
    signals: pd.DataFrame,
    *,
    date_col: str,
    symbol_col: str,
) -> pd.DataFrame:
    if {"signal_name", "value"}.issubset(signals.columns):
        _reject_duplicate_keys(signals, [date_col, symbol_col, "signal_name"])
        wide = signals.pivot(
            index=[date_col, symbol_col],
            columns="signal_name",
            values="value",
        ).reset_index()
        wide.columns.name = None
        return wide
    return signals.copy()


def _require_columns(frame: pd.DataFrame, columns: list[str], label: str) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"{label} missing required columns: {missing}")


def _reject_duplicate_keys(frame: pd.DataFrame, columns: list[str]) -> None:
    if frame.duplicated(columns).any():
        raise ValueError(f"Duplicate text signal keys detected: {columns}")
