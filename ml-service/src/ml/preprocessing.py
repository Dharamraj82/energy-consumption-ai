"""Time-aware preparation and aggregation helpers for ML experiments."""

import math
from typing import Tuple

import numpy as np
import pandas as pd


def clean_and_aggregate_hourly(data: pd.DataFrame) -> pd.DataFrame:
    """Validate, clean, and aggregate minute-level electricity readings into hourly mean kW.

    Parameters
    ----------
    data : pd.DataFrame
        Raw or pre-parsed DataFrame containing date/time and active power measurements.

    Returns
    -------
    pd.DataFrame
        Chronologically sorted hourly DataFrame with columns ['timestamp', 'global_active_power'].
    """
    if data.empty:
        raise ValueError("Input data is empty.")

    df = data.copy()

    # Normalize column names for flexible ingestion
    col_map = {col: str(col).strip().lower() for col in df.columns}
    df = df.rename(columns=col_map)

    # Resolve timestamp
    if "timestamp" not in df.columns:
        if "date" in df.columns and "time" in df.columns:
            df["timestamp"] = pd.to_datetime(
                df["date"].astype(str) + " " + df["time"].astype(str),
                format="%d/%m/%Y %H:%M:%S",
                errors="coerce",
            )
        else:
            raise ValueError(
                "Input data must contain either 'timestamp' or both 'Date' and 'Time' columns."
            )
    else:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Drop any records where timestamp could not be resolved
    df = df.dropna(subset=["timestamp"])
    if df.empty:
        raise ValueError("No valid timestamps found in input data.")

    # Resolve active power column
    power_col = None
    for candidate in ["global_active_power", "active_power", "power"]:
        if candidate in df.columns:
            power_col = candidate
            break

    if power_col is None:
        raise ValueError(
            "Input data missing active power column ('Global_active_power')."
        )

    # Coerce active power to numeric; convert '?' or invalid strings to NaN
    df["global_active_power"] = pd.to_numeric(df[power_col], errors="coerce")

    # Filter out impossible negative power values
    df.loc[df["global_active_power"] < 0, "global_active_power"] = np.nan

    # Sort strictly by timestamp
    df = df.sort_values("timestamp")

    # Resample to hourly intervals taking the mean of observed minute readings
    hourly = (
        df.set_index("timestamp")["global_active_power"]
        .resample("1h")
        .mean()
    )

    # Handle missing hourly periods via linear interpolation to maintain time-series continuity
    hourly = hourly.interpolate(method="linear", limit_direction="both")

    result = hourly.reset_index()
    result.columns = ["timestamp", "global_active_power"]

    # Final check: all values must be finite numbers
    if result["global_active_power"].isna().any():
        raise ValueError("Hourly series contains unresolved missing values.")

    return result


def chronological_split(data: pd.DataFrame, test_fraction: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split ordered rows without shuffling; return train and test DataFrames."""
    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1.")
    if len(data) < 3:
        raise ValueError("At least three rows are required for a chronological split.")
    boundary = int(len(data) * (1 - test_fraction))
    boundary = min(max(boundary, 1), len(data) - 1)
    return data.iloc[:boundary].copy(), data.iloc[boundary:].copy()


def chronological_train_validation_test_split(
    data: pd.DataFrame,
    train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split ordered rows into train, validation, and untouched test segments.

    Default split proportions are 60% train, 20% validation, and 20% test.
    Custom fractions such as (0.70, 0.15) can be passed for 70/15/15 splits.
    """
    if (
        not math.isfinite(train_fraction)
        or not math.isfinite(validation_fraction)
        or train_fraction <= 0
        or validation_fraction <= 0
    ):
        raise ValueError("Train and validation fractions must be positive.")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("Train and validation fractions must sum to less than 1.")
    if len(data) < 3:
        raise ValueError("At least three rows are required for a three-way split.")

    train_end = int(len(data) * train_fraction)
    validation_end = int(len(data) * (train_fraction + validation_fraction))
    if train_end < 1 or validation_end <= train_end or validation_end >= len(data):
        raise ValueError(
            "The dataset is too small for non-empty train, validation, and test splits."
        )
    return (
        data.iloc[:train_end].copy(),
        data.iloc[train_end:validation_end].copy(),
        data.iloc[validation_end:].copy(),
    )
