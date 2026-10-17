
"""
File: database.py

Purpose:
Configure SQLAlchemy for the ScamShield KE PostgreSQL database.

The engine manages database connectivity, SessionLocal creates
individual database sessions, and Base is the parent class for
SQLAlchemy database models.
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Use an environment variable when configured; otherwise, use the
# local development database defined in docker-compose.yml.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://scamshield:scamshield_dev_password"
    "@localhost:5433/scamshield",
)

# pool_pre_ping checks stale connections before they are reused.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Each request or operation can obtain its own database session.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class inherited by all SQLAlchemy ORM models."""


def get_db() -> Generator[Session, None, None]:
    """
    Yield a database session and close it when the caller finishes.

    FastAPI will use this function as a dependency when we integrate
    database persistence into the endpoints.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
