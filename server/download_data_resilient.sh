#!/usr/bin/env bash
# Resilient yfinance download: one symbol per year, skip existing, long sleeps, merge at end.
#
# Usage:
#   conda activate /mnt/localDisk3/weizian/conda_envs/quant-mas
#   cd /mnt/localDisk3/weizian/Quant-MAS
#   bash server/download_data_resilient.sh
#
# Environment overrides:
#   SYMBOLS="AAPL MSFT" START_YEAR=2018 END_YEAR=2025 SLEEP_SECONDS=90
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
STORAGE_CONFIG="${STORAGE_CONFIG:-configs/storage.server.yaml}"
SYMBOLS="${SYMBOLS:-AAPL MSFT SPY}"
START_YEAR="${START_YEAR:-2018}"
END_YEAR="${END_YEAR:-2025}"
SLEEP_SECONDS="${SLEEP_SECONDS:-60}"
RETRIES="${RETRIES:-8}"
RETRY_BACKOFF="${RETRY_BACKOFF:-20}"
JITTER_MIN="${JITTER_MIN:-30}"
JITTER_MAX="${JITTER_MAX:-60}"

cd "${REPO_DIR}"

RAW_DIR="$(STORAGE_CONFIG="${STORAGE_CONFIG}" python - <<'PY'
from quant_mas.data import DataCatalog
import os
print(DataCatalog.from_yaml(os.environ["STORAGE_CONFIG"]).raw_data_dir)
PY
)"

echo "[resilient] raw dir: ${RAW_DIR}"
mkdir -p "${RAW_DIR}"

for sym in ${SYMBOLS}; do
  for year in $(seq "${START_YEAR}" "${END_YEAR}"); do
    outfile="${sym}_${year}.parquet"
    outpath="${RAW_DIR}/${outfile}"

    if [[ -f "${outpath}" ]]; then
      echo "[resilient] skip existing ${outpath}"
      continue
    fi

    next_year=$((year + 1))
    echo "[resilient] download ${sym} ${year}-01-01 -> ${next_year}-01-01"
    python scripts/download_data.py \
      --symbols "${sym}" \
      --start "${year}-01-01" \
      --end "${next_year}-01-01" \
      --storage-config "${STORAGE_CONFIG}" \
      --filename "${outfile}" \
      --retries "${RETRIES}" \
      --retry-backoff "${RETRY_BACKOFF}" \
      --delay 0 \
      --jitter-min "${JITTER_MIN}" \
      --jitter-max "${JITTER_MAX}" \
      || echo "[resilient] WARN failed ${sym} ${year}, continue"

    echo "[resilient] sleep ${SLEEP_SECONDS}s before next request"
    sleep "${SLEEP_SECONDS}"
  done
done

echo "[resilient] merging chunks -> market_data.parquet"
python scripts/merge_parquet.py \
  --input-dir "${RAW_DIR}" \
  --pattern "*_*.parquet" \
  --exclude market_data.parquet \
  --output "${RAW_DIR}/market_data.parquet"

echo "[resilient] done: ${RAW_DIR}/market_data.parquet"
