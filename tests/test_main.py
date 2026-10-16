"""
File: test_main.py

Purpose:
Verify that the ScamShield KE API starts correctly and
returns the expected responses from its basic endpoints.
"""

from fastapi.testclient import TestClient

from scamshield.main import app

client = TestClient(app)


def test_root_endpoint():
    """The root endpoint should return API information."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "ScamShield API"
    assert response.json()["version"] == "0.1.0"


def test_health_endpoint():
    """The health endpoint should report a healthy API process."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_documentation_is_available():
    """FastAPI should expose its OpenAPI schema."""
    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "ScamShield API"
