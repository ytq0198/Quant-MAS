#!/usr/bin/env bash
# Run pytest on the server and save logs.
# Usage:
#   conda activate quant-mas
#   bash server/run_server_tests.sh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
STORAGE_CONFIG="${STORAGE_CONFIG:-configs/storage.server.yaml}"
LOG_DIR="${LOG_DIR:-logs}"

mkdir -p "${REPO_DIR}/${LOG_DIR}"
cd "${REPO_DIR}"

echo "[test] running pytest..."
pytest 2>&1 | tee "${LOG_DIR}/server_pytest.log"
echo "[test] log saved to ${LOG_DIR}/server_pytest.log"
