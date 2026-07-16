import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'sos_orchestrator'))


def test_rul_normal():
    from digital_twin.paris_rul import ParisLawParameters, rul_days
    params = ParisLawParameters(C=6.9e-12, m=3.0, Y=1.12, delta_sigma=50e6, k_ic=25e6, sigma_max=100e6)
    result = rul_days(a0=0.001, params=params, cycles_per_day=1e5)
    assert result.rul_cycles > 0
    assert result.rul_days > 0
    assert result.crack_critical_m > result.crack_length_m


def test_rul_at_critical():
    from digital_twin.paris_rul import ParisLawParameters, rul_days
    params = ParisLawParameters(C=6.9e-12, m=3.0, Y=1.12, delta_sigma=50e6, k_ic=25e6, sigma_max=100e6)
    import math
    ac = (params.k_ic / (params.Y * params.sigma_max)) ** 2 / math.pi
    result = rul_days(a0=ac, params=params, cycles_per_day=1e5)
    assert result.rul_cycles == pytest.approx(0.0, abs=1e-3)


def test_rul_zero_cpd():
    from digital_twin.paris_rul import ParisLawParameters, rul_days
    import math
    params = ParisLawParameters(C=6.9e-12, m=3.0, Y=1.12, delta_sigma=50e6, k_ic=25e6, sigma_max=100e6)
    result = rul_days(a0=0.001, params=params, cycles_per_day=0)
    assert result.rul_days == math.inf


def test_evoc_positive():
    from digital_twin.evoc import EVOCInputs, evoc_score, should_dispatch_contact_scan
    inp = EVOCInputs(
        severity_variance=0.1,
        ut_variance=0.02,
        decision_risk_before=0.8,
        decision_risk_after=0.3,
        contact_scan_cost=0.1,
        lambda_cost=1.0,
    )
    assert evoc_score(inp) == pytest.approx(0.4, abs=1e-6)
    assert should_dispatch_contact_scan(inp)


def test_evoc_negative():
    from digital_twin.evoc import EVOCInputs, should_dispatch_contact_scan
    inp = EVOCInputs(
        severity_variance=0.05,
        ut_variance=0.01,
        decision_risk_before=0.2,
        decision_risk_after=0.19,
        contact_scan_cost=2.0,
        lambda_cost=1.0,
    )
    assert not should_dispatch_contact_scan(inp)
