import torch
import librosa
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from tqdm import tqdm

#Model initalisieren
print("Initialisiere STT-Modell (openai/whisper-small)...")
model_id = "openai/whisper-small"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)

# Optional: Beschleunigung, falls eine Grafikkarte vorhanden ist
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Zwingt das Modell, auf Deutsch zu bleiben
forced_decoder_ids = processor.get_decoder_prompt_ids(language="german", task="transcribe")
print("✅ STT-Modell erfolgreich geladen und bereit!")




#Hauptfunktion um in api.py zu funktionieren

import subprocess
import os
# librosa, torch, tqdm etc. bleiben natürlich auch importiert

def transcribe_audio(audio_pfad: str) -> str:
    """
    Nimmt den Pfad zu einer Audiodatei, transkribiert sie in 30s-Blöcken
    und gibt den kompletten Text als String zurück.
    """
    print(f"Lade Audiodatei für Transkription: '{audio_pfad}'...")
    
    # --- NEU: KONVERTIERUNG VON WEBM ZU WAV ---
    # Wir erstellen einen neuen Dateinamen, der auf .wav endet
    wav_pfad = audio_pfad.replace(".webm", ".wav")
    
    # FFmpeg wandelt die Datei lautlos im Hintergrund in sauberes 16kHz Mono-Audio um
    subprocess.run([
        "ffmpeg", "-y", "-i", audio_pfad, 
        "-ar", "16000", "-ac", "1", 
        wav_pfad
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    # ------------------------------------------

    # librosa lädt jetzt die SAUBERE .wav Datei in den Arbeitsspeicher (nicht mehr die .webm)
    audio_array, sampling_rate = librosa.load(wav_pfad, sr=16000)
    
    # Optional aber sauber: Die temporäre .wav Datei direkt wieder löschen, 
    # da wir das Audio jetzt komplett im Arbeitsspeicher (audio_array) haben.
    if os.path.exists(wav_pfad):
        os.remove(wav_pfad)

    # Manuelles Zerschneiden in 30-Sekunden-Blöcke
    chunk_length_s = 30 
    chunk_size = chunk_length_s * sampling_rate
    total_chunks = (len(audio_array) + chunk_size - 1) // chunk_size

    fertiger_text = []

    print("Starte Transkription...")
    # Dein Ladebalken läuft weiterhin wunderschön in der Konsole!
    for i in tqdm(range(0, len(audio_array), int(chunk_size)), total=int(total_chunks), desc="Fortschritt"):
        
        # Aktuellen Block ausschneiden
        chunk = audio_array[i : i + int(chunk_size)]
        
        # Für das Modell vorbereiten
        inputs = processor(chunk, sampling_rate=sampling_rate, return_tensors="pt").to(device)
        
        # Generieren mit fest eingestellter Sprache (Deutsch)
        with torch.no_grad():
            predicted_ids = model.generate(
                inputs.input_features,
                forced_decoder_ids=forced_decoder_ids
            )
            
        # Zahlen in Text umwandeln und zur Liste hinzufügen
        text = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]
        fertiger_text.append(text.strip())

    # Alle Blöcke zu einem langen Text zusammenfügen
    end_resultat = " ".join(fertiger_text)
    
    print(f"✅ Transkription abgeschlossen!")
    
    # Wir geben den Text ZURÜCK an denjenigen, der die Funktion gerufen hat
    return end_resultat