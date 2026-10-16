
"""
File: test_prediction.py

Purpose:
Test the ScamShield prediction endpoint using the real baseline model.
"""

import pytest
from fastapi.testclient import TestClient

from scamshield.main import app


@pytest.fixture(scope="module")
def client():
    """Start the application and load its model for this test module."""
    with TestClient(app) as test_client:
        yield test_client


def test_predict_ordinary_message(client):
    """An ordinary example should be classified as ham by the baseline."""
    response = client.post(
        "/predict",
        json={"message": "Hi, are we still meeting for lunch tomorrow?"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["predicted_label"] == "ham"
    assert body["screening_result"] == "no_spam_pattern_detected"
    assert 0.0 <= body["ham_probability"] <= 1.0
    assert 0.0 <= body["spam_probability"] <= 1.0
    assert (
        body["ham_probability"] + body["spam_probability"]
    ) == pytest.approx(1.0)
    assert body["disclaimer"]


def test_predict_suspicious_prize_message(client):
    """A prize-offer example should be flagged by the baseline."""
    response = client.post(
        "/predict",
        json={
            "message": (
                "Congratulations! You have won a free prize. "
                "Claim now by sending your details."
            )
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["predicted_label"] == "spam"
    assert body["screening_result"] == "potentially_suspicious"
    assert body["spam_probability"] > body["ham_probability"]


def test_predict_rejects_missing_message(client):
    """Requests without the required message field should be rejected."""
    response = client.post("/predict", json={})

    assert response.status_code == 422


def test_predict_rejects_empty_message(client):
    """An empty string should fail request validation."""
    response = client.post("/predict", json={"message": ""})

    assert response.status_code == 422


def test_predict_rejects_oversized_message(client):
    """Messages beyond the configured size limit should be rejected."""
    response = client.post(
        "/predict",
        json={"message": "x" * 5001},
    )

    assert response.status_code == 422


def test_predict_rejects_whitespace_only_message(client):
    """Whitespace-only messages should be rejected by the service."""
    response = client.post("/predict", json={"message": "   "})

    assert response.status_code == 422
