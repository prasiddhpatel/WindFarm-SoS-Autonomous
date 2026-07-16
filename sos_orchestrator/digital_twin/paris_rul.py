from dataclasses import dataclass
import math


@dataclass
class ParisLawParameters:
    C: float
    m: float
    Y: float
    delta_sigma: float
    k_ic: float
    sigma_max: float


@dataclass
class RULResult:
    crack_length_m: float
    crack_critical_m: float
    rul_cycles: float
    rul_days: float


def critical_crack_length(k_ic: float, Y: float, sigma_max: float) -> float:
    return (k_ic / (Y * sigma_max)) ** 2 / math.pi


def rul_cycles(a0: float, params: ParisLawParameters) -> float:
    ac = critical_crack_length(params.k_ic, params.Y, params.sigma_max)
    if a0 >= ac:
        return 0.0
    exp = 1.0 - params.m / 2.0
    denom = params.C * (params.Y * params.delta_sigma * math.sqrt(math.pi)) ** params.m
    if abs(exp) < 1e-9:
        return math.log(ac / a0) / denom
    return (ac ** exp - a0 ** exp) / (denom * exp)


def rul_days(a0: float, params: ParisLawParameters, cycles_per_day: float) -> RULResult:
    ac = critical_crack_length(params.k_ic, params.Y, params.sigma_max)
    n = rul_cycles(a0, params)
    return RULResult(
        crack_length_m=a0,
        crack_critical_m=ac,
        rul_cycles=n,
        rul_days=n / cycles_per_day if cycles_per_day > 0 else float("inf"),
    )
