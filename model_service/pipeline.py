"""Feature engineering utilities for commodity price prediction."""
from __future__ import annotations

import pandas as pd


def _ensure_datetime(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Return a copy with the date column parsed to datetime."""
    out = df.copy()
    out[date_col] = pd.to_datetime(out[date_col])
    return out


def create_lag_features(df: pd.DataFrame, price_col: str = "modal_price") -> pd.DataFrame:
    """Add lag features (1, 3, 7) for the given price column, grouped by market."""
    out = _ensure_datetime(df)
    out = out.sort_values(["market", "date"])
    out["price_lag_1"] = out.groupby("market")[price_col].shift(1)
    out["price_lag_3"] = out.groupby("market")[price_col].shift(3)
    out["price_lag_7"] = out.groupby("market")[price_col].shift(7)
    return out


def create_rolling_features(df: pd.DataFrame, price_col: str = "modal_price") -> pd.DataFrame:
    """Add rolling mean features (3, 7, 30) for the given price column, grouped by market."""
    out = _ensure_datetime(df)
    out = out.sort_values(["market", "date"])
    out["price_roll_mean_3"] = (
        out.groupby("market")[price_col].transform(lambda s: s.rolling(window=3, min_periods=1).mean())
    )
    out["price_roll_mean_7"] = (
        out.groupby("market")[price_col].transform(lambda s: s.rolling(window=7, min_periods=1).mean())
    )
    out["price_roll_mean_30"] = (
        out.groupby("market")[price_col].transform(lambda s: s.rolling(window=30, min_periods=1).mean())
    )
    return out


def create_volatility_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add simple volatility features based on daily price spread."""
    out = df.copy()
    out["price_spread"] = out["Max_Price"] - out["Min_Price"]
    return out


def create_time_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    """Add calendar-based time features from the date column."""
    out = _ensure_datetime(df, date_col=date_col)
    out["day_of_week"] = out[date_col].dt.dayofweek
    out["month"] = out[date_col].dt.month
    out["day_of_year"] = out[date_col].dt.dayofyear
    return out


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full feature pipeline and return a feature-ready dataframe."""
    features = create_time_features(df)
    features = create_volatility_features(features)
    features = create_lag_features(features)
    features = create_rolling_features(features)

    required_cols = [
        "price_lag_1",
        "price_lag_3",
        "price_lag_7",
        "price_roll_mean_3",
        "price_roll_mean_7",
        "price_roll_mean_30",
    ]
    features = features.dropna(subset=required_cols)
    return features
