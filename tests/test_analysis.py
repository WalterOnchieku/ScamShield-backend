
"""
File: test_analysis.py

Purpose:
Test how ScamShield combines model predictions with rule findings.
"""

from unittest.mock import Mock

import pytest

from scamshield.services.analysis import (
    analyze_message,
    assess_screening_level,
    build_recommendations,
)


def test_high_severity_finding_produces_high_screening_level():
    findings = [
        {
            "rule_id": "credential_request",
            "category": "credential_request",
            "severity": "high",
            "matched_text": "confirm your password",
            "explanation": "Possible credential request.",
        }
    ]

    level, reasons = assess_screening_level("ham", findings)

    assert level == "high"
    assert reasons


def test_spam_with_multiple_findings_produces_high_level():
    findings = [
        {
            "rule_id": "urgency_pressure",
            "category": "urgency",
            "severity": "medium",
            "matched_text": "act now",
            "explanation": "Urgent language.",
        },
        {
            "rule_id": "unsolicited_prize",
            "category": "prize_claim",
            "severity": "medium",
            "matched_text": "you have won",
            "explanation": "Prize claim.",
        },
    ]

    level, _ = assess_screening_level("spam", findings)

    assert level == "high"


def test_no_signals_produce_low_level():
    level, reasons = assess_screening_level("ham", [])

    assert level == "low"
    assert reasons


def test_prize_finding_generates_recommendation():
    findings = [
        {
            "rule_id": "unsolicited_prize",
            "category": "prize_claim",
            "severity": "medium",
            "matched_text": "you have won",
            "explanation": "Prize claim.",
        }
    ]

    recommendations = build_recommendations("ham", findings)

    assert any("Verify prize claims" in item for item in recommendations)
    assert any("definitive proof" in item for item in recommendations)


def test_analysis_combines_prediction_and_findings():
    """Use a mock model to test orchestration without loading the artifact."""
    model = Mock()

    model.predict.return_value = ["spam"]
    model.predict_proba.return_value = [[0.1, 0.9]]
    model.named_steps = {
        "classifier": Mock(classes_=["ham", "spam"]),
    }

    result = analyze_message(
        model,
        "Congratulations! You have won a prize. Claim your reward.",
    )

    assert result["predicted_label"] == "spam"
    assert result["spam_probability"] == pytest.approx(0.9)
    assert result["risk_level"] == "medium"
    assert result["findings"]
    assert result["recommendations"]
    assert result["disclaimer"]


@pytest.mark.parametrize("message", ["", "  ", "\n\t"])
def test_analysis_rejects_blank_messages(message):
    model = Mock()

    with pytest.raises(ValueError, match="must not be empty"):
        analyze_message(model, message)
