
"""
File: test_analysis_history_api.py

Purpose:
Test ScamShield KE analysis-history API endpoints using an
isolated in-memory SQLite database.

These tests do not modify the development PostgreSQL database.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from scamshield.db import models  # noqa: F401
from scamshield.db.database import Base, get_db
from scamshield.main import app


@pytest.fixture
def client():
    """Provide an API client connected to an isolated test database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    def override_get_db():
        """Provide a database session for one API request."""
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def create_analysis(client: TestClient, message: str) -> dict:
    """Create an analysis through the public API."""
    response = client.post(
        "/analyze",
        json={"message": message},
    )

    assert response.status_code == 200
    return response.json()


def test_analyze_saves_record_to_history(client: TestClient):
    """A successful analysis should appear in saved history."""
    message = (
        "Congratulations! You have won a free prize. "
        "Call now to claim your reward."
    )

    result = create_analysis(client, message)

    response = client.get("/history")

    assert response.status_code == 200

    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["message"] == message
    assert body["items"][0]["predicted_label"] == result["predicted_label"]
    assert body["items"][0]["risk_level"] == result["risk_level"]
    assert body["items"][0]["id"] > 0
    assert "created_at" in body["items"][0]


def test_history_supports_pagination(client: TestClient):
    """Limit and offset should return separate pages."""
    create_analysis(client, "Hello, are we still meeting for lunch?")
    create_analysis(client, "Congratulations! Claim your free prize now!")

    first_page = client.get("/history?limit=1&offset=0")
    second_page = client.get("/history?limit=1&offset=1")

    assert first_page.status_code == 200
    assert second_page.status_code == 200

    first_body = first_page.json()
    second_body = second_page.json()

    assert len(first_body["items"]) == 1
    assert len(second_body["items"]) == 1
    assert first_body["limit"] == 1
    assert first_body["offset"] == 0
    assert second_body["offset"] == 1
    assert first_body["items"][0]["id"] != second_body["items"][0]["id"]


def test_history_can_filter_by_risk_level(client: TestClient):
    """The risk-level filter should return only matching records."""
    result = create_analysis(
        client,
        "Congratulations! You have won a free prize. Call now!",
    )

    risk_level = result["risk_level"]
    response = client.get(f"/history?risk_level={risk_level}")

    assert response.status_code == 200
    assert response.json()["items"]
    assert all(
        item["risk_level"] == risk_level
        for item in response.json()["items"]
    )


def test_history_rejects_invalid_query_parameters(client: TestClient):
    """Invalid pagination and risk filters should return HTTP 422."""
    assert client.get("/history?limit=0").status_code == 422
    assert client.get("/history?offset=-1").status_code == 422
    assert client.get("/history?risk_level=critical").status_code == 422


def test_get_history_item_returns_saved_record(client: TestClient):
    """A saved analysis should be retrievable by its ID."""
    create_analysis(client, "Hello, see you tomorrow.")

    listing = client.get("/history")
    record_id = listing.json()["items"][0]["id"]

    response = client.get(f"/history/{record_id}")

    assert response.status_code == 200
    assert response.json()["id"] == record_id
    assert response.json()["message"] == "Hello, see you tomorrow."


def test_get_missing_history_item_returns_404(client: TestClient):
    """Unknown analysis IDs should return HTTP 404."""
    response = client.get("/history/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Analysis record not found."


def test_delete_history_item(client: TestClient):
    """Deleting a saved analysis should remove it from history."""
    create_analysis(client, "Hello, see you tomorrow.")

    listing = client.get("/history")
    record_id = listing.json()["items"][0]["id"]

    deletion = client.delete(f"/history/{record_id}")

    assert deletion.status_code == 200
    assert deletion.json()["message"] == "Analysis record deleted."

    retrieval = client.get(f"/history/{record_id}")
    assert retrieval.status_code == 404


def test_delete_missing_history_item_returns_404(client: TestClient):
    """Deleting an unknown analysis should return HTTP 404."""
    response = client.delete("/history/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Analysis record not found."
