"""LightGBM direction model."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.models.base import BasePredictiveModel
from quant_mas.utils import (
    ResolvedDevice,
    build_lightgbm_device_params,
    resolve_training_device,
)


class LightGBMDirectionModel(BasePredictiveModel):
    """Binary direction classifier backed by LightGBM."""

    def __init__(
        self,
        device: str = "cpu",
        resolved_device: ResolvedDevice | None = None,
        **params: Any,
    ) -> None:
        configured_device = params.pop("device", device)
        self.params = {
            "objective": "binary",
            "n_estimators": 100,
            "learning_rate": 0.05,
            "num_leaves": 31,
            "random_state": 42,
            "verbosity": -1,
        }
        self.params.update(params)
        self.model: Any | None = None
        self.feature_columns: list[str] = []
        self.device_requested = configured_device
        self.resolved_device: ResolvedDevice | None = resolved_device

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "LightGBMDirectionModel":
        try:
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise ImportError(
                "LightGBMDirectionModel requires lightgbm. Install it with "
                "`pip install lightgbm` or `pip install -e .[ml]`."
            ) from exc

        self.feature_columns = list(features.columns)
        self.resolved_device = resolve_training_device(self.device_requested)
        params = {
            **self.params,
            **build_lightgbm_device_params(self.resolved_device),
        }
        self.model = LGBMClassifier(**params)
        self.model.fit(features, target.astype(int))
        return self

    def predict(self, features: pd.DataFrame) -> pd.Series:
        self._require_fitted()
        predictions = self.model.predict(features.loc[:, self.feature_columns])
        return pd.Series(predictions, index=features.index, name="prediction")

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        self._require_fitted()
        probabilities = self.model.predict_proba(features.loc[:, self.feature_columns])[:, 1]
        return pd.Series(probabilities, index=features.index, name="probability")

    def save(self, path: str | Path) -> Path:
        self._require_fitted()
        target = Path(path).expanduser()
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as file:
            pickle.dump(self, file)
        return target

    @classmethod
    def load(cls, path: str | Path) -> "LightGBMDirectionModel":
        with Path(path).expanduser().open("rb") as file:
            model = pickle.load(file)
        if not isinstance(model, cls):
            raise TypeError(f"Expected {cls.__name__}, got {type(model).__name__}")
        return model

    def metadata(self) -> dict[str, Any]:
        return {
            "model_type": "lightgbm_direction",
            "params": self.params,
            "feature_columns": self.feature_columns,
            "device_requested": self.device_metadata()["device_requested"],
            "device_resolved": self.device_metadata()["device_resolved"],
            "device_fallback": self.device_metadata()["device_fallback"],
            "device_reason": self.device_metadata()["device_reason"],
        }

    def device_metadata(self) -> dict[str, Any]:
        resolved = self.resolved_device or resolve_training_device(self.device_requested)
        return {
            "device_requested": resolved.requested,
            "device_resolved": resolved.resolved,
            "device_fallback": resolved.fallback,
            "device_reason": resolved.reason,
        }

    def feature_importance(self) -> pd.DataFrame:
        self._require_fitted()
        if not hasattr(self.model, "feature_importances_"):
            return pd.DataFrame(
                {"feature": self.feature_columns, "importance": [0.0] * len(self.feature_columns)}
            )
        return pd.DataFrame(
            {
                "feature": self.feature_columns,
                "importance": self.model.feature_importances_,
            }
        ).sort_values("importance", ascending=False, ignore_index=True)

    def _require_fitted(self) -> None:
        if self.model is None:
            raise ValueError("Model is not fitted")
