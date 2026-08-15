"""Async SQLAlchemy engine/session setup.

Reads the database URL from the ``DATABASE_URL`` environment variable at
call time (not import time), so this module can be imported safely without
a reachable database. ``Base`` is the shared declarative base for future
ORM models; Alembic's env is wired to it (see ``alembic/env.py``) so future
models can autogenerate migrations.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL_ENV_VAR = "DATABASE_URL"


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


def get_database_url() -> str:
    """Return the configured database URL.

    Raises:
        RuntimeError: if ``DATABASE_URL`` is not set. Credentials must never
            be hardcoded; this is read from the environment only.
    """
    database_url = os.environ.get(DATABASE_URL_ENV_VAR)
    if not database_url:
        raise RuntimeError(
            f"{DATABASE_URL_ENV_VAR} environment variable is not set. "
            "Example: postgresql+asyncpg://user:password@localhost:5432/market_intel"
        )
    return database_url


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Return a process-wide async engine, created lazily on first use."""
    return create_async_engine(get_database_url())


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return a process-wide async session factory, created lazily."""
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding an ``AsyncSession`` for a single request."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
