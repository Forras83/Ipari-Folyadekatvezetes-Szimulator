class FlowMeter:


    def __init__(self, name: str = "FQ", lowpass_tau_s: float = 0.0):
        self.name = name


        self.last_lps = 0.0
        self.last_kgps = 0.0


        self.total_l = 0.0
        self.total_kg = 0.0


        self.tau_s = max(0.0, float(lowpass_tau_s))
        self._y_lps = 0.0


        self.min_lps = float("+inf")
        self.max_lps = float("-inf")

    # --- Fő API ---

    def measure(self, lps: float, rho_kgm3: float, dt_s: float):

        if dt_s <= 0.0:
            return

        q_lps = max(0.0, float(lps))
        rho = max(0.0, float(rho_kgm3))


        if self.tau_s > 0.0:
            alpha = dt_s / (self.tau_s + dt_s)
            self._y_lps += alpha * (q_lps - self._y_lps)
            q_filt = self._y_lps
        else:
            q_filt = q_lps
            self._y_lps = q_filt


        self.last_lps = q_filt
        self.last_kgps = rho * (q_filt * 1e-3)  # 1 L = 1e-3 m³


        self.total_l  += self.last_lps  * dt_s
        self.total_kg += self.last_kgps * dt_s


        self.min_lps = min(self.min_lps, q_filt)
        self.max_lps = max(self.max_lps, q_filt)



    def reset_totals(self):

        self.total_l = 0.0
        self.total_kg = 0.0

    def reset_peaks(self):

        self.min_lps = float("+inf")
        self.max_lps = float("-inf")

    def set_lowpass_tau(self, tau_s: float):

        self.tau_s = max(0.0, float(tau_s))



    def snapshot(self) -> dict:

        return {
            "name": self.name,
            "lps": round(self.last_lps, 3),
            "kgps": round(self.last_kgps, 3),
            "total_l": round(self.total_l, 3),
            "total_kg": round(self.total_kg, 3),
            "min_lps": None if self.min_lps == float("+inf") else round(self.min_lps, 3),
            "max_lps": None if self.max_lps == float("-inf") else round(self.max_lps, 3),
            "tau_s": self.tau_s,
        }
