import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


def test_api_health(client):
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json()['status'] == 'ok'


def test_rul_endpoint(client):
    payload = {
        'C': 6.9e-12, 'm': 3.0, 'Y': 1.12,
        'delta_sigma': 50e6, 'k_ic': 25e6,
        'sigma_max': 100e6, 'a0': 0.001,
        'cycles_per_day': 1e5,
    }
    resp = client.post('/rul/estimate', json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert 'rul_days' in body
    assert body['rul_cycles'] > 0


def test_evoc_endpoint(client):
    payload = {
        'severity_variance': 0.1,
        'ut_variance': 0.02,
        'decision_risk_before': 0.8,
        'decision_risk_after': 0.3,
        'contact_scan_cost': 0.1,
        'lambda_cost': 1.0,
    }
    resp = client.post('/decision/evoc', json=payload)
    assert resp.status_code == 200
    body = resp.json()
    assert 'evoc' in body
    assert body['dispatch_contact_scan'] is True


def test_turbines_empty(client):
    resp = client.get('/turbines')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_tasks_empty(client):
    resp = client.get('/tasks')
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
