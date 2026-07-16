"""pytest configuration — provides a mocked FastAPI TestClient.

Key fix: patch 'api.main.SessionLocal' (the name as imported into main.py)
rather than 'db.session.SessionLocal'. By the time the fixture runs the
app module has already bound its own reference to SessionLocal, so the
patch must target that binding directly.
"""
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


def _make_mock_session():
    """Return a MagicMock that behaves like a SQLAlchemy Session."""
    def mock_query(*args, **kwargs):
        q = MagicMock()
        q.all.return_value    = []
        q.limit.return_value  = q
        q.filter.return_value = q
        q.first.return_value  = None
        return q

    session = MagicMock()
    session.query.side_effect   = mock_query
    session.close               = MagicMock()
    session.__enter__           = lambda s: s
    session.__exit__            = MagicMock(return_value=False)
    return session


@pytest.fixture(scope='session')
def client():
    """FastAPI TestClient with DB fully mocked — no live Postgres needed."""
    mock_session = _make_mock_session()

    # Patch at the name as bound in api.main AFTER import
    with patch('api.main.SessionLocal', return_value=mock_session), \
         patch('db.session.SessionLocal', return_value=mock_session):
        from api.main import app
        from fastapi.testclient import TestClient
        with TestClient(app) as c:
            yield c
