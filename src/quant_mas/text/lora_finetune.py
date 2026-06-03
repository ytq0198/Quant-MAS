"""LoRA fine-tuning skeleton for server-side text experiments."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from quant_mas.text.data_schema import FinancialTextRecord


def train_lora_text_classifier(
    config: dict[str, Any],
    *,
    records: list[FinancialTextRecord],
    output_dir: str | Path,
) -> dict[str, Any]:
    """Train or stub a LoRA text classifier.

    Real LoRA training is intentionally server-only. In mode=mock this writes
    auditable placeholder artifacts without loading transformer weights.
    """
    mode = str(config.get("mode", config.get("text_model", {}).get("mode", "mock")))
    destination = Path(output_dir).expanduser()
    destination.mkdir(parents=True, exist_ok=True)
    if mode != "mock":
        try:
            import accelerate  # noqa: F401
            import peft  # noqa: F401
            import transformers  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                'LoRA text training requires optional dependencies: python -m pip install -e ".[text]"'
            ) from exc
        raise NotImplementedError("Real LoRA training skeleton is server-only TODO.")
    metrics = {
        "mode": "mock",
        "records": len(records),
        "train_loss": 0.0,
        "validation_accuracy": 1.0 if records else 0.0,
    }
    metadata = {
        "model_type": "lora_text_classifier_stub",
        "mode": mode,
        "records": len(records),
        "status": "mock_completed",
    }
    (destination / "metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (destination / "adapter_placeholder.txt").write_text(
        "mock adapter placeholder; no weights stored\n",
        encoding="utf-8",
    )
    return {"metrics": metrics, "artifacts": {"metadata": str(destination / "metadata.json")}}
