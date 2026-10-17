
"""
File: test_analysis_repository.py

Purpose:
Test saving, retrieving, filtering, and deleting analysis records
without requiring a running PostgreSQL database.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from scamshield.db.database import Base
from scamshield.repositories.analysis import (
    delete_analysis,
    get_analysis_by_id,
    list_analyses,
    save_analysis,
)


@pytest.fixture
def db_session():
    """Create an isolated in-memory SQLite database for one test."""
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=test_engine)

    with Session(test_engine) as session:
        yield session

    test_engine.dispose()


@pytest.fixture
def sample_result():
    """Provide a representative analysis-service response."""
    return {
        "predicted_label": "spam",
        "ham_probability": 0.15,
        "spam_probability": 0.85,
        "risk_level": "high",
        "risk_reasons": ["Credential request detected"],
        "findings": [
            {
                "rule_id": "credential_request",
                "category": "credential_request",
                "severity": "high",
                "matched_text": "confirm your password",
                "explanation": "The message requests account credentials.",
            }
        ],
        "recommendations": ["Do not share your password."],
        "disclaimer": "This is a screening signal, not proof of fraud.",
    }


def test_save_analysis_persists_record(db_session, sample_result):
    """A saved analysis receives an ID and preserves its fields."""
    record = save_analysis(
        db_session,
        "Please confirm your password.",
        sample_result,
    )

    assert record.id is not None
    assert record.message == "Please confirm your password."
    assert record.predicted_label == "spam"
    assert record.risk_level == "high"
    assert record.findings[0]["rule_id"] == "credential_request"
    assert record.recommendations == ["Do not share your password."]
    assert record.created_at is not None


def test_get_analysis_by_id_returns_record(db_session, sample_result):
    """An existing analysis can be retrieved by its ID."""
    saved = save_analysis(db_session, "Suspicious message", sample_result)

    retrieved = get_analysis_by_id(db_session, saved.id)

    assert retrieved is not None
    assert retrieved.id == saved.id
    assert retrieved.message == "Suspicious message"


def test_get_analysis_by_id_returns_none_for_missing_id(db_session):
    """A nonexistent ID returns None instead of raising an error."""
    assert get_analysis_by_id(db_session, 9999) is None


def test_list_analyses_filters_by_risk_level(db_session, sample_result):
    """The optional risk-level filter limits returned records."""
    save_analysis(db_session, "High risk message", sample_result)

    low_risk_result = {
        **sample_result,
        "predicted_label": "ham",
        "risk_level": "low",
        "risk_reasons": [],
        "findings": [],
    }
    save_analysis(db_session, "Ordinary message", low_risk_result)

    records = list_analyses(db_session, risk_level="high")

    assert len(records) == 1
    assert records[0].message == "High risk message"


def test_list_analyses_supports_pagination(db_session, sample_result):
    """Limit and offset allow clients to request history in pages."""
    for index in range(3):
        save_analysis(
            db_session,
            f"Message {index}",
            sample_result,
        )

    records = list_analyses(db_session, limit=2, offset=1)

    assert len(records) == 2


def test_delete_analysis_removes_existing_record(
    db_session,
    sample_result,
):
    """Deleting an existing record removes it from the database."""
    saved = save_analysis(db_session, "Delete this message", sample_result)

    assert delete_analysis(db_session, saved.id) is True
    assert get_analysis_by_id(db_session, saved.id) is None


def test_delete_analysis_returns_false_for_missing_id(db_session):
    """Deleting a nonexistent record reports that nothing was deleted."""
    assert delete_analysis(db_session, 9999) is False
