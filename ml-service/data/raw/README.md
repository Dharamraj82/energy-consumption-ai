# Raw Dataset Metadata

- **Dataset Name:** Individual Household Electric Power Consumption
- **Source:** UCI Machine Learning Repository
- **URL:** https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption
- **Download Date:** Not recorded
- **License:** Checked the UCI dataset API on 2026-10-18; it does not provide a license field. License terms remain unconfirmed; verify before redistribution.
- **Number of Records:** 10 data records in the local sample; the official UCI dataset lists 2,075,259 records.
- **Number of Columns:** 9
- **Target Variable:** `Global_active_power` (candidate target for future prediction experiments)
- **Time Resolution:** One-minute intervals
- **Units:**
  - `Global_active_power`, `Global_reactive_power`: kilowatts (kW)
  - `Voltage`: volts (V)
  - `Global_intensity`: amperes (A)
  - `Sub_metering_1`, `Sub_metering_2`, `Sub_metering_3`: watt-hours of active energy (Wh)
  - `Date`, `Time`: date (`dd/mm/yyyy`) and time (`hh:mm:ss`)
- **Missing Value Representation:** `?` in the raw, semicolon-delimited source file
- **Description:** Minute-averaged household electricity measurements, including active and reactive power, voltage, current intensity, and three household energy sub-meter readings.
- **Reason for Selection:** The dataset was selected because it contains historical energy consumption observations and time/environmental variables that can support future energy-consumption prediction experiments.

## Data dictionary

| Column | Type | Meaning | Unit | Role |
| --- | --- | --- | --- | --- |
| `Date` | Date string | Calendar date of observation | `dd/mm/yyyy` | Time component |
| `Time` | Time string | Time of observation | `hh:mm:ss` | Time component |
| `Global_active_power` | Numeric | Household global minute-averaged active power | kW | Candidate target |
| `Global_reactive_power` | Numeric | Household global minute-averaged reactive power | kW | Feature |
| `Voltage` | Numeric | Minute-averaged voltage | V | Feature |
| `Global_intensity` | Numeric | Household global current intensity | A | Feature |
| `Sub_metering_1` | Numeric | Kitchen active energy sub-meter | Wh | Feature |
| `Sub_metering_2` | Numeric | Laundry-room active energy sub-meter | Wh | Feature |
| `Sub_metering_3` | Numeric | Water-heater and air-conditioner active energy sub-meter | Wh | Feature |

UCI does not declare a target column; `Global_active_power` is only a candidate
for a future prediction experiment. Column meanings and units are based on the
UCI variable descriptions.

The file is named `original_dataset.csv` but preserves the source's
semicolon-delimited format. Keep it unchanged so downstream pipeline stages
can be reproduced.
