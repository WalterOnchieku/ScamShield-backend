
"""
File: rule_engine.py

Purpose:
Detect interpretable suspicious-message patterns using predefined rules.

The rule engine complements the machine-learning classifier. It does not
prove that a message is fraudulent, and its findings must be interpreted
in context.
"""

import re
from typing import Any

# Each rule has a stable identifier, a category, a severity indicator,
# a regular expression, and a human-readable explanation.
#
# Keep patterns reasonably specific to reduce false positives.
RULES: tuple[dict[str, Any], ...] = (
    {
        "rule_id": "urgency_pressure",
        "category": "urgency",
        "severity": "medium",
        "pattern": (
            r"\b(?:act now|act immediately|urgent action required|"
            r"immediate action required|within \d+\s*(?:minutes?|hours?|days?)|"
            r"limited time offer|final warning|expires today)\b"
        ),
        "explanation": (
            "The message uses urgent or time-limited language that may "
            "pressure the recipient into acting quickly."
        ),
    },
    {
        "rule_id": "unsolicited_prize",
        "category": "prize_claim",
        "severity": "medium",
        "pattern": (
            r"\b(?:you have won|you.ve won|you are the winner|"
            r"you have been selected to win|claim your prize|"
            r"claim your reward|congratulations.{0,40}\b(?:winner|prize|reward))\b"
        ),
        "explanation": (
            "The message makes a prize or reward claim that should be "
            "verified independently before responding."
        ),
    },
    {
        "rule_id": "credential_request",
        "category": "credential_request",
        "severity": "high",
        "pattern": (
            r"\b(?:confirm|verify|update|provide|submit|enter|share)"
            r"\s+(?:your\s+)?(?:password|pin|passcode|"
            r"login details|bank details|one[- ]time password|otp)\b"
        ),
        "explanation": (
            "The message appears to request sensitive authentication "
            "or financial information."
        ),
    },
    {
        "rule_id": "advance_fee_request",
        "category": "payment_request",
        "severity": "high",
        "pattern": (
            r"\b(?:pay|send|deposit|transfer)\s+(?:a\s+)?"
            r"(?:processing|registration|activation|release|"
            r"delivery|clearance)\s+(?:fee|charge|payment)\b"
            r"|\bpay\s+(?:to\s+)?(?:claim|release|unlock)\s+"
            r"(?:your\s+)?(?:prize|reward|funds|package)\b"
        ),
        "explanation": (
            "The message links a payment to releasing a prize, benefit, "
            "or service. Verify the request through an official channel."
        ),
    },
    {
        "rule_id": "suspicious_url_pattern",
        "category": "suspicious_link",
        "severity": "medium",
        "pattern": (
            r"\bhttps?://(?:"
            r"bit\.ly|tinyurl\.com|t\.co|is\.gd|cutt\.ly|"
            r"rb\.gy|shorturl\.at|ow\.ly"
            r")(?:[/:\s?#]|$)"
            r"|https?://(?:\d{1,3}\.){3}\d{1,3}(?=[:/]\S|$)"
        ),
        "explanation": (
            "The message contains a known URL-shortening domain or a "
            "URL using an IP address. Inspect the destination carefully."
        ),
    },
    {
        "rule_id": "account_threat",
        "category": "impersonation_or_account_threat",
        "severity": "medium",
        "pattern": (
            r"\b(?:your\s+)?(?:account|bank account|"
            r"mobile money account|mpesa account)\s+"
            r"(?:will be|has been|is being)\s+"
            r"(?:suspended|blocked|locked|restricted|terminated)\b"
            r"|\b(?:verify|confirm|restore|reactivate)\s+"
            r"(?:your\s+)?(?:account|bank account|mpesa account)\s+"
            r"(?:immediately|now|to avoid suspension)\b"
        ),
        "explanation": (
            "The message threatens account access or urges account "
            "verification. Confirm such claims with the organization "
            "through a contact method you already trust."
        ),
    },
)


def analyze_message_rules(message: str) -> list[dict[str, str]]:
    """
    Scan a message and return all distinct rule findings.

    Args:
        message: The text to inspect.

    Returns:
        A list of findings. Each rule contributes at most one finding,
        containing the first matching phrase.

    Raises:
        ValueError: If the message is empty or whitespace-only.
    """
    if not message or not message.strip():
        raise ValueError("Message must not be empty or whitespace only.")

    findings: list[dict[str, str]] = []

    for rule in RULES:
        match = re.search(
            rule["pattern"],
            message,
            flags=re.IGNORECASE,
        )

        if match:
            findings.append(
                {
                    "rule_id": rule["rule_id"],
                    "category": rule["category"],
                    "severity": rule["severity"],
                    "matched_text": match.group(0),
                    "explanation": rule["explanation"],
                }
            )

    return findings
