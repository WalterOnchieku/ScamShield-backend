
"""
File: main.py

Purpose:
Create the ScamShield FastAPI application.

Endpoints:
- GET /: Basic API information.
- GET /health: Health check.
- POST /predict: Original ML prediction endpoint.
- POST /analyze: Explainable message analysis with risk indicators.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from scamshield.schemas.analysis import AnalysisResponse
from scamshield.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)
from scamshield.services.analysis import analyze_message
from scamshield.services.prediction import (
    load_prediction_model,
    predict_message,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the model once when the API starts and release it at shutdown."""
    app.state.prediction_model = load_prediction_model()
    yield
    app.state.prediction_model = None


app = FastAPI(
    title="ScamShield API",
    description=(
        "API for screening potentially suspicious messages using "
        "machine learning and explainable detection rules."
    ),
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/", tags=["General"])
def read_root() -> dict[str, str]:
    """Return basic information about the API."""
    return {
        "name": "ScamShield API",
        "version": "0.2.0",
        "message": "Welcome to the ScamShield API.",
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Report that the API process is responding."""
    return {"status": "ok"}


@app.post(
    "/predict",
    response_model=PredictionResponse,
    tags=["Prediction"],
)
def screen_message(
    payload: PredictionRequest,
    request: Request,
) -> dict[str, Any]:
    """Run the original ML-only prediction workflow."""
    model = request.app.state.prediction_model

    try:
        return predict_message(model, payload.message)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.post(
    "/analyze",
    response_model=AnalysisResponse,
    tags=["Analysis"],
)
def analyze_submitted_message(
    payload: PredictionRequest,
    request: Request,
) -> dict[str, Any]:
    """Return an explainable assessment of a submitted message."""
    model = request.app.state.prediction_model

    try:
        return analyze_message(model, payload.message)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
