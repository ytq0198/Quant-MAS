"""Training device resolution helpers."""

from __future__ import annotations

import subprocess
import warnings
from dataclasses import dataclass


VALID_TRAINING_DEVICES = {"auto", "cpu", "gpu", "cuda"}


@dataclass(frozen=True)
class ResolvedDevice:
    requested: str
    resolved: str
    fallback: bool
    reason: str | None = None


def resolve_training_device(requested: str) -> ResolvedDevice:
    """Resolve requested training device with safe CPU fallback."""
    normalized = (requested or "cpu").lower()
    if normalized not in VALID_TRAINING_DEVICES:
        raise ValueError(
            f"Unsupported training device {requested!r}; "
            "expected one of auto, cpu, gpu, cuda"
        )

    if normalized == "cpu":
        return ResolvedDevice(requested=normalized, resolved="cpu", fallback=False)

    if normalized == "cuda":
        if is_cuda_available():
            return ResolvedDevice(requested=normalized, resolved="cuda", fallback=False)
        return _fallback(normalized, "cuda requested but unavailable")

    if normalized == "gpu":
        if is_gpu_available():
            return ResolvedDevice(requested=normalized, resolved="gpu", fallback=False)
        return _fallback(normalized, "gpu requested but unavailable")

    if is_cuda_available():
        return ResolvedDevice(requested=normalized, resolved="cuda", fallback=False)
    if is_gpu_available():
        return ResolvedDevice(requested=normalized, resolved="gpu", fallback=False)
    return _fallback(normalized, "auto could not find cuda or gpu")


def is_cuda_available() -> bool:
    """Return whether NVIDIA CUDA appears available.

    This is intentionally lightweight. Detection failures are treated as
    unavailable so local tests and CPU-only machines remain safe.
    """
    try:
        result = subprocess.run(
            ["nvidia-smi"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def is_gpu_available() -> bool:
    """Return whether generic LightGBM GPU training appears available."""
    return is_cuda_available()


def build_lightgbm_device_params(resolved: ResolvedDevice) -> dict[str, str]:
    if resolved.resolved not in {"cpu", "gpu", "cuda"}:
        raise ValueError(f"Unsupported resolved device: {resolved.resolved}")
    return {"device": resolved.resolved}


def _fallback(requested: str, reason: str) -> ResolvedDevice:
    warnings.warn(reason + "; falling back to cpu", RuntimeWarning, stacklevel=2)
    return ResolvedDevice(
        requested=requested,
        resolved="cpu",
        fallback=True,
        reason=reason,
    )

