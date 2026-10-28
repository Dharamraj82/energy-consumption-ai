<p align="center">
  <img src="./reports/figures/banner.svg" alt="AI-Based Energy Consumption Prediction System" width="100%" />
</p>

# ML Service — AI-Based Energy Consumption Prediction System

A lightweight, reproducible machine learning pipeline that forecasts a household's electricity consumption for the **next 1 hour** (in kilowatts, kW) using 4 years of real smart-meter telemetry.

---

## 📌 At a Glance

* **Goal:** Predict next hour's mean active power (`Global_active_power`, kW)
* **Dataset:** UCI Individual Household Electric Power Consumption — 2,075,259 minute-level rows → 34,589 hourly steps
* **Features:** 8 leak-free features derived strictly from past data (lags, rolling averages, calendar hour/day)
* **Split:** Strict chronological — **70% Train** (24,195) · **15% Validation** (5,185) · **15% Test** (5,185)
* **Winner:** Tuned Random Forest (250 trees, max_depth=10) — **0.3239 kW MAE · 13.12% error reduction · 88% smaller model**

---

## 📊 Experimental Results

| Model | Test MAE (kW) | Test RMSE (kW) | Test R² | Test MAPE (%) | Error Reduction | File Size |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | 0.3728 | 0.5752 | 0.3291 | 44.75% | Baseline | *None* |
| **Linear Regression** | 0.3598 | 0.5058 | 0.4811 | 50.08% | +3.49% | < 0.1 MB |
| **Original Random Forest** | 0.3283 | 0.4734 | 0.5454 | 44.78% | +11.94% | 201.7 MB |
| **Tuned Random Forest** | **0.3239** | **0.4682** | **0.5555** | **44.19%** | **+13.12%** | **23.8 MB (−88%)** |

> **Key Finding:** Restricting tree depth (20 → 10) acts as regularization against load spikes — better accuracy *and* 88% smaller file, making it ideal for edge smart-meter devices.

---

## 🖼️ Visual Results & Diagrams

<!-- ============================================================
     FIGURE 1 — System Architecture
     ============================================================ -->
<p align="center">
  <strong>① System Architecture — 7-Stage Training & Evaluation Pipeline</strong>
</p>

<p align="center">
  <a href="./reports/figures/figure_3_1_system_architecture.svg">
    <img src="./reports/figures/figure_3_1_system_architecture.svg"
         alt="System Architecture — 7-stage offline training & evaluation pipeline"
         width="100%" />
  </a>
</p>

<p align="center"><em>Click image to open full-resolution SVG · 7-stage offline training &amp; evaluation pipeline</em></p>

---

<!-- ============================================================
     FIGURE 2 — Workflow Diagram
     ============================================================ -->
<p align="center">
  <strong>② End-to-End Workflow — 12-Step Data Processing Sequence</strong>
</p>

<p align="center">
  <a href="./reports/figures/figure_3_2_workflow.svg">
    <img src="./reports/figures/figure_3_2_workflow.svg"
         alt="Workflow Diagram — 12-step end-to-end data processing"
         width="100%" />
  </a>
</p>

<p align="center"><em>Click image to open full-resolution SVG · 12-step end-to-end data processing workflow</em></p>

---

<!-- ============================================================
     FIGURE 3 — Model MAE Benchmark
     ============================================================ -->
<p align="center">
  <strong>③ Model MAE Benchmark — 4-Model Bar Comparison on Held-Out Test Data</strong>
</p>

<p align="center">
  <a href="./reports/figures/model_mae_comparison_all_models.png">
    <img src="./reports/figures/model_mae_comparison_all_models.png"
         alt="Model MAE Comparison — 4-model bar chart"
         width="85%" />
  </a>
</p>

<p align="center"><em>Tuned RF achieves lowest MAE (0.3239 kW) across all 4 models on 5,185 held-out test hours</em></p>

---

<!-- ============================================================
     FIGURE 4 — Actual vs Predicted
     ============================================================ -->
<p align="center">
  <strong>④ Actual vs. Predicted — 168-Hour Tracking with 48-Hour Zoom</strong>
</p>

<p align="center">
  <a href="./reports/figures/model_comparison_actual_vs_predicted.png">
    <img src="./reports/figures/model_comparison_actual_vs_predicted.png"
         alt="Actual vs Predicted — 168-hour time-series tracking"
         width="95%" />
  </a>
</p>

<p align="center"><em>Tuned RF (orange) closely follows real consumption (blue) with tighter band than baseline models</em></p>

---

<!-- ============================================================
     FIGURE 5 — Hyperparameter Tuning
     ============================================================ -->
<p align="center">
  <strong>⑤ Hyperparameter Tuning — Validation MAE & RMSE vs Tree Depth</strong>
</p>

<p align="center">
  <a href="./reports/figures/model_tuning_comparison.png">
    <img src="./reports/figures/model_tuning_comparison.png"
         alt="Hyperparameter Tuning — MAE & RMSE drop with max_depth"
         width="85%" />
  </a>
</p>

<p align="center"><em>max_depth=10 minimises both validation MAE &amp; RMSE — regularization sweet spot</em></p>

---

<!-- ============================================================
     FIGURE 6 — Feature Importance
     ============================================================ -->
<p align="center">
  <strong>⑥ Feature Importance Ranking — MDI Gini Importance</strong>
</p>

<p align="center">
  <a href="./reports/figures/feature_importance.png">
    <img src="./reports/figures/feature_importance.png"
         alt="Feature Importance — lag_1 dominance at ~61%"
         width="85%" />
  </a>
</p>

<p align="center"><em><code>lag_1</code> dominates at ~61%, followed by calendar <code>hour</code> and <code>lag_24</code> — confirms autocorrelation-driven forecasting</em></p>

---

<!-- ============================================================
     FIGURE 7 — Residual Error Distribution
     ============================================================ -->
<p align="center">
  <strong>⑦ Residual Error Distribution — Prediction Error Histogram & KDE</strong>
</p>

<p align="center">
  <a href="./reports/figures/error_summary.png">
    <img src="./reports/figures/error_summary.png"
         alt="Error Summary — histogram and KDE centered at 0"
         width="85%" />
  </a>
</p>

<p align="center"><em>Error distribution is centred at 0 kW with low spread — no systematic bias detected</em></p>

---

## ⚡ Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Run Automated Tests (41 Tests)
```powershell
python -m unittest discover -s tests -v
```
```text
Ran 41 tests in 3.363s
OK
```

### 3. Make an Instant Prediction via CLI
```powershell
python -m src.ml.predict --lag-1 1.25 --lag-2 1.10 --lag-3 1.05 --lag-24 1.30 --rolling-3h 1.13 --rolling-24h 1.22 --hour 18 --day-of-week 2 --model-path models/random_forest_tuned.joblib
```
```json
=== Prediction Result ===
{
  "prediction_kw": 1.5753,
  "unit": "kW",
  "horizon": "next_1_hour",
  "input_features": {
    "lag_1": 1.25,
    "lag_2": 1.1,
    "lag_3": 1.05,
    "lag_24": 1.3,
    "rolling_mean_3h": 1.13,
    "rolling_mean_24h": 1.22,
    "hour": 18.0,
    "day_of_week": 2.0
  }
}
```

### 4. Train & Benchmark All Models
```powershell
python scripts/train_model.py
```

### 5. Run Hyperparameter Tuning
```powershell
python scripts/tune_model.py
```

---

## 📁 Repository Structure

```text
ml-service/
├── data/
│   ├── raw/household_power_consumption.txt    # Raw 2M+ readings (133 MB)
│   └── processed/hourly_consumption.csv       # Cleaned hourly series (34,589 rows)
├── models/
│   ├── random_forest_tuned.joblib             # Best model (23.8 MB)
│   ├── random_forest.joblib                   # Original model (201.7 MB)
│   └── random_forest_tuned_metadata.json      # Complete parameters and scores
├── reports/
│   ├── figures/                               # All generated 200 DPI charts and SVGs
│   ├── metrics/                               # Metrics CSVs and prediction outputs
│   └── final_experiment_summary.md            # Detailed academic summary
├── scripts/
│   ├── train_model.py                         # Runs baseline benchmark
│   └── tune_model.py                          # Runs 20-configuration grid search
├── src/
│   └── ml/
│       ├── features.py                        # 8 leak-free features
│       ├── predict.py                         # CLI inference tool
│       ├── preprocessing.py                   # Chronological splitting
│       ├── train.py                           # Benchmark training logic
│       └── tune.py                            # Tuning search logic
├── tests/                                     # 41 unit tests
└── requirements.txt                           # Dependencies
```
