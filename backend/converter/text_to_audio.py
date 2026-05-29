import subprocess
import sys
import re
from pathlib import Path

def convert_txt_to_mp3(raw_text):
    BASE_DIR = Path(__file__).resolve().parent
    model_path = (BASE_DIR.parent.parent / ".model" / "de_DE-thorsten_emotional-medium.onnx").resolve()
    output_mp3_path = BASE_DIR / "ausgabe.mp3" # könntem an noch in Data machen

    # --- EMOTION AUSLESEN ---
    emotion_match = re.match(r'^\[(\d+)\]', raw_text)
    if emotion_match:
        speaker_id = int(emotion_match.group(1))
        if not (0 <= speaker_id <= 7):
            speaker_id = 4
        raw_text = raw_text[emotion_match.end():].strip()
    else:
        speaker_id = 4

    # --- TEXT BEREINIGEN ---
    raw_text = raw_text.replace('[PAUSE]', ' ... ')
    clean_text = re.sub(r'\[.*?\]', '', raw_text).strip()

    print(f"Generiere MP3-Audio (Emotion/Speaker ID: {speaker_id})...")

    piper_command = [
        sys.executable, "-m", "piper",
        "--model", str(model_path),
        "--output-raw",
        "--speaker", str(speaker_id)
    ]
    ffmpeg_command = [
        "ffmpeg",
        "-y",
        "-f", "s16le",
        "-ar", "22050",
        "-ac", "1",
        "-i", "pipe:0",
        "-af", "adelay=1000|1000",  # ← Fix: Stereo-safe (beide Kanäle)
        "-b:a", "128k",
        str(output_mp3_path)
    ]

    try:
        piper_process = subprocess.Popen(
            piper_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # ✅ Fix 1: Text ZUERST senden und stdin schließen
        piper_stdout, piper_stderr = piper_process.communicate(
            input=clean_text.encode("utf-8")
        )

        if piper_process.returncode != 0:
            print(f"Piper Fehler:\n{piper_stderr.decode('utf-8', errors='replace')}")
            return output_mp3_path

        if not piper_stdout:
            print("Fehler: Piper hat keine Audiodaten ausgegeben!")
            return output_mp3_path

        print(f"Piper hat {len(piper_stdout)} Bytes Rohdaten generiert.")

        # ✅ Fix 2: FFmpeg bekommt die fertigen Piper-Daten
        ffmpeg_process = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, ffmpeg_stderr = ffmpeg_process.communicate(input=piper_stdout)

        if ffmpeg_process.returncode == 0:
            print(f"Erfolgreich: Audio gespeichert unter '{output_mp3_path}'.")
        else:
            print(f"FFmpeg Fehler:\n{ffmpeg_stderr.decode('utf-8', errors='replace')}")

    except FileNotFoundError:
        print("Kritischer Fehler: 'ffmpeg' wurde im System nicht gefunden.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    return output_mp3_path