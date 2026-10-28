# APPENDIX: SUPPLEMENTARY EXPERIMENTAL RESULTS AND TESTING EVIDENCE

**Project Title:** AI-Based Energy Consumption Prediction System  
**Institution:** Galgotias University, Greater Noida  
**Department:** Master of Computer Applications (MCA)  
**Authors:** Dharamraj Prasad Yadav, Yash Kumar, Saurabh Kumar  

---

## Appendix A: Complete Model Comparison Results

### A.1 Comprehensive Cross-Split Evaluation Table

All models were evaluated on identical chronological partitions of the **UCI Individual Household Electric Power Consumption dataset** (34,565 clean hourly samples):
* **Training Partition (70%):** 24,195 samples (Dec 17, 2006, 16:00 to Sep 20, 2009, 18:00)
* **Validation Partition (15%):** 5,185 samples (Sep 20, 2009, 19:00 to Apr 24, 2010, 19:00) — *used exclusively for model selection and tuning*
* **Held-Out Test Partition (15%):** 5,185 samples (Apr 24, 2010, 20:00 to Nov 26, 2010, 20:00) — *held untouched until final out-of-sample evaluation*

| Model Name | Evaluation Split | MAE (kW) | RMSE (kW) | $R^2$ Score | MAPE (%) [$\epsilon = 10^{-4}$] | MAE Improvement vs. Baseline | Model Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | Validation (15%) | 0.4555 | 0.6844 | 0.4147 | 44.13% | Reference | Non-parametric |
| | **Held-Out Test (15%)** | **0.3728** | **0.5752** | **0.3291** | **44.75%** | **Reference** | Primary Baseline |
| **Linear Regression (OLS)** | Validation (15%) | 0.4405 | 0.6096 | 0.5355 | 50.81% | +3.30% | Parametric Comparator |
| | **Held-Out Test (15%)** | **0.3598** | **0.5058** | **0.4811** | **50.08%** | **+3.49%** | Linear Comparator |
| **Original Random Forest** | Validation (15%) | 0.3747 | 0.5443 | 0.6297 | 39.59% | +17.74% | Pre-tuning ($d=20$) |
| | **Held-Out Test (15%)** | **0.3283** | **0.4734** | **0.5454** | **44.78%** | **+11.94%** | Baseline Ensemble |
| **Tuned Random Forest** | Validation (15%) | 0.3703 | 0.5411 | 0.6340 | 38.88% | +18.70% | Selected via Val MAE |
| | **Held-Out Test (15%)** | **0.3239** | **0.4682** | **0.5555** | **44.19%** | **+13.12%** | **★ Final Winning Model** |

### A.2 Artifact Footprint & Computational Resource Comparison

| Model Architecture | Serialization File Path | Model Disk Size | Number of Estimators | Max Tree Depth | Min Samples per Leaf |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Persistence Baseline** | *Non-parametric (no saved file)* | 0.0 MB | N/A | N/A | N/A |
| **Linear Regression** | `models/linear_regression.joblib` *(in pipeline)* | < 0.1 MB | N/A | N/A | N/A |
| **Original Random Forest** | `models/random_forest.joblib` | **201.7 MB** | 250 | 20 | 2 |
| **Tuned Random Forest** | `models/random_forest_tuned.joblib` | **23.8 MB** | 250 | 10 | 2 |
| **Optimization Benefit** | **Disk Footprint Reduction** | **-88.2% (177.9 MB saved)** | — | **Regularized** | — |

---

## Appendix B: Additional Random Forest Tuning Results

### B.1 Complete 20-Configuration Hyperparameter Grid Search Table

Hyperparameter tuning was conducted strictly over the **5,185 validation observations** to preserve the test set's out-of-sample integrity. The search space encompassed 20 distinct parameter combinations across tree count ($n \in \{150, 250, 400\}$), tree depth ($\text{max\_depth} \in \{10, 20, 30, \text{None}\}$), minimum leaf samples ($\text{min\_leaf} \in \{1, 2, 4\}$), and feature subsampling fractions ($\text{max\_features} \in \{0.7, 1.0\}$).

*Data source: `reports/metrics/random_forest_tuning.csv`*

| Trial ID | $n_{\text{est}}$ | Max Depth | Min Leaf | Max Features | Val MAE (kW) | Val RMSE (kW) | Val $R^2$ | Val MAPE (%) | Fit Time (s) | Best Selected? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 250 | 20 | 2 | 1.0 | 0.3747 | 0.5443 | 0.6297 | 39.59 | 23.74 | No (Original) |
| 2 | 150 | 10 | 2 | 1.0 | 0.3707 | 0.5414 | 0.6336 | 38.91 | 2.80 | No |
| 3 | 150 | 20 | 2 | 1.0 | 0.3750 | 0.5451 | 0.6287 | 39.60 | 10.99 | No |
| 4 | 150 | 30 | 2 | 1.0 | 0.3757 | 0.5455 | 0.6281 | 39.70 | 17.05 | No |
| 5 | 150 | None | 2 | 1.0 | 0.3757 | 0.5455 | 0.6280 | 39.68 | 17.48 | No |
| 6 | 150 | 20 | 1 | 1.0 | 0.3754 | 0.5443 | 0.6297 | 39.91 | 11.17 | No |
| 7 | 150 | 20 | 4 | 1.0 | 0.3743 | 0.5430 | 0.6315 | 39.39 | 4.95 | No |
| 8 | 150 | 10 | 1 | 1.0 | 0.3706 | 0.5413 | 0.6338 | 38.93 | 8.11 | No |
| 9 | 150 | 10 | 4 | 1.0 | 0.3710 | 0.5415 | 0.6336 | 38.95 | 11.17 | No |
| 10 | 150 | 20 | 2 | 0.7 | 0.3735 | 0.5416 | 0.6334 | 39.58 | 12.28 | No |
| 11 | 150 | 10 | 2 | 0.7 | 0.3720 | 0.5416 | 0.6334 | 39.27 | 7.25 | No |
| 12 | 150 | 10 | 4 | 0.7 | 0.3719 | 0.5413 | 0.6339 | 39.25 | 7.10 | No |
| 13 | 150 | None | 4 | 0.7 | 0.3733 | 0.5406 | 0.6347 | 39.47 | 9.52 | No |
| **14** | **250** | **10** | **2** | **1.0** | **0.3703** | **0.5411** | **0.6340** | **38.88** | **17.95** | **★ WINNER (BEST)** |
| 15 | 250 | 10 | 2 | 0.7 | 0.3715 | 0.5415 | 0.6336 | 39.20 | 12.25 | No |
| 16 | 250 | 10 | 4 | 1.0 | 0.3708 | 0.5413 | 0.6338 | 38.96 | 17.84 | No |
| 17 | 250 | 10 | 4 | 0.7 | 0.3716 | 0.5414 | 0.6336 | 39.25 | 11.73 | No |
| 18 | 400 | 10 | 2 | 1.0 | 0.3704 | 0.5410 | 0.6342 | 38.87 | 28.46 | No |
| 19 | 400 | 10 | 2 | 0.7 | 0.3713 | 0.5413 | 0.6338 | 39.20 | 18.78 | No |
| 20 | 400 | 20 | 2 | 0.7 | 0.3732 | 0.5413 | 0.6339 | 39.53 | 27.91 | No |

### B.2 Hyperparameter Sensitivity Analysis
1. **Influence of Maximum Depth (`max_depth`):**  
   Restricting depth to 10 consistently produced the lowest validation errors across all tree counts ($0.3703 \sim 0.3720$ kW). Unconstrained depths ($20, 30, \text{None}$) degraded validation MAE to $> 0.3750$ kW, demonstrating that excessive tree depth causes individual estimators to overfit to stochastic appliance switching noise.
2. **Influence of Tree Count (`n_estimators`):**  
   Increasing trees from 150 to 250 improved stability and reduced error ($0.3707 \rightarrow 0.3703$ kW). Further scaling to 400 trees produced negligible improvement ($0.3704$ kW) while increasing fit time by 58% ($17.95\text{s} \rightarrow 28.46\text{s}$), making $250$ trees the optimal trade-off.
3. **Influence of Feature Subsampling (`max_features`):**  
   Using all features ($1.0$) achieved slightly lower validation MAE ($0.3703$ kW vs. $0.3715$ kW for $0.7$), as all 8 engineered features provide complementary signals that individual split nodes benefit from considering.

---

## Appendix C: Supplementary Evaluation Graphs Catalog

The repository provides high-resolution figures (200 DPI, vector SVG and PNG) saved in `reports/figures/`:

| Figure Label | File Name | Format | Purpose & Description |
| :--- | :--- | :---: | :--- |
| **Figure C.1** | `figure_3_1_system_architecture.svg` | SVG | Clean 16:9 system architecture diagram depicting the 7 pipeline phases. |
| **Figure C.2** | `figure_3_2_workflow.svg` | SVG | Sequential 12-step data processing and model development workflow diagram. |
| **Figure C.3** | `model_mae_comparison_all_models.png` | PNG | Consolidated bar chart of Test MAE across all 4 models (Persistence, Linear Regression, Original RF, and Tuned RF) with exact numeric annotations. |
| **Figure C.4** | `model_comparison_actual_vs_predicted.png` | PNG | Dual-panel time-series tracking: 168-hour (1 week) dynamic tracking overlay + 48-hour zoomed peak/trough detail. |
| **Figure C.5** | `model_tuning_comparison.png` | PNG | Grouped bar chart comparing Validation MAE and RMSE between Original and Tuned Random Forest. |
| **Figure C.6** | `actual_vs_predicted.png` | PNG | Scatter plot of true vs. predicted active power over all 5,185 test samples against the ideal $y=x$ reference line ($R^2 = 0.5555$). |
| **Figure C.7** | `residuals_plot.png` | PNG | Residual error distribution against predicted power and over chronological test sequence with $\pm 1.96\sigma$ bounds. |
| **Figure C.8** | `feature_importance.png` | PNG | Horizontal bar chart of Mean Decrease in Impurity (Gini importance) ranking all 8 features (`lag_1`: 0.611, `hour`: 0.082, `lag_24`: 0.078). |
| **Figure C.9** | `error_summary.png` | PNG | Histogram and Kernel Density Estimation (KDE) curve of prediction residuals centered around 0.0 kW. |

---

## Appendix D: Automated Test Suite Execution Evidence

### D.1 Test Execution Command & Terminal Output
The complete unit test suite was executed in PowerShell from the `ml-service` root directory using Python's standard `unittest` framework:

```powershell
PS D:\energy-consumption-ai\ml-service> python -m unittest discover -s tests -v
test_health_reports_liveness_without_claiming_model_readiness (test_api_routes.ApiRouteTests.test_health_reports_liveness_without_claiming_model_readiness) ... ok
test_model_info_reports_blocker_without_local_paths (test_api_routes.ApiRouteTests.test_model_info_reports_blocker_without_local_paths) ... ok
test_openapi_lists_routes_without_claiming_a_prediction_schema (test_api_routes.ApiRouteTests.test_openapi_lists_routes_without_claiming_a_prediction_schema) ... ok
test_predict_returns_service_unavailable_not_a_fake_prediction (test_api_routes.ApiRouteTests.test_predict_returns_service_unavailable_not_a_fake_prediction) ... ok
test_empty_files_fail_clearly (test_data_loader.DataLoaderTests.test_empty_files_fail_clearly) ... ok
test_invalid_timestamp_and_measurement_are_rejected (test_data_loader.DataLoaderTests.test_invalid_timestamp_and_measurement_are_rejected) ... ok
test_loads_valid_csv_and_adds_timestamp (test_data_loader.DataLoaderTests.test_loads_valid_csv_and_adds_timestamp) ... ok
test_missing_file_has_a_useful_error (test_data_loader.DataLoaderTests.test_missing_file_has_a_useful_error) ... ok
test_missing_required_columns_are_rejected (test_data_loader.DataLoaderTests.test_missing_required_columns_are_rejected) ... ok
test_cleaning_drops_incomplete_rows (test_data_pipeline.DataPipelineTests.test_cleaning_drops_incomplete_rows) ... ok
test_cleaning_rejects_colliding_or_empty_normalized_column_names (test_data_pipeline.DataPipelineTests.test_cleaning_rejects_colliding_or_empty_normalized_column_names) ... ok
test_final_report_includes_cleaning_counts_and_output_path (test_data_pipeline.DataPipelineTests.test_final_report_includes_cleaning_counts_and_output_path) ... ok
test_inspection_report_documents_structure_and_quality (test_data_pipeline.DataPipelineTests.test_inspection_report_documents_structure_and_quality) ... ok
test_load_raw_data_parses_source_delimiter_and_missing_marker (test_data_pipeline.DataPipelineTests.test_load_raw_data_parses_source_delimiter_and_missing_marker) ... ok
test_normalize_column_name_standardizes_spaces_punctuation_and_case (test_data_pipeline.DataPipelineTests.test_normalize_column_name_standardizes_spaces_punctuation_and_case) ... ok
test_validation_preserves_missing_values_and_converts_numbers (test_data_pipeline.DataPipelineTests.test_validation_preserves_missing_values_and_converts_numbers) ... ok
test_validation_rejects_invalid_dates_and_numeric_values (test_data_pipeline.DataPipelineTests.test_validation_rejects_invalid_dates_and_numeric_values) ... ok
test_appending_same_result_twice_does_not_duplicate_it (test_evaluate.EvaluationTests.test_appending_same_result_twice_does_not_duplicate_it) ... ok
test_distinct_result_is_appended (test_evaluate.EvaluationTests.test_distinct_result_is_appended) ... ok
test_incompatible_empty_and_nonfinite_values_fail_clearly (test_evaluate.EvaluationTests.test_incompatible_empty_and_nonfinite_values_fail_clearly) ... ok
test_incompatible_existing_results_schema_fails_clearly (test_evaluate.EvaluationTests.test_incompatible_existing_results_schema_fails_clearly) ... ok
test_metrics_match_known_values (test_evaluate.EvaluationTests.test_metrics_match_known_values) ... ok
test_non_vector_input_fails_clearly (test_evaluate.EvaluationTests.test_non_vector_input_fails_clearly) ... ok
test_missing_and_nonfinite_targets_are_rejected (test_features.FeatureTests.test_missing_and_nonfinite_targets_are_rejected) ... ok
test_missing_columns_invalid_timestamps_and_empty_input_fail_clearly (test_features.FeatureTests.test_missing_columns_invalid_timestamps_and_empty_input_fail_clearly) ... ok
test_repeated_calls_are_deterministic (test_features.FeatureTests.test_repeated_calls_are_deterministic) ... ok
test_sorts_rows_and_uses_only_prior_observations (test_features.FeatureTests.test_sorts_rows_and_uses_only_prior_observations) ... ok
test_chronological_70_15_15_split (test_hourly_pipeline.HourlyPipelineTests.test_chronological_70_15_15_split) ... ok
test_fair_model_comparison_evaluates_identical_timestamps_and_features (test_hourly_pipeline.HourlyPipelineTests.test_fair_model_comparison_evaluates_identical_timestamps_and_features) ... ok
test_hourly_aggregation_computes_means_and_preserves_continuity (test_hourly_pipeline.HourlyPipelineTests.test_hourly_aggregation_computes_means_and_preserves_continuity) ... ok
test_hourly_features_contain_all_required_columns_and_no_leakage (test_hourly_pipeline.HourlyPipelineTests.test_hourly_features_contain_all_required_columns_and_no_leakage) ... ok
test_predict_validation_rejects_missing_and_invalid_inputs (test_hourly_pipeline.HourlyPipelineTests.test_predict_validation_rejects_missing_and_invalid_inputs) ... ok
test_preservation_of_chronological_order_and_zero_leakage (test_hourly_pipeline.HourlyPipelineTests.test_preservation_of_chronological_order_and_zero_leakage) ... ok
test_regression_metrics_handles_zero_values_with_epsilon (test_hourly_pipeline.HourlyPipelineTests.test_regression_metrics_handles_zero_values_with_epsilon) ... ok
test_tuning_parameter_selection_and_reproducibility (test_hourly_pipeline.HourlyPipelineTests.test_tuning_parameter_selection_and_reproducibility) ... ok
test_three_way_split_preserves_order_and_rows (test_preprocessing.PreprocessingTests.test_three_way_split_preserves_order_and_rows) ... ok
test_three_way_split_rejects_invalid_fraction_and_too_few_rows (test_preprocessing.PreprocessingTests.test_three_way_split_rejects_invalid_fraction_and_too_few_rows) ... ok
test_two_way_split_retains_existing_behavior (test_preprocessing.PreprocessingTests.test_two_way_split_retains_existing_behavior) ... ok
test_fixed_random_seeds_produce_repeatable_results (test_train.TrainingTests.test_fixed_random_seeds_produce_repeatable_results) ... ok
test_missing_target_fails_without_leaking_target_as_a_feature (test_train.TrainingTests.test_missing_target_fails_without_leaking_target_as_a_feature) ... ok
test_synthetic_data_runs_through_baselines (test_train.TrainingTests.test_synthetic_data_runs_through_baselines) ... ok

----------------------------------------------------------------------
Ran 41 tests in 3.363s

OK
```

### D.2 Test Suite Execution Summary
* **Total Automated Tests:** 41
* **Passed:** 41 (100%)
* **Failed:** 0
* **Errors:** 0
* **Execution Duration:** 3.36 seconds
* **Coverage Scope:** Data ingestion, timestamp parsing, missing-value interpolation, feature construction causality, chronological partitioning, metric math correctness, model determinism, and API route safety.

---

## Appendix E: Command-Line Prediction Output Evidence

### E.1 Prediction Using the Baseline Random Forest Model
* **Execution Command:**
  ```powershell
  python -m src.ml.predict --lag-1 1.25 --lag-2 1.10 --lag-3 1.05 --lag-24 1.30 --rolling-3h 1.13 --rolling-24h 1.22 --hour 18 --day-of-week 2
  ```
* **Actual Console JSON Output:**
  ```json
  === Prediction Result ===
  {
    "prediction_kw": 1.6585,
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

### E.2 Prediction Using the Tuned Random Forest Model
* **Execution Command:**
  ```powershell
  python -m src.ml.predict --lag-1 1.25 --lag-2 1.10 --lag-3 1.05 --lag-24 1.30 --rolling-3h 1.13 --rolling-24h 1.22 --hour 18 --day-of-week 2 --model-path models/random_forest_tuned.joblib
  ```
* **Actual Console JSON Output:**
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
