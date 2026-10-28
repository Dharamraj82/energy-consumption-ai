"""Evaluation metrics, visual reporting, and experiment result recording."""

from io import StringIO
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # Headless backend for reliable server/script execution
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RESULTS_PATH = PROJECT_ROOT / "reports" / "model_comparison.csv"
METRICS_DIR = PROJECT_ROOT / "reports" / "metrics"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

RESULT_COLUMNS = [
    "experiment_id", "model_name", "feature_set", "split_strategy",
    "evaluation_split", "mae", "rmse", "r2", "notes"
]


def regression_metrics(
    actual,
    predicted,
    include_mape: bool = True,
    epsilon: float = 1e-4,
) -> dict:
    """Compute regression metrics (MAE, RMSE, R2, and optionally MAPE).

    Parameters
    ----------
    actual : array-like
        Ground truth numeric values.
    predicted : array-like
        Predicted numeric values.
    include_mape : bool, default=True
        Whether to compute Mean Absolute Percentage Error (MAPE).
    epsilon : float, default=1e-4
        Epsilon floor to avoid division-by-zero or numerical inflation when
        actual values are zero or near zero (e.g. household power near 0 kW).
        Formula: 100 * mean( |y - y_hat| / max(|y|, epsilon) )

    Returns
    -------
    dict
        Dictionary containing 'mae', 'rmse', 'r2', and optionally 'mape'.
    """
    try:
        actual = np.asarray(actual, dtype=float)
        predicted = np.asarray(predicted, dtype=float)
    except (TypeError, ValueError) as error:
        raise ValueError("Actual and predicted values must be numeric.") from error
    if actual.ndim != 1 or predicted.ndim != 1:
        raise ValueError("Actual and predicted values must be one-dimensional.")
    if actual.size == 0:
        raise ValueError("Actual and predicted values must not be empty.")
    if actual.size != predicted.size:
        raise ValueError(
            f"Actual and predicted lengths differ: {actual.size} != {predicted.size}."
        )
    if not np.isfinite(actual).all() or not np.isfinite(predicted).all():
        raise ValueError("Actual and predicted values must all be finite.")

    metrics = {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
        "r2": float(r2_score(actual, predicted)) if len(actual) >= 2 else float("nan"),
    }

    if include_mape:
        # Explicit epsilon floor strategy for low/zero actual power readings
        denom = np.maximum(np.abs(actual), epsilon)
        metrics["mape"] = float(np.mean(np.abs(actual - predicted) / denom) * 100)

    return metrics


def append_result(result: dict, path: Path = RESULTS_PATH) -> None:
    """Append a measured result unless the exact result is already recorded."""
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {column: result.get(column, "") for column in RESULT_COLUMNS}
    result_frame = pd.DataFrame([row], columns=RESULT_COLUMNS)
    if path.exists():
        existing = pd.read_csv(path, dtype=str, keep_default_na=False)
        if list(existing.columns) != RESULT_COLUMNS:
            raise ValueError(
                f"Experiment results have an unexpected schema in {path}."
            )
        normalized_result = pd.read_csv(
            StringIO(result_frame.to_csv(index=False)),
            dtype=str,
            keep_default_na=False,
        ).iloc[0]
        if existing.eq(normalized_result).all(axis=1).any():
            return
    result_frame.to_csv(
        path, mode="a", header=not path.exists(), index=False
    )


def save_metrics_report(
    train_metrics: dict,
    val_metrics: dict,
    test_metrics: dict,
    output_dir: Path = METRICS_DIR,
) -> Tuple[Path, Path]:
    """Save evaluation metrics to structured JSON and CSV files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "train": train_metrics,
        "validation": val_metrics,
        "test": test_metrics,
    }

    json_path = output_dir / "evaluation_metrics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    df_rows = []
    for split_name, scores in summary.items():
        df_rows.append({"split": split_name, **scores})
    df = pd.DataFrame(df_rows)
    csv_path = output_dir / "evaluation_metrics.csv"
    df.to_csv(csv_path, index=False)

    return json_path, csv_path


def generate_evaluation_plots(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    timestamps: Optional[pd.Series] = None,
    feature_importances: Optional[np.ndarray] = None,
    feature_names: Optional[List[str]] = None,
    output_dir: Path = FIGURES_DIR,
) -> Dict[str, Path]:
    """Generate conference-grade publication figures for Random Forest evaluation.

    Generates:
    1. actual_vs_predicted.png (Time-series overlay + scatter plot)
    2. residuals_plot.png (Residuals vs. predicted and over time)
    3. feature_importance.png (Horizontal bar chart of Gini importances)
    4. error_summary.png (Histogram and KDE of prediction residuals)
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = {}

    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    residuals = y_true - y_pred

    sns.set_theme(style="whitegrid", font_scale=1.05)

    # 1. Actual versus Predicted Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Top panel: 168-hour (one full week) sample time-series comparison
    sample_len = min(168, len(y_true))
    x_axis = (
        timestamps.iloc[:sample_len]
        if timestamps is not None and len(timestamps) >= sample_len
        else np.arange(sample_len)
    )
    ax1.plot(x_axis, y_true[:sample_len], label="Actual Power (kW)", color="#1f77b4", lw=2)
    ax1.plot(x_axis, y_pred[:sample_len], label="Predicted Power (kW)", color="#ff7f0e", lw=2, linestyle="--")
    ax1.set_title(f"Test Set Prediction Horizon — One-Week Dynamic Tracking (First {sample_len} Hours)")
    ax1.set_ylabel("Active Power (kW)")
    ax1.set_xlabel("Timestamp / Hourly Step")
    ax1.legend(loc="upper right")

    # Bottom panel: Full test set scatter plot
    ax2.scatter(y_true, y_pred, alpha=0.25, color="#2ca02c", edgecolors="none", s=20)
    min_val = min(y_true.min(), y_pred.min())
    max_val = max(y_true.max(), y_pred.max())
    ax2.plot([min_val, max_val], [min_val, max_val], "r--", lw=2, label="Ideal Perfect Fit (y = x)")
    r2_val = r2_score(y_true, y_pred)
    mae_val = mean_absolute_error(y_true, y_pred)
    ax2.set_title(f"Actual vs. Predicted Scatter (Test Set: {len(y_true):,} samples | R² = {r2_val:.4f}, MAE = {mae_val:.4f} kW)")
    ax2.set_xlabel("Actual Power (kW)")
    ax2.set_ylabel("Predicted Power (kW)")
    ax2.legend(loc="upper left")

    plt.tight_layout()
    path1 = output_dir / "actual_vs_predicted.png"
    fig.savefig(path1, dpi=200)
    plt.close(fig)
    generated["actual_vs_predicted"] = path1

    # 2. Residuals Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 9))

    # Top panel: Residuals vs. Predicted
    ax1.scatter(y_pred, residuals, alpha=0.25, color="#9467bd", edgecolors="none", s=20)
    ax1.axhline(0, color="red", linestyle="--", lw=1.8, label="Zero Error Line")
    std_res = np.std(residuals)
    ax1.axhline(1.96 * std_res, color="gray", linestyle=":", label="±1.96σ Bounds")
    ax1.axhline(-1.96 * std_res, color="gray", linestyle=":")
    ax1.set_title("Residuals vs. Predicted Values")
    ax1.set_xlabel("Predicted Power (kW)")
    ax1.set_ylabel("Residual (Actual - Predicted, kW)")
    ax1.legend(loc="upper right")

    # Bottom panel: Residuals across chronological test index
    ax2.plot(residuals, color="#7f7f7f", lw=0.8, alpha=0.7)
    ax2.axhline(0, color="red", linestyle="--", lw=1.8)
    ax2.set_title("Prediction Error Over Chronological Test Sequence")
    ax2.set_xlabel("Chronological Test Step (Hours)")
    ax2.set_ylabel("Residual (kW)")

    plt.tight_layout()
    path2 = output_dir / "residuals_plot.png"
    fig.savefig(path2, dpi=200)
    plt.close(fig)
    generated["residuals_plot"] = path2

    # 3. Feature Importance Plot
    if feature_importances is not None and feature_names is not None:
        fig, ax = plt.subplots(figsize=(10, 6))
        fi_df = pd.DataFrame({
            "feature": feature_names,
            "importance": feature_importances,
        }).sort_values("importance", ascending=True)

        bars = ax.barh(fi_df["feature"], fi_df["importance"], color="#3b528b", edgecolor="black")
        for bar in bars:
            width = bar.get_width()
            ax.text(
                width + 0.005,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.4f}",
                va="center",
                ha="left",
                fontsize=10,
            )
        ax.set_title("Random Forest Regressor — Relative Feature Importance (MDI)")
        ax.set_xlabel("Mean Decrease in Impurity (Gini Importance)")
        ax.set_xlim(0, max(fi_df["importance"]) * 1.15)
        plt.tight_layout()
        path3 = output_dir / "feature_importance.png"
        fig.savefig(path3, dpi=200)
        plt.close(fig)
        generated["feature_importance"] = path3

    # 4. Error Summary Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(residuals, bins=60, kde=True, color="#d62728", ax=ax, stat="density")
    mean_err = np.mean(residuals)
    rmse_val = np.sqrt(mean_squared_error(y_true, y_pred))

    ax.axvline(0, color="black", linestyle="--", lw=1.5, label="Zero Error")
    ax.axvline(mean_err, color="blue", linestyle="-.", lw=1.5, label=f"Mean Error ({mean_err:.4f} kW)")

    info_text = (
        f"Mean Error (Bias): {mean_err:.4f} kW\n"
        f"Std Dev: {std_res:.4f} kW\n"
        f"MAE: {mae_val:.4f} kW\n"
        f"RMSE: {rmse_val:.4f} kW\n"
        f"Sample Count: {len(residuals):,}"
    )
    ax.text(
        0.05, 0.95, info_text,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="white", alpha=0.9, edgecolor="gray"),
    )
    ax.set_title("Test-Set Prediction Error (Residual) Distribution")
    ax.set_xlabel("Error (Actual - Predicted, kW)")
    ax.set_ylabel("Probability Density")
    ax.legend(loc="upper right")

    plt.tight_layout()
    path4 = output_dir / "error_summary.png"
    fig.savefig(path4, dpi=200)
    plt.close(fig)
    generated["error_summary"] = path4

    return generated


def generate_model_comparison_plots(
    y_true: np.ndarray,
    predictions: Dict[str, np.ndarray],
    timestamps: Optional[pd.Series] = None,
    output_dir: Path = FIGURES_DIR,
) -> Dict[str, Path]:
    """Generate comparative visualization plots for model benchmark.

    Generates:
    1. model_mae_comparison.png (Bar chart comparing Test MAE across all models)
    2. model_comparison_actual_vs_predicted.png (Time-series trajectory tracking overlay)

    Parameters
    ----------
    y_true : np.ndarray
        True target values on test set.
    predictions : Dict[str, np.ndarray]
        Dictionary mapping model names to predicted values arrays.
    timestamps : Optional[pd.Series]
        Timestamp series for chronological time axis.
    output_dir : Path
        Directory to save generated figures.

    Returns
    -------
    Dict[str, Path]
        Dictionary of generated plot paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated = {}

    y_true = np.asarray(y_true, dtype=float)
    sns.set_theme(style="whitegrid", font_scale=1.05)

    # 1. Test MAE Comparison Bar Chart
    model_labels = {
        "persistence": "Persistence Baseline",
        "linear_regression": "Linear Regression",
        "random_forest": "Random Forest Regressor",
    }
    mae_values = {}
    for name, preds in predictions.items():
        label = model_labels.get(name, name.replace("_", " ").title())
        mae_values[label] = mean_absolute_error(y_true, preds)

    fig, ax = plt.subplots(figsize=(9, 6))
    names = list(mae_values.keys())
    values = list(mae_values.values())
    colors = ["#d95f02", "#7570b3", "#1b9e77"]

    bars = ax.bar(names, values, color=colors[:len(names)], width=0.55, edgecolor="black")
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height:.4f} kW",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.set_title("Test Set Mean Absolute Error (MAE) Comparison", fontsize=14, pad=15)
    ax.set_ylabel("MAE (kW)", fontsize=12)
    ax.set_ylim(0, max(values) * 1.2)
    plt.tight_layout()

    mae_chart_path = output_dir / "model_mae_comparison.png"
    fig.savefig(mae_chart_path, dpi=200)
    plt.close(fig)
    generated["model_mae_comparison"] = mae_chart_path

    # 2. Actual vs Predicted Trajectory Tracking Comparison (168 Hours / 1 Week Window)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 11), sharex=False)

    sample_len = min(168, len(y_true))
    x_axis = (
        timestamps.iloc[:sample_len]
        if timestamps is not None and len(timestamps) >= sample_len
        else np.arange(sample_len)
    )

    # Top Panel: Actual vs Random Forest vs Baselines
    ax1.plot(x_axis, y_true[:sample_len], label="Actual Observed Power", color="black", lw=2.5, zorder=5)
    if "random_forest" in predictions:
        ax1.plot(x_axis, predictions["random_forest"][:sample_len], label="Random Forest", color="#1b9e77", lw=2, linestyle="-")
    if "linear_regression" in predictions:
        ax1.plot(x_axis, predictions["linear_regression"][:sample_len], label="Linear Regression", color="#7570b3", lw=1.8, linestyle="--")
    if "persistence" in predictions:
        ax1.plot(x_axis, predictions["persistence"][:sample_len], label="Persistence", color="#d95f02", lw=1.5, linestyle=":")

    ax1.set_title(f"Dynamic Trajectory Tracking on Untouched Test Set (One-Week Slice: {sample_len} Hours)", fontsize=13)
    ax1.set_ylabel("Active Power (kW)", fontsize=11)
    ax1.legend(loc="upper right", frameon=True)

    # Bottom Panel: Zoomed 48-Hour Detail
    zoom_len = min(48, sample_len)
    x_zoom = x_axis[:zoom_len]
    ax2.plot(x_zoom, y_true[:zoom_len], label="Actual Observed Power", color="black", lw=2.5, marker="o", markersize=3, zorder=5)
    if "random_forest" in predictions:
        ax2.plot(x_zoom, predictions["random_forest"][:zoom_len], label="Random Forest", color="#1b9e77", lw=2, marker="s", markersize=3)
    if "linear_regression" in predictions:
        ax2.plot(x_zoom, predictions["linear_regression"][:zoom_len], label="Linear Regression", color="#7570b3", lw=1.8, linestyle="--")
    if "persistence" in predictions:
        ax2.plot(x_zoom, predictions["persistence"][:zoom_len], label="Persistence", color="#d95f02", lw=1.5, linestyle=":")

    ax2.set_title(f"High-Resolution 48-Hour Peak and Trough Response", fontsize=13)
    ax2.set_ylabel("Active Power (kW)", fontsize=11)
    ax2.set_xlabel("Observation Timestamp / Hour", fontsize=11)
    ax2.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    comparison_curve_path = output_dir / "model_comparison_actual_vs_predicted.png"
    fig.savefig(comparison_curve_path, dpi=200)
    plt.close(fig)
    generated["model_comparison_actual_vs_predicted"] = comparison_curve_path

    return generated


def generate_tuning_comparison_plot(
    orig_val_metrics: dict,
    tuned_val_metrics: dict,
    output_dir: Path = FIGURES_DIR,
) -> Path:
    """Generate comparison bar chart of Original vs. Tuned Random Forest validation metrics."""
    output_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", font_scale=1.05)

    labels = ["Validation MAE", "Validation RMSE"]
    orig_vals = [orig_val_metrics["mae"], orig_val_metrics["rmse"]]
    tuned_vals = [tuned_val_metrics["mae"], tuned_val_metrics["rmse"]]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 6))
    bars1 = ax.bar(x - width / 2, orig_vals, width, label="Original Random Forest", color="#4393c3", edgecolor="black")
    bars2 = ax.bar(x + width / 2, tuned_vals, width, label="Tuned Random Forest", color="#2166ac", edgecolor="black")

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.4f} kW",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=11,
                fontweight="bold",
            )

    # Annotate percentage improvement on MAE
    mae_diff = ((orig_vals[0] - tuned_vals[0]) / orig_vals[0]) * 100
    if mae_diff > 0:
        improvement_note = f"Validation MAE Improvement: -{mae_diff:.2f}%"
    else:
        improvement_note = f"Validation MAE Difference: {abs(mae_diff):.2f}%"

    ax.set_title(f"Random Forest Hyperparameter Tuning — Validation Set Comparison\n({improvement_note})", fontsize=13, pad=15)
    ax.set_ylabel("Error Metric (kW)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylim(0, max(orig_vals + tuned_vals) * 1.25)
    ax.legend(loc="upper right", frameon=True)

    plt.tight_layout()
    plot_path = output_dir / "model_tuning_comparison.png"
    fig.savefig(plot_path, dpi=200)
    plt.close(fig)

    return plot_path


