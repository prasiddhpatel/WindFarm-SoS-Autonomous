"""Database session factory — engine is created lazily so tests that mock
the DB do not require a live PostgreSQL connection at import time."""
from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings

_engine = None
_SessionLocal = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            future=True,
            pool_pre_ping=True,
        )
    return _engine


def SessionLocal() -> Session:  # type: ignore[override]
    """Return a new SQLAlchemy Session (lazy engine creation)."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=_get_engine(),
            autoflush=False,
            autocommit=False,
            future=True,
        )
    return _SessionLocal()
