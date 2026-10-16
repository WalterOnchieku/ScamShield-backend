
"""
File: test_analysis_api.py

Purpose:
Test the public /analyze endpoint and its response contract.
"""

from fastapi.testclient import TestClient

from scamshield.main import app


def test_analyze_returns_findings_and_recommendations():
    """A suspicious prize message should produce an explainable result."""
    with TestClient(app) as client:
        response = client.post(
            "/analyze",
            json={
                "message": (
                    "Congratulations! You have won a prize. "
                    "Claim your reward."
                )
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["predicted_label"] == "spam"
    assert result["risk_level"] in {"medium", "high"}
    assert result["findings"]
    assert result["recommendations"]
    assert result["disclaimer"]

    assert any(
        finding["rule_id"] == "unsolicited_prize"
        for finding in result["findings"]
    )


def test_analyze_detects_high_severity_credential_request():
    """A credential request should trigger a high screening level."""
    with TestClient(app) as client:
        response = client.post(
            "/analyze",
            json={
                "message": "Confirm your password to restore access."
            },
        )

    assert response.status_code == 200

    result = response.json()

    assert result["risk_level"] == "high"
    assert any(
        finding["category"] == "credential_request"
        for finding in result["findings"]
    )


def test_analyze_rejects_missing_message():
    """The request must include the required message field."""
    with TestClient(app) as client:
        response = client.post("/analyze", json={})

    assert response.status_code == 422


def test_analyze_rejects_oversized_message():
    """Messages over the configured limit should be rejected."""
    with TestClient(app) as client:
        response = client.post(
            "/analyze",
            json={"message": "x" * 5001},
        )

    assert response.status_code == 422


def test_analyze_response_has_expected_fields():
    """The endpoint should follow the documented response schema."""
    with TestClient(app) as client:
        response = client.post(
            "/analyze",
            json={"message": "Hi, are we still meeting for lunch?"},
        )

    assert response.status_code == 200

    result = response.json()

    assert {
        "predicted_label",
        "ham_probability",
        "spam_probability",
        "risk_level",
        "risk_reasons",
        "findings",
        "recommendations",
        "disclaimer",
    }.issubset(result.keys())
