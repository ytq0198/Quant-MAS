"""Dataset helpers for financial text records."""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

from quant_mas.text.data_schema import FinancialTextRecord, parse_record_date


def load_text_records(path: str | Path) -> list[FinancialTextRecord]:
    """Load text records from JSONL or parquet."""
    source = Path(path).expanduser()
    if source.suffix.lower() == ".jsonl":
        records = []
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(FinancialTextRecord.from_dict(json.loads(line)))
        return records
    if source.suffix.lower() == ".parquet":
        frame = pd.read_parquet(source)
        return [
            FinancialTextRecord.from_dict(row)
            for row in frame.to_dict(orient="records")
        ]
    raise ValueError("Text records path must be .jsonl or .parquet")


def split_text_records_by_time(
    records: list[FinancialTextRecord],
    *,
    train_end: str | date,
    val_end: str | date,
) -> tuple[list[FinancialTextRecord], list[FinancialTextRecord], list[FinancialTextRecord]]:
    """Chronologically split text records without random shuffling."""
    train_cutoff = parse_record_date(train_end)
    val_cutoff = parse_record_date(val_end)
    if train_cutoff >= val_cutoff:
        raise ValueError("train_end must be before val_end")
    sorted_records = sorted(records, key=lambda record: (parse_record_date(record.date), record.symbol))
    train = [record for record in sorted_records if parse_record_date(record.date) <= train_cutoff]
    val = [
        record
        for record in sorted_records
        if train_cutoff < parse_record_date(record.date) <= val_cutoff
    ]
    test = [record for record in sorted_records if parse_record_date(record.date) > val_cutoff]
    return train, val, test


def build_synthetic_text_records(
    n_days: int,
    *,
    symbol: str = "AAA",
    start: str | date = "2024-01-01",
) -> list[FinancialTextRecord]:
    """Build deterministic tiny text records for tests and dry-runs."""
    if n_days < 0:
        raise ValueError("n_days must be non-negative")
    start_date = parse_record_date(start)
    records = []
    templates = [
        "earnings improved and guidance is positive",
        "margin pressure and risk remain elevated",
        "neutral update with mixed analyst commentary",
    ]
    for index in range(n_days):
        day = start_date + timedelta(days=index)
        records.append(
            FinancialTextRecord(
                date=day.isoformat(),
                symbol=symbol,
                source="synthetic",
                text=templates[index % len(templates)],
                metadata={"synthetic_index": index},
            )
        )
    return records


def build_text_records_from_features(
    features: pd.DataFrame,
    *,
    date_col: str = "date",
    symbol_col: str = "symbol",
    source: str = "feature_aligned_smoke",
    text_template: str = "{symbol} market headline for {date}",
) -> list[FinancialTextRecord]:
    """Build one text record per feature row for coverage-aligned smoke runs."""
    _require_feature_columns(features, date_col=date_col, symbol_col=symbol_col)
    sorted_frame = features[[date_col, symbol_col]].copy()
    sorted_frame[date_col] = pd.to_datetime(sorted_frame[date_col])
    sorted_frame = sorted_frame.sort_values([symbol_col, date_col]).reset_index(drop=True)

    records: list[FinancialTextRecord] = []
    for row in sorted_frame.itertuples(index=False):
        day = getattr(row, date_col)
        symbol = str(getattr(row, symbol_col))
        day_str = day.date().isoformat() if hasattr(day, "date") else str(day)[:10]
        records.append(
            FinancialTextRecord(
                date=day_str,
                symbol=symbol,
                source=source,
                text=text_template.format(symbol=symbol, date=day_str),
                metadata={"feature_aligned": True},
            )
        )
    return records


def write_text_records_jsonl(records: list[FinancialTextRecord], path: str | Path) -> Path:
    """Write text records as JSONL."""
    output = Path(path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
    return output


def _require_feature_columns(
    features: pd.DataFrame,
    *,
    date_col: str,
    symbol_col: str,
) -> None:
    missing = [column for column in (date_col, symbol_col) if column not in features.columns]
    if missing:
        raise ValueError(f"features missing required columns: {missing}")
    if features.empty:
        raise ValueError("features frame is empty")
