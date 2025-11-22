class Pump:


    def __init__(self, max_flow_lps: float = 35.0, name: str = "P"):
        self.name = name
        self.max_flow_lps = float(max_flow_lps)

        self.command = 0.0
        self.run_lamp = False
        self.hours = 0.0

    def flow_lps(self) -> float:

        c = max(-1.0, min(1.0, float(self.command)))
        return abs(c) * self.max_flow_lps

    def signed_flow_lps(self) -> float:

        c = max(-1.0, min(1.0, float(self.command)))
        return c * self.max_flow_lps

    @property
    def direction(self) -> int:

        return 1 if self.command >= 0 else -1

    def tick_hours(self, dt_s: float) -> None:

        is_running = self.flow_lps() > 1e-6
        self.run_lamp = is_running
        if is_running:
            self.hours += dt_s / 3600.0
