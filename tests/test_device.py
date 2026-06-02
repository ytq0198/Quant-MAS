from __future__ import annotations

import pytest

import quant_mas.utils.device as device_module
from quant_mas.utils import build_lightgbm_device_params, resolve_training_device


def test_auto_prefers_cuda_when_available(monkeypatch) -> None:
    monkeypatch.setattr(device_module, "is_cuda_available", lambda: True)
    monkeypatch.setattr(device_module, "is_gpu_available", lambda: True)

    resolved = resolve_training_device("auto")

    assert resolved.resolved == "cuda"
    assert resolved.fallback is False


def test_auto_falls_back_to_gpu_when_cuda_unavailable(monkeypatch) -> None:
    monkeypatch.setattr(device_module, "is_cuda_available", lambda: False)
    monkeypatch.setattr(device_module, "is_gpu_available", lambda: True)

    resolved = resolve_training_device("auto")

    assert resolved.resolved == "gpu"
    assert resolved.fallback is False


def test_auto_falls_back_to_cpu_when_no_gpu_available(monkeypatch) -> None:
    monkeypatch.setattr(device_module, "is_cuda_available", lambda: False)
    monkeypatch.setattr(device_module, "is_gpu_available", lambda: False)

    with pytest.warns(RuntimeWarning, match="falling back to cpu"):
        resolved = resolve_training_device("auto")

    assert resolved.resolved == "cpu"
    assert resolved.fallback is True
    assert resolved.reason == "auto could not find cuda or gpu"


def test_requested_cpu_forces_cpu(monkeypatch) -> None:
    monkeypatch.setattr(device_module, "is_cuda_available", lambda: True)
    monkeypatch.setattr(device_module, "is_gpu_available", lambda: True)

    resolved = resolve_training_device("cpu")

    assert resolved.requested == "cpu"
    assert resolved.resolved == "cpu"
    assert resolved.fallback is False


def test_requested_cuda_unavailable_falls_back_cpu(monkeypatch) -> None:
    monkeypatch.setattr(device_module, "is_cuda_available", lambda: False)

    with pytest.warns(RuntimeWarning, match="cuda requested but unavailable"):
        resolved = resolve_training_device("cuda")

    assert resolved.resolved == "cpu"
    assert resolved.fallback is True
    assert resolved.reason == "cuda requested but unavailable"


def test_requested_gpu_unavailable_falls_back_cpu(monkeypatch) -> None:
    monkeypatch.setattr(device_module, "is_gpu_available", lambda: False)

    with pytest.warns(RuntimeWarning, match="gpu requested but unavailable"):
        resolved = resolve_training_device("gpu")

    assert resolved.resolved == "cpu"
    assert resolved.fallback is True
    assert resolved.reason == "gpu requested but unavailable"


@pytest.mark.parametrize(
    ("requested", "expected"),
    [
        ("cpu", {"device": "cpu"}),
        ("gpu", {"device": "gpu"}),
        ("cuda", {"device": "cuda"}),
    ],
)
def test_build_lightgbm_device_params(requested: str, expected: dict[str, str]) -> None:
    resolved = device_module.ResolvedDevice(
        requested=requested,
        resolved=requested,
        fallback=False,
    )

    assert build_lightgbm_device_params(resolved) == expected


def test_invalid_requested_device_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported training device"):
        resolve_training_device("tpu")

