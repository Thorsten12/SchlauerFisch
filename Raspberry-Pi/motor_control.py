import time
from gpiozero import PWMOutputDevice

# =========================================================
# 1. HARDWARE-KONFIGURATION (GPIO PINS)
# ==========================================
# HINWEIS: Passe die GPIO-Nummern (BCM-Zählung) an deine echte Verkabelung an!

# Mund-Motor Pins
MUND_FWD_PIN = 17    # Entspricht z.B. Mund öffnen (Wert 220 im Array)
MUND_BWD_PIN = 27    # Entspricht z.B. Mund aktiv schließen (Wert 180 im Array)

# Körper-Motor Pins
KOERPER_FWD_PIN = 22  # Entspricht Körper nach vorne/hoch (Wert 150 im Array)
KOERPER_BWD_PIN = 23  # Entspricht Körper zurück (falls genutzt)

# Initialisierung als PWM-Geräte (erlaubt feine Geschwindigkeitsstufen von 0.0 bis 1.0)
mund_fwd = PWMOutputDevice(MUND_FWD_PIN)
mund_bwd = PWMOutputDevice(MUND_BWD_PIN)
koerper_fwd = PWMOutputDevice(KOERPER_FWD_PIN)
koerper_bwd = PWMOutputDevice(KOERPER_BWD_PIN)


# =========================================================
# 2. BASIS-STEUERUNG
# =========================================================
def set_motors(m_fwd, m_bwd, k_fwd, k_bwd):
    """
    Erwartet Werte von 0.0 bis 1.0 und gibt sie an die Pins weiter.
    """
    mund_fwd.value = max(0.0, min(1.0, m_fwd))
    mund_bwd.value = max(0.0, min(1.0, m_bwd))
    koerper_fwd.value = max(0.0, min(1.0, k_fwd))
    koerper_bwd.value = max(0.0, min(1.0, k_bwd))

def stop_all():
    """Schaltet alle Motoren sofort stromlos."""
    mund_fwd.value = 0
    mund_bwd.value = 0
    koerper_fwd.value = 0
    koerper_bwd.value = 0


# =========================================================
# 3. TIMELINE-ABSPIELER (Wird vom HTTP-Server aufgerufen)
# =========================================================
def execute_timeline(motor_frames: list, fps_ms: int):
    """
    Spielt die vom Server berechneten Frames im richtigen Timing ab.
    """
    delay = fps_ms / 1000.0  # Umrechnung z.B. 50ms -> 0.05 Sekunden
    
    print(f"[Hardware] Starte Choreographie mit {len(motor_frames)} Frames...")
    
    try:
        for frame_data in motor_frames:
            # Info: Der Server schickt entweder eine Liste von Dictionaries (wie in testing.py)
            if isinstance(frame_data, dict):
                frame = frame_data["motor"]
            else:
                frame = frame_data
                
            # Werte von 0-255 auf 0.0-1.0 für PWM skalieren
            m_fwd = frame[0] / 255.0
            m_bwd = frame[1] / 255.0
            k_fwd = frame[2] / 255.0
            k_bwd = frame[3] / 255.0
            
            # Hardware ansteuern
            set_motors(m_fwd, m_bwd, k_fwd, k_bwd)
            
            # Warten bis zum nächsten Frame
            time.sleep(delay)
            
    except Exception as e:
        print(f"[Hardware] Fehler bei der Bewegungsausführung: {e}")
    finally:
        # AUS SICHERHEIT: Am Ende (oder bei Abbruch) Motoren IMMER abschalten!
        stop_all()
        print("[Hardware] Choreographie beendet. Motoren sicher gestoppt.")


# =========================================================
# 4. DIREKTER HARDWARE-TEST (Ohne Netzwerk)
# =========================================================
if __name__ == "__main__":
    print("Führe lokalen Hardware-Trockentest aus (3 Sekunden Mund-Aktivität)...")
    
    # Wir simulieren ein paar Testframes (Mund auf, Mund zu, Mund auf)
    test_frames = [
        [220, 0, 150, 0], # Mund auf, Körper vor
        [220, 0, 150, 0],
        [0, 180, 0, 0],   # Mund zu
        [0, 180, 0, 0],
        [220, 0, 0, 0],   # Nur Mund auf
        [0, 0, 0, 0]      # Stop
    ]
    
    # Test ausführen mit 500ms pro Schritt, damit man es gut sieht
    execute_timeline(test_frames, fps_ms=500)