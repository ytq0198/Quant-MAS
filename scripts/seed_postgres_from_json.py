"""Import experiment records from JSON into Postgres memory (EXP-026 smoke helper)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from quant_mas.memory import ExperimentMemory, create_memory_store


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seed PostgresMemoryStore from experiments JSON (one-time smoke import)."
    )
    parser.add_argument(
        "--json-path",
        default="/mnt/localDisk3/weizian/reports/experiments.json",
        help="Source experiments JSON.",
    )
    parser.add_argument("--postgres-dsn", help="Postgres DSN; defaults to POSTGRES_DSN env.")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip records whose experiment_id already exists in Postgres.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    json_path = Path(args.json_path).expanduser()
    if not json_path.exists():
        print(f"[seed] ERROR: JSON not found: {json_path}", file=sys.stderr)
        return 1
    try:
        source = ExperimentMemory(json_path)
        store = create_memory_store("postgres", postgres_dsn=args.postgres_dsn)
    except Exception as exc:
        print(f"[seed] ERROR: {exc}", file=sys.stderr)
        return 1

    existing_ids: set[str] = set()
    if args.skip_existing:
        existing_ids = {record.experiment_id for record in store.list()}

    imported = 0
    skipped = 0
    for record in source.list():
        if record.experiment_id in existing_ids:
            skipped += 1
            continue
        store.add(
            name=record.name,
            status=record.status,
            metrics=record.metrics,
            artifacts=record.artifacts,
            params=record.params,
            notes=record.notes,
            experiment_id=record.experiment_id,
        )
        imported += 1

    print(f"[seed] source={json_path} imported={imported} skipped={skipped}")
    try:
        best = store.find_best("oos.sharpe")
        oos = best.metrics.get("oos", {})
        sharpe = oos.get("sharpe") if isinstance(oos, dict) else None
        print(f"[seed] best oos.sharpe -> {best.name!r} sharpe={sharpe}")
    except ValueError as exc:
        print(f"[seed] WARN: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
