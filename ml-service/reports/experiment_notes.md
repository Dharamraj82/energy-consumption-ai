# Experiment Notes: Next-Hour Electricity Consumption Model Benchmark

## 1. Prediction Problem and Scope

The objective is to predict the next hour's mean household active power (`Global_active_power` in kilowatts, kW) using historical telemetry from the UCI Individual Household Electric Power Consumption dataset.

* **Target Variable:** `target` = Mean active power at hour $t+1$ (kW).
* **Forecast Horizon:** Next 1 hour.
* **Telemetry Granularity:** Hourly mean aggregated from raw minute-level readings.

---

## 2. Dataset and Preprocessing

* **Data Source:** UCI Machine Learning Repository (Dataset ID: 235).
* **Raw Dataset:** `data/raw/household_power_consumption.txt` (2,075,259 records spanning December 16, 2006 to November 26, 2010).
* **Hourly Aggregation:** Minute readings aggregated into 1-hour means (`resample('1h').mean()`), totaling 34,589 chronological hours.
* **Missing Entry Imputation:** 421 missing hours (~1.2%) were filled via time-based linear interpolation to maintain unbroken sequence continuity for autoregressive lag calculations.
* **Cached Clean Series:** `data/processed/hourly_consumption.csv`.

---

## 3. Feature Engineering and Leakage Prevention

All features are strictly derived from observations recorded at or prior to observation hour $t$:

| Feature | Description | Causality Check |
| :--- | :--- | :--- |
| `lag_1` | Mean active power at current observation hour $t$ (kW) | Uses hour $t$ (1 hr prior to target) |
| `lag_2` | Mean active power at hour $t-1$ (kW) | Uses hour $t-1$ |
| `lag_3` | Mean active power at hour $t-2$ (kW) | Uses hour $t-2$ |
| `lag_24` | Mean active power at hour $t-23$ (kW) (same hour yesterday) | Uses hour $t-23$ |
| `rolling_mean_3h` | 3-hour moving average over $[t-2, t-1, t]$ (kW) | Uses past 3 hours only |
| `rolling_mean_24h`| 24-hour moving average over $[t-23, \dots, t]$ (kW) | Uses past 24 hours only |
| `hour` | Hour of day of current observation (0–23) | Deterministic calendar time |
| `day_of_week` | Day of week (0 = Monday, 6 = Sunday) | Deterministic calendar time |

* **Total Available Samples:** 34,565 rows (first 23 hours dropped due to 24h lag; last hour dropped due to target shift).

---

## 4. Chronological Dataset Partitioning

To avoid temporal data leakage and respect sequential dependency, observations were split chronologically without shuffling:

* **Training Set (70%):** 24,195 samples (Dec 2006 – Sep 2009)
* **Validation Set (15%):** 5,185 samples (Sep 2009 – Apr 2010) — used exclusively for model selection
* **Test Set (15%):** 5,185 samples (Apr 2010 – Nov 2010) — held-out, untouched until final evaluation

---

## 5. Models Benchmarked

1. **Persistence Baseline:**
   * Assumes electricity consumption in the next hour equals the consumption of the current hour: $\hat{y}_{t+1} = y_t$ (`lag_1`).
   * Non-parametric; serves as the primary time-series benchmark.
2. **Linear Regression:**
   * Ordinary Least Squares (OLS) linear regressor trained on all 8 features.
   * Model: $\hat{y} = \mathbf{w}^T \mathbf{x} + b$.
3. **Random Forest Regressor:**
   * Ensemble of 250 decision trees with bootstrap aggregation.
   * Hyperparameters:
     ```python
     RandomForestRegressor(
         n_estimators=250,
         max_depth=20,
         min_samples_leaf=2,
         random_state=42,
         n_jobs=-1,
     )
     ```

---

## 6. Model Selection Protocol

* **Criterion:** Lowest Mean Absolute Error (MAE) on the chronological **Validation Set**.
* **Strict Independence:** The test set was not read, scored, or utilized during hyperparameter setting or model choice.

---

## 7. Experimental Results

Evaluated across the exact same chronological validation and test partitions:

### Validation Set (Model Selection Phase — 5,185 samples)

| Model | MAE (kW) | RMSE (kW) | R² | MAPE (%) | Validation Rank |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Regressor** | **0.3747** | **0.5443** | **0.6297** | **39.59%** | **1 (Selected)** |
| **Linear Regression** | 0.4405 | 0.6096 | 0.5355 | 50.81% | 2 |
| **Persistence Baseline** | 0.4555 | 0.6844 | 0.4147 | 44.13% | 3 |

*Decision:* **Random Forest Regressor** was selected due to achieving the lowest MAE ($0.3747$ kW vs. $0.4405$ kW and $0.4555$ kW) and highest R² ($0.6297$).

---

### Untouched Test Set (Final Out-of-Sample Evaluation — 5,185 samples)

| Model | MAE (kW) | RMSE (kW) | R² | MAPE (%) | Improvement vs. Persistence |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Regressor** | **0.3283** | **0.4734** | **0.5454** | **44.78%** | **+11.9% MAE reduction** |
| **Linear Regression** | 0.3598 | 0.5058 | 0.4811 | 50.08% | +3.5% MAE reduction |
| **Persistence Baseline** | 0.3728 | 0.5752 | 0.3291 | 44.75% | Baseline reference |

---

## 8. MAPE Calculation Methodology & Limitations

Standard Mean Absolute Percentage Error is defined as:
$$\text{MAPE}_{\text{raw}} = \frac{100\%}{N} \sum_{i=1}^N \frac{|y_i - \hat{y}_i|}{y_i}$$

### Failure Mode in Electricity Metering
During deep night or idle standby periods, household active power drops to very low baseline values (e.g. $0.12 - 0.20$ kW). When the true denominator $y_i \approx 0$, small absolute residuals (e.g., $0.15$ kW error) inflate to percentage errors exceeding $100\%$, skewing arithmetic means.

### Implemented Strategy
To prevent zero-division and unrepresentative skew while retaining valid bounded percentages, an epsilon floor is applied:
$$\text{MAPE}_{\epsilon} = \frac{100\%}{N} \sum_{i=1}^N \frac{|y_i - \hat{y}_i|}{\max(|y_i|, \epsilon)}$$
where $\epsilon = 10^{-4}$ kW ($0.1$ W).

---

## 9. Artifact Locations

* **Comparison Summary CSV:** [`reports/metrics/model_comparison.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/model_comparison.csv)
* **Out-of-Sample Predictions CSV:** [`reports/metrics/model_comparison_predictions.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/model_comparison_predictions.csv)
* **Test MAE Bar Chart:** [`reports/figures/model_mae_comparison.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/model_mae_comparison.png)
* **Trajectory Tracking Chart:** [`reports/figures/model_comparison_actual_vs_predicted.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/model_comparison_actual_vs_predicted.png)
* **Winning Model Artifact:** [`models/random_forest.joblib`](file:///D:/energy-consumption-ai/ml-service/models/random_forest.joblib)

---

## 10. Random Forest Hyperparameter Optimization

A systematic search was conducted across the hyperparameter space:
* `n_estimators`: `[150, 250, 400]`
* `max_depth`: `[10, 20, 30, None]`
* `min_samples_leaf`: `[1, 2, 4]`
* `max_features`: `[0.7, 1.0]`

### Model Selection on Validation Data Only
* **Initial Model:** `n_estimators=250, max_depth=20, min_samples_leaf=2, max_features=1.0`
* **Best Tuned Model:** `n_estimators=250, max_depth=10, min_samples_leaf=2, max_features=1.0`
* **Key Finding:** Restricting tree depth from 20 to 10 effectively regularizes individual estimators against noise from rapid household load switches, improving validation MAE from **0.3747 kW to 0.3703 kW** and test MAE from **0.3283 kW to 0.3239 kW**.
* **Model Footprint Reduction:** The tuned model artifact (`models/random_forest_tuned.joblib`) is **23.8 MB** (an 88% reduction in disk size compared to the 201.7 MB original model).

| Split | Metric | Original Random Forest | Tuned Random Forest | Difference |
| :--- | :--- | :---: | :---: | :---: |
| **Validation (15%)** | **MAE (kW)** | 0.3747 | **0.3703** | -0.0045 kW |
| Validation | **RMSE (kW)** | 0.5443 | **0.5411** | -0.0032 kW |
| Validation | **R²** | 0.6297 | **0.6340** | +0.0043 |
| **Test (15%)** | **MAE (kW)** | 0.3283 | **0.3239** | -0.0045 kW |
| Test | **RMSE (kW)** | 0.4734 | **0.4682** | -0.0053 kW |
| Test | **R²** | 0.5454 | **0.5555** | +0.0101 |
| Test | **MAPE (%)** | 44.78% | **44.19%** | -0.59% |

### Optimization Artifacts:
* **Tuning Grid Records:** [`reports/metrics/random_forest_tuning.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/random_forest_tuning.csv)
* **Tuned Model Artifact:** [`models/random_forest_tuned.joblib`](file:///D:/energy-consumption-ai/ml-service/models/random_forest_tuned.joblib)
* **Tuned Metadata:** [`models/random_forest_tuned_metadata.json`](file:///D:/energy-consumption-ai/ml-service/models/random_forest_tuned_metadata.json)
* **Validation Comparison Chart:** [`reports/figures/model_tuning_comparison.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/model_tuning_comparison.png)
* **Tuned Out-of-Sample Predictions:** [`reports/metrics/test_predictions_tuned.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/test_predictions_tuned.csv)

