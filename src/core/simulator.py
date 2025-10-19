# src/core/simulator_fl.py

from .tank import Tank
from .pump import Pump
from .flowmeter import FlowMeter

CAP_L = 1000.0  # 1000 L kapacitás/tartály

class Simulator_FL:
    def __init__(self):
        self.t1 = Tank(1000, 700, 60.0)
        self.t2 = Tank(1000, 250, 35.0)
        self.t3 = Tank(1000, 100, 25.0)

        self.p1 = Pump(35, "P1")   # T1 ↔ T2
        self.p2 = Pump(35, "P2")   # T2 ↔ T3

        self.fq12 = FlowMeter("FQ12")
        self.fq23 = FlowMeter("FQ23")

        self.drain_lps = 0.0
        self.t = 0.0
        self.history = []

        self.last_q12_lps = 0.0
        self.last_q23_lps = 0.0

    #
    def _transfer_FL(self, src: Tank, dst: Tank, q_cmd_lps: float, dt_s: float) -> float:
        if abs(q_cmd_lps) <= 1e-12:
            return 0.0

        # Forrás–cél védelem (LL/HH) – clamp a parancsra
        if q_cmd_lps > 0:  # src -> dst
            if src.level_l <= 0 or dst.level_l >= CAP_L:
                return 0.0
            max_out = src.level_l / max(1.0, dt_s)
            max_in  = max(0.0, CAP_L - dst.level_l) / max(1.0, dt_s)
            q_lps = min(q_cmd_lps, max_out, max_in)
            moved = src.remove(q_lps * dt_s)
            dst.add(moved, src.temperature_c)
            return q_lps
        else:              # dst -> src
            if dst.level_l <= 0 or src.level_l >= CAP_L:
                return 0.0
            q_cmd_lps = -q_cmd_lps
            max_out = dst.level_l / max(1.0, dt_s)
            max_in  = max(0.0, CAP_L - src.level_l) / max(1.0, dt_s)
            q_lps = min(q_cmd_lps, max_out, max_in)
            moved = dst.remove(q_lps * dt_s)
            src.add(moved, dst.temperature_c)
            return -q_lps

    #
    def step_FL(self, dt_s: float = 1.0):
        # P1 interlock (irányfüggő): ne töltsön tele/üresre
        q1_cmd = self.p1.signed_flow_lps()
        if q1_cmd > 0 and (self.t1.level_l <= 0 or self.t2.level_l >= CAP_L):
            self.p1.command = 0.0; q1_cmd = 0.0
        if q1_cmd < 0 and (self.t2.level_l <= 0 or self.t1.level_l >= CAP_L):
            self.p1.command = 0.0; q1_cmd = 0.0

        q12 = self._transfer_FL(self.t1, self.t2, q1_cmd, dt_s)
        self.last_q12_lps = q12
        rho_src12 = self.t1.density_kgm3 if q12 >= 0 else self.t2.density_kgm3
        self.fq12.measure(abs(q12), rho_src12, dt_s)
        self.p1.tick_hours(dt_s)

        # P2 interlock
        q2_cmd = self.p2.signed_flow_lps()
        if q2_cmd > 0 and (self.t2.level_l <= 0 or self.t3.level_l >= CAP_L):
            self.p2.command = 0.0; q2_cmd = 0.0
        if q2_cmd < 0 and (self.t3.level_l <= 0 or self.t2.level_l >= CAP_L):
            self.p2.command = 0.0; q2_cmd = 0.0

        q23 = self._transfer_FL(self.t2, self.t3, q2_cmd, dt_s)
        self.last_q23_lps = q23
        rho_src23 = self.t2.density_kgm3 if q23 >= 0 else self.t3.density_kgm3
        self.fq23.measure(abs(q23), rho_src23, dt_s)
        self.p2.tick_hours(dt_s)

        # Leeresztés T3-ból (clamp: ne menjen 0 alá)
        drain = min(self.drain_lps * dt_s, self.t3.level_l)
        self.t3.remove(drain)


        self.t1.thermal_losses(dt_s)
        self.t2.thermal_losses(dt_s)
        self.t3.thermal_losses(dt_s)


        self.t += dt_s
        self.history.append((
            self.t,
            self.t1.level_l, self.t2.level_l, self.t3.level_l,
            q12, q23,
            self.t1.temperature_c, self.t2.temperature_c, self.t3.temperature_c,
            self.t1.density_kgm3, self.t2.density_kgm3, self.t3.density_kgm3
        ))


    def step(self, dt_s: float = 1.0):
        self.step_FL(dt_s)
