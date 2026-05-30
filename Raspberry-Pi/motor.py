"""
player.py – Liest output.json und steuert Motoren frame-genau:
  - Kein Audio
  - Motor-Frames: [mund, kopf, flosse]
      mund  (frame[0]) : motor_3 – controller_3, HB9(HIGH)+HB7(LOW), speed 255
      kopf  (frame[1]) : motor_1 – controller_1, HB5(HIGH)+HB6(LOW), speed 200
      flosse(frame[2]) : motor_2 – controller_2, HB6(HIGH)+HB5(LOW), speed 200
  Regeln:
    - Kopf und Flosse laufen NIE gleichzeitig (teilen sich Pins HB5 & HB6)
    - Alle drei laufen mit start → sleep → coast
    - Mund läuft parallel
"""

import json
import os
import time
import threading

import multi_half_bridge_py as mhb

# ── Controller & Motoren Instanzen ────────────────────────────────────────

print("[INFO] Erstelle Controller-Instanzen...")
controller_1 = mhb.Tle94112Rpi() # Kopf
controller_2 = mhb.Tle94112Rpi() # Flosse
controller_3 = mhb.Tle94112Rpi() # Mund

motor_1 = mhb.Tle94112Motor(controller_1)
motor_2 = mhb.Tle94112Motor(controller_2)
motor_3 = mhb.Tle94112Motor(controller_3)


# ── Feste Initialisierung (Mund) ──────────────────────────────────────────
# Der Mund teilt sich keine Pins und kann einmalig global konfiguriert werden.

print("[INFO] Initialisiere Controller 3 (Mund)...")
controller_3.begin()
controller_3.clearErrors()
motor_3.connect(motor_3.HIGHSIDE, controller_3.TLE_HB9)
motor_3.connect(motor_3.LOWSIDE,  controller_3.TLE_HB7)
motor_3.setPwm(motor_3.LOWSIDE,   controller_3.TLE_NOPWM)
motor_3.setPwm(motor_3.HIGHSIDE,  controller_3.TLE_PWM1)
motor_3.begin()


# ── Hilfsfunktionen ─────────────────────────────────────────────────────────

# Lock: Kopf und Flosse dürfen nie gleichzeitig laufen (da selbe Hardware-Pins)
kopf_flosse_lock = threading.Lock()

def run_mund(dauer):
    """Mund: start → sleep → coast"""
    motor_3.start(255)
    time.sleep(dauer)
    motor_3.coast()

def run_kopf(dauer):
    """Kopf: Lock holen → Controller konfigurieren → start → sleep → coast → Lock freigeben"""
    with kopf_flosse_lock:
        controller_1.begin()
        controller_1.clearErrors()
        
        motor_1.connect(motor_1.HIGHSIDE, controller_1.TLE_HB5)
        motor_1.connect(motor_1.LOWSIDE,  controller_1.TLE_HB6)
        motor_1.setPwm(motor_1.LOWSIDE,   controller_1.TLE_NOPWM)
        motor_1.setPwm(motor_1.HIGHSIDE,  controller_1.TLE_PWM1)
        motor_1.begin()
        
        motor_1.start(200)
        time.sleep(dauer)
        motor_1.coast()

def run_flosse(dauer):
    """Flosse: Lock holen → Controller konfigurieren → start → sleep → coast → Lock freigeben"""
    with kopf_flosse_lock:
        controller_2.begin()
        controller_2.clearErrors()
        
        motor_2.connect(motor_2.HIGHSIDE, controller_2.TLE_HB6)
        motor_2.connect(motor_2.LOWSIDE,  controller_2.TLE_HB5)
        motor_2.setPwm(motor_2.LOWSIDE,   controller_2.TLE_NOPWM)
        motor_2.setPwm(motor_2.HIGHSIDE,  controller_2.TLE_PWM1)
        motor_2.begin()
        
        motor_2.start(200)
        time.sleep(dauer)
        motor_2.coast()


def play_block(block):
    fps_ms    = 200  # ms pro Frame
    frames    = block["motor_frames"]
    frame_sec = fps_ms / 1000.0

    prev_mund   = 0
    prev_kopf   = 0
    prev_flosse = 0

    for frame in frames:
        mund   = frame[0]
        kopf   = frame[1]
        flosse = frame[2]

        threads = []

        # Mund: bei Zustandsänderung 0→1 starten (in eigenem Thread)
        if mund and not prev_mund:
            t = threading.Thread(target=run_mund, args=(frame_sec,), daemon=True)
            threads.append(t)

        # Kopf: bei Zustandsänderung 0→1 starten
        if kopf and not prev_kopf:
            t = threading.Thread(target=run_kopf, args=(frame_sec,), daemon=True)
            threads.append(t)

        # Flosse: bei Zustandsänderung 0→1 starten
        if flosse and not prev_flosse:
            t = threading.Thread(target=run_flosse, args=(frame_sec,), daemon=True)
            threads.append(t)

        for t in threads:
            t.start()

        prev_mund   = mund
        prev_kopf   = kopf
        prev_flosse = flosse

        time.sleep(frame_sec)

    # Block fertig: alles aus
    motor_1.coast()
    motor_2.coast()
    motor_3.coast()


# ── Hauptprogramm ───────────────────────────────────────────────────────────

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path  = os.path.join(script_dir, "output.json")

    print(f"[INFO] Lade {json_path}...")
    with open(json_path, "r") as f:
        data = json.load(f)

    blocks = data if isinstance(data, list) else data.get("blocks", [])
    print(f"[INFO] {len(blocks)} Block(s) gefunden.")

    for idx, block in enumerate(blocks):
        print(f"[PLAY] Block {idx + 1}/{len(blocks)} – "
              f"{len(block['motor_frames'])} Frames @ 200 ms/Frame")
        play_block(block)
        print(f"[DONE] Block {idx + 1} abgeschlossen.")

    print("[INFO] Alle Blöcke abgespielt.")
    motor_1.coast()
    motor_2.coast()
    motor_3.coast()
    print("[INFO] Alle Motoren aus. Programm beendet.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ABBRUCH] Strg+C – alle Motoren ausschalten.")
        motor_1.coast()
        motor_2.coast()
        motor_3.coast()