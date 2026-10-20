"""
File: analysis.py

Purpose:
Provide database operations for saved ScamShield KE analyses.

This repository handles persistence and retrieval only. It does not
run the machine-learning model or decide whether a message is risky.
"""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from scamshield.db.models import AnalysisRecord


async def save_analysis(
    db: AsyncSession,
    message: str,
    result: dict[str, Any],
) -> AnalysisRecord:
    """Save an analysis result and return the persisted record."""
    record = AnalysisRecord(
        message=message,
        predicted_label=result["predicted_label"],
        ham_probability=result["ham_probability"],
        spam_probability=result["spam_probability"],
        risk_level=result["risk_level"],
        risk_reasons=result["risk_reasons"],
        findings=result["findings"],
        recommendations=result["recommendations"],
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)

    return record


async def get_analysis_by_id(
    db: AsyncSession,
    analysis_id: int,
) -> AnalysisRecord | None:
    """Retrieve one saved analysis by its ID."""
    statement = select(AnalysisRecord).where(
        AnalysisRecord.id == analysis_id
    )

    # Await the async scalar execution
    return await db.scalar(statement)


async def list_analyses(
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    risk_level: str | None = None,
) -> list[AnalysisRecord]:
    """Return the newest analyses, optionally filtered by risk level."""
    statement = select(AnalysisRecord)

    if risk_level is not None:
        statement = statement.where(
            AnalysisRecord.risk_level == risk_level
        )

    statement = (
        statement
        .order_by(AnalysisRecord.created_at.desc(), AnalysisRecord.id.desc())
        .offset(offset)
        .limit(limit)
    )

    # Await the async scalars execution
    result = await db.scalars(statement)
    return list(result.all())


async def delete_analysis(
    db: AsyncSession,
    analysis_id: int,
) -> bool:
    """Delete one analysis; return False when its ID does not exist."""
    # Await the async get_analysis_by_id function
    record = await get_analysis_by_id(db, analysis_id)

    if record is None:
        return False

    await db.delete(record)
    await db.commit()

    return True