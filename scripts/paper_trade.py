"""Run paper trading.

Placeholder CLI for the project skeleton. Implementation comes in a later phase.
"""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run paper trading.")
    parser.add_argument("--config", default="configs/risk.yaml", help="Risk config path.")
    return parser


def main() -> None:
    parser = build_parser()
    parser.parse_args()
    parser.exit(status=0, message="paper_trade is not implemented yet.\n")


if __name__ == "__main__":
    main()

