from dataclasses import dataclass


@dataclass
class EVOCInputs:
    severity_variance: float
    ut_variance: float
    decision_risk_before: float
    decision_risk_after: float
    contact_scan_cost: float
    lambda_cost: float = 1.0


def evoc_score(inp: EVOCInputs) -> float:
    risk_reduction = inp.decision_risk_before - inp.decision_risk_after
    return risk_reduction - inp.lambda_cost * inp.contact_scan_cost


def should_dispatch_contact_scan(inp: EVOCInputs) -> bool:
    return evoc_score(inp) > 0.0
