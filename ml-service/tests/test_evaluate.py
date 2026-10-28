"""Tests for regression metric validation and calculation."""

import math
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.ml.evaluate import append_result, regression_metrics


class EvaluationTests(unittest.TestCase):
    def test_metrics_match_known_values(self):
        metrics = regression_metrics([1, 2, 3], [1, 2, 4])

        self.assertAlmostEqual(metrics["mae"], 1 / 3)
        self.assertAlmostEqual(metrics["rmse"], math.sqrt(1 / 3))
        self.assertAlmostEqual(metrics["r2"], 0.5)

    def test_incompatible_empty_and_nonfinite_values_fail_clearly(self):
        with self.assertRaisesRegex(ValueError, "lengths differ"):
            regression_metrics([1, 2], [1])
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            regression_metrics([], [])
        with self.assertRaisesRegex(ValueError, "must all be finite"):
            regression_metrics([1, float("nan")], [1, 2])

    def test_non_vector_input_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, "one-dimensional"):
            regression_metrics([[1], [2]], [[1], [2]])
        with self.assertRaisesRegex(ValueError, "must be numeric"):
            regression_metrics(["not-numeric"], [1])

    def test_appending_same_result_twice_does_not_duplicate_it(self):
        result = {
            "experiment_id": "test-v1",
            "model_name": "persistence",
            "feature_set": "lag1",
            "split_strategy": "chronological",
            "evaluation_split": "validation",
            "mae": 0.25,
            "rmse": 0.5,
            "r2": 0.75,
            "notes": "synthetic test result",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.csv"

            append_result(result, path)
            append_result(result, path)

            recorded = pd.read_csv(path)

        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded.loc[0, "model_name"], "persistence")

    def test_distinct_result_is_appended(self):
        first = {
            "experiment_id": "test-v1",
            "model_name": "persistence",
            "feature_set": "lag1",
            "split_strategy": "chronological",
            "evaluation_split": "validation",
            "mae": 0.25,
            "rmse": 0.5,
            "r2": 0.75,
            "notes": "first result",
        }
        second = {**first, "model_name": "linear_regression"}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.csv"

            append_result(first, path)
            append_result(second, path)

            recorded = pd.read_csv(path)

        self.assertEqual(recorded["model_name"].tolist(), [
            "persistence", "linear_regression"
        ])

    def test_incompatible_existing_results_schema_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.csv"
            path.write_text("unexpected,columns\n1,2\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "unexpected schema"):
                append_result({}, path)


if __name__ == "__main__":
    unittest.main()
