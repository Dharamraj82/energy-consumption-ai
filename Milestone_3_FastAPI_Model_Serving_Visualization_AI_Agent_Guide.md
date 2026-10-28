# Milestone 3 — ML Model Serving with FastAPI
## Complete AI Coding Agent Instructions: Model, Prediction API, Visualizations, Tests, and Documentation

**Project:** AI-Based Energy Consumption Prediction System  
**Repository root:** `D:\energy-consumption-ai\`  
**Milestone directory:** `D:\energy-consumption-ai\ml-service\`  
**Primary goal:** Serve the model selected through Milestone 2 experiments using a reliable Python FastAPI service, verify its predictions, and provide clear visual evidence of model behaviour.

> **Critical rule:** Do not choose or claim a winning model before inspecting the actual Milestone 2 experiment results. The deployed model must be the model justified by real validation results and evaluated on the held-out test set. Never invent feature names, units, scores, plots, predictions, or test results.

---

# 1. What Milestone 3 does

Milestone 1 prepared and cleaned the dataset. Milestone 2 explored the data, generated features, trained candidate models, and compared their metrics. Milestone 3 turns the chosen fitted pipeline into an API that other applications can call.

The end-to-end serving flow is:

```text
Client / later application
        |
        | JSON request containing the real model inputs
        v
FastAPI route
        |
        v
Pydantic request validation
        |
        v
Prediction service
        |
        +--> The same feature-generation logic used during training, if required
        |
        +--> Saved fitted preprocessing pipeline
        |
        v
Selected fitted regression model
        |
        v
Validate that the result is numeric and finite
        |
        v
JSON prediction response
```

In parallel, an offline validation/reporting workflow loads recorded experiment results and a labelled holdout dataset, runs the saved model on known examples, and creates plots to inspect prediction behaviour. **Do not generate charts or run training inside every API request.** The API should provide inference; analysis plots belong in notebooks or an offline report script.

## In scope

- Inspect the actual Milestone 2 results and selected model.
- Load and validate the saved model pipeline and metadata.
- Expose `GET /health`, `GET /model-info`, and `POST /predict`.
- Reuse the exact training-time features and preprocessing.
- Validate requests and return clear errors.
- Add model-loading, service, route, and integration tests.
- Add or update documentation and verified run commands.
- Produce optional offline plots that verify model behaviour on labelled test data.
- Use Pandas, NumPy, Matplotlib, Seaborn, and scikit-learn where appropriate for offline analysis/testing.

## Out of scope

Do not implement the Node.js backend, PostgreSQL, frontend dashboard, user authentication, cloud deployment, Docker, CI/CD, IoT ingestion, weather API integration, or new advanced ML features in this milestone unless requested separately. Do not retrain a model at API startup.

---

# 2. Repository: preserve the current structure

Existing project structure supplied by the owner:

```text
D:\energy-consumption-ai\
├── backend/                         # Existing; leave unchanged in this milestone
├── frontend/                        # Existing; leave unchanged in this milestone
├── ml-service/
│   ├── data/
│   │   ├── raw/                     # Original source data; read-only
│   │   ├── interim/                 # Existing intermediate data
│   │   └── processed/               # Cleaned data from Milestone 1
│   ├── notebooks/                   # Milestone 2 notebooks
│   ├── reports/                     # Experiment notes and reports
│   ├── src/
│   │   └── data/                    # Existing data-related code
│   ├── tests/                       # Existing tests; preserve and extend
│   └── ...
└── research/                        # Existing research material
```

Do not create a second root-level `data/`, `notebooks/`, `models/`, `reports/`, `src/`, or `tests/` directory. Do not move or delete previous milestone files. Inspect the actual tree before adding files.

Suggested target structure (adapt it to the repository's existing conventions; create only what is missing):

```text
ml-service/
├── data/
│   ├── raw/                                  # Preserve, read-only
│   ├── interim/                              # Preserve
│   └── processed/                            # Preserve
├── notebooks/
│   ├── 04_eda.ipynb                          # Existing Milestone 2 work
│   ├── 05_feature_engineering.ipynb           # Existing Milestone 2 work
│   ├── 06_baseline_models.ipynb               # Existing Milestone 2 work
│   └── 07_model_serving_validation.ipynb      # Optional; create if useful
├── reports/
│   ├── figures/                              # Existing or create if missing
│   │   └── model_serving/                    # Create for offline prediction QA plots
│   ├── model_comparison.csv                  # Existing; preserve actual results
│   ├── experiment_notes.md                   # Existing; preserve and update only as needed
│   └── serving_validation.md                 # Create for API/prediction verification summary
├── models/
│   ├── energy_prediction_pipeline.joblib     # Reuse actual selected model artifact
│   └── model_metadata.json                   # Reuse/complete from verified experiment data
├── src/
│   ├── data/                                 # Existing; preserve
│   ├── ml/                                   # Existing Milestone 2 modules
│   └── api/                                  # Create if this layout fits the project
│       ├── __init__.py
│       ├── main.py                           # FastAPI app and lifecycle
│       ├── config.py                         # Paths/settings
│       ├── schemas.py                        # Request and response models
│       ├── dependencies.py                   # Access to loaded artifacts/service
│       ├── service.py                        # Prediction orchestration
│       └── routes/
│           ├── __init__.py
│           ├── health.py
│           ├── model_info.py
│           └── predict.py
├── tests/
│   ├── ...                                   # Existing tests; preserve
│   ├── test_model_loading.py                 # Add if missing
│   ├── test_prediction_service.py             # Add if missing
│   ├── test_api_health.py                    # Add if missing
│   ├── test_api_model_info.py                # Add if missing
│   ├── test_api_predict.py                    # Add if missing
│   └── test_api_validation.py                 # Add if missing
├── requirements.txt                          # Inspect and update only as needed
└── README.md                                 # Inspect and update only as needed
```

Do not create a separate `07_model_serving_validation.ipynb` if a suitable validation/reporting script or notebook already exists. Keep the final structure simple and aligned with the existing codebase.

---

# 3. Mandatory agent workflow before coding

The agent must first inspect the repository without modifying files. Then it must present a short implementation plan before editing.

## 3.1 Inspect the existing implementation

Inspect:

1. Repository tree, Git working tree/branch if Git is available, and `.gitignore`.
2. `ml-service/README.md`, the root README, and environment instructions if present.
3. `requirements.txt`, `pyproject.toml`, or whichever file actually manages dependencies.
4. Existing Python version and test framework.
5. `reports/model_comparison.csv` and `reports/experiment_notes.md` from Milestone 2.
6. The selected model artifact and model metadata, if present.
7. Existing code that loads data, engineers features, preprocesses inputs, trains models, and evaluates models.
8. Existing tests and any FastAPI code already in the repository.

## 3.2 Determine the real serving contract

Discover and document:

- Actual selected model name/type and why it was selected.
- Model artifact path and format.
- Target column and unit, only if documented.
- Exact required input feature names, types, and order/schema.
- Any input ranges supported by documented domain rules.
- Whether each prediction needs one feature row, a timestamp, a batch, or a history/time window.
- Which transformations are already inside the saved fitted pipeline and which feature-generation functions must run before it.
- Whether model and preprocessing library versions are compatible.
- Whether the selected model truly beats the appropriate baseline on validation and how it performs on the test set.

If the selected artifact, metadata, schema, or usable Milestone 2 results are absent, report the blocker. Do not invent a default model or a fake input schema. Make only safe preparatory changes until the missing prerequisite is resolved.

## 3.3 Implementation plan required

Before editing, list:

1. What exists and should be reused.
2. Which files will be added or updated.
3. Which model was selected from actual evidence.
4. The exact API request/response contract, based on the real feature schema.
5. Whether offline model-prediction plots are appropriate and which plots the data supports.
6. Tests that will be added or updated.
7. Dependency and compatibility risks.

After presenting the plan, implement incrementally according to the repository's normal approval/autonomy process. Run focused tests after each significant component.

## 3.4 Non-negotiable safety and quality rules

- Never modify `data/raw/` in place.
- Preserve Milestone 1 and Milestone 2 artifacts and tests.
- Do not silently drop data or change target units.
- Do not fit imputers, encoders, scalers, feature selectors, or models inside a prediction request.
- Do not retrain on app startup.
- Do not accept a client-provided model file path or load a client-uploaded pickle/joblib file.
- Do not send internal tracebacks, secrets, local paths, or raw private records to API clients.
- Do not make tests depend on internet access.
- Do not suppress or delete failing tests just to get a passing result.
- Do not claim a command, test, notebook, endpoint, plot, or prediction was successful unless it actually ran.

---

# 4. Which model should the service use?

**Use the model justified by Milestone 2 experiment results. Do not automatically use Random Forest or XGBoost just because they are popular.** This is a regression problem if the target is a numeric energy-consumption value, but the agent must confirm the actual target and task.

Candidate models that may have been evaluated in Milestone 2 include:

| Candidate | Why it may be useful | Risks/limitations |
|---|---|---|
| Mean/median or problem-appropriate naive baseline | Establishes the minimum reference that a useful model should beat | Simple and usually unable to represent rich patterns |
| Linear Regression | Transparent, fast baseline for approximately linear relationships | May underfit nonlinear behaviour |
| Decision Tree Regressor | Captures nonlinear interactions and is easy to inspect | Can overfit and make unstable predictions |
| Random Forest Regressor | Captures nonlinear relationships and often provides a strong tabular baseline | Larger artifact and less interpretable than a linear model |
| XGBoost Regressor, if evaluated | Can perform well on structured/tabular data | Extra dependency and tuning complexity; not automatically better |

## Model selection rules

1. Read the actual recorded comparison results.
2. Confirm that candidate metrics use the same target and comparable evaluation rows/splits.
3. Choose based primarily on validation performance and the project objective, considering MAE, RMSE, stability, inference cost, complexity, and improvement over the baseline.
4. Confirm the chosen model's final held-out test metrics were recorded independently of model selection.
5. If there is no defensible winner, do not deploy a model as “best.” Report the issue and request/recommend completing the missing experiment first.
6. Record in `model_metadata.json` and `reports/serving_validation.md` the selected model and the evidence supporting the choice. Use actual metrics from the report; never generate illustrative metrics and present them as real.

### Metrics explained

- **MAE (Mean Absolute Error):** Average absolute difference between actual and predicted target, in the target's unit. Lower is better.
- **RMSE (Root Mean Squared Error):** Square root of mean squared error; large misses affect this metric more. It uses the target's unit. Lower is better.
- **R²:** Measures improvement over a constant-mean reference on the evaluated sample. Higher is generally better; it can be negative, and it should not be used alone.

Metrics measure prediction error, not actual energy savings or bill reduction. Do not claim that the system reduces consumption or bills unless that outcome has been measured by a suitable study.

---

# 5. Model packaging and loading

## 5.1 Preferred artifact

Prefer one saved fitted pipeline containing all learned preprocessing and the estimator, for example:

```text
ml-service/models/energy_prediction_pipeline.joblib
```

The exact file path and filename must be confirmed from the actual repository. Do not fabricate a model file if one does not exist.

A complete pipeline may include supported transformations (imputation, encoding, scaling) and the final estimator. If time-series features such as lags/rolling statistics are created outside the pipeline, the serving service must reuse the exact tested feature-generation functions from training. It must not implement a subtly different version.

## 5.2 Model metadata

Use the existing metadata if valid. Fill only fields supported by the actual experiment. Useful fields include:

- Model name/type and experiment/model version.
- Target column and documented target unit.
- Input features and types/schema.
- Whether timestamps or a history window are required.
- Artifact identifier/relative path.
- Training dataset version or hash, if recorded.
- Split strategy and train/validation/test period or boundaries.
- Actual validation and final test metrics.
- Important hyperparameters.
- Python and important library versions.
- Known limitations and creation time.

Never put credentials, personal/household records, or arbitrary raw rows into metadata. Do not disclose internal machine-specific absolute paths in the public `/model-info` response.

## 5.3 Trusted serialization

`joblib` and pickle-based formats can execute code while loading. Only load artifacts created by this project or obtained from an explicitly trusted source. Never expose an API route that accepts arbitrary model files.

## 5.4 Load once per application lifecycle

Load and validate artifacts at application startup/lifespan or another clear one-time initialization path. Reuse the loaded object for requests. Do not reload the file on every `POST /predict`. Do not call `.fit()` or `.fit_transform()` during inference.

If the required model cannot load, the app should fail clearly at startup or mark model readiness unavailable according to the chosen lifecycle design. It must not silently use a random, untrained, or fallback estimator.

---

# 6. FastAPI implementation requirements

Implement a modular app consistent with the existing repo; the following modules are suggestions, not a requirement to over-split a small service.

## Configuration

- Resolve artifact paths using `pathlib.Path` and project/package-relative defaults or explicit environment settings.
- Do not hard-code `D:\energy-consumption-ai\...` in runtime code.
- Validate required paths and settings.
- Keep local secrets out of the repository.
- Document the current working directory and the verified run command.

## Request/response schemas

Use Pydantic schemas compatible with the installed FastAPI/Pydantic versions.

The request must reflect the model's real input contract. Require the necessary fields; validate types; reject non-finite numeric values; and reject unknown fields unless a documented reason requires them. Validate ranges only if supported by the data contract/domain rules. If the model requires a series of past observations, define its exact structure, ordering, interval, and minimum history length. Do not pretend one independent row is enough for a lag-dependent model.

The response must be JSON-safe. For a numeric regression target, return a finite numeric prediction and the documented target/model metadata that is safe to expose. Do not include unsupported units or a fabricated model version.

## Endpoint 1 — `GET /health`

Purpose: report service liveness, meaning that the process responds.

Example simple response:

```json
{"status": "ok"}
```

Return HTTP 200 when the process can answer health requests. If model readiness is separate, implement and document the distinction (for example, a readiness endpoint) instead of incorrectly treating liveness as proof that a model was loaded.

## Endpoint 2 — `GET /model-info`

Purpose: expose verified, non-sensitive metadata for the loaded model.

Include only fields actually available, such as model name/type, version/experiment id, target name/unit, input schema and real recorded metrics. Omit unknown optional fields or follow a documented `null` policy. Filter internal paths and private metadata rather than returning the raw metadata file unfiltered.

## Endpoint 3 — `POST /predict`

Purpose: validate a request, prepare model inputs in the exact expected format, and return inference.

Example response *shape only* (replace placeholders with verified metadata; do not hard-code these placeholder strings or use the example value as an actual prediction):

```json
{
  "prediction": 0.0,
  "target": "<actual-target-column>",
  "unit": "<documented-unit-if-known>",
  "model_version": "<real-version-if-available>"
}
```

Build a real request example for documentation only after identifying the actual model feature schema. Never show fake input fields as a working request.

## Error behaviour

Use consistent, documented status codes and safe responses:

- `422 Unprocessable Entity`: malformed or invalid request according to FastAPI/Pydantic validation (unless the repository already uses a justified consistent scheme).
- `503 Service Unavailable`: prediction is unavailable because the model is not ready/loaded, if the application supports running in that state.
- `500 Internal Server Error`: unexpected inference/internal error. Return a generic client-safe message; log technical details on the server.
- Do not turn a model error into an HTTP 200 response or return zero as a substitute for a failed prediction.

Use clear summaries/descriptions so FastAPI generates useful `/docs` and `/openapi.json` documentation. Do not expose detailed exception messages to clients if they reveal implementation details.

---

# 7. Pandas, Matplotlib, Seaborn, heatmaps, and model prediction graphs

This project should have understandable visual evidence of the data and model quality. Most exploratory graphs belong to Milestone 2. Milestone 3 should preserve those results and may add an **offline model-serving validation notebook/report** based on the selected saved model and labelled holdout data.

Use:
- **Pandas:** Load structured evaluation data, align predictions with actual rows, summarize residuals/metrics, and export tables/CSVs.
- **NumPy:** Numeric utilities and safe array checks.
- **Matplotlib:** Plot creation, axes, labels, titles, legends, layout, and saving figures.
- **Seaborn:** Useful statistical visuals such as correlation heatmaps and residual/distribution plots.
- **scikit-learn:** The actual selected pipeline and trusted metric calculations.

Do not install or use every library merely for its name. Check which are already in the environment; update dependencies only as needed.

## 7.1 Preserve/reuse Milestone 2 EDA graphs

Check which are already generated in `reports/figures/`. Only add missing plots that are justified by the data:

1. **Target distribution histogram:** helps inspect skew and the range of target values.
2. **Target over time line plot:** use when real timestamps/time-series structure exist; sort timestamps first.
3. **Boxplot of the target:** helps inspect potential extreme values; an outlier is not automatically an error.
4. **Numeric feature correlation heatmap:** compute with Pandas `DataFrame.corr(numeric_only=True)` and display with Seaborn `heatmap`. Include only appropriate numeric features and label the figure clearly. Correlation is not causation and should not be used alone for feature selection.
5. **Target-vs-feature scatterplots:** create only for meaningful numeric features and manageable chart counts.
6. **Model metric comparison:** use the actual recorded comparison CSV. Because MAE/RMSE and R² have different meanings and ranges, use clear separate charts or clearly separated axes rather than making a misleading single-scale plot.

Do not rerun exploratory plotting from inside FastAPI routes. Do not alter the raw/processed dataset to make charts look cleaner. Do not infer causal relationships from correlations.

## 7.2 Milestone 3 model-validation graphs

If a labelled holdout/test dataset and selected fitted model are available, create an optional notebook such as `notebooks/07_model_serving_validation.ipynb` or an equivalent offline script. Use the actual selected pipeline and actual feature logic. Save figures to:

```text
ml-service/reports/figures/model_serving/
```

Create the following, where appropriate to the task and data:

### A. Actual vs predicted scatter plot

- X-axis: actual target value.
- Y-axis: model prediction.
- Add a reference diagonal `y = x` where axes are on the same scale.
- Label target units if known.
- Good alignment to the diagonal indicates closer predictions; interpret alongside MAE/RMSE, not alone.
- Use only the held-out test predictions for the final test plot, and clearly label the dataset split.

Suggested filename: `actual_vs_predicted_test.png`.

### B. Residuals vs predicted plot

Define residual as `actual - predicted` and use that sign convention consistently.
- X-axis: predicted target.
- Y-axis: residual.
- Draw a horizontal zero-residual line.
- Look for patterns, heteroscedasticity, or systematic under/overprediction.

Suggested filename: `residuals_vs_predicted_test.png`.

### C. Residual distribution

Plot a histogram or density-style distribution of `actual - predicted`.
- Label the residual units if known.
- A distribution centred near zero can be informative but is not sufficient to prove good performance.

Suggested filename: `residual_distribution_test.png`.

### D. Actual vs predicted over time

Create this only for time-dependent data.
- Sort by the true timestamp.
- Plot actual and predicted values over the held-out test window.
- Label both series and show the test time period.
- Do not shuffle the timestamps.

Suggested filename: `actual_vs_predicted_over_time_test.png`.

### E. Error over time or by relevant subgroup

If enough data exists, inspect MAE or residual summaries by time segment or legitimate subgroup (such as device/household category if it is part of the dataset and suitable for analysis). Do not expose private data or make unsupported claims. Explain the sample sizes and limitations.

Suggested filename: `error_by_test_period.png`.

### F. Prediction output sanity check

Plot or summarize prediction and actual ranges to detect invalid values, unexpected constants, overflow, or schema mistakes. Do not present this as an accuracy metric by itself.

## 7.3 Prediction output table

Using Pandas, make a diagnostic table for a limited number of test rows containing appropriate fields, for example:

```text
row_identifier_or_timestamp, actual_target, predicted_target, residual, absolute_error
```

Use only columns that actually exist. Avoid exposing personal identifiers in public reports. Export a limited, safe diagnostic sample or aggregate error report if appropriate. Do not commit sensitive raw data or the entire test set just to show results.

`residual = actual_target - predicted_target`  
`absolute_error = abs(residual)`

Generate a summary with real MAE, RMSE, and R² using the same evaluation rows as the plots. If this is a time-series forecast, compare selected model results with the same baseline over exactly the same timestamps.

## 7.4 Visualization correctness rules

- All graphs must be based on actual data and actual predictions; do not fabricate plots or illustrative scores.
- Add meaningful title, axis labels, legend where useful, unit where documented, and a note of the split (validation/test).
- Save high-quality images to the stated reports directory and close figures after saving when running batch scripts.
- Keep plotting code offline; do not add Matplotlib/Seaborn dependencies to the runtime inference path if the API does not use them.
- Never generate a heatmap of the API response. A heatmap is a diagnostic chart over a structured dataset, usually correlations or aggregated errors.
- A correlation heatmap is generally an EDA artifact from Milestone 2. Keep it there; do not duplicate it in Milestone 3 unless it adds a specific model-serving validation insight.
- If a suitable labelled test set is missing, do not manufacture actual-vs-predicted/residual plots. Report that only API smoke tests could be performed, and identify what is needed for offline model validation.
- Avoid plots with unreadable labels or unnecessarily many charts. Make each chart answer a question.

---

# 8. Recommended offline serving-validation workflow

The agent should implement the following only if the trained artifact and labelled holdout dataset are available:

1. Load the real saved fitted pipeline using the same artifact-loading function as the app, where appropriate.
2. Load the actual test/holdout dataset and required feature columns.
3. Run the exact reusable training feature-generation code without leakage.
4. Generate predictions without calling `.fit()`.
5. Assert that predictions have the expected number of rows and are finite numeric values.
6. Align actuals and predictions by the same row identifiers/timestamps to prevent accidental misalignment.
7. Calculate MAE, RMSE, and R² using the same metric implementation as Milestone 2.
8. Compare with saved Milestone 2 test metrics; investigate discrepancies. Do not overwrite prior results silently.
9. Produce appropriate actual-vs-predicted, residual, and time-based plots as applicable.
10. Save figures and a concise `reports/serving_validation.md` containing exact input data/split, measured results, artifact version, plots created, and limitations.
11. Ensure this analysis is a repeatable offline script or notebook, not work performed on every API request.

If Milestone 2 metrics were computed on transformed labels, a different test period, or a different prediction target, do not compare them directly without explaining the differences.

---

# 9. Automated testing requirements

Inspect and follow the existing test framework. If the project uses `pytest`, extend it rather than introducing another runner. Use synthetic data and test doubles for unit tests. Do not require internet access or the full real dataset for ordinary unit tests.

## `test_model_loading.py`

Test:
- Correct trusted model artifact and metadata load.
- Missing model file fails clearly.
- Corrupt/incompatible artifact fails clearly.
- Required metadata/schema fields are validated.
- Loaded object supports the required prediction method.
- Artifact is not reloaded for every request where the application lifecycle design permits a direct test.
- Tests use only controlled temporary/trusted objects.

## `test_prediction_service.py`

Test:
- Actual input schema is converted to the model's expected format.
- The same preprocessing/feature-generation path as training is used.
- Input feature names and order are correct.
- The target is not included in the feature matrix.
- No fit/refit occurs during inference.
- Prediction has the expected shape and finite values.
- Unexpected model errors become controlled service errors.
- Non-finite or wrong-shaped output is rejected.
- Repeated identical inputs produce consistent output within an appropriate tolerance for a deterministic model.
- Lag/rolling calculations, if required, cannot use future rows.

## `test_api_health.py`

Test:
- Correct success status/body.
- No path or stack trace is disclosed.
- If readiness is separate, readiness reflects whether the model is available.

## `test_api_model_info.py`

Test:
- Returns accurate loaded metadata.
- Missing optional fields are omitted or handled according to schema.
- Does not expose local paths, secrets, or raw records.
- Not-ready behaviour is consistent when artifacts are unavailable.

## `test_api_predict.py`

Test:
- A valid schema-derived request succeeds.
- Response fields/types are correct.
- Prediction is finite and numeric.
- Metadata/unit fields, when returned, match actual metadata.
- Prediction result matches the service/loaded test double as expected.
- Model loading and inference failures do not return a fake successful result.

## `test_api_validation.py`

Test:
- Missing required fields return validation errors.
- Wrong types and malformed timestamps are rejected where relevant.
- NaN and positive/negative infinity are rejected for numeric inputs.
- Unknown fields follow the explicit schema policy.
- Domain bounds are checked only if documented.
- Invalid history length/order/spacing is rejected if the model depends on a history window.
- Empty batch is rejected if batch inference exists.
- Validation errors do not leak stack traces or implementation details.

## Integration and artifact smoke tests

Where the environment supports it:
- Use FastAPI's test client to hit all routes.
- Confirm `/openapi.json` can be generated.
- Load the actual selected Milestone 2 artifact.
- Call the service with a valid request derived from its real schema.
- Compare service output with direct invocation of the same saved pipeline and prepared input.
- Check the error path when an artifact is missing.
- Run all existing `ml-service/tests/` tests.
- Verify no unrelated frontend/backend files changed.

Do not set arbitrary thresholds for real model accuracy in unit tests. Unit tests verify functions and API contracts; actual predictive performance is reported from a legitimate held-out evaluation.

---

# 10. Dependencies and environment

First inspect the actual dependency manager and versions. Preserve current dependencies and constraints. Add only what the implementation needs.

Likely packages include:
- `fastapi`
- `uvicorn`
- `pydantic` (compatible with installed FastAPI)
- `joblib` (if used by the existing artifact)
- `pandas`
- `numpy`
- `scikit-learn` (compatible with the serialized model)
- `matplotlib` and `seaborn` for offline plots
- `pytest` if it is the project's test runner
- `httpx` if required by the chosen FastAPI test-client versions

Do not blindly upgrade everything. An already serialized scikit-learn model can be version-sensitive; verify the artifact with the actual installed environment. Add XGBoost only if the selected artifact uses it and the existing environment does not already provide it.

Use the existing virtual environment instructions. Never commit environment secrets or local `.env` files.

---

# 11. Run and verify the API

The following commands are examples only. The agent must confirm the project's import path and working directory, then document the exact verified commands.

Example from `D:\energy-consumption-ai\ml-service\`:

```bash
python --version
python -m pip install -r requirements.txt
python -m pytest tests -q
```

If the app structure is `src/api/main.py` and the import resolves correctly, a development launch could be:

```bash
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

If the package layout differs, replace the import path with the working one and document it. Do not hard-code this sample command if it does not match the implemented structure.

When running locally, check:

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/model-info`
- `POST http://127.0.0.1:8000/predict` with an actual-schema request
- `GET http://127.0.0.1:8000/docs`
- `GET http://127.0.0.1:8000/openapi.json`

Test both positive and negative requests. Do not include a made-up field list in the documented working request. If actual request examples cannot be provided because the model contract is missing, report that as a blocker.

---

# 12. Logging, security, and reliability

- Log application startup and artifact load success/failure.
- Log unexpected inference failures without exposing details to clients.
- Avoid logging raw household/energy input records by default.
- Do not display tracebacks, environment variables, secrets, or absolute internal paths in API responses.
- Do not expose a route for arbitrary file access or model replacement.
- Do not load user-uploaded pickle/joblib files.
- Restrict CORS origins if a browser caller needs it; do not use wildcard origins by default without an explicit requirement.
- Do not claim an unauthenticated local service is production-safe for public exposure.
- Apply sensible payload/sequence-length limits if supporting batch or history-window input.
- Keep errors stable and documented: invalid request, model unavailable, and unexpected inference failure must be distinguishable.
- Keep health checks fast and independent from training.

---

# 13. Documentation to update

Update `ml-service/README.md` if present; otherwise create one without replacing root-level documentation. Add a Milestone 3 section including:

1. Purpose of the service.
2. How the selected Milestone 2 model was identified, using actual results.
3. Artifact path and metadata fields.
4. Python/environment requirements and verified installation command.
5. Exact, verified command to start the service and required working directory.
6. `GET /health`, `GET /model-info`, and `POST /predict` paths and schemas.
7. A real request example derived from the actual input schema.
8. Example response shape using actual metadata conventions; do not invent a performance claim.
9. How to open `/docs` and `/openapi.json` locally.
10. How to run tests and an artifact smoke test.
11. How to regenerate offline model-validation plots, if implemented.
12. Known limitations, dependencies, artifact compatibility, and security cautions.
13. Clear statement that training is not run when the API starts.

Document only commands confirmed to work or label unverified commands accurately.

---

# 14. Required report outputs

## `reports/serving_validation.md`

If the relevant artifact and holdout data are available, include:

```markdown
# Milestone 3 Serving Validation

## Selected Model and Evidence
## Artifact and Dependency Versions
## Input Schema
## Inference Preprocessing Path
## API Routes Verified
## Test Commands and Results
## Offline Prediction Evaluation
## Actual Test Metrics
## Figures Generated
## Differences from Milestone 2 Results
## Limitations
```

Include only factual information from actual files, actual commands, and actual model runs. Clearly distinguish API functionality tests from predictive-accuracy evaluation.

## Figures

Use `reports/figures/model_serving/` for the optional serving-validation charts listed in Section 7.2. Preserve existing EDA figures. Do not create empty or fabricated image files to satisfy the checklist.

---

# 15. Milestone completion checklist

Milestone 3 is complete only when every applicable item is verified:

- [ ] Existing repository and Milestone 2 outputs inspected before editing.
- [ ] Selected model justified by actual recorded validation results and baseline comparison.
- [ ] Final test metrics are available or the limitation is explicitly reported.
- [ ] Input feature names, types, unit, and any history/window needs confirmed.
- [ ] Existing trained artifact reused; no unapproved retraining occurred.
- [ ] Training preprocessing/feature generation matches inference.
- [ ] Artifact and metadata load correctly.
- [ ] FastAPI app starts using the verified command.
- [ ] `/health` behaves as documented.
- [ ] `/model-info` reports correct, non-sensitive metadata.
- [ ] `/predict` accepts a valid real-schema request and returns a finite numeric prediction.
- [ ] Invalid input and artifact/inference failures are handled safely.
- [ ] Model is not refitted or reloaded on each prediction request.
- [ ] Unit/integration tests added or updated, and existing tests retained.
- [ ] Tests run and outcomes honestly recorded.
- [ ] Actual artifact smoke test performed if environment/artifact available.
- [ ] Offline plots created only when supported by actual labelled data.
- [ ] `serving_validation.md` and README are updated as applicable.
- [ ] No unexpected change to raw data, Milestone 1, Milestone 2, frontend, or application backend.
- [ ] No credentials/private records committed.
- [ ] Final report lists files, commands, results, metrics, artifacts, and known blockers.

If required model/schema artifacts are missing, Milestone 3 is **blocked**, not complete. The agent must explain the blocker and request/identify the required correction rather than fabricate a working service.

---

# 16. Required final response from the AI agent

After implementation, the coding agent must provide:

1. **Implementation summary:** How a request reaches the saved model and returns a prediction.
2. **Model selection:** Actual selected model type and evidence-based reason, including real baseline/validation/test metrics where available.
3. **Input/output contract:** Actual request fields, target name/unit if documented, and a valid request/response example.
4. **Changed files:** Every created/modified file and its purpose.
5. **Run commands:** Exact verified command and working directory.
6. **API routes:** Methods, paths, success behaviour, and error codes.
7. **Testing:** Exact commands, passed/failed/skipped counts, and environment blockers.
8. **Prediction verification:** Whether direct pipeline and API service outputs agree for comparable input.
9. **Visualizations:** Exact plot filenames, what each graph shows, and which split/data was used. Include actual-versus-predicted/residual plots only if valid labelled data was available.
10. **Artifacts/reports:** Paths to model metadata, report CSV/Markdown, and figures.
11. **Limitations:** Any missing metadata, schema uncertainty, dependency issue, or lack of test data.
12. **Next milestone:** Node.js integration and PostgreSQL are Milestone 4 and remain untouched.

**Final rule:** Source files existing does not prove that the model service works. Report completion only after the relevant implementation, tests, and inference checks were actually executed. Never report fabricated metrics or a guessed “best” model.
