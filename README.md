# Ipari Folyadékátvezetés Szimulátor

## Hallgató
**Név:Forrás László-WN0JPF
**Monogram:** FL  
**Szak:** Mérnök informatikus  
**Téma:** Ipari irányítástechnikai szimuláció – folyadékátvezető rendszer

---

## Feladat leírása
A program célja egy **háromtartályos ipari folyadékátvezető rendszer** működésének szimulálása, két szivattyú (P1, P2) és két áramlásmérő (FQ12, FQ23) modellezésével.  
A rendszer **valós idejű vezérlést és grafikus megjelenítést** biztosít Tkinter és Matplotlib használatával.

A szimulátor képes:
- tartályszintek, hőmérséklet és sűrűség változását számolni,  
- szivattyúkat és irányokat vezérelni,  
- leeresztést szimulálni,  
- trendgrafikonon megjeleníteni a mért értékeket.  

---

## Modulok és a modulokban használt fő függvények

# `controllers/app_controller_fl.py`
- `AppController_FL` – a szimuláció központi vezérlője  
  - `tick()` – időlépés szimulálása  
  - `set_p1(), set_p2(), set_drain()` – pumpák és leeresztés beállítása  
  - `get_levels(), get_flows(), get_temps()` – állapot-lekérdezések  

# `core/simulator.py`
- `Simulator_FL` – a rendszer fizikai szimulációját végzi  
  - `update()` – folyadékszintek, hőmérséklet és tömegáram számítása  

# `core/tank.py`
- `Tank` – tartálymodell  
  - `fill(), drain()` – folyadék be-/kiáramlás számítása  

# `core/pump.py`
- `Pump` – szivattyúmodell  
  - `set_speed()` – fordulatszám szabályozás  
  - `get_flow_lps()` – aktuális térfogatáram lekérdezése  

# `core/flowmeter.py`
- `FlowMeter` – mennyiségmérő eszköz  
  - `measure()` – átfolyó mennyiség regisztrálása  

# `ui/app_fl.py`
- `App_FL` – grafikus Tkinter felület  
  - `_build()` – kezelőfelület elemek létrehozása  
  - `_draw_dynamic()` – valós idejű vizuális frissítés  
  - `start()` / `stop()` – szimuláció indítása/leállítása  

---

## Osztályok
| Osztály | Modul | Funkció |
|----------|--------|----------|
| `App_FL` | ui.app_fl | Felhasználói felület és grafikus vezérlés |
| `AppController_FL` | controllers.app_controller_fl | Szimulációs logika és adatkezelés |
| `Simulator_FL` | core.simulator | Folyamatmodellezés |
| `Tank` | core.tank | Tartály objektum, szint és hőmérséklet |
| `Pump` | core.pump | Szivattyú objektum, irány és sebesség |
| `FlowMeter` | core.flowmeter | Átfolyásmérő objektum |

---

## Indítás
A projekt fő belépési pontja:
```bash
python src/main_fl.py
