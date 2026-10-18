# ML Service: Run the Data Pipeline

This guide takes you from the raw dataset to the cleaned dataset. Run the
commands from a terminal, in the order shown.

## 1. Open this folder

In the terminal, change to the `ml-service` folder:

```bash
cd ml-service
```

All commands below assume your terminal is in this folder.

## 2. Install the required packages

```bash
python -m pip install -r requirements.txt
```

This installs the packages needed for the pipeline and notebooks.

## 3. Inspect the raw dataset first

```bash
python -m src.data.inspect_data
```

This checks the raw file and writes the findings to
`reports/data_quality_report.md`. It does not change the raw data.

For the sample currently included, the report shows:

- 10 rows and 9 columns
- 750 bytes
- 7 missing cells in 1 row
- No duplicate rows
- No invalid timestamps
- One-minute intervals in the sample

The included file is a 10-row sample of the full UCI dataset.

## 4. Load the data

```bash
python -m src.data.load_data
```

This reads `data/raw/original_dataset.csv` into a pandas DataFrame. The source
file is semicolon-delimited and uses `?` for missing measurements. The loader
converts `?` to pandas missing values and prints a summary.

Example output:

```text
Loaded 10 rows and 9 columns from ...\data\raw\original_dataset.csv

Missing values by column:
Date                     0
Time                     0
Global_active_power      1
Global_reactive_power    1
Voltage                  1
Global_intensity         1
Sub_metering_1           1
Sub_metering_2           1
Sub_metering_3           1
```

This step only displays the loaded data summary; it does not create another
file.

## 5. Validate and save the intermediate data

```bash
python -m src.data.validate_data
```

Validation checks the column names, date and time formats, and numeric
measurements. It keeps rows with missing measurements so they can be reviewed
before cleaning.

Files written:

- `data/interim/validated_dataset.csv` — validated data, including rows with
  missing values
- `reports/data_quality_report.md` — refreshed inspection report with
  validation status

Example output:

```text
Validated 10 rows: ...\data\interim\validated_dataset.csv
Data quality report: ...\reports\data_quality_report.md
```

## 6. Clean and save the processed data

```bash
python -m src.data.clean_data
```

Cleaning removes rows that contain one or more missing values.
It also standardizes the column names: trims whitespace, converts to lowercase,
replaces punctuation or spaces with underscores, and removes repeated or
edge underscores. For example, `Global_active_power` becomes
`global_active_power`. If two names would become identical, cleaning stops
with an error rather than writing ambiguous output.

File written:

- `data/processed/cleaned_dataset.csv` — data ready for the next analysis step
- `reports/data_quality_report.md` — complete report including inspection
  findings, outlier observations, cleaning decisions, before/after statistics,
  final output location, architecture, and milestone checklist

Example output:

```text
Saved 9 complete rows to ...\data\processed\cleaned_dataset.csv (1 rows removed).
```

For the current sample, cleaning removes 1 incomplete row and keeps 9 rows.
The processed file uses lowercase snake_case headers. The raw and validated
files remain unchanged by this step. This step refreshes the report with the
final cleaning results and before/after statistics.

## 7. Run the tests

```bash
python -m unittest discover -s tests -v
```

The tests check loading, validation, cleaning, and the inspection report. A
successful run ends with `OK`.

## Output files

After running the pipeline, the data files are:

```text
data/
├── raw/
│   ├── original_dataset.csv
│   └── README.md
├── interim/
│   └── validated_dataset.csv
└── processed/
    └── cleaned_dataset.csv
```

The raw sample has 10 rows, the validated file keeps all 10 rows, and the
cleaned file has 9 complete rows. If you replace the sample with the full UCI
dataset, row counts and output sizes will be different.

## Notebooks

The notebooks in `notebooks/` provide a guided introduction to understanding,
loading, and cleaning the data. Start Jupyter from the `ml-service` folder so
the notebook imports can find `src`.
