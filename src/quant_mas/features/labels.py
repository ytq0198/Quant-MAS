"""Label builders for supervised learning."""

from __future__ import annotations

import pandas as pd


def add_future_return_label(
    frame: pd.DataFrame,
    price_column: str = "close",
    horizon: int = 5,
) -> pd.DataFrame:
    """Add future return and binary direction labels.

    The label is allowed to look forward because it is a target, not a feature.
    """
    if horizon <= 0:
        raise ValueError("horizon must be positive")

    result = frame.copy()
    future_return = result[price_column].shift(-horizon) / result[price_column] - 1.0
    result[f"future_return_{horizon}"] = future_return
    result[f"future_direction_{horizon}"] = (future_return > 0).astype("Int64")
    result.loc[future_return.isna(), f"future_direction_{horizon}"] = pd.NA
    return result

