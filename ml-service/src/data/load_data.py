"""Read the raw household power dataset."""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "original_dataset.csv"


def load_raw_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the source's semicolon-delimited data and parse '?' as missing."""
    if not path.is_file():
        raise FileNotFoundError(f"Raw dataset not found: {path}")

    return pd.read_csv(path, sep=";", na_values=["?"])


def main() -> None:
    data = load_raw_data()
    print(f"Loaded {len(data)} rows and {len(data.columns)} columns from {RAW_DATA_PATH}")
    print("\nMissing values by column:")
    print(data.isna().sum().to_string())


if __name__ == "__main__":
    main()
