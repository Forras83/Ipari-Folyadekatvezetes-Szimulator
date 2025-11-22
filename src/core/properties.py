from __future__ import annotations
from typing import Dict


_T_MIN = 0.0
_T_MAX = 100.0

def _clamp_T(T_c: float) -> float:
    return max(_T_MIN, min(_T_MAX, float(T_c)))


def rho_water(T_c: float) -> float:

    T = _clamp_T(T_c)
    return max(950.0, 998.2 * (1.0 - 0.0003 * (T - 20.0)))


def cp_water(T_c: float) -> float:

    _ = _clamp_T(T_c)
    return 4.18


def mu_water(T_c: float) -> float:

    T = _clamp_T(T_c)
    mu_ref = 1.002e-3
    k = 0.017
    return mu_ref * (2.718281828 ** (-k * (T - 20.0)))


def k_water(T_c: float) -> float:

    T = _clamp_T(T_c)
    return 0.561 + 0.00116 * T


def beta_water(T_c: float) -> float:

    T = _clamp_T(T_c)
    return 1.8e-4 + 3.0e-6 * (T - 20.0)


def water_props(T_c: float) -> Dict[str, float]:

    return {
        "rho_kgm3": rho_water(T_c),
        "cp_kJkgK": cp_water(T_c),
        "mu_Pas":   mu_water(T_c),
        "k_WmK":    k_water(T_c),
        "beta_1K":  beta_water(T_c),
    }


def lps_to_m3h(lps: float) -> float:

    return float(lps) * 3.6e-3

def m3h_to_lps(m3h: float) -> float:

    return float(m3h) / 3.6e-3
