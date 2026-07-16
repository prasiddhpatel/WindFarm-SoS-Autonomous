import os, sys, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


def test_health(client):
    r = client.get('/health')
    assert r.status_code == 200
    assert r.json() == {'status': 'ok'}


def test_turbines(client):
    r = client.get('/turbines')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_patches(client):
    r = client.get('/patches')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_tasks(client):
    r = client.get('/tasks')
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_rul_estimate(client):
    r = client.post('/rul/estimate', json={
        'C': 6.9e-12, 'm': 3.0, 'Y': 1.12,
        'delta_sigma': 50e6, 'k_ic': 25e6,
        'sigma_max': 100e6, 'a0': 0.001,
        'cycles_per_day': 1e5
    })
    assert r.status_code == 200
    d = r.json()
    assert d['rul_cycles'] > 0
    assert d['rul_days'] > 0
    assert d['crack_critical_m'] > d['crack_length_m']


def test_evoc_dispatch(client):
    r = client.post('/decision/evoc', json={
        'severity_variance': 0.1, 'ut_variance': 0.02,
        'decision_risk_before': 0.8, 'decision_risk_after': 0.3,
        'contact_scan_cost': 0.1, 'lambda_cost': 1.0,
    })
    assert r.status_code == 200
    assert r.json()['dispatch_contact_scan'] is True


def test_evoc_no_dispatch(client):
    r = client.post('/decision/evoc', json={
        'severity_variance': 0.05, 'ut_variance': 0.01,
        'decision_risk_before': 0.2, 'decision_risk_after': 0.19,
        'contact_scan_cost': 2.0, 'lambda_cost': 1.0,
    })
    assert r.status_code == 200
    assert r.json()['dispatch_contact_scan'] is False


def test_rul_bad_request(client):
    r = client.post('/rul/estimate', json={})
    assert r.status_code in (422, 500)
