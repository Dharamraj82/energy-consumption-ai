"""Build leakage-aware features for energy consumption prediction models."""

from typing import List
import numpy as np
import pandas as pd

# Preserved for backward compatibility with baseline minute experiments
TARGET = "global_active_power"
FEATURE_COLUMNS = ["previous_active_power", "hour", "minute", "day_of_week"]

# Feature columns for next-hour Random Forest prediction
HOURLY_FEATURE_COLUMNS: List[str] = [
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_24",
    "rolling_mean_3h",
    "rolling_mean_24h",
    "hour",
    "day_of_week",
]
HOURLY_TARGET_COLUMN: str = "target"


def make_next_observation_dataset(data: pd.DataFrame) -> pd.DataFrame:
    """Pair current known power and clock features with the next observation (minute baseline)."""
    required = {"timestamp", TARGET}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Input is missing columns: {sorted(missing)}")
    if data.empty:
        raise ValueError("Input data is empty.")
    ordered = data.copy()
    ordered["timestamp"] = pd.to_datetime(ordered["timestamp"], errors="coerce")
    if ordered["timestamp"].isna().any():
        raise ValueError("Input contains missing or invalid timestamps.")
    ordered[TARGET] = pd.to_numeric(ordered[TARGET], errors="coerce")
    if not np.isfinite(ordered[TARGET].to_numpy(dtype=float)).all():
        raise ValueError(f"Input column '{TARGET}' contains missing or non-finite values.")
    ordered = ordered.sort_values("timestamp", kind="mergesort")
    result = pd.DataFrame(index=ordered.index)
    result["timestamp"] = ordered["timestamp"]
    result["previous_active_power"] = ordered[TARGET]
    result["hour"] = ordered["timestamp"].dt.hour
    result["minute"] = ordered["timestamp"].dt.minute
    result["day_of_week"] = ordered["timestamp"].dt.dayofweek
    result["target"] = ordered[TARGET].shift(-1)
    result["target_timestamp"] = ordered["timestamp"].shift(-1)
    return result.dropna(subset=["target"]).reset_index(drop=True)


def create_hourly_features(data: pd.DataFrame) -> pd.DataFrame:
    """Create strictly leakage-free historical features to predict next hour's mean active power.

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with at least 'timestamp' and 'global_active_power' columns.

    Returns
    -------
    pd.DataFrame
        DataFrame containing 'timestamp', 'target', and all columns in HOURLY_FEATURE_COLUMNS.
    """
    if data.empty:
        raise ValueError("Input dataset is empty.")

    required = {"timestamp", "global_active_power"}
    missing = required - set(data.columns)
    if missing:
        raise ValueError(f"Input dataset is missing required columns: {sorted(missing)}")

    df = data.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    if df["timestamp"].isna().any():
        raise ValueError("Input contains missing or unparseable timestamps.")

    df["global_active_power"] = pd.to_numeric(df["global_active_power"], errors="coerce")
    if df["global_active_power"].isna().any():
        raise ValueError("Input contains missing or non-numeric power measurements.")

    # Sort chronologically to preserve sequence order
    df = df.sort_values("timestamp").reset_index(drop=True)

    power = df["global_active_power"]
    ts = df["timestamp"]

    features_df = pd.DataFrame(index=df.index)
    features_df["timestamp"] = ts

    # Target: next hour's mean active power (hour t+1)
    features_df[HOURLY_TARGET_COLUMN] = power.shift(-1)

    # Historical power lag features (strictly observations at or before hour t)
    features_df["lag_1"] = power                # Current observation (t)
    features_df["lag_2"] = power.shift(1)       # Observation at t-1
    features_df["lag_3"] = power.shift(2)       # Observation at t-2
    features_df["lag_24"] = power.shift(23)     # Observation at t-23 (24h before target t+1)

    # Rolling window statistics (computed strictly using past observations up to hour t)
    features_df["rolling_mean_3h"] = power.rolling(window=3, closed="right").mean()
    features_df["rolling_mean_24h"] = power.rolling(window=24, closed="right").mean()

    # Calendar features based on the observation timestamp
    features_df["hour"] = ts.dt.hour
    features_df["day_of_week"] = ts.dt.dayofweek

    # Drop uncomputable rows due to lags (first 23 rows) and target shift (last row)
    clean_features = features_df.dropna().reset_index(drop=True)

    return clean_features
