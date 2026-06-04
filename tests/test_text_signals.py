from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest

from quant_mas.features import merge_text_signals_into_features, summarize_text_signal_coverage
from quant_mas.text import (
    FinancialTextRecord,
    MockSentimentClassifier,
    TextSignalRecord,
    build_synthetic_text_records,
    load_text_records,
    predict_sentiment,
    split_text_records_by_time,
    train_lora_text_classifier,
)


def test_text_record_schema_round_trip() -> None:
    record = FinancialTextRecord(
        date="2024-01-01",
        symbol="AAA",
        source="synthetic",
        text="positive earnings",
        metadata={"id": 1},
    )
    signal = TextSignalRecord(
        date="2024-01-01",
        symbol="AAA",
        signal_name="finbert_sentiment",
        value=0.5,
        model_id="mock",
    )

    assert FinancialTextRecord.from_dict(record.to_dict()) == record
    assert TextSignalRecord.from_dict(signal.to_dict()) == signal


def test_split_text_records_by_time_is_chronological() -> None:
    records = [
        FinancialTextRecord("2024-03-01", "AAA", "synthetic", "c", {}),
        FinancialTextRecord("2024-01-01", "AAA", "synthetic", "a", {}),
        FinancialTextRecord("2024-02-01", "AAA", "synthetic", "b", {}),
    ]

    train, val, test = split_text_records_by_time(
        records,
        train_end="2024-01-31",
        val_end="2024-02-15",
    )

    assert [item.text for item in train] == ["a"]
    assert [item.text for item in val] == ["b"]
    assert [item.text for item in test] == ["c"]


def test_mock_sentiment_classifier_is_deterministic() -> None:
    classifier = MockSentimentClassifier()

    first = classifier.predict(["same text", "other text"])
    second = classifier.predict(["same text", "other text"])

    assert first == second
    assert all(-1.0 <= score <= 1.0 for score in first)


def test_predict_sentiment_generates_signal_records() -> None:
    records = build_synthetic_text_records(3, symbol="AAA")

    signals = predict_sentiment(records, classifier=MockSentimentClassifier())

    assert len(signals) == 3
    assert {signal.signal_name for signal in signals} == {"finbert_sentiment"}
    assert {signal.symbol for signal in signals} == {"AAA"}


def test_merge_text_signals_adds_columns_without_row_growth() -> None:
    features = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "symbol": ["AAA", "AAA"],
            "close": [10.0, 11.0],
        }
    )
    signals = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "symbol": ["AAA", "AAA"],
            "signal_name": ["finbert_sentiment", "finbert_sentiment"],
            "value": [0.1, -0.2],
            "model_id": ["mock", "mock"],
        }
    )

    merged = merge_text_signals_into_features(features, signals)

    assert len(merged) == len(features)
    assert "finbert_sentiment" in merged.columns
    assert merged["finbert_sentiment"].tolist() == [0.1, -0.2]


def test_merge_text_signals_rejects_future_leakage() -> None:
    features = pd.DataFrame(
        {"date": ["2024-01-01"], "symbol": ["AAA"], "close": [10.0]}
    )
    signals = pd.DataFrame(
        {
            "date": ["2024-01-02"],
            "symbol": ["AAA"],
            "finbert_sentiment": [0.5],
        }
    )

    with pytest.raises(ValueError, match="Future text leakage"):
        merge_text_signals_into_features(features, signals)


def test_merge_text_signals_rejects_duplicate_keys() -> None:
    features = pd.DataFrame(
        {"date": ["2024-01-01"], "symbol": ["AAA"], "close": [10.0]}
    )
    signals = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-01"],
            "symbol": ["AAA", "AAA"],
            "finbert_sentiment": [0.1, 0.2],
        }
    )

    with pytest.raises(ValueError, match="Duplicate"):
        merge_text_signals_into_features(features, signals)


def test_summarize_text_signal_coverage_reports_match_rate() -> None:
    features = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-01", "2024-01-02"]
            ),
            "symbol": ["AAA", "AAA", "BBB", "BBB"],
            "close": [10.0, 11.0, 20.0, 21.0],
        }
    )
    signals = pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "symbol": ["AAA", "BBB"],
            "signal_name": ["finbert_sentiment", "finbert_sentiment"],
            "value": [0.4, -0.3],
            "model_id": ["mock", "mock"],
        }
    )

    summary = summarize_text_signal_coverage(features, signals)

    assert summary["feature_rows"] == 4
    assert summary["signal_rows"] == 2
    assert summary["matched_rows"] == 2
    assert summary["coverage_ratio"] == 0.5
    assert summary["matched_symbols"] == ["AAA", "BBB"]
    assert summary["column_coverage"]["finbert_sentiment"]["matched_rows"] == 2


def test_load_text_records_jsonl_and_write_signal_parquet(tmp_path: Path) -> None:
    records = build_synthetic_text_records(4, symbol="AAA")
    jsonl_path = tmp_path / "records.jsonl"
    jsonl_path.write_text(
        "\n".join(json.dumps(record.to_dict()) for record in records) + "\n",
        encoding="utf-8",
    )

    loaded = load_text_records(jsonl_path)
    signals = predict_sentiment(loaded, classifier=MockSentimentClassifier())
    signal_path = tmp_path / "signals.parquet"
    pd.DataFrame([signal.to_dict() for signal in signals]).to_parquet(signal_path, index=False)

    assert len(loaded) == 4
    assert signal_path.exists()
    assert len(pd.read_parquet(signal_path)) == 4


def test_lora_mock_training_writes_metadata(tmp_path: Path) -> None:
    result = train_lora_text_classifier(
        {"mode": "mock"},
        records=build_synthetic_text_records(2),
        output_dir=tmp_path / "lora",
    )

    assert result["metrics"]["mode"] == "mock"
    assert Path(result["artifacts"]["metadata"]).exists()


def test_train_text_model_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/train_text_model.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--mode" in result.stdout


def test_audit_text_signals_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/audit_text_signals.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--features-path" in result.stdout


def test_audit_text_signals_cli_writes_artifacts(tmp_path: Path) -> None:
    features_path = tmp_path / "features.parquet"
    signals_path = tmp_path / "signals.parquet"
    output_dir = tmp_path / "audit"
    pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "symbol": ["AAA", "AAA"],
            "close": [10.0, 11.0],
        }
    ).to_parquet(features_path, index=False)
    pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "symbol": ["AAA"],
            "finbert_sentiment": [0.25],
        }
    ).to_parquet(signals_path, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_text_signals.py",
            "--features-path",
            str(features_path),
            "--signals-path",
            str(signals_path),
            "--output-dir",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
    assert metrics["coverage_ratio"] == 0.5
    assert (output_dir / "summary.md").exists()


def test_audit_text_signals_cli_fails_under_coverage_threshold(tmp_path: Path) -> None:
    features_path = tmp_path / "features.parquet"
    signals_path = tmp_path / "signals.parquet"
    pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "symbol": ["AAA", "AAA"],
            "close": [10.0, 11.0],
        }
    ).to_parquet(features_path, index=False)
    pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "symbol": ["AAA"],
            "finbert_sentiment": [0.25],
        }
    ).to_parquet(signals_path, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_text_signals.py",
            "--features-path",
            str(features_path),
            "--signals-path",
            str(signals_path),
            "--output-dir",
            str(tmp_path / "audit"),
            "--fail-under-coverage",
            "0.75",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "coverage below threshold" in result.stderr


def test_train_text_model_mock_dry_run(tmp_path: Path) -> None:
    signals_output = tmp_path / "signals.parquet"
    output_dir = tmp_path / "model"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/train_text_model.py",
            "--mode",
            "mock",
            "--config",
            "configs/text_model.yaml",
            "--output-dir",
            str(output_dir),
            "--signals-output",
            str(signals_output),
            "--dry-run",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert signals_output.exists()
    assert (output_dir / "metadata.json").exists()
