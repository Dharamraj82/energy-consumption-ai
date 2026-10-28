"""Tests for validation-only baseline model experiments."""

import unittest

import numpy as np
import pandas as pd

from src.ml.train import run_baselines


def synthetic_series(rows=40):
    timestamps = pd.date_range("2024-01-01", periods=rows, freq="min")
    values = 2 + np.sin(np.arange(rows) / 3)
    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "global_active_power": values,
        }
    )


class TrainingTests(unittest.TestCase):
    def test_synthetic_data_runs_through_baselines(self):
        results = run_baselines(synthetic_series(), record_results=False)

        self.assertEqual(
            set(results),
            {"persistence", "linear_regression", "decision_tree", "random_forest"},
        )
        for metrics in results.values():
            self.assertEqual(set(metrics), {"mae", "rmse", "r2"})
            self.assertTrue(all(np.isfinite(value) for value in metrics.values()))

    def test_fixed_random_seeds_produce_repeatable_results(self):
        data = synthetic_series()
        first = run_baselines(data, record_results=False)
        second = run_baselines(data, record_results=False)

        self.assertEqual(first, second)

    def test_missing_target_fails_without_leaking_target_as_a_feature(self):
        data = synthetic_series()
        data.loc[0, "global_active_power"] = float("nan")
        with self.assertRaisesRegex(ValueError, "non-finite"):
            run_baselines(data, record_results=False)


if __name__ == "__main__":
    unittest.main()
