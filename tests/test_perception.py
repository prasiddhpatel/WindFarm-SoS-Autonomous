import os, sys, pytest
sys.path.insert(0, 'ros2_ws/src/drone_perception')

from drone_perception.fusion import SeverityTemporalFusion


def test_first_observation_passthrough():
    f = SeverityTemporalFusion(alpha=0.5)
    obs = {'severity': 0.6, 'defect_class': 2, 'uncertainty_aleatoric': 0.1}
    out = f.update('p0', obs)
    assert out['severity'] == pytest.approx(0.6)
    assert out['defect_class'] == 2


def test_ema_converges():
    f = SeverityTemporalFusion(alpha=0.5)
    f.update('p0', {'severity': 0.0, 'defect_class': 0, 'uncertainty_aleatoric': 0.0})
    for _ in range(20):
        f.update('p0', {'severity': 1.0, 'defect_class': 3, 'uncertainty_aleatoric': 0.05})
    out = f.get('p0')
    assert out['severity'] > 0.99


def test_severity_below_threshold_no_class_escalation():
    f = SeverityTemporalFusion(alpha=0.9)
    f.update('p1', {'severity': 0.1, 'defect_class': 0, 'uncertainty_aleatoric': 0.0})
    out = f.update('p1', {'severity': 0.1, 'defect_class': 1, 'uncertainty_aleatoric': 0.0})
    assert out['defect_class'] == 0


def test_severity_above_threshold_escalates_class():
    f = SeverityTemporalFusion(alpha=0.9)
    f.update('p2', {'severity': 0.8, 'defect_class': 1, 'uncertainty_aleatoric': 0.0})
    out = f.update('p2', {'severity': 0.8, 'defect_class': 3, 'uncertainty_aleatoric': 0.0})
    assert out['defect_class'] == 3


def test_reset_single_patch():
    f = SeverityTemporalFusion(alpha=0.5)
    f.update('p3', {'severity': 0.7, 'defect_class': 2, 'uncertainty_aleatoric': 0.1})
    f.reset('p3')
    assert f.get('p3') is None


def test_reset_all():
    f = SeverityTemporalFusion(alpha=0.5)
    for i in range(5):
        f.update(f'p{i}', {'severity': 0.5, 'defect_class': 1, 'uncertainty_aleatoric': 0.0})
    f.reset()
    assert f.all_patches() == {}


def test_invalid_alpha():
    with pytest.raises(ValueError):
        SeverityTemporalFusion(alpha=0.0)
    with pytest.raises(ValueError):
        SeverityTemporalFusion(alpha=1.5)
