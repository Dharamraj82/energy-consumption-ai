"""Tests for chronological dataset splitting."""

import unittest

import pandas as pd

from src.ml.preprocessing import (
    chronological_split,
    chronological_train_validation_test_split,
)


class PreprocessingTests(unittest.TestCase):
    def test_three_way_split_preserves_order_and_rows(self):
        data = pd.DataFrame({"row": range(10)})

        train, validation, test = chronological_train_validation_test_split(data)

        self.assertEqual(train["row"].tolist(), list(range(6)))
        self.assertEqual(validation["row"].tolist(), [6, 7])
        self.assertEqual(test["row"].tolist(), [8, 9])

    def test_three_way_split_rejects_invalid_fraction_and_too_few_rows(self):
        data = pd.DataFrame({"row": range(3)})
        with self.assertRaisesRegex(ValueError, "sum to less than 1"):
            chronological_train_validation_test_split(data, 0.7, 0.3)
        with self.assertRaisesRegex(ValueError, "too small"):
            chronological_train_validation_test_split(data, 0.2, 0.2)
        with self.assertRaisesRegex(ValueError, "fractions must be positive"):
            chronological_train_validation_test_split(data, float("nan"), 0.2)

    def test_two_way_split_retains_existing_behavior(self):
        data = pd.DataFrame({"row": range(5)})

        train, test = chronological_split(data)

        self.assertEqual(train["row"].tolist(), [0, 1, 2, 3])
        self.assertEqual(test["row"].tolist(), [4])


if __name__ == "__main__":
    unittest.main()
