"""FastAPI routes for service health and model availability."""

import logging
from typing import Literal

from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

MODEL_BLOCKER = (
    "Prediction is unavailable until Milestone 2 selects a model and provides "
    "a fitted pipeline, metadata, and verified input schema."
)


class HealthResponse(BaseModel):
    """Liveness response; this does not imply model readiness."""

    status: Literal["ok"]


class ModelInfoResponse(BaseModel):
    """Safe model readiness information without internal artifact paths."""

    status: Literal["blocked"]
    prediction_available: Literal[False]
    reason: str


app = FastAPI(
    title="Energy Consumption Prediction API",
    version="0.1.0",
    description=(
        "Milestone 3 API scaffold. Liveness is available, but predictions "
        "remain disabled until a selected fitted model and verified input "
        "schema are available."
    ),
)


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Check service liveness",
    description="Returns success when the API process can respond.",
)
def health() -> HealthResponse:
    """Report process liveness independently from model readiness."""
    return HealthResponse(status="ok")


@app.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Check prediction model availability",
    description="Reports the current model-serving blocker without local paths.",
)
def model_info() -> ModelInfoResponse:
    """Report that no deployable model has been selected or packaged."""
    return ModelInfoResponse(
        status="blocked",
        prediction_available=False,
        reason=MODEL_BLOCKER,
    )


@app.post(
    "/predict",
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    summary="Predict energy consumption",
    description=(
        "Unavailable until a selected fitted model and its real request schema "
        "are provided. No request schema is accepted or inferred yet."
    ),
)
async def predict(_request: Request) -> None:
    """Refuse inference rather than inventing a model or input contract."""
    logger.warning("Prediction requested while no deployable model is available.")
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Prediction is unavailable because no deployable model is configured.",
    )
