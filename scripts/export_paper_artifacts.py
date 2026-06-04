"""Export paper-grade experiment tables and audit summaries."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from quant_mas.research.paper_artifacts import export_paper_artifacts  # noqa: E402


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export paper-grade Quant MAS experiment artifacts.",
    )
    parser.add_argument(
        "--memory-path",
        required=True,
        type=Path,
        help="Path to ExperimentMemory JSON file.",
    )
    parser.add_argument(
        "--audit-dir",
        type=Path,
        default=None,
        help="Optional directory containing M13 audit.jsonl files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/paper"),
        help="Directory for paper CSV/Markdown/JSON outputs.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = export_paper_artifacts(
            memory_path=args.memory_path,
            audit_dir=args.audit_dir,
            output_dir=args.output_dir,
        )
    except Exception as exc:
        print(f"[paper] ERROR: {exc}", file=sys.stderr)
        return 1
    for key, value in result.items():
        print(f"[paper] {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
