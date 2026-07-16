import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


@pytest.fixture(scope='session')
def client():
    mock_session = MagicMock()
    mock_session.query.return_value.all.return_value = []
    mock_session.query.return_value.limit.return_value.all.return_value = []

    with patch('db.session.SessionLocal', return_value=mock_session):
        from api.main import app
        c = TestClient(app)
        yield c
