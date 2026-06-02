"""LightGBM direction model."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import pandas as pd

from quant_mas.models.base import BasePredictiveModel


class LightGBMDirectionModel(BasePredictiveModel):
    """Binary direction classifier backed by LightGBM."""

    def __init__(self, **params: Any) -> None:
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

    def fit(self, features: pd.DataFrame, target: pd.Series) -> "LightGBMDirectionModel":
        try:
            from lightgbm import LGBMClassifier
        except ImportError as exc:
            raise ImportError(
                "LightGBMDirectionModel requires lightgbm. Install it with "
                "`pip install lightgbm` or `pip install -e .[ml]`."
            ) from exc

        self.feature_columns = list(features.columns)
        self.model = LGBMClassifier(**self.params)
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
        }

    def _require_fitted(self) -> None:
        if self.model is None:
            raise ValueError("Model is not fitted")

