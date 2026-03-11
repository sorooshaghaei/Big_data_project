"""Feature engineering for forecasting and anomaly analysis."""

from __future__ import annotations

import pandas as pd


def add_time_features(
    df: pd.DataFrame,
    date_col: str = "date",
    value_col: str = "value",
    group_cols: tuple[str, ...] = ("region", "source", "metric_type"),
) -> pd.DataFrame:
    """Add standard time-series features to a daily fact table."""
    out = df.copy().sort_values([*group_cols, date_col])
    out[date_col] = pd.to_datetime(out[date_col], errors="coerce")

    out["day_of_week"] = out[date_col].dt.dayofweek
    out["is_weekend"] = (out["day_of_week"] >= 5).astype(int)
    out["month"] = out[date_col].dt.month
    out["year"] = out[date_col].dt.year
    out["week_of_year"] = out[date_col].dt.isocalendar().week.astype(int)
    out["day_of_year"] = out[date_col].dt.dayofyear

    grouped = out.groupby(list(group_cols))[value_col]
    out["lag_1"] = grouped.shift(1)
    out["lag_7"] = grouped.shift(7)
    out["lag_14"] = grouped.shift(14)
    out["rolling_7_mean"] = grouped.transform(lambda s: s.rolling(7, min_periods=3).mean())
    out["rolling_7_std"] = grouped.transform(lambda s: s.rolling(7, min_periods=3).std())
    out["rolling_30_mean"] = grouped.transform(lambda s: s.rolling(30, min_periods=7).mean())
    out["rolling_30_std"] = grouped.transform(lambda s: s.rolling(30, min_periods=7).std())
    out["pct_change_1"] = grouped.pct_change()
    out["zscore_30"] = (
        (out[value_col] - out["rolling_30_mean"]) / out["rolling_30_std"].replace({0: pd.NA})
    )

    return out
