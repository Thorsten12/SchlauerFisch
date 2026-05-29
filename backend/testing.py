import pygame
import sys
import time
import math
import os
try:
    from pydub import AudioSegment
except ImportError:
    print("Fehler: pydub nicht gefunden. (pip install pydub)")
    sys.exit()

# ---------------------------------------------------------
# 1. AUDIO ANALYSE LOGIK
# ---------------------------------------------------------
def analyze_audio_to_frames(file_path, fps_ms=50, volume_threshold=-15.0):
    print(f"Lese Audio ein und berechne Frames für: {file_path} ...")
    try:
        audio = AudioSegment.from_file(file_path)
    except Exception as e:
        print(f"Fehler beim Laden der Audio-Datei: {e}")
        sys.exit()
    
    frames = []
    # Gehe in 50ms-Schritten durch das Audio
    for i in range(0, len(audio), fps_ms):
        chunk = audio[i:i + fps_ms]
        volume = -100 if math.isinf(chunk.dBFS) else chunk.dBFS
        
        body_fwd = 0
        body_bwd = 0
        
        # Schwellenwert-Logik
        if volume > volume_threshold:
            mouth_fwd = 220
            mouth_bwd = 0
            body_fwd = 150 
        else:
            mouth_fwd = 0
            mouth_bwd = 180
            
        # NEU: Wir speichern jetzt ein Dictionary, um die Lautstärke (volume)
        # an das Pygame-Fenster weiterzugeben
        frames.append({
            "motor": [mouth_fwd, mouth_bwd, body_fwd, body_bwd],
            "volume": volume
        })
        
    print(f"Fertig! {len(frames)} Frames berechnet.")
    return frames

# ---------------------------------------------------------
# 2. PYGAME VISUALISIERUNG MIT LIVE-PEGEL
# ---------------------------------------------------------
def run_visualizer(mp3_path, threshold=-15.0, fps_ms=50):
    if not os.path.exists(mp3_path):
        print(f"Datei '{mp3_path}' nicht gefunden!")
        return

    # Timeline im Voraus berechnen
    motor_frames = analyze_audio_to_frames(mp3_path, fps_ms, threshold)

    pygame.init()
    # Das Fenster etwas breiter machen für den Pegel
    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("🐟 Billy Bass - Live Volume Tracker")
    clock = pygame.time.Clock()
    
    font = pygame.font.SysFont("Arial", 24, bold=True)
    small_font = pygame.font.SysFont("monospace", 18)

    BG_COLOR = (30, 30, 30)
    FISH_COLOR = (46, 204, 113)
    MOUTH_COLOR = (20, 20, 20)
    TEXT_COLOR = (255, 255, 255)
    ACTIVE_COLOR = (255, 235, 59)
    VOL_COLOR = (52, 152, 219)

    pygame.mixer.init()
    pygame.mixer.music.load(mp3_path)
    pygame.mixer.music.play()
    
    start_time = time.time()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        elapsed = time.time() - start_time
        frame_idx = int((elapsed * 1000) / fps_ms)

        if frame_idx >= len(motor_frames):
            running = False
            break

        # Daten für den aktuellen Frame entpacken
        current_data = motor_frames[frame_idx]
        current_frame = current_data["motor"]
        current_volume = current_data["volume"]
        
        is_mouth_open = current_frame[0] > 0

        screen.fill(BG_COLOR)

        # --- FISCH ZEICHNEN (Linke Seite) ---
        center_x, center_y = WIDTH // 2 - 120, HEIGHT // 2 - 50
        pygame.draw.circle(screen, FISH_COLOR, (center_x, center_y), 100)
        pygame.draw.circle(screen, TEXT_COLOR, (center_x - 30, center_y - 40), 15)
        pygame.draw.circle(screen, (0, 0, 0), (center_x - 35, center_y - 40), 5)

        if is_mouth_open:
            pygame.draw.ellipse(screen, MOUTH_COLOR, (center_x - 80, center_y + 10, 80, 60))
            status_text = "🗣️ MUND AUF"
            status_color = ACTIVE_COLOR
        else:
            pygame.draw.line(screen, MOUTH_COLOR, (center_x - 80, center_y + 40), (center_x, center_y + 40), 8)
            status_text = "🤐 MUND ZU"
            status_color = TEXT_COLOR

        # --- LIVE PEGEL-METER ZEICHNEN (Rechte Seite) ---
        # Wir definieren eine Skala von -50 dB (leise) bis 0 dB (maximal)
        bar_x = WIDTH - 300
        bar_y_start = 50
        bar_width = 40
        bar_max_height = 250
        
        # Hintergrund des Pegels (Dunkelgrau)
        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y_start, bar_width, bar_max_height))
        
        # Berechne, wie hoch der Pegel gerade ausschlagen muss
        display_vol = max(-50, min(0, current_volume)) # Limitiere optisch zwischen -50 und 0
        vol_percent = (display_vol + 50) / 50.0 
        
        current_bar_height = int(bar_max_height * vol_percent)
        current_bar_y = bar_y_start + (bar_max_height - current_bar_height)
        
        # Der Balken wird gelb, wenn er über den Threshold schießt
        bar_color = ACTIVE_COLOR if current_volume > threshold else VOL_COLOR
        pygame.draw.rect(screen, bar_color, (bar_x, current_bar_y, bar_width, current_bar_height))

        # Rote Schwellenwert-Linie (Threshold) einzeichnen
        thresh_percent = (threshold + 50) / 50.0
        thresh_y = bar_y_start + (bar_max_height - int(bar_max_height * thresh_percent))
        pygame.draw.line(screen, (255, 50, 50), (bar_x - 15, thresh_y), (bar_x + bar_width + 15, thresh_y), 3)

        # --- TEXTE RENDERN ---
        # Fisch-Status
        txt_status = font.render(status_text, True, status_color)
        txt_array = small_font.render(f"Array: {current_frame}", True, (200, 200, 200))
        
        # Pegel-Status (Direkt neben dem Balken)
        txt_vol = font.render(f"{current_volume:.1f} dB", True, bar_color)
        txt_thresh = small_font.render(f"Schwelle: {threshold} dB", True, (255, 100, 100))

        # Texte auf dem Bildschirm platzieren
        screen.blit(txt_status, (center_x - txt_status.get_width() // 2, HEIGHT - 130))
        screen.blit(txt_array, (center_x - txt_array.get_width() // 2, HEIGHT - 90))
        
        # Damit die dB-Zahl mit dem Pegel mitwandert:
        text_y_pos = current_bar_y - 15 if current_volume > -49 else bar_y_start + bar_max_height - 20
        screen.blit(txt_vol, (bar_x + 60, text_y_pos))
        screen.blit(txt_thresh, (bar_x + 60, thresh_y - 10))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    print("Test beendet.")

if __name__ == "__main__":
    # HIER den Namen deiner MP3-Datei anpassen
    MEINE_AUDIO_DATEI = "speaker_0.mp3" 
    
    # Justiere diesen Wert, wenn der Mund zu oft/selten aufgeht
    MEIN_SCHWELLENWERT = -20.0 
    
    run_visualizer(MEINE_AUDIO_DATEI, threshold=MEIN_SCHWELLENWERT)