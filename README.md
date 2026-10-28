<p align="center">
  <img src="./banner.svg" alt="AI-Based Energy Consumption Prediction System" width="100%" />
</p>

# AI-Based Energy Consumption Prediction System

A lightweight, reproducible machine learning pipeline that forecasts residential electricity consumption for the **next 1 hour** (in kilowatts, kW) using 4 years of historical smart-meter telemetry.

---

<!-- Animated highlight box for ml-service link -->
<p align="center">
  <a href="./ml-service/README.md">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=22&pause=1000&color=00D2FF&center=true&vCenter=true&width=700&lines=⚡+Active+Machine+Learning+Service;Full+Pipeline+%7C+Visual+Charts+%7C+Benchmarks;👉+Open+ml-service%2FREADME.md" alt="Active ML Service" />
  </a>
</p>

<p align="center">
  <a href="./ml-service/README.md">
    <img src="https://img.shields.io/badge/📂_ML_Service-Open_Full_Implementation_%26_Visual_Results-00D2FF?style=for-the-badge&labelColor=0B132B&color=7B2FF7" alt="Open ml-service README" />
  </a>
</p>

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
