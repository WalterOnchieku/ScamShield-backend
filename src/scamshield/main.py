from fastapi import FastAPI

app = FastAPI(
    title="ScamShield API",
    description="API for screening potentially suspicious messages.",
    version="0.1.0",
)


@app.get("/", tags=["General"])
def read_root() -> dict[str, str]:
    """Return basic information about the API."""
    return {
        "name": "ScamShield API",
        "version": "0.1.0",
        "message": "Welcome to the ScamShield API.",
    }


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Report that the API process is responding."""
    return {"status": "ok"}
