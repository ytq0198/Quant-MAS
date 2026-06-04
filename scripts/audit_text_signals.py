"""Audit text signal coverage before text-enhanced walk-forward experiments."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.features import summarize_text_signal_coverage


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit text signal coverage against a feature table."
    )
    parser.add_argument("--features-path", required=True, help="Feature parquet path.")
    parser.add_argument("--signals-path", required=True, help="Text signals parquet path.")
    parser.add_argument(
        "--signal-column",
        action="append",
        dest="signal_columns",
        help="Signal column to audit; repeat for multiple columns.",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs/reports/text_signal_audit",
        help="Directory for metrics.json and summary.md.",
    )
    parser.add_argument(
        "--fail-under-coverage",
        type=float,
        default=None,
        help="Exit non-zero if overall coverage_ratio is below this threshold.",
    )
    args = parser.parse_args()

    try:
        metrics = audit_text_signals(
            features_path=Path(args.features_path),
            signals_path=Path(args.signals_path),
            output_dir=Path(args.output_dir),
            signal_columns=args.signal_columns,
            fail_under_coverage=args.fail_under_coverage,
        )
    except Exception as exc:  # noqa: BLE001 - CLI should print clean failures.
        print(f"[text-signal-audit] ERROR: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


def audit_text_signals(
    *,
    features_path: Path,
    signals_path: Path,
    output_dir: Path,
    signal_columns: list[str] | None = None,
    fail_under_coverage: float | None = None,
) -> dict[str, Any]:
    """Load local parquet files, summarize coverage, and write audit artifacts."""
    features = pd.read_parquet(features_path.expanduser())
    signals = pd.read_parquet(signals_path.expanduser())
    metrics = summarize_text_signal_coverage(
        features,
        signals,
        signal_columns=signal_columns,
    )
    metrics["features_path"] = str(features_path)
    metrics["signals_path"] = str(signals_path)

    output_dir = output_dir.expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "metrics.json"
    summary_path = output_dir / "summary.md"
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    summary_path.write_text(_summary_markdown(metrics), encoding="utf-8")
    metrics["artifacts"] = {
        "metrics": str(metrics_path),
        "summary": str(summary_path),
    }

    if fail_under_coverage is not None and metrics["coverage_ratio"] < fail_under_coverage:
        raise ValueError(
            "text signal coverage below threshold: "
            f"{metrics['coverage_ratio']:.4f} < {fail_under_coverage:.4f}"
        )
    return metrics


def _summary_markdown(metrics: dict[str, Any]) -> str:
    lines = [
        "# Text Signal Coverage Audit",
        "",
        f"- feature_rows: {metrics['feature_rows']}",
        f"- signal_rows: {metrics['signal_rows']}",
        f"- matched_rows: {metrics['matched_rows']}",
        f"- coverage_ratio: {metrics['coverage_ratio']:.6f}",
        f"- matched_symbol_count: {metrics['matched_symbol_count']}",
        f"- feature_date_range: {metrics['feature_start_date']} -> {metrics['feature_end_date']}",
        f"- signal_date_range: {metrics['signal_start_date']} -> {metrics['signal_end_date']}",
        "",
        "| Signal | Matched Rows | Coverage |",
        "|--------|--------------|----------|",
    ]
    for name, item in metrics["column_coverage"].items():
        lines.append(
            f"| {name} | {item['matched_rows']} | {item['coverage_ratio']:.6f} |"
        )
    lines.extend(
        [
            "",
            "This audit only measures local feature/signal alignment. It is not an OOS result.",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
