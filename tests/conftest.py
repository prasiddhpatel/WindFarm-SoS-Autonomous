import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


def make_mock_query(rows=None):
    mock_q = MagicMock()
    mock_q.all.return_value = rows or []
    mock_q.limit.return_value = mock_q
    return mock_q


@pytest.fixture(scope='session')
def client():
    mock_session = MagicMock()
    mock_session.query.side_effect = lambda *a, **kw: make_mock_query()
    mock_session.__enter__ = lambda s: s
    mock_session.__exit__ = MagicMock(return_value=False)

    with patch('db.session.SessionLocal', return_value=mock_session):
        from api.main import app
        with TestClient(app) as c:
            yield c
