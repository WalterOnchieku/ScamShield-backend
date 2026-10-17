
"""
File: history.py

Purpose:
Define API response schemas for saved ScamShield KE analyses.

These schemas convert database records into validated API responses
without exposing SQLAlchemy internals.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AnalysisHistoryItem(BaseModel):
    """Represent one saved analysis in a history response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    predicted_label: Literal["ham", "spam"]

    ham_probability: float = Field(ge=0.0, le=1.0)
    spam_probability: float = Field(ge=0.0, le=1.0)

    risk_level: Literal["low", "medium", "high"]
    risk_reasons: list[str]
    findings: list[dict]
    recommendations: list[str]

    created_at: datetime


class AnalysisHistoryResponse(BaseModel):
    """Represent a paginated list of saved analyses."""

    items: list[AnalysisHistoryItem]
    limit: int
    offset: int
