"""
Folyadéktulajdonságok – egyszerűsített vízmodell ipari szimulációhoz.
Minden hőmérséklet °C-ban, kimenetek SI-ben (kg/m^3, kJ/(kg*K), Pa*s, W/(m*K)).

Megjegyzések:
- Beadandóhoz bőven elég pontos; ha kell, később finomítható polinomokkal/adattáblával.
- A régiek (rho_water, cp_water) megmaradnak a kompatibilitás miatt.
"""
from __future__ import annotations
from typing import Dict

# ----------- belső konstansok -----------
_T_MIN = 0.0     # °C (folyékony tartomány alja modellezéshez)
_T_MAX = 100.0   # °C

def _clamp_T(T_c: float) -> float:
    return max(_T_MIN, min(_T_MAX, float(T_c)))

# ----------- sűrűség -----------
def rho_water(T_c: float) -> float:
    """
    Sűrűség [kg/m^3] ~ víz, 0–100 °C tartományban egyszerű, stabil közelítés.
    ρ(T) = 998.2 * (1 - 0.0003*(T-20)), 950 kg/m^3 alsó korláttal.
    """
    T = _clamp_T(T_c)
    return max(950.0, 998.2 * (1.0 - 0.0003 * (T - 20.0)))

# ----------- fajhő -----------
def cp_water(T_c: float) -> float:
    """
    Fajhő [kJ/(kg*K)] ~ víz. Itt konstans: 4.18 kJ/(kg*K).
    (Ha szeretnéd, később lehet enyhén T-függő.)
    """
    _ = _clamp_T(T_c)
    return 4.18

# ----------- viszkozitás -----------
def mu_water(T_c: float) -> float:
    """
    Dinamikai viszkozitás [Pa*s] ~ víz (egyszerű exponenciális közelítés).
    Tipikus értékek: 20°C ~ 1.0e-3 Pa*s; 60°C ~ 0.47e-3 Pa*s.

    Modell: μ(T) = μ_ref * exp( -k * (T - T_ref) )
      μ_ref = 1.002e-3 Pa*s  @ T_ref = 20°C
      k ≈ 0.017  [1/°C]   (empirikus, beadandóhoz elegendő)
    """
    T = _clamp_T(T_c)
    mu_ref = 1.002e-3
    k = 0.017
    return mu_ref * (2.718281828 ** (-k * (T - 20.0)))

# ----------- hővezetés -----------
def k_water(T_c: float) -> float:
    """
    Hővezetési tényező [W/(m*K)] ~ víz.
    Egyszerű lineáris közelítés 0–100°C között (~0.561→0.677):
      k(T) = 0.561 + 0.00116 * T
    """
    T = _clamp_T(T_c)
    return 0.561 + 0.00116 * T

# ----------- térfogati hőtágulási együttható -----------
def beta_water(T_c: float) -> float:
    """
    Térfogati hőtágulási együttható β [1/K] ~ víz (nagyságrendi becslés).
    20–80°C: ~ 2.1e-4 … 4.0e-4 1/K. Itt enyhén növekvő lineáris:
      β(T) = 1.8e-4 + 3.0e-6 * (T-20)
    """
    T = _clamp_T(T_c)
    return 1.8e-4 + 3.0e-6 * (T - 20.0)

# ----------- segéd: összefoglaló -----------
def water_props(T_c: float) -> Dict[str, float]:
    """
    Összesített tulajdonságok dict-ben, UI/naplózáshoz kényelmes.
    Keys: rho_kgm3, cp_kJkgK, mu_Pas, k_WmK, beta_1K
    """
    return {
        "rho_kgm3": rho_water(T_c),
        "cp_kJkgK": cp_water(T_c),
        "mu_Pas":   mu_water(T_c),
        "k_WmK":    k_water(T_c),
        "beta_1K":  beta_water(T_c),
    }

# ----------- egység-segédek (kényelmi) -----------
def lps_to_m3h(lps: float) -> float:
    """Liter/s → m^3/h."""
    return float(lps) * 3.6e-3

def m3h_to_lps(m3h: float) -> float:
    """m^3/h → Liter/s."""
    return float(m3h) / 3.6e-3
