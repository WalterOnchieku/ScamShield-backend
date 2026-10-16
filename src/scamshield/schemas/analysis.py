
"""
File: analysis.py

Purpose:
Define validated response schemas for explainable ScamShield analysis.

The schemas separate the ML prediction from rule-based evidence and
the overall screening assessment.
"""

from typing import Literal

from pydantic import BaseModel, Field


class RuleFinding(BaseModel):
    """Represent one suspicious pattern detected in a message."""

    rule_id: str
    category: str
    severity: Literal["low", "medium", "high"]
    matched_text: str
    explanation: str


class AnalysisResponse(BaseModel):
    """Return a complete, explainable message-screening result."""

    predicted_label: Literal["ham", "spam"]

    ham_probability: float = Field(ge=0.0, le=1.0)
    spam_probability: float = Field(ge=0.0, le=1.0)

    risk_level: Literal["low", "medium", "high"]
    risk_reasons: list[str]

    findings: list[RuleFinding]
    recommendations: list[str]

    disclaimer: str
