"""Execution script to optimize Random Forest Regressor and benchmark against original."""

from pathlib import Path
import sys
import time

# Ensure project root is in sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.ml.tune import tune_random_forest


def main():
    print("=" * 78)
    print(" RANDOM FOREST HYPERPARAMETER OPTIMIZATION WORKFLOW")
    print(" Evaluation Split: Strictly Validation Period for Model Selection")
    print("=" * 78)

    results = tune_random_forest(
        save_artifacts=True,
        generate_plots=True,
    )

    best_cfg = results["best_config"]
    orig_v = results["orig_val_metrics"]
    tuned_v = results["tuned_val_metrics"]
    orig_t = results["orig_test_metrics"]
    tuned_t = results["tuned_test_metrics"]
    artifacts = results["artifacts"]

    print("\n" + "=" * 78)
    print(" OPTIMIZATION SUMMARY REPORT")
    print("=" * 78)
    print(f"Best Hyperparameters:")
    print(f"  • n_estimators     : {best_cfg['n_estimators']}")
    print(f"  • max_depth        : {best_cfg['max_depth']}")
    print(f"  • min_samples_leaf : {best_cfg['min_samples_leaf']}")
    print(f"  • max_features     : {best_cfg['max_features']}")
    print("-" * 78)
    print(f"Validation Metric Improvement:")
    print(f"  • MAE  : {orig_v['mae']:.4f} kW  ->  {tuned_v['mae']:.4f} kW  ({tuned_v['mae'] - orig_v['mae']:+.4f} kW)")
    print(f"  • RMSE : {orig_v['rmse']:.4f} kW  ->  {tuned_v['rmse']:.4f} kW  ({tuned_v['rmse'] - orig_v['rmse']:+.4f} kW)")
    print(f"  • R²   : {orig_v['r2']:.4f}     ->  {tuned_v['r2']:.4f}     ({tuned_v['r2'] - orig_v['r2']:+.4f})")
    print("-" * 78)
    print(f"Final Held-Out Test Set Generalization:")
    print(f"  • MAE  : {orig_t['mae']:.4f} kW  ->  {tuned_t['mae']:.4f} kW  ({tuned_t['mae'] - orig_t['mae']:+.4f} kW)")
    print(f"  • RMSE : {orig_t['rmse']:.4f} kW  ->  {tuned_t['rmse']:.4f} kW  ({tuned_t['rmse'] - orig_t['rmse']:+.4f} kW)")
    print(f"  • R²   : {orig_t['r2']:.4f}     ->  {tuned_t['r2']:.4f}     ({tuned_t['r2'] - orig_t['r2']:+.4f})")
    print(f"  • MAPE : {orig_t['mape']:.2f}%    ->  {tuned_t['mape']:.2f}%    ({tuned_t['mape'] - orig_t['mape']:+.2f}%)")
    print("-" * 78)
    print(f"Total Workflow Duration: {results['duration_seconds']:.2f} seconds")

    print("\nGenerated Artifacts:")
    for name, path in artifacts.items():
        print(f"  • {name:<25}: {path}")
    print("=" * 78)


if __name__ == "__main__":
    main()
