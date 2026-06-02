#!/usr/bin/env bash
# Quant MAS server environment setup.
#
# Usage:
#   CONDA_ENV_PREFIX=/mnt/localDisk3/weizian/conda_envs/quant-mas bash server/setup_server.sh
#
# Force recreate:
#   FORCE_RECREATE=1 CONDA_ENV_PREFIX=... bash server/setup_server.sh
set -euo pipefail

REPO_DIR="${REPO_DIR:-$(cd "$(dirname "$0")/.." && pwd)}"
CONDA_ENV_PREFIX="${CONDA_ENV_PREFIX:-/mnt/localDisk3/weizian/conda_envs/quant-mas}"
MIN_PYTHON="3.11"

echo "[setup] repo: ${REPO_DIR}"
echo "[setup] env prefix: ${CONDA_ENV_PREFIX}"

if ! command -v conda >/dev/null 2>&1; then
  echo "[setup] ERROR: conda not found."
  exit 1
fi

# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"

PYTHON="${CONDA_ENV_PREFIX}/bin/python"
PIP() { "${PYTHON}" -m pip "$@"; }

python_major_minor() {
  "${1}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'
}

env_exists() {
  [[ -x "${PYTHON}" ]]
}

needs_recreate=0
if env_exists; then
  EXISTING_PY="$(python_major_minor "${PYTHON}")"
  echo "[setup] existing env Python: ${EXISTING_PY}"
  if [[ "${EXISTING_PY}" != 3.11* ]]; then
    needs_recreate=1
  elif [[ "${FORCE_RECREATE:-0}" == "1" ]]; then
    needs_recreate=1
  fi
fi

if [[ "${needs_recreate}" == "1" ]]; then
  echo "[setup] removing old env at ${CONDA_ENV_PREFIX}"
  rm -rf "${CONDA_ENV_PREFIX}"
fi

if ! env_exists; then
  echo "[setup] creating env (python=${MIN_PYTHON})"
  mkdir -p "$(dirname "${CONDA_ENV_PREFIX}")"
  conda create -p "${CONDA_ENV_PREFIX}" "python=${MIN_PYTHON}" -y
fi

# Force this env's bin first — do NOT rely on bare `pip` (may be ~/.local Python 3.9)
export PATH="${CONDA_ENV_PREFIX}/bin:${PATH}"

PY_VERSION="$(python_major_minor "${PYTHON}")"
echo "[setup] python: ${PYTHON} (${PY_VERSION})"

if [[ "${PY_VERSION}" != 3.11* ]]; then
  echo "[setup] ERROR: need Python 3.11+, got ${PY_VERSION}"
  exit 1
fi

echo "[setup] pip: $("${PYTHON}" -m pip --version)"

cd "${REPO_DIR}"
PIP install --upgrade pip setuptools wheel
PIP install -r requirements.txt
PIP install -e .
PIP install -r requirements-data.txt
PIP install -r requirements-ml.txt

echo ""
echo "[setup] done."
echo "[setup] activate:  conda activate ${CONDA_ENV_PREFIX}"
echo "[setup] verify:    which python && python --version"
echo "[setup] install:   python -m pip install -e .   # never use bare pip"
echo "[setup] test:      python -m pytest -v"
