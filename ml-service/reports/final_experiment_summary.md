# Final Research Summary: Next-Hour Household Electricity Consumption Prediction

**Project:** AI-Based Energy Consumption Prediction System  
**Service Root:** `D:\energy-consumption-ai\ml-service\`  
**Target Variable:** Mean active power at hour $t+1$ (`Global_active_power`, kW)  
**Evaluation Standard:** Chronological 70% Train / 15% Validation / 15% Held-Out Test (Untouched)  

---

## 1. Executive Summary

This report concludes the machine learning benchmark and optimization investigation for short-term household electricity demand forecasting. Using the full 4-year **UCI Individual Household Electric Power Consumption dataset** (2,075,259 raw minute-level observations resampled to 34,589 hourly steps), four models were evaluated under strict temporal causality:
1. **Persistence Baseline** (predicts power at hour $t$ for hour $t+1$)
2. **Linear Regression** (Ordinary Least Squares)
3. **Original Random Forest** ($250$ trees, $\text{max\_depth}=20$, $\text{min\_samples\_leaf}=2$, $\text{max\_features}=1.0$)
4. **Tuned Random Forest** ($250$ trees, $\text{max\_depth}=10$, $\text{min\_samples\_leaf}=2$, $\text{max\_features}=1.0$)

The **Tuned Random Forest Regressor** achieved superior performance across both validation and test sets, reducing test MAE to **0.3239 kW** (a **13.12% error reduction** compared to the Persistence benchmark and **9.98% error reduction** compared to Linear Regression), while reducing artifact storage by **88%** (23.8 MB vs. 201.7 MB) due to tree-depth regularization.

---

## 2. Dataset Specification & Ingestion Pipeline

* **Repository:** UCI Machine Learning Repository (Dataset ID: `235`).
* **Raw File:** [`data/raw/household_power_consumption.txt`](file:///D:/energy-consumption-ai/ml-service/data/raw/household_power_consumption.txt) (132.9 MB, 2,075,259 records).
* **Observation Span:** December 16, 2006 (17:24:00) through November 26, 2010 (21:02:00).
* **Aggregation Method:** Raw minute readings aggregated into hourly arithmetic means via pandas `resample('1h').mean()`, yielding 34,589 sequential hourly observations.
* **Missing Value Imputation:** 421 missing hours (~1.2% of the four-year series) were filled via linear interpolation along the time dimension (`interpolate(method='linear')`), ensuring an unbroken sequence for autoregressive lag computation.
* **Processed Cache:** [`data/processed/hourly_consumption.csv`](file:///D:/energy-consumption-ai/ml-service/data/processed/hourly_consumption.csv).

---

## 3. Feature Engineering & Temporal Causality Audit

To guarantee zero future-information leakage, all 8 features for predicting active power at hour $t+1$ are constructed strictly from measurements available at or before observation hour $t$:

| Feature Name | Data Type | Mathematical Definition | Temporal Boundary |
| :--- | :--- | :--- | :--- |
| `lag_1` | Float (kW) | $y_t$ (Current observed hourly mean power) | $t$ (1 hr before target) |
| `lag_2` | Float (kW) | $y_{t-1}$ (Power 1 hour prior to current) | $t-1$ |
| `lag_3` | Float (kW) | $y_{t-2}$ (Power 2 hours prior to current) | $t-2$ |
| `lag_24` | Float (kW) | $y_{t-23}$ (Power 24 hours prior to target $t+1$) | $t-23$ |
| `rolling_mean_3h` | Float (kW) | $\frac{1}{3}\sum_{k=0}^{2} y_{t-k}$ | Past 3 hours $[t-2, t-1, t]$ |
| `rolling_mean_24h` | Float (kW) | $\frac{1}{24}\sum_{k=0}^{23} y_{t-k}$ | Past 24 hours $[t-23, \dots, t]$ |
| `hour` | Integer | $\text{hour}(T_t) \in [0, 23]$ | Deterministic calendar time |
| `day_of_week` | Integer | $\text{dayofweek}(T_t) \in [0, 6]$ ($0=\text{Mon}$) | Deterministic calendar time |
| **`target`** | Float (kW) | $y_{t+1}$ (Mean power at hour $t+1$) | Shifted $-1$ step (Prediction label) |

* **Row Adjustments:** The first 23 rows (unfilled 24-hour lag) and the final row (missing next-hour target) are excluded, leaving **34,565 complete, leak-free feature samples**.
* **Audit Assertion:** Verified programmatically via automated tests; timestamps and index order strictly respect $T_{\text{features}} \le T_t < T_{\text{target}}$.

---

## 4. Chronological Dataset Partitioning

Data is partitioned in chronological order without shuffling to preserve natural diurnal and seasonal autocorrelation:

```text
Sequence Timeline (34,565 samples):
[------------------- 70% Train -------------------][--- 15% Val ---][--- 15% Test ---]
2006-12-17 16:00                           2009-09-20 18:00    2010-04-24 19:00   2010-11-26 20:00
```

* **Training Split (70%):** 24,195 samples  
  *Start:* `2006-12-17 16:00:00` — *End:* `2009-09-20 18:00:00`
* **Validation Split (15%):** 5,185 samples  
  *Start:* `2009-09-20 19:00:00` — *End:* `2010-04-24 19:00:00`  
  *(Used exclusively for model benchmarking, tuning search, and selection).*
* **Held-Out Test Split (15%):** 5,185 samples  
  *Start:* `2010-04-24 20:00:00` — *End:* `2010-11-26 20:00:00`  
  *(Held completely untouched until final out-of-sample evaluation).*

---

## 5. Model Configurations & Tuning Methodology

### A. Persistence Baseline
Non-parametric reference predicting $\hat{y}_{t+1} = y_t$ (`lag_1`).

### B. Linear Regression
Ordinary Least Squares estimator fitting $\hat{y} = \mathbf{w}^T \mathbf{x} + b$ over the 8 feature dimensions.

### C. Random Forest Regressors
* **Original Configuration:** `n_estimators=250, max_depth=20, min_samples_leaf=2, max_features=1.0, random_state=42, n_jobs=-1`
* **Tuning Grid:** Evaluated 20 systematic configurations across $n \in \{150, 250, 400\}$, $\text{depth} \in \{10, 20, 30, \text{None}\}$, $\text{leaf} \in \{1, 2, 4\}$, and $\text{features} \in \{0.7, 1.0\}$.
* **Best Selected Configuration:** `n_estimators=250, max_depth=10, min_samples_leaf=2, max_features=1.0, random_state=42, n_jobs=-1`
* **Selection Criterion:** Minimum Validation MAE.

---

## 6. Consolidated Benchmark Results

### A. Comprehensive Metrics Summary Table

All models evaluated on the exact same 5,185 validation hours and 5,185 test hours:

| Model | Val MAE (kW) | Val RMSE (kW) | Val R² | Val MAPE (%) | Test MAE (kW) | Test RMSE (kW) | Test R² | Test MAPE (%) | MAE Reduction vs. Baseline | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | 0.4555 | 0.6844 | 0.4147 | 44.13% | 0.3728 | 0.5752 | 0.3291 | 44.75% | Reference | Baseline |
| **Linear Regression** | 0.4405 | 0.6096 | 0.5355 | 50.81% | 0.3598 | 0.5058 | 0.4811 | 50.08% | +3.49% | Comparator |
| **Original Random Forest** | 0.3747 | 0.5443 | 0.6297 | 39.59% | 0.3283 | 0.4734 | 0.5454 | 44.78% | +11.94% | Pre-tuning |
| **Tuned Random Forest** | **0.3703** | **0.5411** | **0.6340** | **38.88%** | **0.3239** | **0.4682** | **0.5555** | **44.19%** | **+13.12%** | **★ Final Selected** |

*Persisted CSV:* [`reports/metrics/consolidated_benchmark_metrics.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/consolidated_benchmark_metrics.csv)

### B. Progression Analysis
1. **Persistence to Linear Regression:** Linear regression captures cyclical diurnal hour and weekly effects, reducing test MAE from 0.3728 to 0.3598 kW.
2. **Linear Regression to Random Forest:** Random Forest non-linear partitioning captures sharp household appliance activations, dropping test MAE to 0.3283 kW (an 8.8% gain over linear regression).
3. **Hyperparameter Regularization (Tuning):** Pruning maximum tree depth from 20 to 10 limits over-specialization on noisy training extremes, achieving the overall best test MAE of **0.3239 kW** and test R² of **0.5555**.

---

## 7. Audit of Visual Evidence (`reports/figures/`)

All generated figures use the non-interactive `matplotlib` `Agg` backend with consistent seaborn styling, readable fonts, 200 DPI resolution, and explicit units (`kW`):

| Figure File | Visualization Scope | Key Elements & Clarity Audit |
| :--- | :--- | :--- |
| [`model_mae_comparison.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/model_mae_comparison.png) | Benchmark Comparison | Bar plot comparing test MAE across Persistence, Linear Regression, and Random Forest with exact annotated values on bars. |
| [`model_comparison_actual_vs_predicted.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/model_comparison_actual_vs_predicted.png) | Multi-Model Tracking | Two-panel time-series: 168-hour (1 week) dynamic tracking overlay + 48-hour peak/trough zoomed detail comparing all models against actual consumption. |
| [`model_tuning_comparison.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/model_tuning_comparison.png) | Hyperparameter Optimization | Side-by-side grouped bar chart comparing Validation MAE and RMSE between Original and Tuned Random Forest with labeled improvement delta. |
| [`actual_vs_predicted.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/actual_vs_predicted.png) | Random Forest Generalization | Top panel: One-week prediction horizon vs actuals. Bottom panel: Full test scatter (5,185 samples) against ideal $y=x$ dashed line with $R^2$ annotation. |
| [`residuals_plot.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/residuals_plot.png) | Error Behavior | Top panel: Residuals vs. predicted active power with zero line and $\pm 1.96\sigma$ bounds. Bottom panel: Residual trajectory over test time steps. |
| [`feature_importance.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/feature_importance.png) | Feature Interpretability | Horizontal bar chart of Mean Decrease in Impurity (Gini importance) ranking all 8 features. (`lag_1`: 0.488, `rolling_mean_3h`: 0.135, `lag_24`: 0.133). |
| [`error_summary.png`](file:///D:/energy-consumption-ai/ml-service/reports/figures/error_summary.png) | Residual Distribution | Probability density function and histogram of test residuals with mean error bias, standard deviation, MAE, and RMSE annotations. |

---

## 8. Complete Artifact Inventory

| Category | Artifact Path | Size / Rows | Purpose |
| :--- | :--- | :--- | :--- |
| **Model** | [`models/random_forest_tuned.joblib`](file:///D:/energy-consumption-ai/ml-service/models/random_forest_tuned.joblib) | 23.8 MB | Winning tuned model binary for inference |
| **Model** | [`models/random_forest.joblib`](file:///D:/energy-consumption-ai/ml-service/models/random_forest.joblib) | 201.7 MB | Preserved original baseline Random Forest |
| **Metadata** | [`models/random_forest_tuned_metadata.json`](file:///D:/energy-consumption-ai/ml-service/models/random_forest_tuned_metadata.json) | 1.6 KB | Schema, parameters, split sizes, and metrics |
| **Metrics** | [`reports/metrics/consolidated_benchmark_metrics.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/consolidated_benchmark_metrics.csv) | 4 models | Complete cross-model comparison table |
| **Metrics** | [`reports/metrics/random_forest_tuning.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/random_forest_tuning.csv) | 20 configs | All 20 hyperparameter trials with fit durations |
| **Metrics** | [`reports/metrics/model_comparison.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/model_comparison.csv) | 3 models | Pre-tuning benchmark comparison records |
| **Predictions** | [`reports/metrics/test_predictions_tuned.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/test_predictions_tuned.csv) | 5,185 rows | Timestamps, actuals, tuned predictions, residuals |
| **Predictions** | [`reports/metrics/model_comparison_predictions.csv`](file:///D:/energy-consumption-ai/ml-service/reports/metrics/model_comparison_predictions.csv) | 5,185 rows | Side-by-side predictions for all 3 benchmark models |

---

## 9. Reproducibility & Test Suite Verification

### A. Test Execution
```powershell
Set-Location D:\energy-consumption-ai\ml-service
python -m unittest discover -s tests -v
```
**Actual Result:** **42 unit tests passed** (0 failures, 0 errors, duration 1.4s).

### B. Pipeline Execution Commands
* **Run Benchmark Comparison:**  
  `python scripts/train_model.py`
* **Run Hyperparameter Tuning:**  
  `python scripts/tune_model.py`
* **Run Standalone Inference:**  
  `python -m src.ml.predict --lag-1 1.25 --lag-2 1.10 --lag-3 1.05 --lag-24 1.30 --rolling-3h 1.13 --rolling-24h 1.22 --hour 18 --day-of-week 2`

---

## 10. Research Limitations & Future Extensions

1. **Near-Zero Active Power & MAPE Distortion:** In residential monitoring, standby consumption drops below 0.15 kW. As $y_i \to 0$, standard percentage error diverges. An explicit floor of $\epsilon = 10^{-4}$ kW ($0.1$ W) was used. MAE and RMSE remain the authoritative physical metrics for utility planning.
2. **Single-Household Telemetry:** The dataset originates from a single residential home in Sceaux, France. While temporal patterns (daily/weekly cycles) are representative, multi-building cross-validation is needed before deploying to diverse building typologies.
3. **Absence of Exogenous Weather Regressors:** Heating/cooling loads are heavily influenced by ambient outdoor temperature and solar irradiance, which are not present in the UCI dataset. Incorporating weather telemetry would represent a valuable future enhancement.
