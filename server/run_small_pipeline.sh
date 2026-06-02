#!/usr/bin/env bash
# Run a small real-data pipeline on the server.
# Usage:
#   conda activate quant-mas
#   cp configs/storage.server.yaml.example configs/storage.server.yaml  # edit <USER> first
#   bash server/run_small_pipeline.sh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
STORAGE_CONFIG="${STORAGE_CONFIG:-configs/storage.server.yaml}"
SYMBOLS="${SYMBOLS:-AAPL MSFT SPY}"
START="${START:-2018-01-01}"
END="${END:-2025-12-31}"
EXPERIMENT_NAME="${EXPERIMENT_NAME:-server_small_pipeline}"

cd "${REPO_DIR}"

python scripts/run_pipeline.py \
  --symbols ${SYMBOLS} \
  --start "${START}" \
  --end "${END}" \
  --storage-config "${STORAGE_CONFIG}" \
  --experiment-name "${EXPERIMENT_NAME}"

echo "[pipeline] finished: ${EXPERIMENT_NAME}"
