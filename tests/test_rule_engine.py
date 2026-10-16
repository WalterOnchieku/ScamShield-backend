
"""
File: test_rule_engine.py

Purpose:
Test ScamShield's rule-based message analysis independently of the
machine-learning prediction service.
"""

import pytest

from scamshield.services.rule_engine import analyze_message_rules


def test_detects_urgent_language():
    """Urgent phrases should trigger the urgency rule."""
    findings = analyze_message_rules(
        "URGENT ACTION REQUIRED: respond within 24 hours."
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "urgency_pressure" in rule_ids


def test_detects_prize_claim():
    """Unsolicited prize claims should trigger the prize rule."""
    findings = analyze_message_rules(
        "Congratulations! You have won a prize. Claim your reward."
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "unsolicited_prize" in rule_ids


def test_detects_credential_request():
    """Requests for passwords or PINs should trigger a finding."""
    findings = analyze_message_rules(
        "Please confirm your password to restore access."
    )

    credential_findings = [
        finding
        for finding in findings
        if finding["rule_id"] == "credential_request"
    ]

    assert len(credential_findings) == 1
    assert credential_findings[0]["severity"] == "high"


def test_detects_advance_fee_request():
    """A fee requested to release a prize should be flagged."""
    findings = analyze_message_rules(
        "Pay a processing fee to claim your prize."
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "advance_fee_request" in rule_ids


def test_detects_known_shortener():
    """Known URL-shortening domains should trigger a link finding."""
    findings = analyze_message_rules(
        "Check this offer: https://bit.ly/example"
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "suspicious_url_pattern" in rule_ids


def test_detects_account_threat():
    """Threats to suspend an account should trigger a finding."""
    findings = analyze_message_rules(
        "Your account will be suspended unless you verify it."
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "account_threat" in rule_ids


def test_returns_evidence_and_explanation():
    """Findings should include evidence useful to the API client."""
    findings = analyze_message_rules("Act now to claim your prize.")

    assert findings

    for finding in findings:
        assert finding["rule_id"]
        assert finding["category"]
        assert finding["severity"]
        assert finding["matched_text"]
        assert finding["explanation"]


def test_ordinary_message_has_no_findings():
    """A routine message should not trigger these specific patterns."""
    findings = analyze_message_rules(
        "Hi, are we still meeting for lunch tomorrow?"
    )

    assert findings == []


def test_legitimate_payment_message_is_not_automatically_flagged():
    """A normal payment reminder should not match the advance-fee rule."""
    findings = analyze_message_rules(
        "Your electricity bill is due tomorrow. Please pay your bill."
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "advance_fee_request" not in rule_ids


@pytest.mark.parametrize("message", ["", " ", "\n\t"])
def test_rejects_empty_or_whitespace_messages(message):
    """Empty messages should raise a clear validation error."""
    with pytest.raises(ValueError, match="must not be empty"):
        analyze_message_rules(message)
