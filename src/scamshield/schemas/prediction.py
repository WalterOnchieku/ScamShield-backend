
"""
File: prediction.py

Purpose:
Define request and response schemas for ScamShield predictions.
"""

from typing import Literal

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    """Validate a message submitted for screening."""

    message: str = Field(
        min_length=1,
        max_length=5000,
        description="The message to screen for SMS spam patterns.",
    )


class PredictionResponse(BaseModel):
    """Represent the model's prediction and estimated class scores."""

    predicted_label: Literal["ham", "spam"]

    ham_probability: float = Field(ge=0.0, le=1.0)
    spam_probability: float = Field(ge=0.0, le=1.0)

    screening_result: Literal[
        "no_spam_pattern_detected",
        "potentially_suspicious",
    ]

    disclaimer: str
