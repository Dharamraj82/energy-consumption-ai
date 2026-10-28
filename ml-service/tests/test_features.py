"""Tests for leakage-aware next-observation feature construction."""

import unittest

import pandas as pd

from src.ml.features import FEATURE_COLUMNS, make_next_observation_dataset


def sample_data():
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(
                ["2006-12-16 17:25", "2006-12-16 17:24", "2006-12-16 17:27"]
            ),
            "global_active_power": [20.0, 10.0, 30.0],
        }
    )


class FeatureTests(unittest.TestCase):
    def test_sorts_rows_and_uses_only_prior_observations(self):
        features = make_next_observation_dataset(sample_data())

        self.assertEqual(features["previous_active_power"].tolist(), [10.0, 20.0])
        self.assertEqual(features["target"].tolist(), [20.0, 30.0])
        self.assertEqual(features["timestamp"].dt.minute.tolist(), [24, 25])
        self.assertEqual(
            features["target_timestamp"].dt.minute.tolist(), [25, 27]
        )
        self.assertEqual(set(FEATURE_COLUMNS), {
            "previous_active_power", "hour", "minute", "day_of_week"
        })
        self.assertNotIn("target", FEATURE_COLUMNS)

    def test_missing_columns_invalid_timestamps_and_empty_input_fail_clearly(self):
        with self.assertRaisesRegex(ValueError, "missing columns"):
            make_next_observation_dataset(
                pd.DataFrame({"global_active_power": [1.0]})
            )
        with self.assertRaisesRegex(ValueError, "invalid timestamps"):
            make_next_observation_dataset(
                pd.DataFrame(
                    {"timestamp": ["invalid"], "global_active_power": [1.0]}
                )
            )
        with self.assertRaisesRegex(ValueError, "empty"):
            make_next_observation_dataset(
                pd.DataFrame(
                    {"timestamp": pd.to_datetime([]), "global_active_power": []}
                )
            )

    def test_missing_and_nonfinite_targets_are_rejected(self):
        data = sample_data()
        data.loc[0, "global_active_power"] = float("nan")
        with self.assertRaisesRegex(ValueError, "non-finite"):
            make_next_observation_dataset(data)

        data.loc[0, "global_active_power"] = float("inf")
        with self.assertRaisesRegex(ValueError, "non-finite"):
            make_next_observation_dataset(data)

    def test_repeated_calls_are_deterministic(self):
        pd.testing.assert_frame_equal(
            make_next_observation_dataset(sample_data()),
            make_next_observation_dataset(sample_data()),
        )


if __name__ == "__main__":
    unittest.main()
