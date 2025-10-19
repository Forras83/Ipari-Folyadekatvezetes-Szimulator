class Pump:
    """
    Irányváltós szivattyúmodell:
      - Parancsvezérelt működés: command ∈ [–1.0, +1.0]
      - Pozitív irány: T1 → T2, negatív: T2 → T1
      - Áramláskor kapcsoló 'futás' lámpa (run_lamp)
      - Üzemidő-számláló (óra)
    """

    def __init__(self, max_flow_lps: float = 35.0, name: str = "P"):
        self.name = name
        self.max_flow_lps = float(max_flow_lps)

        self.command = 0.0           # –1.0 .. +1.0
        self.run_lamp = False        # logikai visszajelzés
        self.hours = 0.0             # összesített futásidő [óra]

    def flow_lps(self) -> float:
        """
        Visszaadja az abszolút térfogatáramot [L/s], a parancs alapján.
        """
        c = max(-1.0, min(1.0, float(self.command)))
        return abs(c) * self.max_flow_lps

    def signed_flow_lps(self) -> float:
        """
        Előjeles térfogatáram [L/s]: a command irányának megfelelően.
        """
        c = max(-1.0, min(1.0, float(self.command)))
        return c * self.max_flow_lps

    @property
    def direction(self) -> int:
        """
        Irány visszajelzés:
        +1 → előreirányú áramlás (pl. T1 → T2),
        –1 → visszairányú (pl. T2 → T1)
        """
        return 1 if self.command >= 0 else -1

    def tick_hours(self, dt_s: float) -> None:
        """
        Időlépés alapú frissítés – ha áramlás van, növeli az üzemidőt és kapcsolja a run_lamp jelzést.
        """
        is_running = self.flow_lps() > 1e-6
        self.run_lamp = is_running
        if is_running:
            self.hours += dt_s / 3600.0
