
"""
File: main.py

Purpose:
Create the ScamShield FastAPI application.

Endpoints:
- GET /: Basic API information.
- GET /health: Health check.
- POST /predict: Screen a message using the trained ML model.
"""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request

from scamshield.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)
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
    description="API for screening potentially suspicious messages.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/", tags=["General"])
def read_root() -> dict[str, str]:
    """Return basic information about the API."""
    return {
        "name": "ScamShield API",
        "version": "0.1.0",
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
    """Screen one message and return its predicted label and scores."""
    model = request.app.state.prediction_model

    try:
        return predict_message(model, payload.message)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
