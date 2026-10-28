"""Hyperparameter tuning and optimization for the Random Forest Regressor."""

from datetime import datetime
import json
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .data_loader import PROJECT_ROOT, load_hourly_data
from .evaluate import (
    FIGURES_DIR,
    METRICS_DIR,
    generate_tuning_comparison_plot,
    regression_metrics,
)
from .features import (
    HOURLY_FEATURE_COLUMNS,
    HOURLY_TARGET_COLUMN,
    create_hourly_features,
)
from .preprocessing import chronological_train_validation_test_split
from .train import DEFAULT_RF_PARAMS, MODEL_OUTPUT_DIR

TUNED_MODEL_PATH = MODEL_OUTPUT_DIR / "random_forest_tuned.joblib"
TUNED_METADATA_PATH = MODEL_OUTPUT_DIR / "random_forest_tuned_metadata.json"
TUNING_RESULTS_CSV = METRICS_DIR / "random_forest_tuning.csv"

# Parameter search space defined by requirements
PARAM_SEARCH_SPACE: Dict[str, List[Any]] = {
    "n_estimators": [150, 250, 400],
    "max_depth": [10, 20, 30, None],
    "min_samples_leaf": [1, 2, 4],
    "max_features": [0.7, 1.0],
}


def build_candidate_configurations() -> List[Dict[str, Any]]:
    """Build a systematic, representative set of candidate hyperparameter configurations.

    Covers all levels for n_estimators (150, 250, 400), max_depth (10, 20, 30, None),
    min_samples_leaf (1, 2, 4), and max_features (0.7, 1.0) while maintaining
    a computationally practical search duration.
    """
    candidates = [
        # 1. Baseline configuration for reference
        {"n_estimators": 250, "max_depth": 20, "min_samples_leaf": 2, "max_features": 1.0},
        # 2. Depth sweep (holding others at initial baseline values)
        {"n_estimators": 150, "max_depth": 10, "min_samples_leaf": 2, "max_features": 1.0},
        {"n_estimators": 150, "max_depth": 20, "min_samples_leaf": 2, "max_features": 1.0},
        {"n_estimators": 150, "max_depth": 30, "min_samples_leaf": 2, "max_features": 1.0},
        {"n_estimators": 150, "max_depth": None, "min_samples_leaf": 2, "max_features": 1.0},
        # 3. Leaf size sweep
        {"n_estimators": 150, "max_depth": 20, "min_samples_leaf": 1, "max_features": 1.0},
        {"n_estimators": 150, "max_depth": 20, "min_samples_leaf": 4, "max_features": 1.0},
        {"n_estimators": 150, "max_depth": 10, "min_samples_leaf": 1, "max_features": 1.0},
        {"n_estimators": 150, "max_depth": 10, "min_samples_leaf": 4, "max_features": 1.0},
        # 4. Feature subsampling (max_features = 0.7 vs 1.0)
        {"n_estimators": 150, "max_depth": 20, "min_samples_leaf": 2, "max_features": 0.7},
        {"n_estimators": 150, "max_depth": 10, "min_samples_leaf": 2, "max_features": 0.7},
        {"n_estimators": 150, "max_depth": 10, "min_samples_leaf": 4, "max_features": 0.7},
        {"n_estimators": 150, "max_depth": None, "min_samples_leaf": 4, "max_features": 0.7},
        # 5. Tree count scaling (n_estimators = 250 and 400 on top tree structures)
        {"n_estimators": 250, "max_depth": 10, "min_samples_leaf": 2, "max_features": 1.0},
        {"n_estimators": 250, "max_depth": 10, "min_samples_leaf": 2, "max_features": 0.7},
        {"n_estimators": 250, "max_depth": 10, "min_samples_leaf": 4, "max_features": 1.0},
        {"n_estimators": 250, "max_depth": 10, "min_samples_leaf": 4, "max_features": 0.7},
        {"n_estimators": 400, "max_depth": 10, "min_samples_leaf": 2, "max_features": 1.0},
        {"n_estimators": 400, "max_depth": 10, "min_samples_leaf": 2, "max_features": 0.7},
        {"n_estimators": 400, "max_depth": 20, "min_samples_leaf": 2, "max_features": 0.7},
    ]

    # Remove duplicates while preserving order
    unique_candidates = []
    seen = set()
    for c in candidates:
        key = (c["n_estimators"], c["max_depth"], c["min_samples_leaf"], c["max_features"])
        if key not in seen:
            seen.add(key)
            unique_candidates.append(c)

    return unique_candidates


def verify_leakage_and_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
) -> None:
    """Rigorous audit for temporal data leakage across feature indices and timestamps."""
    # 1. Non-overlapping chronological boundaries
    if train_df["timestamp"].max() >= val_df["timestamp"].min():
        raise ValueError(
            f"Leakage detected: Training timestamp ({train_df['timestamp'].max()}) "
            f"overlaps with Validation timestamp ({val_df['timestamp'].min()})."
        )
    if val_df["timestamp"].max() >= test_df["timestamp"].min():
        raise ValueError(
            f"Leakage detected: Validation timestamp ({val_df['timestamp'].max()}) "
            f"overlaps with Test timestamp ({test_df['timestamp'].min()})."
        )

    # 2. Sequential integer indices
    if train_df.index.max() >= val_df.index.min() or val_df.index.max() >= test_df.index.min():
        raise ValueError("Sequential chronological order violated in split DataFrames.")


def tune_random_forest(
    hourly_data: Optional[pd.DataFrame] = None,
    candidate_params: Optional[List[Dict[str, Any]]] = None,
    save_artifacts: bool = True,
    generate_plots: bool = True,
    random_state: int = 42,
) -> Dict[str, Any]:
    """Tune Random Forest hyperparameters using strictly the validation split for selection.

    Parameters
    ----------
    hourly_data : Optional[pd.DataFrame]
        Hourly electricity consumption data. Loaded from cache if None.
    candidate_params : Optional[List[Dict[str, Any]]]
        List of parameter dicts to evaluate. Defaults to build_candidate_configurations().
    save_artifacts : bool, default=True
        Whether to save tuned model artifact and tuning reports.
    generate_plots : bool, default=True
        Whether to generate the validation comparison chart.
    random_state : int, default=42
        Reproducible random seed.

    Returns
    -------
    Dict[str, Any]
        Dictionary with tuning records, best parameters, original vs tuned metrics, and artifacts.
    """
    total_start = time.time()

    # 1. Load data and construct leakage-free features
    if hourly_data is None:
        hourly_data = load_hourly_data()

    features_df = create_hourly_features(hourly_data)

    # 2. Chronological 70% train, 15% validation, 15% test split
    train_df, val_df, test_df = chronological_train_validation_test_split(
        features_df, train_fraction=0.70, validation_fraction=0.15
    )

    # 3. Verify zero temporal leakage
    verify_leakage_and_splits(train_df, val_df, test_df)

    X_train = train_df[HOURLY_FEATURE_COLUMNS]
    y_train = train_df[HOURLY_TARGET_COLUMN]

    X_val = val_df[HOURLY_FEATURE_COLUMNS]
    y_val = val_df[HOURLY_TARGET_COLUMN]

    X_test = test_df[HOURLY_FEATURE_COLUMNS]
    y_test = test_df[HOURLY_TARGET_COLUMN]

    # Evaluate original baseline configuration
    print("\n" + "=" * 78)
    print(" RANDOM FOREST HYPERPARAMETER TUNING (VALIDATION SET DRIVEN)")
    print("=" * 78)
    print("Evaluating original baseline configuration...")
    orig_params = dict(DEFAULT_RF_PARAMS)
    orig_rf = RandomForestRegressor(**orig_params)
    t0 = time.time()
    orig_rf.fit(X_train, y_train)
    orig_fit_time = time.time() - t0

    orig_val_preds = orig_rf.predict(X_val)
    orig_val_metrics = regression_metrics(y_val, orig_val_preds, include_mape=True)
    orig_test_preds = orig_rf.predict(X_test)
    orig_test_metrics = regression_metrics(y_test, orig_test_preds, include_mape=True)

    print(
        f"Original Model: Val MAE: {orig_val_metrics['mae']:.4f} kW | "
        f"Val RMSE: {orig_val_metrics['rmse']:.4f} kW | "
        f"Val R²: {orig_val_metrics['r2']:.4f} ({orig_fit_time:.1f}s)"
    )

    # Prepare search candidates
    configs = candidate_params if candidate_params is not None else build_candidate_configurations()
    print(f"\nSearching across {len(configs)} candidate parameter configurations...")
    print("-" * 78)

    tuning_records = []
    best_config = None
    best_val_mae = float("inf")
    best_rf_model = None

    for i, cfg in enumerate(configs, start=1):
        fit_params = dict(cfg)
        fit_params["random_state"] = random_state
        fit_params["n_jobs"] = -1

        t_start_fit = time.time()
        rf = RandomForestRegressor(**fit_params)
        rf.fit(X_train, y_train)
        fit_duration = time.time() - t_start_fit

        val_preds = rf.predict(X_val)
        scores = regression_metrics(y_val, val_preds, include_mape=True)

        is_current_best = scores["mae"] < best_val_mae
        if is_current_best:
            best_val_mae = scores["mae"]
            best_config = fit_params
            best_rf_model = rf

        depth_str = str(cfg["max_depth"]) if cfg["max_depth"] is not None else "None"
        print(
            f"[{i:02d}/{len(configs):02d}] "
            f"n_est={cfg['n_estimators']:<3} depth={depth_str:<4} leaf={cfg['min_samples_leaf']} mf={cfg['max_features']} "
            f"-> Val MAE: {scores['mae']:.4f} | RMSE: {scores['rmse']:.4f} | R²: {scores['r2']:.4f} ({fit_duration:.1f}s)"
            f"{' * NEW BEST' if is_current_best else ''}"
        )

        tuning_records.append({
            "candidate_id": i,
            "n_estimators": cfg["n_estimators"],
            "max_depth": depth_str,
            "min_samples_leaf": cfg["min_samples_leaf"],
            "max_features": cfg["max_features"],
            "val_mae": round(scores["mae"], 4),
            "val_rmse": round(scores["rmse"], 4),
            "val_r2": round(scores["r2"], 4),
            "val_mape": round(scores["mape"], 2),
            "fit_time_sec": round(fit_duration, 2),
            "is_best": False,
        })

    # Flag the winning configuration in records
    for rec in tuning_records:
        depth_val = str(best_config["max_depth"]) if best_config["max_depth"] is not None else "None"
        if (
            rec["n_estimators"] == best_config["n_estimators"]
            and rec["max_depth"] == depth_val
            and rec["min_samples_leaf"] == best_config["min_samples_leaf"]
            and rec["max_features"] == best_config["max_features"]
        ):
            rec["is_best"] = True
            break

    # Final selection decision based on Validation MAE
    # Check if tuning improved over original baseline
    improved = best_val_mae < orig_val_metrics["mae"]
    if not improved:
        print("\nNote: Tuning did not outperform the original baseline validation MAE. Retaining original model.")
        selected_rf_model = orig_rf
        selected_params = orig_params
    else:
        print(f"\nSelection Decision: Tuned configuration achieves lower Validation MAE ({best_val_mae:.4f} kW vs {orig_val_metrics['mae']:.4f} kW).")
        selected_rf_model = best_rf_model
        selected_params = best_config

    # Evaluate the selected model ONCE on the held-out test set
    tuned_val_preds = selected_rf_model.predict(X_val)
    tuned_val_metrics = regression_metrics(y_val, tuned_val_preds, include_mape=True)

    tuned_test_preds = selected_rf_model.predict(X_test)
    tuned_test_metrics = regression_metrics(y_test, tuned_test_preds, include_mape=True)

    total_duration = time.time() - total_start

    print("\n" + "=" * 78)
    print(" TUNING OUTCOME: ORIGINAL VS. TUNED RANDOM FOREST")
    print("=" * 78)
    print(f"{'Metric':<20} {'Original Model':<18} {'Tuned Model':<18} {'Difference':<15}")
    print("-" * 78)
    mae_diff = tuned_val_metrics['mae'] - orig_val_metrics['mae']
    rmse_diff = tuned_val_metrics['rmse'] - orig_val_metrics['rmse']
    r2_diff = tuned_val_metrics['r2'] - orig_val_metrics['r2']
    print(f"{'Validation MAE (kW)':<20} {orig_val_metrics['mae']:<18.4f} {tuned_val_metrics['mae']:<18.4f} {mae_diff:<+15.4f}")
    print(f"{'Validation RMSE (kW)':<20} {orig_val_metrics['rmse']:<18.4f} {tuned_val_metrics['rmse']:<18.4f} {rmse_diff:<+15.4f}")
    print(f"{'Validation R²':<20} {orig_val_metrics['r2']:<18.4f} {tuned_val_metrics['r2']:<18.4f} {r2_diff:<+15.4f}")
    print("-" * 78)
    print(f"{'Test MAE (kW)':<20} {orig_test_metrics['mae']:<18.4f} {tuned_test_metrics['mae']:<18.4f} {tuned_test_metrics['mae'] - orig_test_metrics['mae']:<+15.4f}")
    print(f"{'Test RMSE (kW)':<20} {orig_test_metrics['rmse']:<18.4f} {tuned_test_metrics['rmse']:<18.4f} {tuned_test_metrics['rmse'] - orig_test_metrics['rmse']:<+15.4f}")
    print(f"{'Test R²':<20} {orig_test_metrics['r2']:<18.4f} {tuned_test_metrics['r2']:<18.4f} {tuned_test_metrics['r2'] - orig_test_metrics['r2']:<+15.4f}")
    print(f"{'Test MAPE (%)':<20} {orig_test_metrics['mape']:<18.2f} {tuned_test_metrics['mape']:<18.2f} {tuned_test_metrics['mape'] - orig_test_metrics['mape']:<+15.2f}")
    print("=" * 78)
    print(f"Total tuning workflow duration: {total_duration:.2f} seconds")

    artifacts = {}

    if save_artifacts:
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Save tuning results CSV
        tuning_df = pd.DataFrame(tuning_records)
        tuning_df.to_csv(TUNING_RESULTS_CSV, index=False)
        artifacts["tuning_csv"] = TUNING_RESULTS_CSV
        print(f"\nSaved tuning records to: {TUNING_RESULTS_CSV}")

        # 2. Save tuned model artifact separately without overwriting original
        joblib.dump(selected_rf_model, TUNED_MODEL_PATH)
        artifacts["tuned_model_path"] = TUNED_MODEL_PATH
        print(f"Saved tuned model artifact to: {TUNED_MODEL_PATH}")

        # 3. Save tuned model metadata
        metadata = {
            "model_type": "RandomForestRegressor_Tuned",
            "framework": "scikit-learn",
            "selection_criterion": "Lowest validation MAE",
            "best_hyperparameters": selected_params,
            "original_parameters": orig_params,
            "feature_columns": HOURLY_FEATURE_COLUMNS,
            "target_column": HOURLY_TARGET_COLUMN,
            "target_unit": "kW",
            "split_counts": {
                "train_samples": len(train_df),
                "val_samples": len(val_df),
                "test_samples": len(test_df),
            },
            "validation_metrics": {
                "original": orig_val_metrics,
                "tuned": tuned_val_metrics,
            },
            "test_metrics": {
                "original": orig_test_metrics,
                "tuned": tuned_test_metrics,
            },
            "tuning_duration_seconds": round(total_duration, 2),
            "tuned_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(TUNED_METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        artifacts["tuned_metadata_path"] = TUNED_METADATA_PATH

        # 4. Save tuned test predictions
        tuned_pred_df = pd.DataFrame({
            "timestamp": test_df["timestamp"].values,
            "actual_global_active_power_kw": y_test.values,
            "predicted_global_active_power_kw": np.round(tuned_test_preds, 4),
            "residual_kw": np.round(y_test.values - tuned_test_preds, 4),
            "absolute_error_kw": np.round(np.abs(y_test.values - tuned_test_preds), 4),
        })
        preds_path = METRICS_DIR / "test_predictions_tuned.csv"
        tuned_pred_df.to_csv(preds_path, index=False)
        artifacts["tuned_predictions_csv"] = preds_path

    if generate_plots:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        plot_path = generate_tuning_comparison_plot(
            orig_val_metrics=orig_val_metrics,
            tuned_val_metrics=tuned_val_metrics,
            output_dir=FIGURES_DIR,
        )
        artifacts["tuning_comparison_plot"] = plot_path
        print(f"Saved validation comparison plot to: {plot_path}")

    return {
        "best_config": selected_params,
        "orig_val_metrics": orig_val_metrics,
        "tuned_val_metrics": tuned_val_metrics,
        "orig_test_metrics": orig_test_metrics,
        "tuned_test_metrics": tuned_test_metrics,
        "tuning_records": tuning_records,
        "duration_seconds": total_duration,
        "artifacts": artifacts,
    }


if __name__ == "__main__":
    tune_random_forest()
