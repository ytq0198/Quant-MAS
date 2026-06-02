#!/usr/bin/env bash
# Resilient market data download: one symbol per year, skip existing, merge at end.
#
# Usage (Stooq + API key — recommended when Yahoo rate-limits):
#   cp .env.example .env
#   # edit .env and set STOOQ_API_KEY=...
#   SOURCE=stooq SYMBOLS="AAPL" bash server/download_data_resilient.sh
#
# Environment overrides:
#   SOURCE=stooq|yfinance|auto   (default: stooq)
#   STOOQ_API_KEY=...            (or in repo .env)
#   SYMBOLS="AAPL MSFT" START_YEAR=2018 END_YEAR=2025
#   SLEEP_SECONDS=60
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
STORAGE_CONFIG="${STORAGE_CONFIG:-configs/storage.server.yaml}"
SOURCE="${SOURCE:-stooq}"
SYMBOLS="${SYMBOLS:-AAPL MSFT SPY}"
START_YEAR="${START_YEAR:-2018}"
END_YEAR="${END_YEAR:-2025}"
SLEEP_SECONDS="${SLEEP_SECONDS:-30}"
RETRIES="${RETRIES:-8}"
RETRY_BACKOFF="${RETRY_BACKOFF:-20}"
RATE_LIMIT_BACKOFF="${RATE_LIMIT_BACKOFF:-120}"
JITTER_MIN="${JITTER_MIN:-0}"
JITTER_MAX="${JITTER_MAX:-0}"
INITIAL_COOLDOWN_SECONDS="${INITIAL_COOLDOWN_SECONDS:-0}"

cd "${REPO_DIR}"

if [[ -f "${REPO_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${REPO_DIR}/.env"
  set +a
fi

if [[ "${SOURCE}" == "stooq" || "${SOURCE}" == "auto" ]]; then
  if [[ -z "${STOOQ_API_KEY:-}" ]]; then
    echo "[resilient] ERROR: STOOQ_API_KEY is required for SOURCE=${SOURCE}"
    echo "[resilient] 1) Open https://stooq.com/q/d/?s=aapl.us&get_apikey"
    echo "[resilient] 2) cp .env.example .env && set STOOQ_API_KEY=your_key"
    echo "[resilient] 3) re-run this script"
    exit 1
  fi
fi

RAW_DIR="$(STORAGE_CONFIG="${STORAGE_CONFIG}" python - <<'PY'
from quant_mas.data import DataCatalog
import os
print(DataCatalog.from_yaml(os.environ["STORAGE_CONFIG"]).raw_data_dir)
PY
)"

echo "[resilient] raw dir: ${RAW_DIR}"
echo "[resilient] source: ${SOURCE}"
mkdir -p "${RAW_DIR}"

if [[ "${INITIAL_COOLDOWN_SECONDS}" -gt 0 ]]; then
  echo "[resilient] initial cooldown ${INITIAL_COOLDOWN_SECONDS}s"
  sleep "${INITIAL_COOLDOWN_SECONDS}"
fi

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
    if ! python scripts/download_data.py \
      --symbols "${sym}" \
      --start "${year}-01-01" \
      --end "${next_year}-01-01" \
      --storage-config "${STORAGE_CONFIG}" \
      --filename "${outfile}" \
      --source "${SOURCE}" \
      --skip-existing \
      --retries "${RETRIES}" \
      --retry-backoff "${RETRY_BACKOFF}" \
      --rate-limit-backoff "${RATE_LIMIT_BACKOFF}" \
      --delay 0 \
      --jitter-min "${JITTER_MIN}" \
      --jitter-max "${JITTER_MAX}"; then
      echo "[resilient] WARN failed ${sym} ${year}"
    fi

    echo "[resilient] sleep ${SLEEP_SECONDS}s"
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
