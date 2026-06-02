"""Utility package."""

from quant_mas.utils.device import (
    ResolvedDevice,
    build_lightgbm_device_params,
    is_cuda_available,
    is_gpu_available,
    resolve_training_device,
)

__all__ = [
    "ResolvedDevice",
    "build_lightgbm_device_params",
    "is_cuda_available",
    "is_gpu_available",
    "resolve_training_device",
]

