"""Prediction module for next-hour household electricity consumption using Random Forest."""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd

from .features import HOURLY_FEATURE_COLUMNS

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "random_forest.joblib"
DEFAULT_METADATA_PATH = PROJECT_ROOT / "models" / "model_metadata.json"

PREDICTION_UNIT = "kW"
PREDICTION_HORIZON = "next_1_hour"


def load_model(model_path: Optional[Union[str, Path]] = None):
    """Load the trained Random Forest model from disk."""
    path = Path(model_path) if model_path is not None else DEFAULT_MODEL_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"Trained model artifact not found at {path}. "
            "Run `python scripts/train_model.py` first to train and save the model."
        )
    try:
        model = joblib.load(path)
    except Exception as exc:
        raise RuntimeError(f"Failed to deserialize model artifact from {path}: {exc}") from exc
    return model


def validate_input_features(features: Union[Dict[str, Any], pd.DataFrame]) -> pd.DataFrame:
    """Validate and format input features for next-hour active power prediction.

    Parameters
    ----------
    features : Union[Dict[str, Any], pd.DataFrame]
        Input features containing all required columns:
        'lag_1', 'lag_2', 'lag_3', 'lag_24', 'rolling_mean_3h', 'rolling_mean_24h', 'hour', 'day_of_week'.

    Returns
    -------
    pd.DataFrame
        Validated DataFrame aligned to HOURLY_FEATURE_COLUMNS.
    """
    if isinstance(features, dict):
        df = pd.DataFrame([features])
    elif isinstance(features, pd.DataFrame):
        df = features.copy()
    else:
        raise TypeError(
            f"Expected features as dict or pd.DataFrame, received {type(features).__name__}."
        )

    if df.empty:
        raise ValueError("Input features DataFrame is empty.")

    missing = set(HOURLY_FEATURE_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(
            f"Input features missing required columns: {sorted(missing)}. "
            f"Required: {HOURLY_FEATURE_COLUMNS}"
        )

    # Reorder columns to match training schema
    df = df[HOURLY_FEATURE_COLUMNS].copy()

    # Coerce to numeric
    for col in HOURLY_FEATURE_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any():
            raise ValueError(f"Feature column '{col}' contains non-numeric or NaN values.")
        if not np.isfinite(df[col].to_numpy(dtype=float)).all():
            raise ValueError(f"Feature column '{col}' contains infinite values.")

    # Domain constraints
    if (df["hour"] < 0).any() or (df["hour"] > 23).any():
        raise ValueError("Feature 'hour' must be an integer between 0 and 23.")

    if (df["day_of_week"] < 0).any() or (df["day_of_week"] > 6).any():
        raise ValueError("Feature 'day_of_week' must be an integer between 0 (Monday) and 6 (Sunday).")

    # Power readings cannot be negative in household consumption
    power_features = ["lag_1", "lag_2", "lag_3", "lag_24", "rolling_mean_3h", "rolling_mean_24h"]
    for col in power_features:
        if (df[col] < 0).any():
            raise ValueError(f"Feature '{col}' cannot contain negative power values (kW).")

    return df


def predict_next_hour(
    features: Union[Dict[str, Any], pd.DataFrame],
    model_path: Optional[Union[str, Path]] = None,
) -> Dict[str, Any]:
    """Predict next hour's mean global active power from historical features.

    Parameters
    ----------
    features : Union[Dict[str, Any], pd.DataFrame]
        Feature values for input.
    model_path : Optional[Union[str, Path]]
        Custom path to serialized model artifact.

    Returns
    -------
    Dict[str, Any]
        Dictionary with prediction value, unit (kW), horizon, and verified inputs.
    """
    valid_df = validate_input_features(features)
    model = load_model(model_path)

    preds = model.predict(valid_df)

    if len(preds) == 1:
        pred_val = float(round(preds[0], 4))
        input_data = valid_df.iloc[0].to_dict()
        return {
            "prediction_kw": pred_val,
            "unit": PREDICTION_UNIT,
            "horizon": PREDICTION_HORIZON,
            "input_features": input_data,
        }
    else:
        return {
            "predictions_kw": [float(round(p, 4)) for p in preds],
            "unit": PREDICTION_UNIT,
            "horizon": PREDICTION_HORIZON,
            "count": len(preds),
        }


def main():
    """Command-line interface for next-hour electricity consumption prediction."""
    parser = argparse.ArgumentParser(
        description="Predict next hour's mean electricity consumption (kW) using trained Random Forest."
    )
    parser.add_argument("--lag-1", type=float, help="Power at hour t (kW)")
    parser.add_argument("--lag-2", type=float, help="Power at hour t-1 (kW)")
    parser.add_argument("--lag-3", type=float, help="Power at hour t-2 (kW)")
    parser.add_argument("--lag-24", type=float, help="Power at hour t-23 (same hour yesterday) (kW)")
    parser.add_argument("--rolling-3h", type=float, help="3-hour historical rolling mean power (kW)")
    parser.add_argument("--rolling-24h", type=float, help="24-hour historical rolling mean power (kW)")
    parser.add_argument("--hour", type=int, help="Hour of observation (0-23)")
    parser.add_argument("--day-of-week", type=int, help="Day of week (0=Mon, 6=Sun)")
    parser.add_argument("--json-input", type=str, help="JSON string or file path containing feature dictionary")
    parser.add_argument("--model-path", type=str, default=None, help="Custom model path (.joblib)")

    args = parser.parse_args()

    if args.json_input:
        json_path = Path(args.json_input)
        if json_path.is_file():
            features = json.loads(json_path.read_text(encoding="utf-8"))
        else:
            features = json.loads(args.json_input)
    else:
        required_args = [
            ("lag_1", args.lag_1),
            ("lag_2", args.lag_2),
            ("lag_3", args.lag_3),
            ("lag_24", args.lag_24),
            ("rolling_mean_3h", args.rolling_3h),
            ("rolling_mean_24h", args.rolling_24h),
            ("hour", args.hour),
            ("day_of_week", args.day_of_week),
        ]
        missing = [name for name, val in required_args if val is None]
        if missing:
            parser.error(
                f"Missing arguments: {', '.join(missing)}. "
                "Provide all 8 features or use --json-input."
            )
        features = {name: val for name, val in required_args}

    result = predict_next_hour(features, model_path=args.model_path)
    print("\n=== Prediction Result ===")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
