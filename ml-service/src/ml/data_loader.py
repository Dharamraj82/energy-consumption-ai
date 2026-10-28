"""Data loading module for household electricity consumption datasets."""

import os
from pathlib import Path
from typing import Optional
import urllib.request
import zipfile

import numpy as np
import pandas as pd

from .preprocessing import clean_and_aggregate_hourly

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DATA_TXT_PATH = PROJECT_ROOT / "data" / "raw" / "household_power_consumption.txt"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_dataset.csv"
PROCESSED_HOURLY_PATH = PROJECT_ROOT / "data" / "processed" / "hourly_consumption.csv"

REQUIRED_COLUMNS = {
    "date", "time", "global_active_power", "global_reactive_power", "voltage",
    "global_intensity", "sub_metering_1", "sub_metering_2", "sub_metering_3",
}

UCI_DATASET_URL = (
    "https://archive.ics.uci.edu/static/public/235/"
    "individual+household+electric+power+consumption.zip"
)


def load_processed_data(path: Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Read processed CSV, validate its schema, and add a parsed timestamp."""
    if not path.is_file():
        raise FileNotFoundError(f"Processed dataset not found: {path}")
    try:
        data = pd.read_csv(path)
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        raise ValueError(f"Processed dataset is empty or malformed: {path}") from error
    if data.empty:
        raise ValueError(f"Processed dataset has no rows: {path}")
    missing = REQUIRED_COLUMNS - set(data.columns)
    if missing:
        raise ValueError(f"Processed dataset is missing columns: {sorted(missing)}")
    data["timestamp"] = pd.to_datetime(
        data["date"] + " " + data["time"], format="%d/%m/%Y %H:%M:%S", errors="coerce"
    )
    if data["timestamp"].isna().any():
        raise ValueError("Processed dataset contains invalid timestamps.")
    numeric = sorted(REQUIRED_COLUMNS - {"date", "time"})
    data[numeric] = data[numeric].apply(pd.to_numeric, errors="coerce")
    measurements = data[numeric].to_numpy(dtype=float)
    if pd.isna(measurements).any():
        raise ValueError(
            "Processed dataset contains missing or non-numeric measurements."
        )
    if not np.isfinite(measurements).all():
        raise ValueError("Processed dataset contains infinite measurements.")
    return data.sort_values("timestamp").reset_index(drop=True)


def download_uci_dataset(target_txt_path: Path = RAW_DATA_TXT_PATH) -> Path:
    """Download and extract the UCI Individual Household Electric Power Consumption dataset."""
    target_txt_path.parent.mkdir(parents=True, exist_ok=True)
    temp_zip = target_txt_path.parent / "uci_power_temp.zip"

    print(f"Downloading raw dataset from UCI: {UCI_DATASET_URL}...")
    try:
        urllib.request.urlretrieve(UCI_DATASET_URL, temp_zip)
        with zipfile.ZipFile(temp_zip, "r") as zip_ref:
            zip_ref.extractall(target_txt_path.parent)
        if temp_zip.exists():
            temp_zip.unlink()
    except Exception as exc:
        # Fallback to ucimlrepo if direct download fails
        print(f"Direct download encountered an issue ({exc}). Trying ucimlrepo fallback...")
        try:
            from ucimlrepo import fetch_ucirepo
            dataset = fetch_ucirepo(id=235)
            features = dataset.data.features
            features.to_csv(target_txt_path, sep=";", index=False)
        except Exception as repo_exc:
            raise RuntimeError(
                f"Failed to acquire UCI dataset via direct download or ucimlrepo: {repo_exc}"
            ) from repo_exc

    if not target_txt_path.is_file():
        raise FileNotFoundError(f"Extracted dataset not found at expected path: {target_txt_path}")
    return target_txt_path


def load_raw_uci_data(
    path: Optional[Path] = None,
    nrows: Optional[int] = None,
) -> pd.DataFrame:
    """Load the full raw UCI household electric power consumption dataset.

    Parameters
    ----------
    path : Optional[Path]
        Custom path to raw text/csv file. Defaults to `household_power_consumption.txt`.
    nrows : Optional[int]
        Number of rows to load (useful for fast unit tests or debugging).

    Returns
    -------
    pd.DataFrame
        DataFrame with raw observations, parsing '?' as NaN.
    """
    raw_path = Path(path) if path is not None else RAW_DATA_TXT_PATH

    if not raw_path.is_file():
        print(f"Raw file not found at {raw_path}. Attempting automatic download...")
        download_uci_dataset(raw_path)

    try:
        # Semicolon delimited, '?' represents missing measurements
        data = pd.read_csv(
            raw_path,
            sep=";",
            na_values=["?", "NAN", "nan", "null"],
            nrows=nrows,
            low_memory=False,
            usecols=["Date", "Time", "Global_active_power"],
        )
    except Exception as err:
        raise ValueError(f"Failed to read raw dataset from {raw_path}: {err}") from err

    if data.empty:
        raise ValueError(f"Raw dataset at {raw_path} contains no data.")

    return data


def load_hourly_data(
    processed_path: Optional[Path] = None,
    raw_path: Optional[Path] = None,
    force_recompute: bool = False,
) -> pd.DataFrame:
    """Load hourly aggregated electricity consumption data, computing and caching if needed.

    Returns
    -------
    pd.DataFrame
        Hourly consumption data with columns ['timestamp', 'global_active_power'].
    """
    cache_path = Path(processed_path) if processed_path is not None else PROCESSED_HOURLY_PATH

    if cache_path.is_file() and not force_recompute:
        data = pd.read_csv(cache_path)
        data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
        data["global_active_power"] = pd.to_numeric(data["global_active_power"], errors="coerce")
        return data.sort_values("timestamp").reset_index(drop=True)

    print(f"Computing hourly aggregation from raw data...")
    raw_df = load_raw_uci_data(raw_path)
    hourly_df = clean_and_aggregate_hourly(raw_df)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    hourly_df.to_csv(cache_path, index=False)
    print(f"Saved {len(hourly_df)} hourly observations to {cache_path}")

    return hourly_df
