"""Standalone execution script to run the fair benchmark comparison and train Random Forest."""

import argparse
from pathlib import Path
import sys
import time

# Ensure project root is in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ml.train import DEFAULT_RF_PARAMS, compare_models


def parse_args():
    parser = argparse.ArgumentParser(
        description="Benchmark Persistence, Linear Regression, and Random Forest on UCI Household Electricity dataset."
    )
    parser.add_argument(
        "--n-estimators",
        type=int,
        default=DEFAULT_RF_PARAMS["n_estimators"],
        help=f"Number of trees in forest (default: {DEFAULT_RF_PARAMS['n_estimators']})",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=DEFAULT_RF_PARAMS["max_depth"],
        help=f"Max tree depth (default: {DEFAULT_RF_PARAMS['max_depth']})",
    )
    parser.add_argument(
        "--min-samples-leaf",
        type=int,
        default=DEFAULT_RF_PARAMS["min_samples_leaf"],
        help=f"Min samples per leaf (default: {DEFAULT_RF_PARAMS['min_samples_leaf']})",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=DEFAULT_RF_PARAMS["random_state"],
        help=f"Random seed (default: {DEFAULT_RF_PARAMS['random_state']})",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip figure generation",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    rf_params = {
        "n_estimators": args.n_estimators,
        "max_depth": args.max_depth,
        "min_samples_leaf": args.min_samples_leaf,
        "random_state": args.random_state,
        "n_jobs": -1,
    }

    start_time = time.time()
    results = compare_models(
        rf_params=rf_params,
        save_artifacts=True,
        generate_plots=not args.no_plots,
    )
    elapsed = time.time() - start_time

    val_scores = results["val_scores"]
    test_scores = results["test_scores"]
    selected = results["selected_model"]
    artifacts = results["artifacts"]

    print("\n" + "=" * 80)
    print(" FAIR BENCHMARK SUMMARY (Next-Hour Mean Active Power, kW)")
    print("=" * 80)
    print(f"{'Model Name':<22} {'Val MAE':<10} {'Val RMSE':<10} {'Val R²':<10} {'Test MAE':<10} {'Test RMSE':<10} {'Test R²':<10} {'Test MAPE':<10}")
    print("-" * 80)
    for model_name in ["persistence", "linear_regression", "random_forest"]:
        v = val_scores[model_name]
        t = test_scores[model_name]
        star = " [SELECTED]" if model_name == selected else ""
        print(
            f"{model_name:<22} "
            f"{v['mae']:<10.4f} {v['rmse']:<10.4f} {v['r2']:<10.4f} "
            f"{t['mae']:<10.4f} {t['rmse']:<10.4f} {t['r2']:<10.4f} {t['mape']:<9.2f}%"
            f"{star}"
        )
    print("-" * 80)
    print(f"Total benchmark elapsed time: {elapsed:.2f} seconds")

    print("\nGenerated Artifacts:")
    for key, path in artifacts.items():
        print(f"  • {key:<35}: {path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
