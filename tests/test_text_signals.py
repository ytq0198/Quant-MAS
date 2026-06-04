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
    RealNewsRecord,
    TextSignalRecord,
    align_real_news_to_features,
    build_synthetic_text_records,
    build_text_records_from_features,
    load_real_news_records,
    load_text_records,
    predict_sentiment,
    split_text_records_by_time,
    train_lora_text_classifier,
    write_text_records_jsonl,
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


def test_real_news_record_round_trip() -> None:
    payload = {
        "published_at": "2024-01-02T15:30:00",
        "symbol": "aapl",
        "source": "fixture",
        "title": "Apple reports stronger demand",
        "text": "Analysts revised expectations upward.",
        "url": "https://example.com/aapl",
        "metadata": {"provider": "synthetic"},
    }

    record = RealNewsRecord.from_dict(payload)

    assert record.symbol == "AAPL"
    assert record.to_dict()["metadata"]["provider"] == "synthetic"


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


def test_align_real_news_after_close_to_next_feature_bar() -> None:
    features = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "symbol": ["AAPL", "AAPL"],
            "close": [100.0, 101.0],
        }
    )
    records = [
        RealNewsRecord(
            published_at="2024-01-02T16:30:00",
            symbol="AAPL",
            source="fixture",
            title="After close headline",
        )
    ]

    aligned, audit = align_real_news_to_features(records, features, market_close="16:00")

    assert aligned[0].date == "2024-01-03"
    assert aligned[0].metadata["published_at"] == "2024-01-02T16:30:00"
    assert audit["aligned_records"] == 1
    assert audit["dropped_records"] == 0


def test_align_real_news_before_close_same_feature_bar() -> None:
    features = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "symbol": ["AAPL", "AAPL"],
            "close": [100.0, 101.0],
        }
    )
    records = [
        RealNewsRecord(
            published_at="2024-01-02T09:00:00",
            symbol="AAPL",
            source="fixture",
            title="Premarket headline",
        )
    ]

    aligned, _ = align_real_news_to_features(records, features, market_close="16:00")

    assert aligned[0].date == "2024-01-02"


def test_align_real_news_audits_unknown_symbol_and_no_future_bar() -> None:
    features = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02"]),
            "symbol": ["AAPL"],
            "close": [100.0],
        }
    )
    records = [
        RealNewsRecord("2024-01-02T10:00:00", "MSFT", "fixture", "Unknown symbol"),
        RealNewsRecord("2024-01-02T17:00:00", "AAPL", "fixture", "No future bar"),
    ]

    aligned, audit = align_real_news_to_features(records, features, market_close="16:00")

    assert aligned == []
    assert audit["dropped_records"] == 2
    assert audit["dropped_reasons"] == {"unknown_symbol": 1, "no_future_bar": 1}


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


def test_build_text_records_from_features_matches_feature_rows() -> None:
    features = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-01", "2024-01-01"]),
            "symbol": ["AAA", "AAA", "BBB"],
            "close": [11.0, 10.0, 20.0],
        }
    )

    records = build_text_records_from_features(features)

    assert len(records) == 3
    assert records[0].symbol == "AAA"
    assert records[0].date == "2024-01-01"
    assert records[-1].symbol == "BBB"
    assert records[-1].metadata["feature_aligned"] is True


def test_write_text_records_jsonl_round_trip(tmp_path: Path) -> None:
    records = build_synthetic_text_records(2, symbol="AAA")
    jsonl_path = tmp_path / "records.jsonl"
    write_text_records_jsonl(records, jsonl_path)
    loaded = load_text_records(jsonl_path)
    assert loaded == records


def test_build_text_records_from_features_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/build_text_records_from_features.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--features-path" in result.stdout


def test_build_text_records_from_features_cli_writes_jsonl(tmp_path: Path) -> None:
    features_path = tmp_path / "features.parquet"
    output_path = tmp_path / "news_wf002.jsonl"
    pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "symbol": ["AAA", "AAA"],
            "close": [10.0, 11.0],
        }
    ).to_parquet(features_path, index=False)

    result = subprocess.run(
        [
            sys.executable,
            "scripts/build_text_records_from_features.py",
            "--features-path",
            str(features_path),
            "--output-path",
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert output_path.exists()
    loaded = load_text_records(output_path)
    assert len(loaded) == 2


def test_align_real_news_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/align_real_news.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--news-path" in result.stdout


def test_align_real_news_cli_writes_aligned_jsonl(tmp_path: Path) -> None:
    features_path = tmp_path / "features.parquet"
    news_path = tmp_path / "real_news.jsonl"
    output_dir = tmp_path / "aligned"
    pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-02", "2024-01-03"]),
            "symbol": ["AAPL", "AAPL"],
            "close": [100.0, 101.0],
        }
    ).to_parquet(features_path, index=False)
    news_path.write_text(
        json.dumps(
            {
                "published_at": "2024-01-02T17:15:00",
                "symbol": "AAPL",
                "source": "fixture",
                "title": "Apple after close headline",
                "text": "Full text body",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/align_real_news.py",
            "--news-path",
            str(news_path),
            "--features-path",
            str(features_path),
            "--output-dir",
            str(output_dir),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    aligned = load_text_records(output_dir / "aligned_news.jsonl")
    assert len(aligned) == 1
    assert aligned[0].date == "2024-01-03"
    assert (output_dir / "alignment_metrics.json").exists()
    assert (output_dir / "summary.md").exists()


def test_load_real_news_records_jsonl(tmp_path: Path) -> None:
    news_path = tmp_path / "real_news.jsonl"
    news_path.write_text(
        json.dumps(
            {
                "published_at": "2024-01-02T10:00:00",
                "symbol": "AAPL",
                "source": "fixture",
                "title": "Apple headline",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    records = load_real_news_records(news_path)

    assert len(records) == 1
    assert records[0].symbol == "AAPL"


def test_real_news_documented_sample_matches_schema() -> None:
    records = load_real_news_records("docs/examples/real_news_wf003.sample.jsonl")

    assert len(records) == 2
    assert records[0].source == "example_news_provider"
    assert records[1].published_at.endswith("17:30:00")


def test_parse_finnhub_news_item_maps_fields() -> None:
    from quant_mas.text.finnhub_news import parse_finnhub_news_item

    record = parse_finnhub_news_item(
        {
            "datetime": 1615813200,
            "headline": "Apple beats estimates",
            "summary": "Revenue grew year over year.",
            "source": "CNBC",
            "url": "https://example.com/aapl",
            "id": 42,
            "category": "company",
        },
        symbol="aapl",
    )

    assert record.symbol == "AAPL"
    assert record.source == "finnhub:CNBC"
    assert record.title == "Apple beats estimates"
    assert record.metadata["finnhub_id"] == 42


def test_iter_date_chunks_splits_month_windows() -> None:
    from quant_mas.text.finnhub_news import iter_date_chunks

    chunks = iter_date_chunks("2018-01-15", "2018-03-10", chunk_months=1)

    assert chunks == [
        ("2018-01-15", "2018-01-31"),
        ("2018-02-01", "2018-02-28"),
        ("2018-03-01", "2018-03-10"),
    ]


def test_fetch_finnhub_company_news_records_mock_http(monkeypatch: pytest.MonkeyPatch) -> None:
    from quant_mas.text.finnhub_news import fetch_finnhub_company_news_records

    calls: list[str] = []

    def fake_urlopen(url, timeout=60.0):
        calls.append(str(url))
        payload = [
            {
                "datetime": 1514764800,
                "headline": "Headline",
                "summary": "Summary",
                "source": "Yahoo",
                "url": "https://example.com/1",
                "id": 1,
            }
        ]
        return FakeFinnhubResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    records = fetch_finnhub_company_news_records(
        ["AAPL"],
        start="2018-01-01",
        end="2018-01-31",
        api_key="test-key",
        chunk_months=1,
        delay_seconds=0,
        progress=False,
    )

    assert len(records) == 1
    assert records[0].symbol == "AAPL"
    assert "company-news" in calls[0]


def test_fetch_real_news_cli_help() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/fetch_real_news.py", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "--output-path" in result.stdout


class FakeFinnhubResponse:
    def __init__(self, payload: list[dict]) -> None:
        self.payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self.payload

    def __enter__(self) -> FakeFinnhubResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None
