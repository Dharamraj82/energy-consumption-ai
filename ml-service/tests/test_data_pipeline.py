"""Tests for loading, validating, and cleaning household power data."""

import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data.clean_data import clean_data, normalize_column_name
from src.data.inspect_data import build_quality_report
from src.data.load_data import load_raw_data
from src.data.validate_data import EXPECTED_COLUMNS, validate_data


class DataPipelineTests(unittest.TestCase):
    def test_load_raw_data_parses_source_delimiter_and_missing_marker(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            source.write_text(
                ";".join(EXPECTED_COLUMNS)
                + "\n16/12/2006;17:24:00;?;0.418;234.840;18.400;0;1;17\n",
                encoding="utf-8",
            )
            data = load_raw_data(source)

        self.assertEqual(list(data.columns), EXPECTED_COLUMNS)
        self.assertTrue(pd.isna(data.loc[0, "Global_active_power"]))

    def test_validation_preserves_missing_values_and_converts_numbers(self) -> None:
        data = pd.DataFrame(
            [["16/12/2006", "17:24:00", None, "0.418", "234.840", "18.4", "0", "1", "17"]],
            columns=EXPECTED_COLUMNS,
        )

        validated = validate_data(data)

        self.assertEqual(len(validated), 1)
        self.assertTrue(pd.isna(validated.loc[0, "Global_active_power"]))
        self.assertEqual(validated["Voltage"].dtype.kind, "f")

    def test_validation_rejects_invalid_dates_and_numeric_values(self) -> None:
        data = pd.DataFrame(
            [["invalid", "17:24:00", "4.2", "0.418", "234.840", "18.4", "0", "1", "17"]],
            columns=EXPECTED_COLUMNS,
        )
        with self.assertRaisesRegex(ValueError, "Date"):
            validate_data(data)

        data.loc[0, "Date"] = "16/12/2006"
        data.loc[0, "Voltage"] = "bad"
        with self.assertRaisesRegex(ValueError, "Voltage"):
            validate_data(data)

        data.loc[0, "Voltage"] = "234.8"
        data.loc[0, "Global_active_power"] = "inf"
        with self.assertRaisesRegex(ValueError, "infinite"):
            validate_data(data)

    def test_cleaning_drops_incomplete_rows(self) -> None:
        data = pd.DataFrame(
            [
                ["16/12/2006", "17:24:00", 4.2, 0.4, 234.8, 18.4, 0, 1, 17],
                ["16/12/2006", "17:25:00", None, 0.4, 234.8, 18.4, 0, 1, 17],
            ],
            columns=EXPECTED_COLUMNS,
        )

        cleaned = clean_data(data)

        self.assertEqual(len(cleaned), 1)
        self.assertFalse(cleaned.isna().any().any())
        self.assertEqual(
            list(cleaned.columns),
            [column.lower() for column in EXPECTED_COLUMNS],
        )

    def test_normalize_column_name_standardizes_spaces_punctuation_and_case(self) -> None:
        examples = {
            " Energy Consumption ": "energy_consumption",
            "Day of Week": "day_of_week",
            "temperature (c)": "temperature_c",
            "_temperature__c_": "temperature_c",
            "load-%/# (kWh)": "load_kwh",
        }

        for original, expected in examples.items():
            with self.subTest(original=original):
                self.assertEqual(normalize_column_name(original), expected)

    def test_cleaning_rejects_colliding_or_empty_normalized_column_names(self) -> None:
        colliding = pd.DataFrame([[1, 2]], columns=["A-B", "A B"])
        with self.assertRaisesRegex(ValueError, "not unique"):
            clean_data(colliding)

        empty_name = pd.DataFrame([[1]], columns=["---"])
        with self.assertRaisesRegex(ValueError, "no alphanumeric"):
            clean_data(empty_name)

    def test_inspection_report_documents_structure_and_quality(self) -> None:
        data = pd.DataFrame(
            [
                ["16/12/2006", "17:24:00", 4.2, 0.4, 234.8, 18.4, 0, 1, 17],
                ["16/12/2006", "17:25:00", None, -0.4, 234.8, 18.4, 0, 1, 17],
            ],
            columns=EXPECTED_COLUMNS,
        )
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.csv"
            source.write_text("sample", encoding="utf-8")

            report = build_quality_report(data, source)

        self.assertIn("**File exists:** Yes", report)
        self.assertIn("**Local records:** 2", report)
        self.assertIn("**Columns:** 9", report)
        self.assertIn("**Duplicate rows:** 0", report)
        self.assertIn("**Invalid timestamps:** 0", report)
        self.assertIn("`Global_active_power`: 1", report)
        self.assertIn("`Global_reactive_power`: 1", report)
        self.assertIn("**Target candidate:** `Global_active_power`", report)
        self.assertIn("without modifying it", report)
        for section in (
            "## 1. Dataset information",
            "## 2. Source",
            "## 3. Dataset size",
            "## 4. Columns",
            "## 5. Data types",
            "## 6. Missing values",
            "## 7. Duplicate analysis",
            "## 8. Timestamp analysis",
            "## 9. Invalid-value analysis",
            "## 10. Outlier observations",
            "## 11. Cleaning decisions",
            "## 12. Before/after statistics",
            "## 13. Final dataset location",
            "## Milestone 1 architecture",
            "## Milestone 1 checklist",
        ):
            with self.subTest(section=section):
                self.assertIn(section, report)
        self.assertIn("- [ ] Code committed to Git", report)
        self.assertIn("1.5 x IQR", report)

    def test_final_report_includes_cleaning_counts_and_output_path(self) -> None:
        data = pd.DataFrame(
            [
                ["16/12/2006", "17:24:00", 4.2, 0.4, 234.8, 18.4, 0, 1, 17],
                ["16/12/2006", "17:25:00", None, 0.4, 234.8, 18.4, 0, 1, 17],
            ],
            columns=EXPECTED_COLUMNS,
        )
        validated = validate_data(data)
        cleaned = clean_data(validated)

        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "raw.csv"
            output = Path(directory) / "cleaned.csv"
            source.write_text("sample", encoding="utf-8")
            output.write_text("sample", encoding="utf-8")
            report = build_quality_report(
                data,
                source,
                validated_data=validated,
                cleaned_data=cleaned,
                cleaned_path=output,
            )

        self.assertIn("- Validated rows: 2", report)
        self.assertIn("- Cleaned rows: 1", report)
        self.assertIn("**Rows removed for missing values:** 1", report)
        self.assertIn("`" + str(output) + "`", report)
        self.assertIn("Before mean", report)
        self.assertIn("After mean", report)


if __name__ == "__main__":
    unittest.main()
