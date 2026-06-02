#!/usr/bin/env bash
# Run pytest on the server and save logs.
# Usage:
#   conda activate quant-mas
#   bash server/run_server_tests.sh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
LOG_DIR="${LOG_DIR:-logs}"

mkdir -p "${REPO_DIR}/${LOG_DIR}"
cd "${REPO_DIR}"

PYTHON="${PYTHON:-python}"
if ! command -v "${PYTHON}" >/dev/null 2>&1; then
  echo "[test] ERROR: ${PYTHON} not found. Run: conda activate quant-mas"
  exit 1
fi

PY_VERSION="$("${PYTHON}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
echo "[test] python: $(command -v "${PYTHON}") (${PY_VERSION})"

if [[ "${PY_VERSION}" != 3.11* ]]; then
  echo "[test] WARNING: expected Python 3.11.x in quant-mas env, got ${PY_VERSION}"
  echo "[test] Run: conda activate quant-mas"
fi

echo "[test] running pytest via python -m pytest..."
"${PYTHON}" -m pytest -v 2>&1 | tee "${LOG_DIR}/server_pytest.log"
echo "[test] log saved to ${LOG_DIR}/server_pytest.log"
