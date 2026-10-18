# Data quality report

## 1. Dataset information

- **Dataset:** Individual Household Electric Power Consumption
- **Local file:** `data/raw/original_dataset.csv`
- **File exists:** Yes
- **File format:** CSV-style text; semicolon-delimited; `?` parsed as missing
- **File size:** 750 bytes
- **Source:** UCI Machine Learning Repository - [https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption)
- **License checked:** The UCI dataset API does not provide a license field; license terms are unconfirmed.
- **Download date:** Not recorded with the local file.
- **Local records:** 10 (the local file is a sample, not the full UCI dataset)
- **Official dataset records:** 2,075,259
- **Columns:** 9
- **Target candidate:** `Global_active_power` (candidate for a future prediction task; UCI does not declare a target)

## 2. Source

- UCI Machine Learning Repository: [https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption)
- License: UCI's dataset API has no license field; terms are unconfirmed. Verify before redistribution.

## 3. Dataset size

- Local raw file: 10 rows x 9 columns; 750 bytes
- Validated rows: 10
- Cleaned rows: 9

## 4. Columns

| Column | Observed dtype | Dtype check |
| --- | --- | --- |
| `Date` | str | expected |
| `Time` | str | expected |
| `Global_active_power` | float64 | expected |
| `Global_reactive_power` | float64 | expected |
| `Voltage` | float64 | expected |
| `Global_intensity` | float64 | expected |
| `Sub_metering_1` | float64 | expected |
| `Sub_metering_2` | float64 | expected |
| `Sub_metering_3` | float64 | expected |

### Data dictionary

| Column | Type | Meaning | Unit | Role |
| --- | --- | --- | --- | --- |
| `Date` | string | Calendar date of the observation | dd/mm/yyyy | Time component |
| `Time` | string | Time of the observation | hh:mm:ss | Time component |
| `Global_active_power` | numeric | Household global minute-averaged active power | kW | Candidate target |
| `Global_reactive_power` | numeric | Household global minute-averaged reactive power | kW | Feature |
| `Voltage` | numeric | Minute-averaged voltage | V | Feature |
| `Global_intensity` | numeric | Household global current intensity | A | Feature |
| `Sub_metering_1` | numeric | Kitchen active energy sub-meter | Wh | Feature |
| `Sub_metering_2` | numeric | Laundry-room active energy sub-meter | Wh | Feature |
| `Sub_metering_3` | numeric | Water-heater and air-conditioner active energy sub-meter | Wh | Feature |

## 5. Data types

Observed dtypes are listed in the columns table. Numeric measurements are loaded as numeric values; `Date` and `Time` are source strings parsed for checks.

## 6. Missing values

- **Total:** 7 missing cells in 1 rows.
- **By column:** `Date`: 0, `Time`: 0, `Global_active_power`: 1, `Global_reactive_power`: 1, `Voltage`: 1, `Global_intensity`: 1, `Sub_metering_1`: 1, `Sub_metering_2`: 1, `Sub_metering_3`: 1

## 7. Duplicate analysis

- **Duplicate rows:** 0
- **Duplicate timestamps:** 0

## 8. Timestamp analysis

- **Invalid timestamps:** 0
- **Intervals not equal to one minute in input order:** 0
- **Expected frequency:** One-minute observations, according to the UCI source.

## 9. Invalid-value analysis

- **Non-numeric or infinite values by numeric column:** `Global_active_power`: 0, `Global_reactive_power`: 0, `Voltage`: 0, `Global_intensity`: 0, `Sub_metering_1`: 0, `Sub_metering_2`: 0, `Sub_metering_3`: 0
- **Impossible-value check (negative measurements; zero voltage):** `Global_active_power`: 0, `Global_reactive_power`: 0, `Voltage`: 0, `Global_intensity`: 0, `Sub_metering_1`: 0, `Sub_metering_2`: 0, `Sub_metering_3`: 0
- **Missing expected columns:** None
- **Unexpected columns:** None
- **Unit consistency:** Units follow the UCI variable descriptions; they cannot be independently verified from the raw file because it has no unit metadata.

## 10. Outlier observations

Potential outliers are flagged with the exploratory 1.5 x IQR rule. This small sample is too limited to treat these flags as errors; no outliers are removed.

| Column | Lower fence | Upper fence | Count | Potential observations |
| --- | --- | --- | --- | --- |
| `Global_reactive_power` | 0.4650 | 0.5530 | 2 | row 1: 0.418 at 2006-12-16 17:24:00; row 2: 0.436 at 2006-12-16 17:25:00 |
| `Sub_metering_2` | 1.0000 | 1.0000 | 2 | row 3: 2.0 at 2006-12-16 17:26:00; row 7: 2.0 at 2006-12-16 17:30:00 |
| `Sub_metering_3` | 17.0000 | 17.0000 | 1 | row 2: 16.0 at 2006-12-16 17:25:00 |

## 11. Cleaning decisions

- Preserve the raw source file unchanged.
- Inspection reads the raw file without modifying it; validation and cleaning write separate output files.
- Keep incomplete rows in the validated intermediate file for review.
- Remove rows containing missing values when producing the cleaned file.
- Normalize processed column names to lowercase snake_case.
- No duplicate rows were found; no duplicate-removal step was applied.
- Outlier flags are observations only; no outlier-removal rule was applied.
- **Rows removed for missing values:** 1

## 12. Before/after statistics

Numeric statistics for raw valid values compared with the cleaned dataset. Values are rounded to four decimal places.

| Column | Before mean | After mean | Before min | After min | Before max | After max |
| --- | --- | --- | --- | --- | --- | --- |
| `Global_active_power` | 4.2882 | 4.2882 | 3.5200 | 3.5200 | 5.3880 | 5.3880 |
| `Global_reactive_power` | 0.4949 | 0.4949 | 0.4180 | 0.4180 | 0.5280 | 0.5280 |
| `Voltage` | 234.5000 | 234.5000 | 233.2900 | 233.2900 | 235.6800 | 235.6800 |
| `Global_intensity` | 18.4000 | 18.4000 | 15.0000 | 15.0000 | 23.0000 | 23.0000 |
| `Sub_metering_1` | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `Sub_metering_2` | 1.2222 | 1.2222 | 1.0000 | 1.0000 | 2.0000 | 2.0000 |
| `Sub_metering_3` | 16.8889 | 16.8889 | 16.0000 | 16.0000 | 17.0000 | 17.0000 |

- Rows: 10 before; 9 after.

## 13. Final dataset location

- **Cleaned dataset:** `D:\energy-consumption-ai\ml-service\data\processed\cleaned_dataset.csv`

## Milestone 1 architecture

```text
DATASET
   |
   v
RAW STORAGE
   |
   v
LOAD -> pandas DataFrame
   |
   v
VALIDATION: schema | missing values | timestamps
   |
   v
CLEAN: data types | duplicates | invalid values | column names
   |
   v
QUALITY CHECK -> CLEAN DATASET -> DATA QUALITY REPORT
```

## Milestone 1 checklist

- [x] Dataset selected — UCI Individual Household Electric Power Consumption
- [x] Dataset source documented — https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
- [x] Dataset license/source recorded — Source recorded; UCI API has no license field, terms unconfirmed
- [x] Raw dataset stored separately — data/raw/original_dataset.csv
- [x] Dataset loaded successfully — 10 local rows loaded
- [x] Row/column count verified — 10 rows, 9 columns
- [x] Column meanings documented — See the data dictionary above
- [x] Data types inspected — See observed dtype table above
- [x] Missing values measured — 7 cells in 1 rows
- [x] Duplicate rows checked — 0 duplicate rows
- [x] Duplicate timestamps checked — 0 duplicates
- [x] Timestamp validity checked — 0 invalid
- [x] Measurement frequency understood — Expected one-minute intervals
- [x] Invalid values investigated — Numeric and impossible-value checks reported above
- [x] Outliers investigated — Exploratory 1.5-IQR check; see observations above
- [x] Cleaning rules documented — See cleaning decisions below
- [x] Cleaning script created — src/data/clean_data.py
- [x] Clean dataset generated — D:\energy-consumption-ai\ml-service\data\processed\cleaned_dataset.csv
- [x] Raw dataset preserved — Inspection, validation, and cleaning read the raw file only
- [x] Before/after report created — See before/after statistics below
- [x] Data-quality report created — reports/data_quality_report.md
- [X] Code committed to Git — Not verified by the data pipeline

The Git commit checkbox is intentionally unchecked: this report cannot verify that the current changes have been committed.