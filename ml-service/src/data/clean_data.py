"""Remove incomplete records from the validated dataset."""

import re

import pandas as pd

from src.data.inspect_data import build_quality_report
from src.data.load_data import PROJECT_ROOT, RAW_DATA_PATH, load_raw_data

INTERIM_DATA_PATH = PROJECT_ROOT / "data" / "interim" / "validated_dataset.csv"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_dataset.csv"
QUALITY_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.md"


def normalize_column_name(name: object) -> str:
    """Convert a column label to lowercase ASCII snake_case."""
    normalized = re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    if not normalized:
        raise ValueError(f"Column name {name!r} has no alphanumeric characters.")
    return normalized


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names and return complete records."""
    if data.empty:
        raise ValueError("Validated dataset is empty.")

    cleaned = data.copy()
    normalized_columns = [normalize_column_name(column) for column in cleaned.columns]
    if len(normalized_columns) != len(set(normalized_columns)):
        raise ValueError("Column names are not unique after normalization.")
    cleaned.columns = normalized_columns
    return cleaned.dropna().reset_index(drop=True)


def main() -> None:
    if not INTERIM_DATA_PATH.is_file():
        raise FileNotFoundError(
            f"Validated dataset not found: {INTERIM_DATA_PATH}. "
            "Run `python -m src.data.validate_data` first."
        )

    validated_data = pd.read_csv(INTERIM_DATA_PATH)
    cleaned_data = clean_data(validated_data)
    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_data.to_csv(PROCESSED_DATA_PATH, index=False)
    report = build_quality_report(
        load_raw_data(),
        RAW_DATA_PATH,
        validated_data=validated_data,
        cleaned_data=cleaned_data,
        cleaned_path=PROCESSED_DATA_PATH,
    )
    QUALITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_REPORT_PATH.write_text(report, encoding="utf-8")
    print(
        f"Saved {len(cleaned_data)} complete rows to {PROCESSED_DATA_PATH} "
        f"({len(validated_data) - len(cleaned_data)} rows removed)."
    )
    print(f"Standardized columns: {', '.join(cleaned_data.columns)}")
    print(f"Data quality report: {QUALITY_REPORT_PATH}")


if __name__ == "__main__":
    main()
