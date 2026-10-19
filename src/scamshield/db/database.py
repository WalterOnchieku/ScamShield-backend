"""
File: database.py

Purpose:
Configure SQLAlchemy for the ScamShield KE PostgreSQL database.
"""

import os
from collections.abc import AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Get DATABASE_URL from environment or fall back to local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://scamshield:scamshield_dev_password@localhost:5433/scamshield",
)

# Ensure async URL for asyncpg if running FastAPI app
async_database_url = DATABASE_URL
if async_database_url.startswith("postgresql://"):
    async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

# Async engine for FastAPI app runtime
async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)

# Sync engine / session for migrations or fallback tasks if needed
sync_database_url = DATABASE_URL
if sync_database_url.startswith("postgresql+asyncpg://"):
    sync_database_url = sync_database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

engine = create_engine(
    sync_database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class inherited by all SQLAlchemy ORM models."""


async def get_db() -> AsyncGenerator[AsyncSession, None, None]:
    """
    Yield an async database session for FastAPI dependencies.
    """
    async with AsyncSessionLocal() as session:
        yield session