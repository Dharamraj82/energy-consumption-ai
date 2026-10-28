# Milestone 3 Serving Validation

## Selected Model and Evidence

Blocked: Milestone 2 has not selected a model. The experiment notes state that
the checked-in cleaned dataset has only nine rows and that its two validation
examples are insufficient evidence for selecting a reusable model.

The comparison CSV contains 12 validation rows but only four unique records:
each of the same four model results is repeated three times. The repetitions
have identical metrics and notes, so they do not constitute independent
experiments. The latest recorded validation metrics are:

| Model | MAE (kW) | RMSE (kW) | R² | Evaluation rows |
| --- | ---: | ---: | ---: | ---: |
| Persistence | 0.1640 | 0.1650 | -2.2870 | 2 |
| Linear Regression | 3.2308 | 3.3922 | -1388.5907 | 2 |
| Decision Tree | 1.7490 | 1.7514 | -369.4000 | 2 |
| Random Forest | 1.1134 | 1.1171 | -149.6993 | 2 |

These validation metrics are recorded experiment output, but the tiny sample
does not justify choosing or deploying a model. No final held-out test metrics
are recorded.

## Artifact and Dependency Versions

- Expected model artifact: `models/energy_prediction_pipeline.joblib` —
  absent.
- Expected metadata: `models/model_metadata.json` — absent.
- `ml-service/models/` currently contains only `.gitkeep`.
- The inspected Python environment reports Python 3.14.3, scikit-learn 1.8.0,
  and joblib 1.5.3. The model's training-time library versions cannot be
  verified because no model artifact or metadata exists.
- API scaffold dependencies installed for verification: FastAPI 0.119.1,
  Starlette 0.48.0, Pydantic 2.14.1, Uvicorn 0.54.0, and HTTPX 0.28.1.
  `requirements.txt` constrains FastAPI to `>=0.115,<0.120` for compatibility
  with the tested Starlette TestClient/HTTPX combination.

## Input Schema

No serving input schema is confirmed. Milestone 2's exploratory feature set is
`previous_active_power`, `hour`, `minute`, and `day_of_week`, derived from the
current target observation and timestamp. This does not establish a supported
inference contract for a selected fitted model. A prediction request schema
must not be inferred from these experimental features alone.

## Inference Preprocessing Path

No serving preprocessing path can be verified because no selected fitted
pipeline exists. Milestone 2 creates next-observation features outside the
estimator pipeline and fits a median imputer plus candidate estimator on
training data. This is experimental code, not a packaged inference artifact.

## API Routes Verified

The API scaffold exposes:

- `GET /health` — returns `{"status":"ok"}` for process liveness only.
- `GET /model-info` — reports `status: blocked` and
  `prediction_available: false`; it does not expose local artifact paths.
- `POST /predict` — returns HTTP 503 with a generic unavailable message.
  No request schema is accepted or inferred until the real model contract
  exists.

Route tests verify these responses and `/openapi.json`. The scaffold does not
load or train a model and does not make predictions.

## Test Commands and Results

The route tests are in `tests/test_api_routes.py`. The focused command was
run from `ml-service/`:

```bash
python -m unittest discover -s tests -p "test_api_*.py" -v
```

Result: **4 API tests passed**. The complete suite is also invoked from the
start script after notebook execution. `python start.py` completed successfully;
all three Milestone 2 notebooks executed and all **33 unit/API tests passed**.
The launcher ran validation-score recording in parallel with the full test
suite.

The local server was launched from `ml-service/` with:

```bash
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

An HTTP smoke test verified `GET /health` (200), `GET /model-info` (200),
`POST /predict` (503), `GET /docs` (200), and `GET /openapi.json` (200).
The smoke test sent an unverified JSON body to `/predict`; it received 503,
not a fabricated prediction. The OpenAPI document lists the three routes and
does not claim a prediction request schema. Prediction remains unavailable
until the selected model, saved pipeline, metadata, and input schema exist.
This local scaffold is not production-hardened and should not be exposed
publicly.

## Offline Prediction Evaluation

Not performed. There is no selected model artifact to load and no justified
model choice to evaluate for serving. No actual-versus-predicted or residual
plots were generated.

## Actual Test Metrics

Unavailable. The Milestone 2 notes explicitly state that the newest two rows
were reserved and not evaluated. Test performance must not be inferred from
the validation metrics above.

## Figures Generated

No Milestone 3 serving-validation figures were generated. Existing Milestone 2
EDA figures remain under `reports/figures/`; they are not model-serving test
plots.

## Differences from Milestone 2 Results

No serving prediction was run, so there are no serving metrics to compare with
Milestone 2. The CSV holds four distinct validation results repeated three
times; none is a final-test result. Duplicate rows have not been deleted.

## Limitations

Milestone 3 model serving is blocked until Milestone 2 provides:

1. An adequately sized, authorized dataset and a documented prediction
   horizon.
2. A defensible model selection from comparable chronological validation
   results against the persistence baseline.
3. A one-time evaluation of the selected model and baseline on the untouched
   chronological test segment.
4. A saved fitted pipeline and metadata that identify the model, target and
   unit, exact request feature schema, preprocessing path, split boundaries,
   metrics, and relevant library versions.

After those prerequisites exist, implement and test the API against the
verified artifact and input contract. Do not retrain a model when the API
starts.
