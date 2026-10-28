<p align="center">
  <img src="./banner.svg" alt="AI-Based Energy Consumption Prediction System" width="100%" />
</p>

# AI-Based Energy Consumption Prediction System

A lightweight, reproducible machine learning pipeline that forecasts residential electricity consumption for the **next 1 hour** (in kilowatts, kW) using 4 years of historical smart-meter telemetry.

---

> ### ⚡ Active Machine Learning Service
> The complete implementation, model training code, test suite, visual output charts, and research reports live inside **[`ml-service/`](./ml-service/README.md)**.  
> 👉 **[Open ml-service/README.md for Full Implementation, Visual Charts & Benchmarks](./ml-service/README.md)**

---

## ⚡ Quick Start: Run Everything

Run the entire pipeline from the `ml-service` directory:

### 1. Install Dependencies
```powershell
cd ml-service
pip install -r requirements.txt
```

### 2. Run Test Suite (41 Tests Passed)
```powershell
python -m unittest discover -s tests -v
```

### 3. Run Next-Hour Power Prediction via CLI
Predict next-hour active power (kW) using the tuned Random Forest model:
```powershell
python -m src.ml.predict --lag-1 1.25 --lag-2 1.10 --lag-3 1.05 --lag-24 1.30 --rolling-3h 1.13 --rolling-24h 1.22 --hour 18 --day-of-week 2 --model-path models/random_forest_tuned.joblib
```
**Output:**
```json
=== Prediction Result ===
{
  "prediction_kw": 1.5753,
  "unit": "kW",
  "horizon": "next_1_hour"
}
```

---

## 📁 Repository Structure

```text
energy-consumption-ai/
├── banner.svg                   # Visual repository banner
├── manual.html                  # Beginner-friendly viva & presentation guide
├── backend/                     # Backend API service (planned)
├── frontend/                    # Web dashboard (planned)
├── ml-service/                  # Active machine learning pipeline & models
│   ├── data/                    # Raw & processed hourly telemetry
│   ├── models/                  # Trained model artifacts (.joblib)
│   ├── notebooks/               # Exploratory data analysis notebooks
│   ├── reports/                 # Research reports, metrics & figures
│   ├── scripts/                 # Benchmark training & tuning entry points
│   ├── src/ml/                  # Core feature engineering & training logic
│   └── tests/                   # 41 passing automated unit tests
└── research/                    # Academic papers & references
```

---

## 📖 Key Documentation & Links

* 📘 **[Complete ML Pipeline & Visual Results (`ml-service/README.md`)](./ml-service/README.md)** — In-depth guide with all 7 visual charts and system diagrams.
* 📊 **[Final Experiment Summary (`ml-service/reports/final_experiment_summary.md`)](./ml-service/reports/final_experiment_summary.md)** — Comprehensive metrics, split boundaries, and causality audits.
* 📄 **[Conference Research Paper Draft (`ml-service/reports/conference_paper_draft.md`)](./ml-service/reports/conference_paper_draft.md)** — Verified IEEE paper draft for university submission.
* 🎓 **[Interactive Presentation & Viva Manual (`manual.html`)](./manual.html)** — Step-by-step cheatsheet for viva defense and live demonstration.
