#!/usr/bin/env python3
"""
Standalone integration validator.
Module checks run always; live API checks require --base to be reachable.
Usage:
  # CI / no network:
  PYTHONPATH=sos_orchestrator python3 tests/integration_validation.py --no-live
  # Local full stack:
  PYTHONPATH=sos_orchestrator python3 tests/integration_validation.py --base http://localhost:8080
"""
import argparse, sys

try:
    import httpx
except ImportError:
    httpx = None

PASS = '\033[92mPASS\033[0m'
FAIL = '\033[91mFAIL\033[0m'
SKIP = '\033[93mSKIP\033[0m'


def check(label, cond, detail=''):
    tag = PASS if cond else FAIL
    print(f"  [{tag}] {label}" + (f' — {detail}' if detail else ''))
    return cond


def validate_modules() -> bool:
    ok = True
    sys.path.insert(0, 'sos_orchestrator')
    try:
        from mrta.hungarian import Robot, Task, hungarian_allocate
        robots = [Robot('r1', {'triage'}, 1000), Robot('r2', {'nde'}, 2000)]
        tasks  = [Task('t1', 'triage', 8.0, 2.0, 'triage'), Task('t2', 'nde', 9.0, 3.0, 'nde')]
        result = hungarian_allocate(robots, tasks)
        ok &= check('Hungarian allocation', len(result) == 2, str(result))
    except Exception as e:
        ok &= check('Hungarian allocation', False, str(e))

    try:
        from mrta.auction import auction_allocate
        utilities = {'r1': {'t1': 6.0, 't2': 2.0}, 'r2': {'t1': 1.0, 't2': 7.0}}
        result = auction_allocate(utilities)
        assigned = {r['task_id']: r['robot_id'] for r in result}
        ok &= check('Auction allocation', assigned.get('t1') == 'r1' and assigned.get('t2') == 'r2', str(assigned))
    except Exception as e:
        ok &= check('Auction allocation', False, str(e))

    try:
        from digital_twin.paris_rul import ParisLawParameters, rul_days
        p = ParisLawParameters(C=6.9e-12, m=3.0, Y=1.12, delta_sigma=50e6, k_ic=25e6, sigma_max=100e6)
        r = rul_days(0.001, p, 1e5)
        ok &= check('Paris RUL', r.rul_days > 0, f'days={r.rul_days:.1f}, cycles={r.rul_cycles:.0f}')
    except Exception as e:
        ok &= check('Paris RUL', False, str(e))

    try:
        from digital_twin.evoc import EVOCInputs, evoc_score, should_dispatch_contact_scan
        inp = EVOCInputs(severity_variance=0.1, ut_variance=0.02,
                         decision_risk_before=0.8, decision_risk_after=0.3,
                         contact_scan_cost=0.1, lambda_cost=1.0)
        score = evoc_score(inp)
        ok &= check('EVOC score', should_dispatch_contact_scan(inp), f'score={score:.4f}')
    except Exception as e:
        ok &= check('EVOC score', False, str(e))

    return ok


def validate_api(base: str) -> bool:
    if httpx is None:
        print(f'  [{SKIP}] httpx not installed — pip install httpx')
        return True
    ok = True
    try:
        r = httpx.get(f'{base}/health', timeout=5)
        ok &= check('/health', r.status_code == 200 and r.json().get('status') == 'ok')

        r = httpx.get(f'{base}/turbines', timeout=5)
        ok &= check('/turbines', r.status_code == 200, f'{len(r.json())} rows')

        r = httpx.get(f'{base}/patches', timeout=5)
        ok &= check('/patches', r.status_code == 200, f'{len(r.json())} rows')

        r = httpx.post(f'{base}/rul/estimate', json={
            'C': 6.9e-12, 'm': 3.0, 'Y': 1.12,
            'delta_sigma': 50e6, 'k_ic': 25e6,
            'sigma_max': 100e6, 'a0': 0.001, 'cycles_per_day': 1e5,
        }, timeout=5)
        b = r.json()
        ok &= check('/rul/estimate', r.status_code == 200 and b.get('rul_cycles', 0) > 0,
                    f"rul_days={b.get('rul_days','?')}" if r.status_code == 200 else str(r.status_code))

        r = httpx.post(f'{base}/decision/evoc', json={
            'severity_variance': 0.1, 'ut_variance': 0.02,
            'decision_risk_before': 0.8, 'decision_risk_after': 0.3,
            'contact_scan_cost': 0.1, 'lambda_cost': 1.0,
        }, timeout=5)
        b = r.json()
        ok &= check('/decision/evoc dispatch', r.status_code == 200 and b.get('dispatch_contact_scan') is True,
                    f"evoc={b.get('evoc','?')}" if r.status_code == 200 else str(r.status_code))
    except Exception as e:
        print(f'  [{FAIL}] API unreachable: {e}')
        ok = False
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--base', default='http://localhost:8080')
    ap.add_argument('--no-live', action='store_true', help='Skip live API checks')
    args = ap.parse_args()

    print('=== WindFarm SoS Integration Validation ===')

    print('\n--- Module checks ---')
    mod_ok = validate_modules()

    if not args.no_live:
        print('\n--- Live API checks ---')
        api_ok = validate_api(args.base)
    else:
        print('\n--- Live API checks skipped (--no-live) ---')
        api_ok = True

    passed = mod_ok and api_ok
    print(f'\n=== {"ALL PASSED" if passed else "FAILURES DETECTED"} ===')
    sys.exit(0 if passed else 1)


if __name__ == '__main__':
    main()
