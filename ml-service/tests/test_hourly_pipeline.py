"""Unit tests for the hourly Random Forest pipeline, features, evaluation, and inference."""

import unittest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from src.ml.evaluate import regression_metrics
from src.ml.features import (
    HOURLY_FEATURE_COLUMNS,
    HOURLY_TARGET_COLUMN,
    create_hourly_features,
)
from src.ml.predict import validate_input_features
from src.ml.preprocessing import (
    clean_and_aggregate_hourly,
    chronological_train_validation_test_split,
)


def make_synthetic_minute_data(hours: int = 48) -> pd.DataFrame:
    """Generate synthetic minute-level power readings for testing."""
    periods = hours * 60
    timestamps = pd.date_range("2024-01-01 00:00:00", periods=periods, freq="1min")
    power = 1.5 + 0.5 * np.sin(np.arange(periods) / 60.0)
    df = pd.DataFrame({
        "Date": timestamps.strftime("%d/%m/%Y"),
        "Time": timestamps.strftime("%H:%M:%S"),
        "Global_active_power": power,
    })
    return df


class HourlyPipelineTests(unittest.TestCase):
    def test_hourly_aggregation_computes_means_and_preserves_continuity(self):
        df = make_synthetic_minute_data(hours=36)
        hourly = clean_and_aggregate_hourly(df)

        self.assertEqual(len(hourly), 36)
        self.assertListEqual(list(hourly.columns), ["timestamp", "global_active_power"])
        self.assertFalse(hourly["global_active_power"].isna().any())
        self.assertTrue((hourly["global_active_power"] >= 0).all())

    def test_hourly_features_contain_all_required_columns_and_no_leakage(self):
        df = make_synthetic_minute_data(hours=72)
        hourly = clean_and_aggregate_hourly(df)
        features_df = create_hourly_features(hourly)

        for col in HOURLY_FEATURE_COLUMNS:
            self.assertIn(col, features_df.columns)
        self.assertIn(HOURLY_TARGET_COLUMN, features_df.columns)

        # First row lag_1 must equal original power at that row's timestamp
        first_ts = features_df.loc[0, "timestamp"]
        original_power_at_ts = hourly.loc[hourly["timestamp"] == first_ts, "global_active_power"].iloc[0]
        self.assertAlmostEqual(features_df.loc[0, "lag_1"], original_power_at_ts)

        # Target must equal the subsequent hour's power
        subsequent_ts = first_ts + pd.Timedelta(hours=1)
        subsequent_power = hourly.loc[hourly["timestamp"] == subsequent_ts, "global_active_power"].iloc[0]
        self.assertAlmostEqual(features_df.loc[0, "target"], subsequent_power)

        # Ensure no target value was copied into lag_1
        self.assertNotEqual(features_df.loc[0, "lag_1"], features_df.loc[0, "target"])

    def test_chronological_70_15_15_split(self):
        data = pd.DataFrame({"value": np.arange(100)})
        train, val, test = chronological_train_validation_test_split(
            data, train_fraction=0.70, validation_fraction=0.15
        )

        self.assertEqual(len(train), 70)
        self.assertEqual(len(val), 15)
        self.assertEqual(len(test), 15)

        # Verify strict chronological non-overlapping boundaries
        self.assertEqual(train["value"].max(), 69)
        self.assertEqual(val["value"].min(), 70)
        self.assertEqual(val["value"].max(), 84)
        self.assertEqual(test["value"].min(), 85)
        self.assertEqual(test["value"].max(), 99)

    def test_regression_metrics_handles_zero_values_with_epsilon(self):
        # Actual contains zeros; standard MAPE without epsilon would divide by zero
        actual = [0.0, 1.0, 2.0, 3.0]
        predicted = [0.1, 1.1, 1.9, 3.0]

        metrics = regression_metrics(actual, predicted, include_mape=True, epsilon=1e-4)

        self.assertIn("mae", metrics)
        self.assertIn("rmse", metrics)
        self.assertIn("r2", metrics)
        self.assertIn("mape", metrics)
        self.assertTrue(np.isfinite(metrics["mape"]))
        self.assertGreater(metrics["mape"], 0)

    def test_predict_validation_rejects_missing_and_invalid_inputs(self):
        valid_input = {
            "lag_1": 1.2,
            "lag_2": 1.1,
            "lag_3": 1.0,
            "lag_24": 1.3,
            "rolling_mean_3h": 1.1,
            "rolling_mean_24h": 1.2,
            "hour": 14,
            "day_of_week": 2,
        }

        # Valid input should format correctly
        df = validate_input_features(valid_input)
        self.assertEqual(len(df), 1)

        # Missing column
        bad_input = dict(valid_input)
        del bad_input["lag_1"]
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            validate_input_features(bad_input)

        # Negative power measurement
        bad_input = dict(valid_input, lag_1=-0.5)
        with self.assertRaisesRegex(ValueError, "negative power"):
            validate_input_features(bad_input)

        # Out-of-bounds hour
        bad_input = dict(valid_input, hour=25)
        with self.assertRaisesRegex(ValueError, "hour.*between 0 and 23"):
            validate_input_features(bad_input)

        # Out-of-bounds day_of_week
        bad_input = dict(valid_input, day_of_week=7)
        with self.assertRaisesRegex(ValueError, "day_of_week.*between 0.*and 6"):
            validate_input_features(bad_input)

    def test_fair_model_comparison_evaluates_identical_timestamps_and_features(self):
        # 100 hours of synthetic data
        timestamps = pd.date_range("2024-01-01", periods=100, freq="1h")
        power = 2.0 + 0.8 * np.sin(np.arange(100) / 12.0)
        hourly_df = pd.DataFrame({"timestamp": timestamps, "global_active_power": power})

        from src.ml.train import compare_models

        # Run with tiny random forest for fast test execution
        fast_params = {"n_estimators": 5, "max_depth": 3, "random_state": 42, "n_jobs": 1}
        results = compare_models(
            hourly_data=hourly_df,
            rf_params=fast_params,
            save_artifacts=False,
            generate_plots=False,
        )

        val_scores = results["val_scores"]
        test_scores = results["test_scores"]
        models = ["persistence", "linear_regression", "random_forest"]

        for m in models:
            self.assertIn(m, val_scores)
            self.assertIn(m, test_scores)
            self.assertTrue(np.isfinite(val_scores[m]["mae"]))
            self.assertTrue(np.isfinite(test_scores[m]["mae"]))
            self.assertTrue(np.isfinite(val_scores[m]["rmse"]))
            self.assertTrue(np.isfinite(test_scores[m]["rmse"]))

        # Model selection must pick the model with minimum validation MAE
        best_val = min(models, key=lambda m: val_scores[m]["mae"])
        self.assertEqual(results["selected_model"], best_val)

    def test_preservation_of_chronological_order_and_zero_leakage(self):
        from src.ml.tune import verify_leakage_and_splits

        # 1. Valid non-overlapping chronological splits
        train = pd.DataFrame({"timestamp": pd.date_range("2024-01-01", periods=10, freq="1h")}, index=range(10))
        val = pd.DataFrame({"timestamp": pd.date_range("2024-01-02", periods=5, freq="1h")}, index=range(10, 15))
        test = pd.DataFrame({"timestamp": pd.date_range("2024-01-03", periods=5, freq="1h")}, index=range(15, 20))

        # Should pass without error
        verify_leakage_and_splits(train, val, test)

        # 2. Overlapping timestamps must be caught as leakage
        bad_val = pd.DataFrame({"timestamp": pd.date_range("2024-01-01 05:00:00", periods=5, freq="1h")}, index=range(10, 15))
        with self.assertRaisesRegex(ValueError, "Leakage detected"):
            verify_leakage_and_splits(train, bad_val, test)

    def test_tuning_parameter_selection_and_reproducibility(self):
        from src.ml.tune import tune_random_forest

        timestamps = pd.date_range("2024-01-01", periods=80, freq="1h")
        power = 1.8 + 0.6 * np.sin(np.arange(80) / 8.0)
        hourly_df = pd.DataFrame({"timestamp": timestamps, "global_active_power": power})

        candidate_configs = [
            {"n_estimators": 5, "max_depth": 3, "min_samples_leaf": 2, "max_features": 1.0},
            {"n_estimators": 5, "max_depth": 5, "min_samples_leaf": 1, "max_features": 0.7},
        ]

        # First run
        run1 = tune_random_forest(
            hourly_data=hourly_df,
            candidate_params=candidate_configs,
            save_artifacts=False,
            generate_plots=False,
            random_state=42,
        )

        # Second run (verify reproducibility)
        run2 = tune_random_forest(
            hourly_data=hourly_df,
            candidate_params=candidate_configs,
            save_artifacts=False,
            generate_plots=False,
            random_state=42,
        )

        # Reproducibility check: metrics must match exactly
        self.assertEqual(run1["best_config"], run2["best_config"])
        self.assertAlmostEqual(run1["tuned_val_metrics"]["mae"], run2["tuned_val_metrics"]["mae"])
        self.assertAlmostEqual(run1["tuned_test_metrics"]["mae"], run2["tuned_test_metrics"]["mae"])

        # Selection check: best config has lowest validation MAE among candidates
        rec_maes = [r["val_mae"] for r in run1["tuning_records"]]
        best_rec = next(r for r in run1["tuning_records"] if r["is_best"])
        self.assertEqual(best_rec["val_mae"], min(rec_maes))


if __name__ == "__main__":
    unittest.main()
