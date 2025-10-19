import os, sys, tkinter as tk

BASE = os.path.dirname(__file__)
SRC = os.path.join(BASE, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from ui.app_fl import App_FL

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Folyadékátvezetés Szimulátor – 3T/2P (FL v1)")
    root.geometry("1150x640")
    App_FL(root)
    root.mainloop()
