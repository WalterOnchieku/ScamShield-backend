
"""
File: prediction.py

Purpose:
Load the trained ScamShield model and run message predictions.

The model is loaded by the application lifecycle and passed into
this service, rather than being loaded for every prediction.
"""

from pathlib import Path
from typing import Any

import joblib

# Resolve the model path from this file's location.
BACKEND_ROOT = Path(__file__).resolve().parents[3]
MODEL_PATH = BACKEND_ROOT / "models" / "scamshield_baseline.joblib"

DISCLAIMER = (
    "This result is an automated screening signal, not proof of fraud. "
    "The model was trained on general SMS ham/spam data and has not "
    "been validated for all Kenyan scam patterns."
)


def load_prediction_model() -> Any:
    """Load the trusted, locally stored model artifact."""
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"Trained model not found at {MODEL_PATH}. "
            "Copy scamshield_baseline.joblib into the backend/models "
            "directory before starting the API."
        )

    # Only load model artifacts from sources you trust.
    return joblib.load(MODEL_PATH)


def predict_message(model: Any, message: str) -> dict[str, Any]:
    """Predict a message label and return its estimated class scores."""
    cleaned_message = message.strip()

    if not cleaned_message:
        raise ValueError("Message must not be empty or whitespace only.")

    predicted_label = str(model.predict([cleaned_message])[0])
    probabilities = model.predict_proba([cleaned_message])[0]

    # Read class names from the fitted classifier instead of assuming
    # the order of predict_proba() scores.
    classifier = model.named_steps["classifier"]
    class_scores = dict(zip(classifier.classes_, probabilities))

    spam_probability = float(class_scores["spam"])
    ham_probability = float(class_scores["ham"])

    screening_result = (
        "potentially_suspicious"
        if predicted_label == "spam"
        else "no_spam_pattern_detected"
    )

    return {
        "predicted_label": predicted_label,
        "ham_probability": ham_probability,
        "spam_probability": spam_probability,
        "screening_result": screening_result,
        "disclaimer": DISCLAIMER,
    }
