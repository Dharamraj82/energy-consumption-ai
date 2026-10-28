"""Tests for loading the cleaned prediction dataset."""

import tempfile
import unittest
from pathlib import Path

from src.ml.data_loader import REQUIRED_COLUMNS, load_processed_data


def csv_text(columns=None, row=None):
    columns = list(columns or [
        "date",
        "time",
        "global_active_power",
        "global_reactive_power",
        "voltage",
        "global_intensity",
        "sub_metering_1",
        "sub_metering_2",
        "sub_metering_3",
    ])
    row = row or ["16/12/2006", "17:24:00", *([1.0] * (len(columns) - 2))]
    return ",".join(columns) + "\n" + ",".join(map(str, row)) + "\n"


class DataLoaderTests(unittest.TestCase):
    def test_loads_valid_csv_and_adds_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cleaned.csv"
            path.write_text(csv_text(), encoding="utf-8")

            loaded = load_processed_data(path)

        self.assertEqual(len(loaded), 1)
        self.assertIn("timestamp", loaded.columns)
        self.assertTrue(REQUIRED_COLUMNS.issubset(loaded.columns))
        self.assertEqual(str(loaded.loc[0, "timestamp"]), "2006-12-16 17:24:00")

    def test_missing_file_has_a_useful_error(self):
        with self.assertRaisesRegex(FileNotFoundError, "Processed dataset not found"):
            load_processed_data(Path("missing.csv"))

    def test_missing_required_columns_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-column.csv"
            path.write_text("date,time\n16/12/2006,17:24:00\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "missing columns"):
                load_processed_data(path)

    def test_invalid_timestamp_and_measurement_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            path.write_text(
                csv_text(row=["not-a-date", "17:24:00", *([1.0] * 7)]),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "invalid timestamps"):
                load_processed_data(path)

            path.write_text(
                csv_text(row=["16/12/2006", "17:24:00", "bad", *([1.0] * 6)]),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "non-numeric"):
                load_processed_data(path)

    def test_empty_files_fail_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "empty.csv"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "empty or malformed"):
                load_processed_data(path)


if __name__ == "__main__":
    unittest.main()
