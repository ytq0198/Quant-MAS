"""Train or run text signal models."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd
import yaml

from quant_mas.text import (
    FinBERTSentimentClassifier,
    MockSentimentClassifier,
    build_synthetic_text_records,
    load_text_records,
    predict_sentiment,
    train_lora_text_classifier,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train text model or generate text signals.")
    parser.add_argument("--config", default="configs/text_model.yaml")
    parser.add_argument(
        "--mode",
        choices=["mock", "finbert_baseline", "lora"],
        default=None,
        help="Text model mode. Defaults to config mode or mock.",
    )
    parser.add_argument("--text-path", help="JSONL/parquet text records path.")
    parser.add_argument("--output-dir", help="Output directory for model metadata.")
    parser.add_argument("--signals-output", help="Output parquet path for text signals.")
    parser.add_argument("--dry-run", action="store_true", help="Use synthetic data if input is absent.")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        config = _load_config(args.config)
        text_config = config.get("text_model", {})
        paths = config.get("paths", {})
        mode = args.mode or text_config.get("mode", "mock")
        text_path = Path(args.text_path or paths.get("text_records", "")).expanduser()
        output_dir = Path(args.output_dir or paths.get("output_dir", "outputs/text_models")).expanduser()
        signals_output = Path(
            args.signals_output or paths.get("signals_output", "outputs/text/signals.parquet")
        ).expanduser()
        records = _load_records(text_path, dry_run=args.dry_run)
        output_dir.mkdir(parents=True, exist_ok=True)

        if mode == "mock":
            classifier = MockSentimentClassifier()
        elif mode == "finbert_baseline":
            classifier = FinBERTSentimentClassifier(
                model_name=text_config.get("model_name", "ProsusAI/finbert"),
                max_length=int(text_config.get("max_length", 128)),
            )
        elif mode == "lora":
            result = train_lora_text_classifier(
                {"mode": "mock" if args.dry_run else "lora", **config},
                records=records,
                output_dir=output_dir,
            )
            metadata_path = output_dir / "text_model_metadata.json"
            metadata_path.write_text(
                json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"Saved LoRA training metadata to {metadata_path}")
            return 0
        else:
            raise ValueError(f"Unknown mode: {mode}")

        signal_name = text_config.get("output_signal_name", "finbert_sentiment")
        signals = predict_sentiment(records, classifier=classifier, signal_name=signal_name)
        frame = _signals_to_frame(signals)
        signals_output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_parquet(signals_output, index=False)
        metadata = {
            "mode": mode,
            "model_id": classifier.model_id,
            "records": len(records),
            "signals": len(frame),
            "signals_output": str(signals_output),
            "dry_run": args.dry_run,
        }
        metadata_path = output_dir / "metadata.json"
        metadata_path.write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        print(f"Saved {len(frame)} text signal rows to {signals_output}")
        return 0
    except ImportError as exc:
        print(f"[text-model] ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"[text-model] ERROR: {exc}", file=sys.stderr)
        return 1


def _load_config(path: str) -> dict:
    config_path = Path(path).expanduser()
    if not config_path.exists():
        return {}
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _load_records(path: Path, *, dry_run: bool):
    if path and path.exists():
        return load_text_records(path)
    if dry_run:
        return build_synthetic_text_records(12, symbol="AAPL", start="2024-01-01")
    raise FileNotFoundError(f"Text records not found: {path}. Use --dry-run for synthetic data.")


def _signals_to_frame(signals) -> pd.DataFrame:
    rows = [signal.to_dict() for signal in signals]
    if not rows:
        return pd.DataFrame(columns=["date", "symbol", "signal_name", "value", "model_id"])
    frame = pd.DataFrame(rows)
    return (
        frame.groupby(["date", "symbol", "signal_name"], as_index=False)
        .agg(value=("value", "mean"), model_id=("model_id", "first"))
        .sort_values(["symbol", "date", "signal_name"])
        .reset_index(drop=True)
    )


if __name__ == "__main__":
    raise SystemExit(main())
