
"""
File: main.py

Purpose:
Configure the ScamShield KE FastAPI application.

Provides health checks, machine-learning predictions, explainable
message analysis, and persistent analysis-history endpoints.
"""

from contextlib import asynccontextmanager
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from sqlalchemy.orm import Session

from scamshield.db.database import get_db
from scamshield.repositories.analysis import (
    delete_analysis,
    get_analysis_by_id,
    list_analyses,
    save_analysis,
)
from scamshield.schemas.analysis import AnalysisResponse
from scamshield.schemas.history import (
    AnalysisHistoryItem,
    AnalysisHistoryResponse,
)
from scamshield.schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
)
from scamshield.services.analysis import analyze_message
from scamshield.services.prediction import (
    load_prediction_model,
    predict_message,
)

from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load the prediction model once when the application starts."""
    app.state.prediction_model = load_prediction_model()
    yield


app = FastAPI(
    title="ScamShield API",
    description=(
        "Screen suspicious messages using machine learning and "
        "explainable rules, with persistent analysis history."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://scamshield-frontend-ecru.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root() -> dict[str, str]:
    """Describe the API."""
    return {
        "name": "ScamShield API",
        "version": "0.3.0",
        "message": "Welcome to the ScamShield API.",
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Report application process health."""
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(
    payload: PredictionRequest,
    request: Request,
) -> dict:
    """Return a machine-learning prediction without saving history."""
    try:
        return predict_message(
            request.app.state.prediction_model,
            payload.message,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.post("/analyze", response_model=AnalysisResponse)
def analyze(
    payload: PredictionRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    """Analyze a message, save its result, and return the assessment."""
    try:
        result = analyze_message(
            request.app.state.prediction_model,
            payload.message,
        )

        # Persist only after analysis has completed successfully.
        save_analysis(
            db=db,
            message=payload.message.strip(),
            result=result,
        )

        return result

    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc


@app.get("/history", response_model=AnalysisHistoryResponse)
async def get_history(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    risk_level: Literal["low", "medium", "high"] | None = None,
) -> dict:
    """List saved analyses, with pagination and optional risk filtering."""
    # Await the async repository function
    records = await list_analyses(
        db=db,
        limit=limit,
        offset=offset,
        risk_level=risk_level,
    )

    return {
        "items": records,
        "limit": limit,
        "offset": offset,
    }


@app.get(
    "/history/{analysis_id}",
    response_model=AnalysisHistoryItem,
)
async def get_history_item(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
) -> AnalysisHistoryItem:
    """Return one saved analysis by its ID."""
    # Await the async repository function (e.g., using await db.get() inside)
    record = await get_analysis_by_id(db, analysis_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Analysis record not found.",
        )

    return AnalysisHistoryItem.model_validate(record)


@app.delete("/history/{analysis_id}")
async def remove_history_item(
    analysis_id: int,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete one saved analysis."""
    # Await the async repository function
    deleted = await delete_analysis(db, analysis_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Analysis record not found.",
        )

    return {"message": "Analysis record deleted."}
