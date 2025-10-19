# controllers/app_controller_fl.py
from collections import deque

class AppController_FL:
    """
    3 tartály (T1–T3), 2 szivattyú (P1, P2), T3 leeresztés.
    Parancsok [-1..1], áramlás L/s. FL-változat interlockokkal (LL/HH + hiszterézis).
    """
    CAP_L = 1000.0
    P1_MAX_LPS = 20.0
    P2_MAX_LPS = 20.0
    HH_L = CAP_L
    LL_L = 0.0
    HYST_L = 5.0
    HIST_MAX = 200

    def __init__(self):
        self.L1, self.L2, self.L3 = 1000.0, 0.0, 0.0
        self.T1, self.T2, self.T3 = 51.0, 20.0, 20.0
        self.p1_cmd = 0.0
        self.p2_cmd = 0.0
        self.drain_lps = 0.0
        self.p1_running = False
        self.p2_running = False
        self.p1_hours = 0.0
        self.p2_hours = 0.0
        self.f12_lps = self.f23_lps = 0.0
        self.f12_kgps = self.f23_kgps = 0.0
        self.tot12_L = self.tot23_L = 0.0
        self.time_s = 0.0
        self._hist = deque(maxlen=self.HIST_MAX)

    # ---- GUI API
    def set_p1(self, cmd: float): self.p1_cmd = max(-1.0, min(1.0, float(cmd)))
    def set_p2(self, cmd: float): self.p2_cmd = max(-1.0, min(1.0, float(cmd)))
    def set_drain(self, q_lps: float): self.drain_lps = max(0.0, float(q_lps))
    def get_levels(self): return self.L1, self.L2, self.L3
    def get_temps(self): return self.T1, self.T2, self.T3
    def get_rhos(self): return tuple(self._rho(T) for T in (self.T1, self.T2, self.T3))
    def get_alarms(self):
        ll1, hh1 = self.L1 <= self.LL_L + 1e-6, self.L1 >= self.HH_L - 1e-6
        ll2, hh2 = self.L2 <= self.LL_L + 1e-6, self.L2 >= self.HH_L - 1e-6
        ll3, hh3 = self.L3 <= self.LL_L + 1e-6, self.L3 >= self.HH_L - 1e-6
        return ll1, hh1, ll2, hh2, ll3, hh3
    def get_pumps(self): return self.p1_running, self.p2_running, self.p1_hours, self.p2_hours
    def get_flows(self): return self.f12_lps, self.f23_lps, self.f12_kgps, self.f23_kgps
    def get_totals(self): return self.tot12_L, self.tot23_L
    def get_pump_cmds(self):
        eff1 = 0.0 if not self.p1_running else (1.0 if self.f12_lps>0 else (-1.0 if self.f12_lps<0 else 0.0))
        eff2 = 0.0 if not self.p2_running else (1.0 if self.f23_lps>0 else (-1.0 if self.f23_lps<0 else 0.0))
        if not self.p1_running: eff1 = 0.0 if abs(self.p1_cmd)<1e-6 else (1.0 if self.p1_cmd>0 else -1.0)
        if not self.p2_running: eff2 = 0.0 if abs(self.p2_cmd)<1e-6 else (1.0 if self.p2_cmd>0 else -1.0)
        return eff1, eff2
    def history(self): return list(self._hist)

    # ---- Szimuláció
    def tick_FL(self, dt: float):  # <- saját FL nevű függvény (követelmény)
        dt = float(dt)
        if dt <= 0: return
        p1 = self._apply_interlocks_p1(self.p1_cmd)
        p2 = self._apply_interlocks_p2(self.p2_cmd)
        q1_des = p1 * self.P1_MAX_LPS
        q2_des = p2 * self.P2_MAX_LPS
        q1 = self._clamp_bidir(q1_des, self.L1, self.L2, dt)
        q2 = self._clamp_bidir(q2_des, self.L2, self.L3, dt)
        q_drain = min(self.drain_lps, self.L3/dt if dt>0 else 0.0)

        self._xfer_level(q1, '12', dt)
        self._xfer_level(q2, '23', dt)
        self.L3 = max(self.LL_L, min(self.HH_L, self.L3 - q_drain*dt))

        self._mix_temps(q1, ('T1','T2'), dt)
        self._mix_temps(q2, ('T2','T3'), dt)

        self.f12_lps, self.f23_lps = q1, q2
        r1, r2, r3 = self.get_rhos()
        self.f12_kgps = abs(q1)*0.001*(r2 if q1<0 else r1)
        self.f23_kgps = abs(q2)*0.001*(r2 if q2>0 else r3)
        self.tot12_L += abs(q1)*dt
        self.tot23_L += abs(q2)*dt

        self.p1_running = abs(q1) > 1e-6
        self.p2_running = abs(q2) > 1e-6
        if self.p1_running: self.p1_hours += dt/3600.0
        if self.p2_running: self.p2_hours += dt/3600.0

        self.time_s += dt
        self._hist.append((self.time_s, self.L1, self.L2, self.L3, self.f12_lps, self.f23_lps, self.T1, self.T2, self.T3))

    # kompatibilitás
    def tick(self, dt: float): self.tick_FL(dt)

    # ---- belső segédek
    @staticmethod
    def _rho(T): return max(950.0, min(1000.0, 1000.0 - 0.3*(T-4.0)))
    def _apply_interlocks_p1(self, cmd):
        if cmd < 0:  # T2 -> T1
            if self.L1 >= self.HH_L or self.L2 <= self.LL_L + self.HYST_L: return 0.0
        elif cmd > 0:  # T1 -> T2
            if self.L2 >= self.HH_L or self.L1 <= self.LL_L + self.HYST_L: return 0.0
        return cmd
    def _apply_interlocks_p2(self, cmd):
        if cmd > 0:  # T2 -> T3
            if self.L3 >= self.HH_L or self.L2 <= self.LL_L + self.HYST_L: return 0.0
        elif cmd < 0:  # T3 -> T2
            if self.L2 >= self.HH_L or self.L3 <= self.LL_L + self.HYST_L: return 0.0
        return cmd
    def _clamp_bidir(self, q_des, La, Lb, dt):
        if abs(q_des) < 1e-9: return 0.0
        if q_des > 0:
            max_from_a = max(0.0, La - self.LL_L) / dt
            max_to_b   = max(0.0, self.HH_L - Lb) / dt
            return max(0.0, min(q_des, max_from_a, max_to_b))
        else:
            max_from_b = max(0.0, Lb - self.LL_L) / dt
            max_to_a   = max(0.0, self.HH_L - La) / dt
            return -max(0.0, min(abs(q_des), max_from_b, max_to_a))
    def _xfer_level(self, q, pair, dt):
        dL = q*dt
        if pair=='12':
            self.L1 = max(self.LL_L, min(self.HH_L, self.L1 - dL))
            self.L2 = max(self.LL_L, min(self.HH_L, self.L2 + dL))
        else:
            self.L2 = max(self.LL_L, min(self.HH_L, self.L2 - dL))
            self.L3 = max(self.LL_L, min(self.HH_L, self.L3 + dL))
    def _mix_temps(self, q, pair, dt):
        if abs(q) < 1e-9 or dt<=0: return
        V = abs(q)*dt
        if pair==('T1','T2'):
            if q>0: self.T2 = self._mix(self.T2, self.L2, self.T1, V)
            else:   self.T1 = self._mix(self.T1, self.L1, self.T2, V)
        else:
            if q>0: self.T3 = self._mix(self.T3, self.L3, self.T2, V)
            else:   self.T2 = self._mix(self.T2, self.L2, self.T3, V)
    @staticmethod
    def _mix(Td, Ld, Ts, Vin):
        if Ld <= 1e-9: return Ts
        a = max(0.0, min(1.0, Vin/(Ld+Vin)))
        return (1-a)*Td + a*Ts
