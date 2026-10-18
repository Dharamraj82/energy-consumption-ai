"""Validate the raw dataset and save the validated intermediate data."""

from pathlib import Path

import pandas as pd

from src.data.inspect_data import build_quality_report
from src.data.load_data import PROJECT_ROOT, RAW_DATA_PATH, load_raw_data

INTERIM_DATA_PATH = PROJECT_ROOT / "data" / "interim" / "validated_dataset.csv"
QUALITY_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.md"
EXPECTED_COLUMNS = [
    "Date",
    "Time",
    "Global_active_power",
    "Global_reactive_power",
    "Voltage",
    "Global_intensity",
    "Sub_metering_1",
    "Sub_metering_2",
    "Sub_metering_3",
]
NUMERIC_COLUMNS = EXPECTED_COLUMNS[2:]


def validate_data(data: pd.DataFrame) -> pd.DataFrame:
    """Check the expected schema and field formats without removing missing rows."""
    if data.empty:
        raise ValueError("Dataset is empty.")
    if list(data.columns) != EXPECTED_COLUMNS:
        raise ValueError(
            f"Unexpected dataset columns: expected {EXPECTED_COLUMNS}, "
            f"received {list(data.columns)}"
        )

    validated = data.copy()
    for column, date_format in (("Date", "%d/%m/%Y"), ("Time", "%H:%M:%S")):
        parsed = pd.to_datetime(validated[column], format=date_format, errors="coerce")
        if parsed.isna().any():
            raise ValueError(f"Column '{column}' contains missing or invalid values.")

    for column in NUMERIC_COLUMNS:
        converted = pd.to_numeric(validated[column], errors="coerce")
        invalid = (validated[column].notna() & converted.isna()) | converted.isin(
            [float("inf"), float("-inf")]
        )
        if invalid.any():
            raise ValueError(
                f"Column '{column}' contains non-numeric or infinite values."
            )
        validated[column] = converted

    return validated


def write_quality_report(
    raw_data: pd.DataFrame, validated_data: pd.DataFrame, path: Path
) -> None:
    """Write a concise summary of input and validation results."""
    report = build_quality_report(raw_data, RAW_DATA_PATH)
    report += (
        "\n## Validation\n\n"
        f"- **Status:** Passed\n"
        f"- **Validated rows:** {len(validated_data)}\n"
        f"- **Validated columns:** {len(validated_data.columns)}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def main() -> None:
    raw_data = load_raw_data()
    validated_data = validate_data(raw_data)
    INTERIM_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    validated_data.to_csv(INTERIM_DATA_PATH, index=False)
    write_quality_report(raw_data, validated_data, QUALITY_REPORT_PATH)
    print(f"Validated {len(validated_data)} rows: {INTERIM_DATA_PATH}")
    print(f"Data quality report: {QUALITY_REPORT_PATH}")


if __name__ == "__main__":
    main()
