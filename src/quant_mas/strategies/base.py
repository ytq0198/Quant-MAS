"""Strategy abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Strategy(ABC):
    """Base class for deterministic strategies."""

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Return a DataFrame with date, symbol, and target_weight columns."""

