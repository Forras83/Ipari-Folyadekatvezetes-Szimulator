class FlowMeter:
    """
    Mennyiségmérő (FQ):
      - Pillanatnyi térfogatáram [L/s] és tömegáram [kg/s]
      - Összegzett mennyiség [L] és tömeg [kg]
      - Opcionális elsőrendű low-pass szűrés (időállandó: tau_s)
      - Min/Max csúcsértékek követése

    Megőrzött kompatibilitás:
      - .last_lps, .last_kgps, .total_l, .measure() továbbra is használható.
    """

    def __init__(self, name: str = "FQ", lowpass_tau_s: float = 0.0):
        self.name = name

        # Pillanatnyi mért értékek
        self.last_lps = 0.0        # L/s – szűrt
        self.last_kgps = 0.0       # kg/s

        # Összegzett mennyiségek
        self.total_l = 0.0         # liter
        self.total_kg = 0.0        # kilogramm

        # Szűrés
        self.tau_s = max(0.0, float(lowpass_tau_s))
        self._y_lps = 0.0          # belső szűrő állapot (L/s)

        # Diagnosztika – csúcsértékek
        self.min_lps = float("+inf")
        self.max_lps = float("-inf")

    # --- Fő API ---

    def measure(self, lps: float, rho_kgm3: float, dt_s: float):
        """
        Frissíti a mért értékeket és totalizált adatokat.

        :param lps: nyers térfogatáram [L/s], ≥ 0
        :param rho_kgm3: sűrűség [kg/m³], ≥ 0
        :param dt_s: időlépés [s], > 0
        """
        if dt_s <= 0.0:
            return

        q_lps = max(0.0, float(lps))
        rho = max(0.0, float(rho_kgm3))

        # Low-pass szűrés, ha be van kapcsolva
        if self.tau_s > 0.0:
            alpha = dt_s / (self.tau_s + dt_s)
            self._y_lps += alpha * (q_lps - self._y_lps)
            q_filt = self._y_lps
        else:
            q_filt = q_lps
            self._y_lps = q_filt

        # Pillanatnyi értékek frissítése
        self.last_lps = q_filt
        self.last_kgps = rho * (q_filt * 1e-3)  # 1 L = 1e-3 m³

        # Összegzés (totalizálás)
        self.total_l  += self.last_lps  * dt_s
        self.total_kg += self.last_kgps * dt_s

        # Csúcsok frissítése
        self.min_lps = min(self.min_lps, q_filt)
        self.max_lps = max(self.max_lps, q_filt)

    # --- Kényelmi metódusok ---

    def reset_totals(self):
        """Totalizált mennyiségek nullázása."""
        self.total_l = 0.0
        self.total_kg = 0.0

    def reset_peaks(self):
        """Min/Max csúcsértékek nullázása."""
        self.min_lps = float("+inf")
        self.max_lps = float("-inf")

    def set_lowpass_tau(self, tau_s: float):
        """Low-pass szűrés időállandó beállítása (0 = kikapcsolva)."""
        self.tau_s = max(0.0, float(tau_s))

    # --- Diagnosztika / snapshot ---

    def snapshot(self) -> dict:
        """Kompakt pillanatkép logoláshoz vagy UI megjelenítéshez."""
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
