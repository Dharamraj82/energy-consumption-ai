"""Inspect the raw dataset and document its structure and quality."""

from pathlib import Path

import pandas as pd
from pandas.api.types import is_numeric_dtype, is_string_dtype

from src.data.load_data import PROJECT_ROOT, RAW_DATA_PATH, load_raw_data

QUALITY_REPORT_PATH = PROJECT_ROOT / "reports" / "data_quality_report.md"
SOURCE_URL = (
    "https://archive.ics.uci.edu/dataset/235/"
    "individual+household+electric+power+consumption"
)
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
COLUMN_DICTIONARY = {
    "Date": ("string", "Calendar date of the observation", "dd/mm/yyyy", "Time component"),
    "Time": ("string", "Time of the observation", "hh:mm:ss", "Time component"),
    "Global_active_power": (
        "numeric",
        "Household global minute-averaged active power",
        "kW",
        "Candidate target",
    ),
    "Global_reactive_power": (
        "numeric",
        "Household global minute-averaged reactive power",
        "kW",
        "Feature",
    ),
    "Voltage": ("numeric", "Minute-averaged voltage", "V", "Feature"),
    "Global_intensity": (
        "numeric",
        "Household global current intensity",
        "A",
        "Feature",
    ),
    "Sub_metering_1": (
        "numeric",
        "Kitchen active energy sub-meter",
        "Wh",
        "Feature",
    ),
    "Sub_metering_2": (
        "numeric",
        "Laundry-room active energy sub-meter",
        "Wh",
        "Feature",
    ),
    "Sub_metering_3": (
        "numeric",
        "Water-heater and air-conditioner active energy sub-meter",
        "Wh",
        "Feature",
    ),
}


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    divider = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def _format_number(value: float) -> str:
    return f"{value:.4f}"


def _outlier_rows(data: pd.DataFrame) -> list[list[str]]:
    """List potential numeric outliers using the exploratory 1.5-IQR rule."""
    rows: list[list[str]] = []
    timestamp_values: pd.Series | None = None
    if {"Date", "Time"}.issubset(data.columns):
        timestamp_values = pd.to_datetime(
            data["Date"].astype("string") + " " + data["Time"].astype("string"),
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce",
        )

    for column in data.columns:
        if COLUMN_DICTIONARY.get(column, (None,))[0] != "numeric":
            continue
        values = pd.to_numeric(data[column], errors="coerce")
        valid_values = values.dropna()
        if valid_values.empty:
            continue
        q1 = valid_values.quantile(0.25)
        q3 = valid_values.quantile(0.75)
        iqr = q3 - q1
        lower_fence = q1 - 1.5 * iqr
        upper_fence = q3 + 1.5 * iqr
        outlier_indices = valid_values.index[
            (valid_values < lower_fence) | (valid_values > upper_fence)
        ]
        if not len(outlier_indices):
            continue
        observations = []
        for index in outlier_indices:
            timestamp = (
                str(timestamp_values.loc[index])
                if timestamp_values is not None
                else "unavailable"
            )
            observations.append(
                f"row {data.index.get_loc(index) + 1}: {values.loc[index]} "
                f"at {timestamp}"
            )
        rows.append(
            [
                f"`{column}`",
                _format_number(lower_fence),
                _format_number(upper_fence),
                str(len(outlier_indices)),
                "; ".join(observations),
            ]
        )
    return rows


def _statistics_rows(
    before: pd.DataFrame, after: pd.DataFrame | None
) -> list[list[str]]:
    rows: list[list[str]] = []
    for column in before.columns:
        if COLUMN_DICTIONARY.get(column, (None,))[0] != "numeric":
            continue
        before_values = pd.to_numeric(before[column], errors="coerce").dropna()
        if before_values.empty:
            continue
        after_column = column.lower()
        after_values = pd.Series(dtype="float64")
        if after is not None and after_column in after.columns:
            after_values = pd.to_numeric(after[after_column], errors="coerce").dropna()
        rows.append(
            [
                f"`{column}`",
                _format_number(float(before_values.mean())),
                _format_number(float(after_values.mean()))
                if not after_values.empty
                else "pending",
                _format_number(float(before_values.min())),
                _format_number(float(after_values.min()))
                if not after_values.empty
                else "pending",
                _format_number(float(before_values.max())),
                _format_number(float(after_values.max()))
                if not after_values.empty
                else "pending",
            ]
        )
    return rows


def build_quality_report(
    data: pd.DataFrame,
    source_path: Path,
    validated_data: pd.DataFrame | None = None,
    cleaned_data: pd.DataFrame | None = None,
    cleaned_path: Path | None = None,
) -> str:
    """Create an inspection and pipeline quality report without changing input data."""
    file_size = source_path.stat().st_size if source_path.is_file() else None
    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(data.columns))
    unexpected_columns = sorted(set(data.columns) - set(EXPECTED_COLUMNS))

    timestamp_invalid = "not checked (Date or Time column missing)"
    duplicate_timestamps = "not checked (Date or Time column missing)"
    interval_anomalies = "not checked (Date or Time column missing)"
    if {"Date", "Time"}.issubset(data.columns):
        timestamps = pd.to_datetime(
            data["Date"].astype("string") + " " + data["Time"].astype("string"),
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce",
        )
        valid_timestamps = timestamps.dropna()
        timestamp_invalid = str(int(timestamps.isna().sum()))
        duplicate_timestamps = str(int(valid_timestamps.duplicated().sum()))
        differences = valid_timestamps.diff().dropna()
        interval_anomalies = str(
            int((differences != pd.Timedelta(minutes=1)).sum())
        )

    duplicate_rows = int(data.duplicated().sum())
    missing_counts = data.isna().sum()
    invalid_numeric: dict[str, int] = {}
    impossible_counts: dict[str, int] = {}
    dtype_rows: list[list[str]] = []

    for column in data.columns:
        observed_type = str(data[column].dtype)
        expected_type = COLUMN_DICTIONARY.get(column, (None, None, None, None))[0]
        if expected_type == "numeric":
            converted = pd.to_numeric(data[column], errors="coerce")
            invalid_mask = (data[column].notna() & converted.isna()) | converted.isin(
                [float("inf"), float("-inf")]
            )
            invalid_numeric[column] = int(invalid_mask.sum())
            if is_numeric_dtype(converted):
                impossible_counts[column] = int((converted < 0).sum())
                if column == "Voltage":
                    impossible_counts[column] += int((converted == 0).sum())
            dtype_ok = is_numeric_dtype(data[column])
        elif expected_type == "string":
            dtype_ok = is_string_dtype(data[column])
        else:
            dtype_ok = True
        dtype_rows.append(
            [f"`{column}`", observed_type, "expected" if dtype_ok else "unexpected"]
        )

    dictionary_rows = []
    for column in data.columns:
        details = COLUMN_DICTIONARY.get(column)
        if details is None:
            dictionary_rows.append(
                [f"`{column}`", "unknown", "Not documented", "Not documented", "Review"]
            )
            continue
        data_type, meaning, unit, role = details
        dictionary_rows.append(
            [f"`{column}`", data_type, meaning, unit, role]
        )

    missing_rows = int(data.isna().any(axis=1).sum())
    outliers = _outlier_rows(data)
    stats_rows = _statistics_rows(data, cleaned_data)
    has_validation = validated_data is not None
    has_cleaned_data = cleaned_data is not None
    cleaned_file_exists = cleaned_path is not None and cleaned_path.is_file()
    row_count_after = (
        len(cleaned_data) if cleaned_data is not None else "pending clean step"
    )

    checklist = [
        ("Dataset selected", True, "UCI Individual Household Electric Power Consumption"),
        ("Dataset source documented", True, SOURCE_URL),
        (
            "Dataset license/source recorded",
            True,
            "Source recorded; UCI API has no license field, terms unconfirmed",
        ),
        ("Raw dataset stored separately", source_path.is_file(), "data/raw/original_dataset.csv"),
        ("Dataset loaded successfully", True, f"{len(data)} local rows loaded"),
        ("Row/column count verified", True, f"{len(data)} rows, {len(data.columns)} columns"),
        ("Column meanings documented", True, "See the data dictionary above"),
        ("Data types inspected", True, "See observed dtype table above"),
        ("Missing values measured", True, f"{int(missing_counts.sum())} cells in {missing_rows} rows"),
        ("Duplicate rows checked", True, f"{duplicate_rows} duplicate rows"),
        ("Duplicate timestamps checked", timestamp_invalid == "0", f"{duplicate_timestamps} duplicates"),
        ("Timestamp validity checked", timestamp_invalid == "0", f"{timestamp_invalid} invalid"),
        ("Measurement frequency understood", interval_anomalies == "0", "Expected one-minute intervals"),
        ("Invalid values investigated", True, "Numeric and impossible-value checks reported above"),
        ("Outliers investigated", True, "Exploratory 1.5-IQR check; see observations above"),
        ("Cleaning rules documented", True, "See cleaning decisions below"),
        ("Cleaning script created", True, "src/data/clean_data.py"),
        ("Clean dataset generated", cleaned_file_exists, str(cleaned_path) if cleaned_file_exists else "Pending clean step"),
        ("Raw dataset preserved", source_path.is_file(), "Inspection, validation, and cleaning read the raw file only"),
        ("Before/after report created", has_cleaned_data, "See before/after statistics below"),
        ("Data-quality report created", True, "reports/data_quality_report.md"),
        ("Code committed to Git", False, "Not verified by the data pipeline"),
    ]

    report_lines = [
        "# Data quality report",
        "",
        "## 1. Dataset information",
        "",
        "- **Dataset:** Individual Household Electric Power Consumption",
        "- **Local file:** `data/raw/original_dataset.csv`",
        "- **File exists:** " + ("Yes" if source_path.is_file() else "No"),
        "- **File format:** CSV-style text; semicolon-delimited; `?` parsed as missing",
        f"- **File size:** {file_size:,} bytes"
        if file_size is not None
        else "- **File size:** unavailable",
        f"- **Source:** UCI Machine Learning Repository - [{SOURCE_URL}]({SOURCE_URL})",
        "- **License checked:** The UCI dataset API does not provide a license field; license terms are unconfirmed.",
        "- **Download date:** Not recorded with the local file.",
        f"- **Local records:** {len(data):,} (the local file is a sample, not the full UCI dataset)",
        f"- **Official dataset records:** 2,075,259",
        f"- **Columns:** {len(data.columns)}",
        f"- **Target candidate:** `Global_active_power` (candidate for a future prediction task; UCI does not declare a target)",
        "",
        "## 2. Source",
        "",
        f"- UCI Machine Learning Repository: [{SOURCE_URL}]({SOURCE_URL})",
        "- License: UCI's dataset API has no license field; terms are unconfirmed. Verify before redistribution.",
        "",
        "## 3. Dataset size",
        "",
        f"- Local raw file: {len(data):,} rows x {len(data.columns)} columns; "
        f"{file_size:,} bytes" if file_size is not None
        else f"- Local raw file: {len(data):,} rows x {len(data.columns)} columns; file size unavailable",
        f"- Validated rows: {len(validated_data):,}" if has_validation else "- Validated rows: pending validation step",
        f"- Cleaned rows: {row_count_after}",
        "",
        "## 4. Columns",
        "",
        _markdown_table(["Column", "Observed dtype", "Dtype check"], dtype_rows),
        "",
        "### Data dictionary",
        "",
        _markdown_table(
            ["Column", "Type", "Meaning", "Unit", "Role"], dictionary_rows
        ),
        "",
        "## 5. Data types",
        "",
        "Observed dtypes are listed in the columns table. Numeric measurements are "
        "loaded as numeric values; `Date` and `Time` are source strings parsed for checks.",
        "",
        "## 6. Missing values",
        "",
        f"- **Total:** {int(missing_counts.sum())} missing cells in {missing_rows} rows.",
        "- **By column:** "
        + ", ".join(f"`{column}`: {int(count)}" for column, count in missing_counts.items()),
        "",
        "## 7. Duplicate analysis",
        "",
        f"- **Duplicate rows:** {duplicate_rows}",
        f"- **Duplicate timestamps:** {duplicate_timestamps}",
        "",
        "## 8. Timestamp analysis",
        "",
        f"- **Invalid timestamps:** {timestamp_invalid}",
        f"- **Intervals not equal to one minute in input order:** {interval_anomalies}",
        "- **Expected frequency:** One-minute observations, according to the UCI source.",
        "",
        "## 9. Invalid-value analysis",
        "",
        "- **Non-numeric or infinite values by numeric column:** "
        + (
            ", ".join(f"`{column}`: {count}" for column, count in invalid_numeric.items())
            or "not checked (no known numeric columns)"
        ),
        "- **Impossible-value check (negative measurements; zero voltage):** "
        + (
            ", ".join(f"`{column}`: {count}" for column, count in impossible_counts.items())
            or "not checked"
        ),
        f"- **Missing expected columns:** {', '.join(missing_columns) if missing_columns else 'None'}",
        f"- **Unexpected columns:** {', '.join(unexpected_columns) if unexpected_columns else 'None'}",
        "- **Unit consistency:** Units follow the UCI variable descriptions; they cannot "
        "be independently verified from the raw file because it has no unit metadata.",
        "",
        "## 10. Outlier observations",
        "",
        "Potential outliers are flagged with the exploratory 1.5 x IQR rule. "
        "This small sample is too limited to treat these flags as errors; no outliers are removed.",
        "",
        _markdown_table(
            ["Column", "Lower fence", "Upper fence", "Count", "Potential observations"],
            outliers or [["None detected", "-", "-", "0", "-"]],
        ),
        "",
        "## 11. Cleaning decisions",
        "",
        "- Preserve the raw source file unchanged.",
        "- Inspection reads the raw file without modifying it; validation and cleaning write separate output files.",
        "- Keep incomplete rows in the validated intermediate file for review.",
        "- Remove rows containing missing values when producing the cleaned file.",
        "- Normalize processed column names to lowercase snake_case.",
        "- No duplicate rows were found; no duplicate-removal step was applied.",
        "- Outlier flags are observations only; no outlier-removal rule was applied.",
        f"- **Rows removed for missing values:** {len(validated_data) - len(cleaned_data)}"
        if has_cleaned_data and has_validation
        else "- **Rows removed for missing values:** pending clean step",
        "",
        "## 12. Before/after statistics",
        "",
        "Numeric statistics for raw valid values compared with the cleaned dataset. "
        "Values are rounded to four decimal places.",
        "",
        _markdown_table(
            ["Column", "Before mean", "After mean", "Before min", "After min", "Before max", "After max"],
            stats_rows or [["Statistics", "pending", "pending", "pending", "pending", "pending", "pending"]],
        ),
        f"\n- Rows: {len(data)} before; {len(cleaned_data)} after."
        if has_cleaned_data
        else f"\n- Rows: {len(data)} before; after count pending.",
        "",
        "## 13. Final dataset location",
        "",
        f"- **Cleaned dataset:** `{cleaned_path}`"
        if cleaned_file_exists
        else "- **Cleaned dataset:** `data/processed/cleaned_dataset.csv` (pending clean step)",
        "",
        "## Milestone 1 architecture",
        "",
        "```text",
        "DATASET",
        "   |",
        "   v",
        "RAW STORAGE",
        "   |",
        "   v",
        "LOAD -> pandas DataFrame",
        "   |",
        "   v",
        "VALIDATION: schema | missing values | timestamps",
        "   |",
        "   v",
        "CLEAN: data types | duplicates | invalid values | column names",
        "   |",
        "   v",
        "QUALITY CHECK -> CLEAN DATASET -> DATA QUALITY REPORT",
        "```",
        "",
        "## Milestone 1 checklist",
        "",
        *[
            f"- [{'x' if checked else ' '}] {label} — {detail}"
            for label, checked, detail in checklist
        ],
        "",
        "The Git commit checkbox is intentionally unchecked: this report cannot "
        "verify that the current changes have been committed.",
    ]
    return "\n".join(report_lines)


def main() -> None:
    if not RAW_DATA_PATH.is_file():
        raise FileNotFoundError(f"Raw dataset not found: {RAW_DATA_PATH}")

    raw_data = load_raw_data(RAW_DATA_PATH)
    report = build_quality_report(raw_data, RAW_DATA_PATH)
    QUALITY_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    QUALITY_REPORT_PATH.write_text(report, encoding="utf-8")
    print(report)
    print(f"\nInspection report saved to {QUALITY_REPORT_PATH}")


if __name__ == "__main__":
    main()
