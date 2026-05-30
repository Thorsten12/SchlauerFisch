"""
player.py – Liest output.json und spielt jeden Block synchron ab:
  - Audio über pygame (Kabel-Lautsprecher)
  - Motor-Frames: [mund, kopf, flosse]
      mund  (frame[0]) : Motor 1 – controller_1, HB6,      speed 200
      kopf  (frame[1]) : Motor 3 – controller_3, HB9+HB7,  speed 255
      flosse(frame[2]) : Motor 2 – controller_2, HB6+HB5,  speed 200
"""

import json
import base64
import tempfile
import os
import time

import pygame
import multi_half_bridge_py as mhb

# ── Motoren initialisieren ──────────────────────────────────────────────────

print("[INFO] Initialisiere Controller 1 (Mund)...")
controller_1 = mhb.Tle94112Rpi()
motor_1 = mhb.Tle94112Motor(controller_1)
controller_1.begin()
controller_1.clearErrors()
motor_1.connect(motor_1.LOWSIDE,  controller_1.TLE_HB6)
motor_1.setPwm(motor_1.LOWSIDE,  controller_1.TLE_NOPWM)
motor_1.setPwm(motor_1.HIGHSIDE, controller_1.TLE_PWM1)
motor_1.begin()

print("[INFO] Initialisiere Controller 2 (Flosse)...")
controller_2 = mhb.Tle94112Rpi()
motor_2 = mhb.Tle94112Motor(controller_2)
controller_2.begin()
controller_2.clearErrors()
motor_2.connect(motor_2.HIGHSIDE, controller_2.TLE_HB6)
motor_2.connect(motor_2.LOWSIDE,  controller_2.TLE_HB5)
motor_2.setPwm(motor_2.LOWSIDE,  controller_2.TLE_NOPWM)
motor_2.setPwm(motor_2.HIGHSIDE, controller_2.TLE_PWM1)
motor_2.begin()

print("[INFO] Initialisiere Controller 3 (Kopf)...")
controller_3 = mhb.Tle94112Rpi()
motor_3 = mhb.Tle94112Motor(controller_3)
controller_3.begin()
controller_3.clearErrors()
motor_3.connect(motor_3.HIGHSIDE, controller_3.TLE_HB9)
motor_3.connect(motor_3.LOWSIDE,  controller_3.TLE_HB7)
motor_3.setPwm(motor_3.LOWSIDE,  controller_3.TLE_NOPWM)
motor_3.setPwm(motor_3.HIGHSIDE, controller_3.TLE_PWM1)
motor_3.begin()

# ── Audio initialisieren ────────────────────────────────────────────────────

pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)

# ── Hilfsfunktionen ─────────────────────────────────────────────────────────

def set_motors(frame):
    """Setzt Mund, Kopf, Flosse anhand eines motor_frames-Eintrags."""
    mund, kopf, flosse = frame[0], frame[1], frame[2]

    # Mund
    if mund:
        motor_1.start(200)
    else:
        motor_1.coast()

    # Kopf
    if kopf:
        motor_3.start(255)
    else:
        motor_3.coast()

    # Flosse
    if flosse:
        motor_2.start(200)
    else:
        motor_2.coast()


def motors_off():
    """Alle Motoren sicher ausschalten."""
    motor_1.coast()
    motor_2.coast()
    motor_3.coast()


def play_block(block):
    """Spielt einen Block synchron ab (Audio + Motor-Frames)."""
    fps_ms    = block["fps_ms"]
    frames    = block["motor_frames"]
    audio_b64 = block["audio_base64"]

    # Audio aus Base64 → temp WAV
    audio_bytes = base64.b64decode(audio_b64)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        pygame.mixer.music.load(tmp_path)
        pygame.mixer.music.play()

        frame_sec  = fps_ms / 1000.0
        start_time = time.monotonic()

        for i, frame in enumerate(frames):
            target = start_time + i * frame_sec
            wait   = target - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            set_motors(frame)

        # Warten bis Audio fertig
        while pygame.mixer.music.get_busy():
            time.sleep(0.01)

    finally:
        motors_off()
        pygame.mixer.music.stop()
        os.unlink(tmp_path)


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
              f"{len(block['motor_frames'])} Frames @ {block['fps_ms']} ms/Frame")
        play_block(block)
        print(f"[DONE] Block {idx + 1} abgeschlossen.")

    print("[INFO] Alle Blöcke abgespielt. Programm beendet.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[ABBRUCH] Strg+C – Motoren werden ausgeschaltet.")
        motors_off()