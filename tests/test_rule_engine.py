
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


@pytest.mark.parametrize(
    ("message", "expected_match"),
    [
        (
            "Send your M-Pesa PIN to claim your reward.",
            "Send your M-Pesa PIN",
        ),
        (
            "Please share your one-time password.",
            "share your one-time password",
        ),
    ],
)
def test_detects_sensitive_credential_requests(message, expected_match):
    """Credential rules should detect common PIN and OTP wording."""
    findings = analyze_message_rules(message)

    credential_findings = [
        finding
        for finding in findings
        if finding["rule_id"] == "credential_request"
    ]

    assert len(credential_findings) == 1
    assert credential_findings[0]["severity"] == "high"
    assert credential_findings[0]["matched_text"].lower() == (
        expected_match.lower()
    )


@pytest.mark.parametrize(
    "message",
    [
        "Pay KSh 500 processing fee to 0712345678 to claim your prize.",
        "Send KES 1,000 registration fee to 0712345678.",
    ],
)
def test_detects_advance_fee_with_amount_and_recipient(message):
    """Advance-fee rules should allow amounts and recipient phone numbers."""
    findings = analyze_message_rules(message)

    fee_findings = [
        finding
        for finding in findings
        if finding["rule_id"] == "advance_fee_request"
    ]

    assert len(fee_findings) == 1
    assert fee_findings[0]["severity"] == "high"


def test_detects_ordinary_http_url():
    """Unencrypted HTTP links should trigger a caution finding."""
    findings = analyze_message_rules(
        "Claim your reward at http://claim-reward.example.com now."
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "suspicious_url_pattern" in rule_ids


def test_http_rule_does_not_flag_ordinary_https_domain_alone():
    """An ordinary HTTPS domain should not match the HTTP-specific rule."""
    findings = analyze_message_rules(
        "Visit https://example.com to read our public information page."
    )

    rule_ids = {finding["rule_id"] for finding in findings}

    assert "suspicious_url_pattern" not in rule_ids
