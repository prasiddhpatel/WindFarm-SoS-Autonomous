"""End-to-end mission orchestration smoke test.

Verifies the full logical pipeline without a running ROS or Gazebo stack:
  1. MRTA allocates tasks to robots
  2. Digital twin computes RUL and EVOC dispatch decision
  3. Perception runner produces an InferenceResult
  4. Temporal fusion accumulates observations
  5. Backend API endpoints respond correctly (via TestClient + mocks)
  6. Integration validator module checks all pass
"""
import sys, os, pytest
import numpy as np

sys.path.insert(0, 'sos_orchestrator')
sys.path.insert(0, 'ros2_ws/src/drone_perception')


# ── 1. MRTA ─────────────────────────────────────────────────────────────────
def test_mrta_hungarian_e2e():
    from mrta.hungarian import Robot, Task, hungarian_allocate
    robots = [
        Robot('uav_1', {'triage', 'rgb_scan'}, 1000),
        Robot('ugv_1', {'nde', 'crawler_deploy'}, 2000),
    ]
    tasks = [
        Task('t_triage_01', 'triage', priority=9.0, duration=3.0, required_capability='triage'),
        Task('t_nde_01',    'nde',    priority=7.0, duration=5.0, required_capability='nde'),
    ]
    result = hungarian_allocate(robots, tasks)
    assigned = {r['task_id']: r['robot_id'] for r in result}
    assert assigned['t_triage_01'] == 'uav_1'
    assert assigned['t_nde_01']    == 'ugv_1'


def test_mrta_auction_e2e():
    from mrta.auction import auction_allocate
    utilities = {
        'uav_1': {'inspect_blade_A': 8.5, 'inspect_blade_B': 3.0},
        'ugv_1': {'inspect_blade_A': 2.0, 'inspect_blade_B': 9.0},
    }
    result = auction_allocate(utilities)
    assigned = {r['task_id']: r['robot_id'] for r in result}
    assert assigned['inspect_blade_A'] == 'uav_1'
    assert assigned['inspect_blade_B'] == 'ugv_1'


# ── 2. Digital twin ───────────────────────────────────────────────────────
def test_rul_e2e():
    from digital_twin.paris_rul import ParisLawParameters, rul_days
    p = ParisLawParameters(C=6.9e-12, m=3.0, Y=1.12,
                           delta_sigma=50e6, k_ic=25e6, sigma_max=100e6)
    r = rul_days(0.001, p, 1e5)
    assert r.rul_days > 0
    assert r.rul_cycles > 0
    assert r.crack_critical_m > 0.001


def test_evoc_dispatch_e2e():
    from digital_twin.evoc import EVOCInputs, evoc_score, should_dispatch_contact_scan
    inp = EVOCInputs(severity_variance=0.12, ut_variance=0.03,
                     decision_risk_before=0.85, decision_risk_after=0.25,
                     contact_scan_cost=0.08, lambda_cost=1.0)
    score = evoc_score(inp)
    assert score > 0
    assert should_dispatch_contact_scan(inp) is True


def test_evoc_no_dispatch_e2e():
    from digital_twin.evoc import EVOCInputs, should_dispatch_contact_scan
    inp = EVOCInputs(severity_variance=0.02, ut_variance=0.01,
                     decision_risk_before=0.15, decision_risk_after=0.14,
                     contact_scan_cost=3.0, lambda_cost=1.0)
    assert should_dispatch_contact_scan(inp) is False


# ── 3. Perception runner ──────────────────────────────────────────────────
def test_perception_runner_e2e():
    from drone_perception.model_runner import ModelRunner
    runner = ModelRunner('nonexistent.onnx')
    rgb     = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    thermal = np.random.randint(0, 255, (224, 224),    dtype=np.uint8)
    result  = runner.infer(rgb, thermal)
    assert 0 <= result.defect_class < 5
    assert 0.0 <= result.severity <= 1.0
    assert result.defect_label in [
        'no_defect','surface_erosion','crack','delamination','lightning_strike'
    ]


# ── 4. Temporal fusion ─────────────────────────────────────────────────────
def test_perception_fusion_pipeline_e2e():
    from drone_perception.model_runner import ModelRunner
    from drone_perception.fusion import SeverityTemporalFusion
    runner = ModelRunner('nonexistent.onnx')
    fusion = SeverityTemporalFusion(alpha=0.3)
    rgb     = np.full((64, 64, 3), 200, dtype=np.uint8)
    thermal = np.full((64, 64),    210, dtype=np.uint8)
    for i in range(8):
        r = runner.infer(rgb, thermal)
        fused = fusion.update('patch_0000', r.to_dict())
    assert 0.0 <= fused['severity'] <= 1.0
    assert fused['defect_class'] in range(5)


# ── 5. API via TestClient ───────────────────────────────────────────────────
def test_api_full_pipeline_e2e(client):
    # health
    r = client.get('/health')
    assert r.status_code == 200

    # RUL
    r = client.post('/rul/estimate', json={
        'C': 6.9e-12, 'm': 3.0, 'Y': 1.12,
        'delta_sigma': 50e6, 'k_ic': 25e6,
        'sigma_max': 100e6, 'a0': 0.001, 'cycles_per_day': 1e5,
    })
    assert r.status_code == 200
    body = r.json()
    assert body['rul_days'] > 0

    # EVOC dispatch
    r = client.post('/decision/evoc', json={
        'severity_variance': 0.1, 'ut_variance': 0.02,
        'decision_risk_before': 0.8, 'decision_risk_after': 0.3,
        'contact_scan_cost': 0.1, 'lambda_cost': 1.0,
    })
    assert r.status_code == 200
    assert r.json()['dispatch_contact_scan'] is True


# ── 6. Integration validator modules ───────────────────────────────────────
def test_integration_validator_modules_pass():
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, 'tests/integration_validation.py', '--no-live'],
        capture_output=True, text=True,
        env={**os.environ, 'PYTHONPATH': 'sos_orchestrator'}
    )
    assert result.returncode == 0, result.stdout + result.stderr
