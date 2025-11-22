import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from controllers.app_controller_fl import AppController_FL

REF_CAPACITY_L = 1000.0


class App_FL(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=8)
        self.pack(fill="both", expand=True)


        self.ctrl = AppController_FL()
        self.running = False
        self.G = None
        self._resize_after = None

        self._build()
        self.canvas.bind("<Configure>", self._on_canvas_resize)


        self._draw_static()
        self.update_display_FL()

    def fl_quick_start(self, *_):

        self.var_p1.set(1.0); self.ctrl.set_p1(1.0)
        self.var_p2.set(1.0); self.ctrl.set_p2(1.0)
        self.var_drain.set(5.0); self.ctrl.set_drain(5.0)
        self.start()

    def fl_emergency_stop(self, *_):

        self.var_p1.set(0.0); self.ctrl.set_p1(0.0)
        self.var_p2.set(0.0); self.ctrl.set_p2(0.0)
        self.var_drain.set(0.0); self.ctrl.set_drain(0.0)
        self.stop()


    def _build(self):
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)


        left = ttk.LabelFrame(paned, text="Vezérlés", padding=8)
        paned.add(left, weight=0)

        self.var_p1 = tk.DoubleVar(value=0.6)
        self.var_p2 = tk.DoubleVar(value=0.6)
        self.var_drain = tk.DoubleVar(value=0.0)

        ttk.Label(left, text="P1 (T1 ↔ T2) [-1..1]").grid(row=0, column=0, sticky="w")
        ttk.Scale(
            left, from_=-1, to=1, variable=self.var_p1, orient="horizontal",
            command=lambda *_: self.ctrl.set_p1(self.var_p1.get())
        ).grid(row=0, column=1, sticky="we")

        left.columnconfigure(1, weight=1)
        left.columnconfigure(2, weight=0)

        frm_p1dir = ttk.Frame(left)
        frm_p1dir.grid(row=0, column=2, padx=(6, 0), sticky="w")
        ttk.Button(frm_p1dir, text="←", width=2,
                   command=lambda: (self.var_p1.set(-1.0), self.ctrl.set_p1(-1.0))
                   ).pack(side="left")
        ttk.Button(frm_p1dir, text="→", width=2,
                   command=lambda: (self.var_p1.set(+1.0), self.ctrl.set_p1(+1.0))
                   ).pack(side="left")

        frm_p2dir = ttk.Frame(left)
        frm_p2dir.grid(row=1, column=2, padx=(6, 0), sticky="w")
        ttk.Button(frm_p2dir, text="←", width=2,
                   command=lambda: (self.var_p2.set(-1.0), self.ctrl.set_p2(-1.0))
                   ).pack(side="left")
        ttk.Button(frm_p2dir, text="→", width=2,
                   command=lambda: (self.var_p2.set(+1.0), self.ctrl.set_p2(+1.0))
                   ).pack(side="left")

        ttk.Label(left, text="P2 (T2 ↔ T3) [-1..1]").grid(row=1, column=0, sticky="w")
        ttk.Scale(
            left, from_=-1, to=1, variable=self.var_p2, orient="horizontal",
            command=lambda *_: self.ctrl.set_p2(self.var_p2.get())
        ).grid(row=1, column=1, sticky="we")

        ttk.Label(left, text="T3 leeresztés [L/s]").grid(row=2, column=0, sticky="w")
        ttk.Scale(
            left, from_=0, to=20, variable=self.var_drain, orient="horizontal",
            command=lambda *_: self.ctrl.set_drain(self.var_drain.get())
        ).grid(row=2, column=1, sticky="we")

        ttk.Button(left, text="Start", command=self.start).grid(row=3, column=0, pady=6, sticky="we")
        ttk.Button(left, text="Stop", command=self.stop).grid(row=3, column=1, pady=6, sticky="we")

        ttk.Label(left, text="Szivattyú vezérlés").grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 2))
        frm_p1ctrl = ttk.Frame(left)
        frm_p1ctrl.grid(row=5, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Label(frm_p1ctrl, text="P1: ").pack(side="left")
        ttk.Button(frm_p1ctrl, text="Start", command=lambda: (
            self.var_p1.set(1.0), self.ctrl.set_p1(1.0))).pack(side="left")
        ttk.Button(frm_p1ctrl, text="Stop", command=lambda: (
            self.var_p1.set(0.0), self.ctrl.set_p1(0.0))).pack(side="left")

        frm_p2ctrl = ttk.Frame(left)
        frm_p2ctrl.grid(row=6, column=0, columnspan=3, sticky="w", pady=2)
        ttk.Label(frm_p2ctrl, text="P2: ").pack(side="left")
        ttk.Button(frm_p2ctrl, text="Start", command=lambda: (
            self.var_p2.set(1.0), self.ctrl.set_p2(1.0))).pack(side="left")
        ttk.Button(frm_p2ctrl, text="Stop", command=lambda: (
            self.var_p2.set(0.0), self.ctrl.set_p2(0.0))).pack(side="left")

        ttk.Label(left, text="Jelmagyarázat:", font=("TkDefaultFont", 9, "bold")).grid(
            row=7, column=0, columnspan=2, sticky="w", pady=(8, 0)
        )
        ttk.Label(left, text="T1/T2/T3 – tartályok").grid(row=8, column=0, columnspan=2, sticky="w")
        ttk.Label(left, text="P1/P2 – szivattyúk").grid(row=9, column=0, columnspan=2, sticky="w")
        ttk.Label(left, text="Zöld lámpa – fut a szivattyú").grid(row=10, column=0, columnspan=2, sticky="w")
        ttk.Label(left, text="LL/HH – szintkapcsolók").grid(row=11, column=0, columnspan=2, sticky="w")


        mid = ttk.Frame(paned)
        paned.add(mid, weight=10)
        self.canvas = tk.Canvas(mid, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)


        right = ttk.Frame(paned)
        paned.add(right, weight=5)

        meas = ttk.LabelFrame(right, text="Mérések / Állapot", padding=8)
        meas.pack(fill="x", expand=False)
        self.lbl_lvls = ttk.Label(meas, text="Szintek [L]  T1:-  T2:-  T3:-"); self.lbl_lvls.pack(anchor="w")
        self.lbl_temp = ttk.Label(meas, text="Hőmérséklet [°C]  T1:-  T2:-  T3:-"); self.lbl_temp.pack(anchor="w")
        self.lbl_rho  = ttk.Label(meas, text="Sűrűség [kg/m³]  T1:-  T2:-  T3:-"); self.lbl_rho.pack(anchor="w")
        self.lbl_flows = ttk.Label(meas, text="Áramlás  L/s: P1 - | P2 -    kg/s: P1 - | P2 -"); self.lbl_flows.pack(anchor="w")
        self.lbl_totals = ttk.Label(meas, text="Mennyiségek összesen [L]  FQ12:-  FQ23:-"); self.lbl_totals.pack(anchor="w")
        self.lbl_pumps = ttk.Label(meas, text="Szivattyúk – P1 üzemóra: - h | P2 üzemóra: - h"); self.lbl_pumps.pack(anchor="w")

        trend = ttk.LabelFrame(right, text="Trend (szintek és hőmérséklet)", padding=4)
        trend.pack(fill="both", expand=True, pady=(8, 0))
        self.fig = Figure(figsize=(4.4, 3.0), constrained_layout=True)
        self.ax1 = self.fig.add_subplot(211); self.ax1.set_ylabel("Szint [L]")
        self.ax2 = self.fig.add_subplot(212); self.ax2.set_ylabel("T [°C]"); self.ax2.set_xlabel("Idő [s]")
        self.canvas_plot = FigureCanvasTkAgg(self.fig, master=trend)
        self.canvas_plot.get_tk_widget().pack(fill="both", expand=True)


        self.after(0, lambda: paned.sashpos(0, 270))
        self.after(0, lambda: paned.sashpos(1, 980))


    def _compute_layout_FL(self):
        c = self.canvas
        w = max(760, c.winfo_width() or 0)
        h = max(520, c.winfo_height() or 0)
        top_margin = max(70, int(h * 0.12))
        bottom_margin = max(40, int(h * 0.10))
        bar_h = max(220, h - top_margin - bottom_margin)
        y_top = top_margin; y_bot = y_top + bar_h; y_mid = (y_top + y_bot) // 2
        right_clearance = 160
        left_margin = max(50, int(w * 0.06))
        usable_w = max(320, w - left_margin - right_clearance)
        x1 = left_margin + usable_w * 1 / 6
        x2 = left_margin + usable_w * 3 / 6
        x3 = left_margin + usable_w * 5 / 6
        bar_w = int(min(90, max(60, usable_w * 0.08)))
        return {"w": w, "h": h, "top": y_top, "bar_h": bar_h, "bar_w": bar_w,
                "x1": x1, "x2": x2, "x3": x3, "y_top": y_top, "y_bot": y_bot, "y_mid": y_mid}


    def _draw_static(self):
        c = self.canvas
        c.delete("all")
        L = self._compute_layout_FL()
        self.G = {"top": L["top"], "bar_h": L["bar_h"], "bar_w": L["bar_w"]}

        x1, x2, x3 = L["x1"], L["x2"], L["x3"]
        y_top, y_bot, y_mid = L["y_top"], L["y_bot"], L["y_mid"]
        bar_w = L["bar_w"]; inset = 6


        self.t1_rect = c.create_rectangle(x1 - bar_w // 2, y_top, x1 + bar_w // 2, y_bot, outline="#2b66ff", width=2)
        c.create_text(x1, y_top - 24, text="T1", font=("TkDefaultFont", 12, "bold"))
        c.create_text(x1 - 36, y_top - 44, text="LL"); c.create_text(x1 + 36, y_top - 44, text="HH")

        self.t2_rect = c.create_rectangle(x2 - bar_w // 2, y_top, x2 + bar_w // 2, y_bot, outline="#ff9b00", width=2)
        c.create_text(x2, y_top - 24, text="T2", font=("TkDefaultFont", 12, "bold"))
        c.create_text(x2 - 36, y_top - 44, text="LL"); c.create_text(x2 + 36, y_top - 44, text="HH")

        self.t3_rect = c.create_rectangle(x3 - bar_w // 2, y_top, x3 + bar_w // 2, y_bot, outline="#00a651", width=2)
        c.create_text(x3, y_top - 24, text="T3", font=("TkDefaultFont", 12, "bold"))
        c.create_text(x3 - 36, y_top - 44, text="LL"); c.create_text(x3 + 36, y_top - 44, text="HH")


        self.t1_fill = c.create_rectangle(x1 - bar_w // 2 + inset, y_bot, x1 + bar_w // 2 - inset, y_bot, fill="#2b66ff", outline="")
        self.t2_fill = c.create_rectangle(x2 - bar_w // 2 + inset, y_bot, x2 + bar_w // 2 - inset, y_bot, fill="#ffba4d", outline="")
        self.t3_fill = c.create_rectangle(x3 - bar_w // 2 + inset, y_bot, x3 + bar_w // 2 - inset, y_bot, fill="#54d18b", outline="")


        self.t1_ll = c.create_oval(x1 - 48, y_top - 36, x1 - 32, y_top - 20, fill="grey", outline="")
        self.t1_hh = c.create_oval(x1 + 32, y_top - 36, x1 + 48, y_top - 20, fill="grey", outline="")
        self.t2_ll = c.create_oval(x2 - 48, y_top - 36, x2 - 32, y_top - 20, fill="grey", outline="")
        self.t2_hh = c.create_oval(x2 + 32, y_top - 36, x2 + 48, y_top - 20, fill="grey", outline="")
        self.t3_ll = c.create_oval(x3 - 48, y_top - 36, x3 - 32, y_top - 20, fill="grey", outline="")
        self.t3_hh = c.create_oval(x3 + 32, y_top - 36, x3 + 48, y_top - 20, fill="grey", outline="")


        self.p1_pipe = c.create_line(x1 + bar_w // 2, y_mid, x2 - bar_w // 2, y_mid, width=3, arrow="last", fill="black")
        self.p1_body = c.create_rectangle(x1 + bar_w // 2 + 22, y_mid - 14, x1 + bar_w // 2 + 62, y_mid + 14, fill="#d8d8d8", outline="#666")
        self.p1_text = c.create_text(x1 + bar_w // 2 + 42, y_mid, text="P1", font=("TkDefaultFont", 10, "bold"))
        self.p1_lamp = c.create_oval(x1 + bar_w // 2 + 70, y_mid - 8, x1 + bar_w // 2 + 86, y_mid + 8, fill="grey", outline="")

        self.p2_pipe = c.create_line(x2 + bar_w // 2, y_mid, x3 - bar_w // 2, y_mid, width=3, arrow="last", fill="black")
        self.p2_body = c.create_rectangle(x2 + bar_w // 2 + 22, y_mid - 14, x2 + bar_w // 2 + 62, y_mid + 14, fill="#d8d8d8", outline="#666")
        self.p2_text = c.create_text(x2 + bar_w // 2 + 42, y_mid, text="P2", font=("TkDefaultFont", 10, "bold"))
        self.p2_lamp = c.create_oval(x2 + bar_w // 2 + 70, y_mid - 8, x2 + bar_w // 2 + 86, y_mid + 8, fill="grey", outline="")


        self.lbl_p1_dir = c.create_text((x1 + x2) / 2, y_mid - 26, text="T1 → T2 (P1)", font=("TkDefaultFont", 9))
        self.lbl_p2_dir = c.create_text((x2 + x3) / 2, y_mid - 26, text="T2 → T3 (P2)", font=("TkDefaultFont", 9))


    def update_display_FL(self):

        self._draw_dynamic()

    def _draw_dynamic(self):
        if not self.G:
            return
        c = self.canvas
        L = self._compute_layout_FL()
        x1, x2, x3 = L["x1"], L["x2"], L["x3"]
        y_top, y_bot, y_mid = L["y_top"], L["y_bot"], L["y_mid"]
        bar_w = L["bar_w"]; inset = 6


        l1, l2, l3 = self.ctrl.get_levels()

        def set_fill(rect, xc, level_l):
            h_px = int(self.G["bar_h"] * max(0.0, min(1.0, level_l / REF_CAPACITY_L)))
            c.coords(rect, xc - bar_w // 2 + inset, y_bot - h_px, xc + bar_w // 2 - inset, y_bot)

        set_fill(self.t1_fill, x1, l1)
        set_fill(self.t2_fill, x2, l2)
        set_fill(self.t3_fill, x3, l3)


        ll1, hh1, ll2, hh2, ll3, hh3 = self.ctrl.get_alarms()
        c.itemconfig(self.t1_ll, fill=("red" if ll1 else "grey")); c.itemconfig(self.t1_hh, fill=("red" if hh1 else "grey"))
        c.itemconfig(self.t2_ll, fill=("red" if ll2 else "grey")); c.itemconfig(self.t2_hh, fill=("red" if hh2 else "grey"))
        c.itemconfig(self.t3_ll, fill=("red" if ll3 else "grey")); c.itemconfig(self.t3_hh, fill=("red" if hh3 else "grey"))


        run1, run2, h1h, h2h = self.ctrl.get_pumps()
        c.itemconfig(self.p1_lamp, fill=("lime green" if run1 else "grey"))
        c.itemconfig(self.p2_lamp, fill=("lime green" if run2 else "grey"))

        f12_lps, f23_lps, f12_kgps, f23_kgps = self.ctrl.get_flows()
        w1 = max(2, int(2 + 8 * (min(35.0, f12_lps) / 35.0)))
        w2 = max(2, int(2 + 8 * (min(35.0, f23_lps) / 35.0)))
        c.coords(self.p1_pipe, x1 + bar_w // 2, y_mid, x2 - bar_w // 2, y_mid)
        c.coords(self.p2_pipe, x2 + bar_w // 2, y_mid, x3 - bar_w // 2, y_mid)
        c.itemconfig(self.p1_pipe, width=w1); c.itemconfig(self.p2_pipe, width=w2)


        cmd1, cmd2 = self.ctrl.get_pump_cmds()
        c.itemconfig(self.p1_pipe, arrow=("last" if cmd1 >= 0 else "first"))
        c.itemconfig(self.p2_pipe, arrow=("last" if cmd2 >= 0 else "first"))
        c.itemconfig(self.lbl_p1_dir, text=("T1 → T2 (P1)" if cmd1 >= 0 else "T2 → T1 (P1)"))
        c.itemconfig(self.lbl_p2_dir, text=("T2 → T3 (P2)" if cmd2 >= 0 else "T3 → T2 (P2)"))


        tot12, tot23 = self.ctrl.get_totals()
        T1, T2, T3 = self.ctrl.get_temps()
        R1, R2, R3 = self.ctrl.get_rhos()
        self.lbl_lvls.config(text=f"Szintek [L]  T1:{l1:.0f}  T2:{l2:.0f}  T3:{l3:.0f}")
        self.lbl_temp.config(text=f"Hőmérséklet [°C]  T1:{T1:.1f}  T2:{T2:.1f}  T3:{T3:.1f}")
        self.lbl_rho.config(text=f"Sűrűség [kg/m³]  T1:{R1:.0f}  T2:{R2:.0f}  T3:{R3:.0f}")
        self.lbl_flows.config(text=f"Áramlás  L/s: P1 {f12_lps:.1f} | P2 {f23_lps:.1f}    kg/s: P1 {f12_kgps:.2f} | P2 {f23_kgps:.2f}")
        self.lbl_totals.config(text=f"Mennyiségek összesen [L]  FQ12:{tot12:.0f}  FQ23:{tot23:.0f}")
        self.lbl_pumps.config(text=f"Szivattyúk – P1 üzemóra: {h1h:.2f} h | P2 üzemóra: {h2h:.2f} h")


        hist = self.ctrl.history()
        if hist:
            ts  = [h[0] for h in hist]
            L1  = [h[1] for h in hist]; L2s = [h[2] for h in hist]; L3s = [h[3] for h in hist]
            T1s = [h[6] for h in hist]; T2s = [h[7] for h in hist]; T3s = [h[8] for h in hist]
            self.ax1.clear(); self.ax2.clear()
            self.ax1.plot(ts, L1,  label="T1"); self.ax1.plot(ts, L2s, label="T2"); self.ax1.plot(ts, L3s, label="T3")
            self.ax1.set_ylabel("Szint [L]"); self.ax1.legend(loc="upper right")
            self.ax2.plot(ts, T1s, label="T1"); self.ax2.plot(ts, T2s, label="T2"); self.ax2.plot(ts, T3s, label="T3")
            self.ax2.set_ylabel("T [°C]"); self.ax2.set_xlabel("Idő [s]"); self.ax2.legend(loc="upper right")
            self.canvas_plot.draw()


    def start(self):
        if self.running:
            return
        self.ctrl.set_p1(self.var_p1.get())
        self.ctrl.set_p2(self.var_p2.get())
        self.ctrl.set_drain(self.var_drain.get())
        self.running = True
        self._tick()

    def stop(self):
        self.running = False

    def _tick(self):
        if not self.running:
            return
        self.ctrl.tick_FL(1.0)
        self.update_display_FL()
        self.after(1000, self._tick)


    def _on_canvas_resize(self, _event):
        if self._resize_after:
            self.after_cancel(self._resize_after)
        self._resize_after = self.after(60, self._redraw_all)

    def _redraw_all(self):
        self._resize_after = None
        self._draw_static()
        self.update_display_FL()
