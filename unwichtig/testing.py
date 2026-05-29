import pygame
import sys
import time
import math
import json
import base64
import io
import os

try:
    from pydub import AudioSegment
except ImportError:
    print("Fehler: pydub nicht gefunden. (pip install pydub)")
    sys.exit()

# ---------------------------------------------------------
# KONSTANTEN
# ---------------------------------------------------------
JSON_PATH     = r"C:\Users\Tsyri\Desktop\SchlauerFisch\SchlauerFisch\output.json"
WIDTH, HEIGHT = 900, 500

BG_COLOR      = (30, 30, 30)
TEXT_COLOR    = (255, 255, 255)
ACTIVE_COLOR  = (255, 235, 59)
INACTIVE_COLOR= (60, 60, 60)
FISH_COLOR    = (46, 204, 113)
MOUTH_COLOR   = (20, 20, 20)

MOTOR_LABELS  = ["KOPF", "KÖRPER", "FLOSSE"]
MOTOR_COLORS  = [
    (52,  152, 219),   # Blau  – Kopf
    (46,  204, 113),   # Grün  – Körper
    (231, 76,  60),    # Rot   – Flosse
]

# ---------------------------------------------------------
# JSON LADEN & AUDIO ZUSAMMENBAUEN
# ---------------------------------------------------------
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def decode_blocks_to_audio(blocks):
    """Alle Base64-Audio-Blöcke zu einem einzigen AudioSegment zusammenführen."""
    combined = AudioSegment.empty()
    for block in blocks:
        raw = base64.b64decode(block["audio_base64"])
        segment = AudioSegment.from_file(io.BytesIO(raw), format="mp3")
        combined += segment
    return combined

def flatten_frames(blocks):
    """Alle motor_frames aus allen Blöcken hintereinander in eine Liste."""
    frames = []
    for block in blocks:
        fps_ms = block["fps_ms"]
        for frame in block["motor_frames"]:
            frames.append(frame)
    return frames, fps_ms

# ---------------------------------------------------------
# PYGAME VISUALISIERUNG
# ---------------------------------------------------------
def run_visualizer(json_path):
    print(f"Lade {json_path} ...")
    blocks = load_json(json_path)

    print("Dekodiere Audio ...")
    audio = decode_blocks_to_audio(blocks)

    # Audio als WAV in BytesIO für pygame
    audio_buffer = io.BytesIO()
    audio.export(audio_buffer, format="wav")
    audio_buffer.seek(0)

    motor_frames, fps_ms = flatten_frames(blocks)
    print(f"{len(motor_frames)} Frames geladen, {fps_ms}ms pro Frame.")

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🐟 Billy Bass – Motor Simulator")
    clock  = pygame.time.Clock()

    font       = pygame.font.SysFont("Arial",    28, bold=True)
    small_font = pygame.font.SysFont("monospace", 18)
    label_font = pygame.font.SysFont("Arial",    22, bold=True)

    pygame.mixer.init()
    pygame.mixer.music.load(audio_buffer)
    pygame.mixer.music.play()

    start_time = time.time()
    running    = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed   = time.time() - start_time
        frame_idx = int((elapsed * 1000) / fps_ms)

        if frame_idx >= len(motor_frames):
            running = False
            break

        frame = motor_frames[frame_idx]  # [kopf, körper, flosse]
        head_on, body_on, tail_on = frame[0], frame[1], frame[2]

        screen.fill(BG_COLOR)

        # --- FISCH ZEICHNEN ---
        cx, cy = 260, 220

        # Körper
        body_col = (ACTIVE_COLOR if body_on else FISH_COLOR)
        pygame.draw.ellipse(screen, body_col, (cx - 110, cy - 60, 220, 130))

        # Schwanz / Flosse
        tail_col = ACTIVE_COLOR if tail_on else (80, 160, 80)
        tail_points = [
            (cx + 110, cy),
            (cx + 175, cy - 55),
            (cx + 175, cy + 55),
        ]
        pygame.draw.polygon(screen, tail_col, tail_points)

        # Kopf
        head_col = ACTIVE_COLOR if head_on else FISH_COLOR
        pygame.draw.circle(screen, head_col, (cx - 90, cy), 65)

        # Auge
        pygame.draw.circle(screen, TEXT_COLOR, (cx - 110, cy - 20), 12)
        pygame.draw.circle(screen, (0, 0, 0),   (cx - 113, cy - 20),  5)

        # Mund
        mouth_open = body_on  # Mund = Körper-Motor als Proxy
        if mouth_open:
            pygame.draw.ellipse(screen, MOUTH_COLOR, (cx - 150, cy + 10, 55, 35))
        else:
            pygame.draw.line(screen, MOUTH_COLOR,
                             (cx - 150, cy + 25), (cx - 100, cy + 25), 5)

        # --- MOTOR STATUS BOXEN ---
        box_w, box_h = 160, 80
        box_y        = HEIGHT - 140
        total_w      = len(MOTOR_LABELS) * box_w + (len(MOTOR_LABELS) - 1) * 20
        start_x      = (WIDTH - total_w) // 2

        for i, (label, color) in enumerate(zip(MOTOR_LABELS, MOTOR_COLORS)):
            active   = bool(frame[i])
            box_x    = start_x + i * (box_w + 20)
            bg_color = color if active else INACTIVE_COLOR
            pygame.draw.rect(screen, bg_color,   (box_x, box_y, box_w, box_h), border_radius=12)
            pygame.draw.rect(screen, TEXT_COLOR, (box_x, box_y, box_w, box_h), 2, border_radius=12)

            txt = label_font.render(label, True, TEXT_COLOR)
            state_txt = font.render("AN" if active else "AUS", True,
                                    TEXT_COLOR if active else (120, 120, 120))

            screen.blit(txt,       (box_x + box_w // 2 - txt.get_width() // 2,       box_y + 10))
            screen.blit(state_txt, (box_x + box_w // 2 - state_txt.get_width() // 2, box_y + 40))

        # --- FRAME INFO ---
        info = small_font.render(
            f"Block-Frame {frame_idx} / {len(motor_frames)}   |   t = {elapsed:.2f}s",
            True, (150, 150, 150)
        )
        screen.blit(info, (20, 20))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Simulation beendet.")

if __name__ == "__main__":
    run_visualizer(JSON_PATH)