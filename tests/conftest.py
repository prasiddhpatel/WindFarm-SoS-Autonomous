"""pytest fixtures — provides a mocked FastAPI TestClient.

Patching strategy
-----------------
We patch 'api.main.SessionLocal' (the name already bound in the main
module at import time) rather than 'db.session.SessionLocal'.
This is required because Python's import system caches the module-level
binding; patching the source module has no effect after the app is loaded.

We also override the FastAPI dependency `get_db` directly via
`app.dependency_overrides` so that no real database is ever contacted,
even if the patch is somehow missed.
"""
from __future__ import annotations
import os
import sys
import pytest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


def _make_mock_db():
    """Return a MagicMock that behaves like a SQLAlchemy Session."""
    def _mock_query(*args, **kwargs):
        q = MagicMock()
        q.all.return_value    = []
        q.limit.return_value  = q
        q.filter.return_value = q
        q.first.return_value  = None
        return q

    db = MagicMock()
    db.query.side_effect = _mock_query
    db.close             = MagicMock()
    db.__enter__         = lambda s: s
    db.__exit__          = MagicMock(return_value=False)
    return db


@pytest.fixture(scope='session')
def client():
    """FastAPI TestClient with database fully mocked — no live Postgres."""
    mock_db = _make_mock_db()

    # Import the app first (triggers db/session lazy init attempt)
    from api.main import app

    # Override FastAPI's dependency injection so get_db() never touches Postgres
    from api.main import get_db
    app.dependency_overrides[get_db] = lambda: mock_db

    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
