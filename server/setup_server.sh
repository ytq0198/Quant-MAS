#!/usr/bin/env bash
# Quant MAS server environment setup.
# Usage: bash server/setup_server.sh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
ENV_NAME="${ENV_NAME:-quant-mas}"

echo "[setup] repo: ${REPO_DIR}"

if ! command -v conda >/dev/null 2>&1; then
  echo "[setup] ERROR: conda not found. Install Miniconda/Anaconda first."
  exit 1
fi

# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"

if conda env list | awk '{print $1}' | grep -qx "${ENV_NAME}"; then
  echo "[setup] conda env '${ENV_NAME}' already exists"
else
  conda create -n "${ENV_NAME}" python=3.11 -y
fi

conda activate "${ENV_NAME}"
python --version
pip --version

cd "${REPO_DIR}"
pip install -r requirements.txt
pip install -e .

echo "[setup] done. Activate with: conda activate ${ENV_NAME}"
