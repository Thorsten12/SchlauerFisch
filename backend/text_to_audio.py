import subprocess
import sys
import re
from pathlib import Path

def convert_txt_to_mp3(txt_file_path, model_path, output_mp3_path):
    # 1. Text einlesen
    try:
        with open(txt_file_path, "r", encoding="utf-8") as file:
            raw_text = file.read().strip()
    except FileNotFoundError:
        print(f"Fehler: Die Datei '{txt_file_path}' wurde nicht gefunden.")
        return
        
    if not raw_text:
        print("Fehler: Der Text ist leer. Generierung abgebrochen.")
        return

    # --- EMOTION AUSLESEN ---
    emotion_match = re.match(r'^\[(\d+)\]', raw_text)
    
    if emotion_match:
        speaker_id = int(emotion_match.group(1))
        if not (0 <= speaker_id <= 7):
            speaker_id = 4
        raw_text = raw_text[emotion_match.end():].strip()
    else:
        speaker_id = 4 

    # --- NEU: TEXT BEREINIGEN & PAUSEN VERARBEITEN ---
    # 1. [PAUSE] durch Punkte ersetzen, damit Piper eine kurze Pause macht
    raw_text = raw_text.replace('[PAUSE]', ' ... ')
    
    # 2. Entfernt restliche Action-Tags wie [FREUEN] oder [NEIN]
    clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()
    
    print(f"Generiere MP3-Audio (Emotion/Speaker ID: {speaker_id})...")
    
    # 2. Befehl für Piper
    piper_command = [
        sys.executable, "-m", "piper",
        "--model", str(model_path),
        "--output-raw", 
        "--speaker", str(speaker_id)
    ]

    # 3. Befehl für FFmpeg (Mit Audiofilter für 1 Sekunde Verzögerung)
    ffmpeg_command = [
        "ffmpeg",
        "-y",                  
        "-f", "s16le",         
        "-ar", "22050",        
        "-ac", "1",            
        "-i", "pipe:0",  
        "-af", "adelay=1000",  # NEU: Verzögert den Audio-Start um 1000 ms (1 Sekunde)
        "-b:a", "128k",        
        str(output_mp3_path)
    ]
    
    try:
        # 4. Verknüpfung der beiden Prozesse (Piping)
        piper_process = subprocess.Popen(
            piper_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        ffmpeg_process = subprocess.Popen(
            ffmpeg_command,
            stdin=piper_process.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        piper_process.stdout.close()

        # 5. BEREINIGTEN Text übergeben und Input-Kanal schließen
        piper_process.stdin.write(clean_text.encode("utf-8"))
        piper_process.stdin.close()

        # 6. Warten, bis FFmpeg fertig ist
        ffmpeg_process.communicate()

        if ffmpeg_process.returncode == 0:
            print(f"Erfolgreich: Audio wurde unter '{output_mp3_path}' gespeichert.")
        else:
            print("Fehler: FFmpeg konnte die MP3-Datei nicht korrekt erstellen.")
            
    except FileNotFoundError:
         print("Kritischer Fehler: 'ffmpeg' wurde im System nicht gefunden.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

# --- Ausführung ---
if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent

    EINGABE_TEXT = BASE_DIR / "mein_text.txt"
    MODELL_DATEI = BASE_DIR / ".." / ".model" / "de_DE-thorsten_emotional-medium.onnx"
    AUSGABE_AUDIO = BASE_DIR / "ausgabe.mp3" 

    convert_txt_to_mp3(EINGABE_TEXT, MODELL_DATEI, AUSGABE_AUDIO)