#!/usr/bin/env bash
# Quant MAS server environment setup.
#
# Usage:
#   bash server/setup_server.sh
#
# Custom conda env prefix (recommended on this server):
#   CONDA_ENV_PREFIX=/mnt/localDisk3/weizian/conda_envs/quant-mas bash server/setup_server.sh
#
# Force recreate if Python != 3.11:
#   FORCE_RECREATE=1 CONDA_ENV_PREFIX=... bash server/setup_server.sh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
ENV_NAME="${ENV_NAME:-quant-mas}"
CONDA_ENV_PREFIX="${CONDA_ENV_PREFIX:-/mnt/localDisk3/weizian/conda_envs/quant-mas}"
MIN_PYTHON="3.11"

echo "[setup] repo: ${REPO_DIR}"
echo "[setup] env prefix: ${CONDA_ENV_PREFIX}"

if ! command -v conda >/dev/null 2>&1; then
  echo "[setup] ERROR: conda not found. Install Miniconda/Anaconda first."
  exit 1
fi

# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"

env_exists() {
  [[ -d "${CONDA_ENV_PREFIX}/bin" ]]
}

python_major_minor() {
  "${1}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
}

needs_recreate=0
if env_exists; then
  EXISTING_PY="$(python_major_minor "${CONDA_ENV_PREFIX}/bin/python" 2>/dev/null || echo "0.0")"
  echo "[setup] existing env Python: ${EXISTING_PY}"
  if [[ "${EXISTING_PY}" != 3.11* ]]; then
    echo "[setup] ERROR: env exists but Python is ${EXISTING_PY}, need ${MIN_PYTHON}+"
    needs_recreate=1
  elif [[ "${FORCE_RECREATE:-0}" == "1" ]]; then
    needs_recreate=1
  else
    echo "[setup] env already exists with Python ${EXISTING_PY}"
  fi
fi

if [[ "${needs_recreate}" == "1" ]]; then
  echo "[setup] removing old env at ${CONDA_ENV_PREFIX}"
  conda deactivate 2>/dev/null || true
  rm -rf "${CONDA_ENV_PREFIX}"
fi

if ! env_exists; then
  echo "[setup] creating env: ${CONDA_ENV_PREFIX} (python=${MIN_PYTHON})"
  mkdir -p "$(dirname "${CONDA_ENV_PREFIX}")"
  conda create -p "${CONDA_ENV_PREFIX}" "python=${MIN_PYTHON}" -y
fi

conda activate "${CONDA_ENV_PREFIX}"

PY_VERSION="$(python_major_minor python)"
echo "[setup] active python: $(which python) (${PY_VERSION})"

if [[ "${PY_VERSION}" != 3.11* ]]; then
  echo "[setup] ERROR: active Python is ${PY_VERSION}, project requires >=3.11"
  echo "[setup] Run: FORCE_RECREATE=1 bash server/setup_server.sh"
  exit 1
fi

pip --version

cd "${REPO_DIR}"
pip install -r requirements.txt
pip install -e ".[data,ml]"

echo ""
echo "[setup] done."
echo "[setup] activate with:"
echo "  conda activate ${CONDA_ENV_PREFIX}"
echo "[setup] run tests with:"
echo "  python -m pytest -v"
