"""Model training and evaluation module for energy consumption prediction."""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor

from .data_loader import PROJECT_ROOT, load_hourly_data, load_processed_data
from .evaluate import (
    FIGURES_DIR,
    METRICS_DIR,
    append_result,
    generate_evaluation_plots,
    generate_model_comparison_plots,
    regression_metrics,
    save_metrics_report,
)
from .features import (
    FEATURE_COLUMNS,
    HOURLY_FEATURE_COLUMNS,
    HOURLY_TARGET_COLUMN,
    create_hourly_features,
    make_next_observation_dataset,
)
from .preprocessing import chronological_train_validation_test_split

MODEL_OUTPUT_DIR = PROJECT_ROOT / "models"
MODEL_FILE_PATH = MODEL_OUTPUT_DIR / "random_forest.joblib"
METADATA_FILE_PATH = MODEL_OUTPUT_DIR / "model_metadata.json"
MODEL_COMPARISON_CSV = METRICS_DIR / "model_comparison.csv"
MODEL_PREDICTIONS_CSV = METRICS_DIR / "model_comparison_predictions.csv"

DEFAULT_RF_PARAMS: Dict[str, Any] = {
    "n_estimators": 250,
    "max_depth": 20,
    "min_samples_leaf": 2,
    "random_state": 42,
    "n_jobs": -1,
}


def run_baselines(data=None, record_results: bool = True):
    """Compare a persistence baseline and candidate models on validation rows (Milestone 2 legacy)."""
    source = load_processed_data() if data is None else data
    samples = make_next_observation_dataset(source)
    train, validation, _ = chronological_train_validation_test_split(
        samples, train_fraction=0.6, validation_fraction=0.2
    )
    candidates = {
        "persistence": None,
        "linear_regression": LinearRegression(),
        "decision_tree": DecisionTreeRegressor(random_state=42),
        "random_forest": RandomForestRegressor(n_estimators=100, random_state=42),
    }
    results = {}
    for name, model in candidates.items():
        if model is None:
            predictions = validation["previous_active_power"].to_numpy()
        else:
            pipeline = Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("regressor", model),
            ])
            pipeline.fit(train[FEATURE_COLUMNS], train["target"])
            predictions = pipeline.predict(validation[FEATURE_COLUMNS])
        # include_mape=False to maintain legacy schema for baseline tests
        scores = regression_metrics(validation["target"], predictions, include_mape=False)
        results[name] = scores
        if record_results:
            append_result({
                "experiment_id": "baseline-v1",
                "model_name": name,
                "feature_set": "lag1+clock",
                "split_strategy": "chronological-60-20-20",
                "evaluation_split": "validation",
                **scores,
                "notes": (
                    f"Validation only ({len(validation)} rows); test segment unused. "
                    "Exploratory score, not evidence for model selection."
                ),
            })
    return results


def compare_models(
    hourly_data: Optional[pd.DataFrame] = None,
    rf_params: Optional[Dict[str, Any]] = None,
    save_artifacts: bool = True,
    generate_plots: bool = True,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
) -> Dict[str, Any]:
    """Perform a rigorous, fair comparison between Persistence, Linear Regression, and Random Forest.

    Uses identical features, identical chronological splits, and untouched test timestamps.
    Model selection is performed strictly on validation metrics. The untouched test set
    is evaluated only after selection to obtain unbiased generalization metrics.

    Parameters
    ----------
    hourly_data : Optional[pd.DataFrame]
        Hourly electricity consumption DataFrame. If None, loads from cache or raw UCI data.
    rf_params : Optional[Dict[str, Any]]
        Hyperparameters for Random Forest. Defaults to DEFAULT_RF_PARAMS.
    save_artifacts : bool, default=True
        Whether to save metrics, predictions, and model artifacts to disk.
    generate_plots : bool, default=True
        Whether to generate comparative plots.
    train_fraction : float, default=0.70
        Proportion of data for training.
    validation_fraction : float, default=0.15
        Proportion of data for validation. Remaining (15%) is untouched test data.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing benchmark metrics, predictions, models, and artifact paths.
    """
    params = dict(DEFAULT_RF_PARAMS)
    if rf_params:
        params.update(rf_params)

    # 1. Ingest hourly data and build leakage-free features
    if hourly_data is None:
        hourly_data = load_hourly_data()

    features_df = create_hourly_features(hourly_data)

    # 2. Chronological split (70% train, 15% validation, 15% test)
    train_df, val_df, test_df = chronological_train_validation_test_split(
        features_df,
        train_fraction=train_fraction,
        validation_fraction=validation_fraction,
    )

    X_train = train_df[HOURLY_FEATURE_COLUMNS]
    y_train = train_df[HOURLY_TARGET_COLUMN]

    X_val = val_df[HOURLY_FEATURE_COLUMNS]
    y_val = val_df[HOURLY_TARGET_COLUMN]

    X_test = test_df[HOURLY_FEATURE_COLUMNS]
    y_test = test_df[HOURLY_TARGET_COLUMN]

    print("\n" + "=" * 75)
    print(" MODEL BENCHMARK: Persistence vs. Linear Regression vs. Random Forest")
    print("=" * 75)
    print(f"Chronological split (no shuffling):")
    print(f"  Training samples:   {len(train_df):,} ({len(train_df)/len(features_df):.1%})")
    print(f"  Validation samples: {len(val_df):,} ({len(val_df)/len(features_df):.1%})")
    print(f"  Test samples:       {len(test_df):,} ({len(test_df)/len(features_df):.1%})")
    print(f"  Features used:      {HOURLY_FEATURE_COLUMNS}")
    print(f"  Target:             {HOURLY_TARGET_COLUMN} (mean kW, 1-hour ahead)")
    print("-" * 75)

    models_trained = {}
    val_predictions = {}
    test_predictions = {}
    val_scores = {}
    test_scores = {}

    # --- 1. Persistence Baseline ---
    # Predicts that power at hour t+1 equals the power observed at hour t (lag_1)
    val_pred_pers = val_df["lag_1"].to_numpy()
    test_pred_pers = test_df["lag_1"].to_numpy()
    val_predictions["persistence"] = val_pred_pers
    test_predictions["persistence"] = test_pred_pers
    val_scores["persistence"] = regression_metrics(y_val, val_pred_pers, include_mape=True)
    test_scores["persistence"] = regression_metrics(y_test, test_pred_pers, include_mape=True)
    models_trained["persistence"] = None

    # --- 2. Linear Regression ---
    print("Fitting Linear Regression model...")
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    val_pred_lr = lr.predict(X_val)
    test_pred_lr = lr.predict(X_test)
    val_predictions["linear_regression"] = val_pred_lr
    test_predictions["linear_regression"] = test_pred_lr
    val_scores["linear_regression"] = regression_metrics(y_val, val_pred_lr, include_mape=True)
    test_scores["linear_regression"] = regression_metrics(y_test, test_pred_lr, include_mape=True)
    models_trained["linear_regression"] = lr

    # --- 3. Random Forest Regressor ---
    print(f"Fitting Random Forest Regressor ({params['n_estimators']} trees, max_depth={params['max_depth']})...")
    rf = RandomForestRegressor(**params)
    rf.fit(X_train, y_train)
    val_pred_rf = rf.predict(X_val)
    test_pred_rf = rf.predict(X_test)
    val_predictions["random_forest"] = val_pred_rf
    test_predictions["random_forest"] = test_pred_rf
    val_scores["random_forest"] = regression_metrics(y_val, val_pred_rf, include_mape=True)
    test_scores["random_forest"] = regression_metrics(y_test, test_pred_rf, include_mape=True)
    models_trained["random_forest"] = rf

    # --- Model Selection Based on Validation MAE ---
    model_names = ["persistence", "linear_regression", "random_forest"]
    val_mae_rank = sorted(model_names, key=lambda m: val_scores[m]["mae"])
    selected_model_name = val_mae_rank[0]

    print("\n" + "=" * 75)
    print(" BENCHMARK COMPARISON TABLE (kW)")
    print("=" * 75)
    print(f"{'Model':<20} {'Split':<12} {'MAE (kW)':<12} {'RMSE (kW)':<12} {'R²':<12} {'MAPE (%)':<12}")
    print("-" * 75)
    for m in model_names:
        v = val_scores[m]
        t = test_scores[m]
        print(f"{m:<20} {'Validation':<12} {v['mae']:<12.4f} {v['rmse']:<12.4f} {v['r2']:<12.4f} {v['mape']:<12.2f}")
        print(f"{m:<20} {'Test':<12} {t['mae']:<12.4f} {t['rmse']:<12.4f} {t['r2']:<12.4f} {t['mape']:<12.2f}")
        print("-" * 75)

    print(f"\nSelection Decision: '{selected_model_name}' selected based on lowest validation MAE ({val_scores[selected_model_name]['mae']:.4f} kW).")
    print(f"Test Set Performance of Selected Model: MAE = {test_scores[selected_model_name]['mae']:.4f} kW | RMSE = {test_scores[selected_model_name]['rmse']:.4f} kW | R² = {test_scores[selected_model_name]['r2']:.4f}")

    artifacts = {}

    if save_artifacts:
        METRICS_DIR.mkdir(parents=True, exist_ok=True)
        MODEL_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Build and save model_comparison.csv
        comparison_rows = []
        for rank, m in enumerate(val_mae_rank, start=1):
            v = val_scores[m]
            t = test_scores[m]
            notes = "Selected model based on validation MAE" if m == selected_model_name else "Baseline comparator"
            comparison_rows.append({
                "model_name": m,
                "validation_mae": round(v["mae"], 4),
                "validation_rmse": round(v["rmse"], 4),
                "validation_r2": round(v["r2"], 4),
                "validation_mape": round(v["mape"], 2),
                "test_mae": round(t["mae"], 4),
                "test_rmse": round(t["rmse"], 4),
                "test_r2": round(t["r2"], 4),
                "test_mape": round(t["mape"], 2),
                "is_selected": (m == selected_model_name),
                "validation_rank": rank,
                "notes": notes,
            })
        comparison_df = pd.DataFrame(comparison_rows)
        comparison_df.to_csv(MODEL_COMPARISON_CSV, index=False)
        artifacts["model_comparison_csv"] = MODEL_COMPARISON_CSV
        print(f"\nSaved model comparison summary to: {MODEL_COMPARISON_CSV}")

        # 2. Build and save model_comparison_predictions.csv
        comparison_preds_df = pd.DataFrame({
            "timestamp": test_df["timestamp"].values,
            "actual_global_active_power_kw": y_test.values,
            "pred_persistence_kw": np.round(test_predictions["persistence"], 4),
            "pred_linear_regression_kw": np.round(test_predictions["linear_regression"], 4),
            "pred_random_forest_kw": np.round(test_predictions["random_forest"], 4),
            "residual_persistence_kw": np.round(y_test.values - test_predictions["persistence"], 4),
            "residual_linear_regression_kw": np.round(y_test.values - test_predictions["linear_regression"], 4),
            "residual_random_forest_kw": np.round(y_test.values - test_predictions["random_forest"], 4),
        })
        comparison_preds_df.to_csv(MODEL_PREDICTIONS_CSV, index=False)
        artifacts["model_predictions_csv"] = MODEL_PREDICTIONS_CSV
        print(f"Saved model comparison predictions to: {MODEL_PREDICTIONS_CSV}")

        # 3. Save selected model artifact and metadata
        joblib.dump(rf, MODEL_FILE_PATH)
        artifacts["model_path"] = MODEL_FILE_PATH

        # Train metrics for RF
        train_preds_rf = rf.predict(X_train)
        train_scores_rf = regression_metrics(y_train, train_preds_rf, include_mape=True)

        metadata = {
            "selected_model": "RandomForestRegressor",
            "selection_criterion": "Lowest validation MAE",
            "framework": "scikit-learn",
            "parameters": params,
            "feature_columns": HOURLY_FEATURE_COLUMNS,
            "target_column": HOURLY_TARGET_COLUMN,
            "target_unit": "kW",
            "prediction_horizon": "next_1_hour",
            "split_counts": {
                "train_samples": len(train_df),
                "val_samples": len(val_df),
                "test_samples": len(test_df),
            },
            "validation_ranking": [
                {"model": m, "val_mae": val_scores[m]["mae"], "val_r2": val_scores[m]["r2"]}
                for m in val_mae_rank
            ],
            "selected_model_metrics": {
                "train": train_scores_rf,
                "validation": val_scores["random_forest"],
                "test": test_scores["random_forest"],
            },
            "trained_at": datetime.utcnow().isoformat() + "Z",
        }
        with open(METADATA_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        artifacts["metadata_path"] = METADATA_FILE_PATH

        # Save single-model test_predictions.csv and metrics report
        save_metrics_report(train_scores_rf, val_scores["random_forest"], test_scores["random_forest"], METRICS_DIR)
        test_pred_df = pd.DataFrame({
            "timestamp": test_df["timestamp"].values,
            "actual_global_active_power_kw": y_test.values,
            "predicted_global_active_power_kw": np.round(test_pred_rf, 4),
            "residual_kw": np.round(y_test.values - test_pred_rf, 4),
            "absolute_error_kw": np.round(np.abs(y_test.values - test_pred_rf), 4),
        })
        test_pred_df.to_csv(METRICS_DIR / "test_predictions.csv", index=False)

    if generate_plots:
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)

        # Generate comparison figures (MAE bar chart and time-series overlay)
        comp_plots = generate_model_comparison_plots(
            y_true=y_test.values,
            predictions=test_predictions,
            timestamps=test_df["timestamp"],
            output_dir=FIGURES_DIR,
        )
        artifacts.update(comp_plots)

        # Generate standard publication figures for Random Forest
        rf_plots = generate_evaluation_plots(
            y_true=y_test.values,
            y_pred=test_pred_rf,
            timestamps=test_df["timestamp"],
            feature_importances=rf.feature_importances_,
            feature_names=HOURLY_FEATURE_COLUMNS,
            output_dir=FIGURES_DIR,
        )
        artifacts.update(rf_plots)
        print(f"Saved evaluation and comparison figures to: {FIGURES_DIR}")

    return {
        "models": models_trained,
        "selected_model": selected_model_name,
        "val_scores": val_scores,
        "test_scores": test_scores,
        "artifacts": artifacts,
    }


def train_random_forest(
    hourly_data: Optional[pd.DataFrame] = None,
    params: Optional[Dict[str, Any]] = None,
    save_artifacts: bool = True,
    generate_plots: bool = True,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
) -> Dict[str, Any]:
    """Train Random Forest Regressor and evaluate against baseline models."""
    results = compare_models(
        hourly_data=hourly_data,
        rf_params=params,
        save_artifacts=save_artifacts,
        generate_plots=generate_plots,
        train_fraction=train_fraction,
        validation_fraction=validation_fraction,
    )
    rf_model = results["models"]["random_forest"]
    return {
        "model": rf_model,
        "train_metrics": results["val_scores"]["random_forest"],
        "val_metrics": results["val_scores"]["random_forest"],
        "test_metrics": results["test_scores"]["random_forest"],
        "artifacts": results["artifacts"],
    }


if __name__ == "__main__":
    compare_models()
