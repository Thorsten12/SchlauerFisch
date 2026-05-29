import subprocess
import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.parent.parent / "data"

audio_output_path = DATA_DIR / "ausgabe.mp3"
model_path = (BASE_DIR.parent.parent / ".model" / "de_DE-thorsten_emotional-medium.onnx").resolve()

def convert_txt_to_mp3(raw_text):

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
    # 0. Geschütztes Leerzeichen reparieren (NBSP)
    clean_text = raw_text.replace('\u00A0', ' ')

    # 0b. Umlaute ersetzen damit Piper sie nicht buchstabiert
    UMLAUT_MAP = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
        'ß': 'ss',
    }
    for umlaut, replacement in UMLAUT_MAP.items():
        clean_text = clean_text.replace(umlaut, replacement)

    # 1. Pausen-Tokens in echte Satzzeichen umwandeln
    clean_text = clean_text.replace('[PAUSE]', ' ... ')

    # 1b. ! und ? → Punkt damit Piper nach jedem Satzende pausiert
    clean_text = clean_text.replace('!', '. ')
    clean_text = clean_text.replace('?', '. ')

    # 2. Alle restlichen eckigen Klammern (z.B. [NEIN], [LACHEN]) entfernen
    clean_text = re.sub(r'\[.*?\]', '', clean_text)

    # 3. Gedankenstriche in Komma umwandeln
    clean_text = re.sub(r'[\u002D\u2013\u2014\u2212]+', ', ', clean_text)

    # 3b. Sonderzeichen die Piper buchstabiert – normalisieren oder löschen
    clean_text = clean_text.replace('~', '')
    clean_text = clean_text.replace('§', '')
    clean_text = clean_text.replace('^', '')
    clean_text = clean_text.replace('|', ',')
    clean_text = clean_text.replace('/', ' ')
    clean_text = clean_text.replace('\\', '')
    clean_text = clean_text.replace('%', ' Prozent')
    clean_text = clean_text.replace('&', ' und ')
    clean_text = clean_text.replace('@', ' at ')
    clean_text = clean_text.replace('=', ' ')
    clean_text = clean_text.replace('+', ' ')
    clean_text = clean_text.replace('<', '')
    clean_text = clean_text.replace('>', '')
    clean_text = clean_text.replace('*', '')
    clean_text = clean_text.replace('#', '')
    clean_text = clean_text.replace('`', '')
    clean_text = clean_text.replace('°', ' Grad')

    # 4. Typografische Apostrophe normalisieren
    clean_text = clean_text.replace('\u2019', "'")

    # Typografische Anführungszeichen entfernen
    clean_text = re.sub(r'[\u201E\u201C\u201D\u00AB\u00BB]', '', clean_text)

    # 5. Markdown-Formatierungen und Zeilenumbrüche entfernen
    clean_text = re.sub(r'[*_#]+', '', clean_text)
    clean_text = clean_text.replace('\n', ' ').replace('\r', '')

    # 6. DER STAUBSAUGER – ! und ? schon ersetzt, daher nicht mehr erlaubt
    clean_text = re.sub(r'[^a-zA-Z0-9\s.,\']', '', clean_text)

    # 7. Überflüssige Leerzeichen reduzieren und Ränder säubern
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()

    print(f"Reinigter Text: {clean_text}")

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
        "-af", "adelay=1000|1000",
        "-b:a", "128k",
        str(audio_output_path)
    ]

    try:
        piper_process = subprocess.Popen(
            piper_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        piper_stdout, piper_stderr = piper_process.communicate(
            input=clean_text.encode("utf-8")
        )

        if piper_process.returncode != 0:
            print(f"Piper Fehler:\n{piper_stderr.decode('utf-8', errors='replace')}")
            return audio_output_path

        if not piper_stdout:
            print("Fehler: Piper hat keine Audiodaten ausgegeben!")
            return audio_output_path

        print(f"Piper hat {len(piper_stdout)} Bytes Rohdaten generiert.")

        ffmpeg_process = subprocess.Popen(
            ffmpeg_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        _, ffmpeg_stderr = ffmpeg_process.communicate(input=piper_stdout)

        if ffmpeg_process.returncode == 0:
            print(f"Erfolgreich: Audio gespeichert unter '{audio_output_path}'.")
        else:
            print(f"FFmpeg Fehler:\n{ffmpeg_stderr.decode('utf-8', errors='replace')}")

    except FileNotFoundError:
        print("Kritischer Fehler: 'ffmpeg' wurde im System nicht gefunden.")
    except Exception as e:
        print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")

    return str(audio_output_path)