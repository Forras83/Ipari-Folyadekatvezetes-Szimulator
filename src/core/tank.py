from dataclasses import dataclass, field
from typing import Optional
from .properties import rho_water, cp_water

@dataclass
class Tank:

    capacity_l: float = 1000.0
    level_l: float = 0.0
    temperature_c: float = 25.0
    ua_kW_per_K: float = 0.005
    ambient_c: float = 20.0

    ll_pct: float = 20.0
    hh_pct: float = 80.0

    _eps: float = field(default=1e-9, repr=False)
    _t_min: float = field(default=-50.0, repr=False)
    _t_max: float = field(default=200.0, repr=False)


    def add(self, q_l: float, t_in_c: Optional[float] = None) -> None:
        q_l = max(0.0, float(q_l))
        if q_l <= 0.0:
            return

        v_old = self.level_l
        v_new = min(self.capacity_l, v_old + q_l)
        dv = max(0.0, v_new - v_old)

        if dv <= self._eps:
            return

        if t_in_c is None:
            self.level_l = v_new
            return

        if v_old <= self._eps:
            self.temperature_c = float(t_in_c)
            self.level_l = v_new
            self._clamp_temp()
            return

        self.temperature_c = (v_old * self.temperature_c + dv * float(t_in_c)) / (v_old + dv)
        self.level_l = v_new
        self._clamp_temp()

    def remove(self, q_l: float) -> float:
        take = min(self.level_l, max(0.0, float(q_l)))
        self.level_l -= take
        return take


    def thermal_losses(self, dt_s: float) -> None:
        if self.level_l <= self._eps or dt_s <= 0.0:
            return

        T = self.temperature_c
        if abs(T - self.ambient_c) <= 1e-9 or self.ua_kW_per_K <= 0.0:
            return

        UA_kJ_per_sK = float(self.ua_kW_per_K)
        dQ_kJ = UA_kJ_per_sK * (T - self.ambient_c) * float(dt_s)

        rho = self.density_kgm3
        V_m3 = self.level_l * 1e-3
        m_kg = rho * V_m3
        cp_kJ_per_kgK = cp_water(T)

        denom = m_kg * cp_kJ_per_kgK
        if denom > self._eps:
            dT = - dQ_kJ / denom
            self.temperature_c += dT
            self._clamp_temp()

    def add_heat(self, power_kW: float, dt_s: float) -> None:
        if self.level_l <= self._eps or dt_s <= 0.0 or abs(power_kW) <= 1e-12:
            return

        rho = self.density_kgm3
        V_m3 = self.level_l * 1e-3
        m_kg = rho * V_m3
        cp_kJ_per_kgK = cp_water(self.temperature_c)

        denom = m_kg * cp_kJ_per_kgK
        if denom > self._eps:
            dQ_kJ = float(power_kW) * float(dt_s)
            self.temperature_c += dQ_kJ / denom
            self._clamp_temp()


    @property
    def level_pct(self) -> float:
        return 0.0 if self.capacity_l <= 0 else 100.0 * self.level_l / self.capacity_l

    @property
    def alarm_ll(self) -> bool:
        return self.level_pct <= self.ll_pct

    @property
    def alarm_hh(self) -> bool:
        return self.level_pct >= self.hh_pct

    @property
    def density_kgm3(self) -> float:
        return rho_water(self.temperature_c)

    def set_alarms(self, ll_pct: float, hh_pct: float) -> None:
        self.ll_pct = float(ll_pct)
        self.hh_pct = float(hh_pct)


    def _clamp_temp(self) -> None:
        if self.temperature_c < self._t_min:
            self.temperature_c = self._t_min
        elif self.temperature_c > self._t_max:
            self.temperature_c = self._t_max
