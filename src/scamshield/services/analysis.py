
"""
File: analysis.py

Purpose:
Combine ML predictions and rule-based findings into an explainable
message-screening assessment.

The service coordinates existing components. It does not claim to
determine conclusively whether a message is fraudulent.
"""

from typing import Any

from scamshield.services.prediction import predict_message
from scamshield.services.rule_engine import analyze_message_rules


def assess_screening_level(
    predicted_label: str,
    findings: list[dict[str, str]],
) -> tuple[str, list[str]]:
    """
    Assign a screening-priority level using transparent rules.

    High:
        At least one high-severity finding, or a spam prediction
        accompanied by at least two rule findings.

    Medium:
        A spam prediction or at least one rule finding.

    Low:
        Neither the classifier nor the rule engine raised a signal.

    These levels describe screening concern, not the probability
    that a message is fraudulent.
    """
    risk_reasons: list[str] = []

    high_severity_findings = [
        finding
        for finding in findings
        if finding["severity"] == "high"
    ]

    if predicted_label == "spam":
        risk_reasons.append(
            "The ML classifier identified patterns associated with spam."
        )

    if high_severity_findings:
        risk_reasons.append(
            "One or more high-severity indicators were detected."
        )

    if len(findings) >= 2 and predicted_label == "spam":
        risk_reasons.append(
            "The classifier and multiple rule-based indicators raised concerns."
        )

    if high_severity_findings or (
        predicted_label == "spam" and len(findings) >= 2
    ):
        return "high", risk_reasons

    if predicted_label == "spam" or findings:
        if findings and predicted_label != "spam":
            risk_reasons.append(
                "The rule engine detected patterns that deserve closer inspection."
            )

        return "medium", risk_reasons

    risk_reasons.append(
        "Neither the classifier nor the configured rules raised a screening signal."
    )
    return "low", risk_reasons


def build_recommendations(
    predicted_label: str,
    findings: list[dict[str, str]],
) -> list[str]:
    """Generate practical precautions from the detected signals."""
    recommendations: list[str] = []

    categories = {finding["category"] for finding in findings}

    if "credential_request" in categories:
        recommendations.append(
            "Do not share passwords, PINs, or one-time codes through "
            "a message or an unverified link."
        )

    if "payment_request" in categories:
        recommendations.append(
            "Verify payment requests independently before sending money."
        )

    if "suspicious_link" in categories:
        recommendations.append(
            "Avoid opening the link until you have verified its destination."
        )

    if "prize_claim" in categories:
        recommendations.append(
            "Verify prize claims with the purported organization using "
            "an independently obtained contact method."
        )

    if "account_threat" in categories:
        recommendations.append(
            "Check account warnings through the organization's official "
            "app or a contact method you already trust."
        )

    if "urgency" in categories:
        recommendations.append(
            "Pause before acting on urgent demands and verify the request."
        )

    if predicted_label == "spam":
        recommendations.append(
            "Treat the message cautiously and verify its claims independently."
        )

    if not recommendations:
        recommendations.append(
            "No configured rule matched and the classifier did not flag "
            "the message. This does not guarantee that the message is safe."
        )

    recommendations.append(
        "Do not treat this automated assessment as definitive proof of fraud."
    )

    return recommendations


def analyze_message(model: Any, message: str) -> dict[str, Any]:
    """
    Combine ML prediction, rule findings, and screening guidance.

    Args:
        model: The already-loaded ScamShield ML pipeline.
        message: The message to analyze.

    Returns:
        A dictionary compatible with AnalysisResponse.

    Raises:
        ValueError: If the message is empty or whitespace-only.
    """
    cleaned_message = message.strip()

    if not cleaned_message:
        raise ValueError("Message must not be empty or whitespace only.")

    prediction = predict_message(model, cleaned_message)
    findings = analyze_message_rules(cleaned_message)

    risk_level, risk_reasons = assess_screening_level(
        predicted_label=prediction["predicted_label"],
        findings=findings,
    )

    recommendations = build_recommendations(
        predicted_label=prediction["predicted_label"],
        findings=findings,
    )

    return {
        "predicted_label": prediction["predicted_label"],
        "ham_probability": prediction["ham_probability"],
        "spam_probability": prediction["spam_probability"],
        "risk_level": risk_level,
        "risk_reasons": risk_reasons,
        "findings": findings,
        "recommendations": recommendations,
        "disclaimer": prediction["disclaimer"],
    }

