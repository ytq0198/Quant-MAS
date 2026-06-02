"""Predictive model abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import pandas as pd


class BasePredictiveModel(ABC):
    """Base interface for supervised predictive models."""

    @abstractmethod
    def fit(self, features: pd.DataFrame, target: pd.Series) -> "BasePredictiveModel":
        """Fit model on features and target."""

    @abstractmethod
    def predict(self, features: pd.DataFrame) -> pd.Series:
        """Predict labels for features."""

    def predict_proba(self, features: pd.DataFrame) -> pd.Series:
        """Predict positive-class probability when supported."""
        return self.predict(features).astype(float)

    @abstractmethod
    def save(self, path: str | Path) -> Path:
        """Persist model to disk."""

    @classmethod
    @abstractmethod
    def load(cls, path: str | Path) -> "BasePredictiveModel":
        """Load model from disk."""

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Return lightweight model metadata."""

    def feature_importance(self) -> pd.DataFrame:
        """Return feature importance as feature/importance rows when available."""
        return pd.DataFrame(columns=["feature", "importance"])
