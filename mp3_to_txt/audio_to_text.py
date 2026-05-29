import torch
import librosa
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq
from tqdm import tqdm

print("1/3: Lade Modell (openai/whisper-small)...")
model_id = "openai/whisper-small"
processor = AutoProcessor.from_pretrained(model_id)
model = AutoModelForSpeechSeq2Seq.from_pretrained(model_id)

# Optional: Beschleunigung, falls du eine Grafikkarte hast
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = model.to(device)

# Hier den Namen deiner Datei eintragen
audio_pfad = "Die Prinzessin auf der Erbse.mp3" 
print(f"2/3: Lade Audiodatei...")

# librosa lädt die komplette Datei in den Arbeitsspeicher
audio_array, sampling_rate = librosa.load(audio_pfad, sr=16000)

# Manuelles Zerschneiden in 30-Sekunden-Blöcke
chunk_length_s = 30 
chunk_size = chunk_length_s * sampling_rate
total_chunks = (len(audio_array) + chunk_size - 1) // chunk_size

fertiger_text = []

# Damit zwingen wir das Modell, auf Deutsch zu bleiben
forced_decoder_ids = processor.get_decoder_prompt_ids(language="german", task="transcribe")

print("3/3: Starte Transkription...")
for i in tqdm(range(0, len(audio_array), chunk_size), total=total_chunks, desc="Fortschritt"):
    
    # Aktuellen Block ausschneiden
    chunk = audio_array[i : i + chunk_size]
    
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

# Speichern
ausgabe_datei = "fertiger_text.txt"
with open(ausgabe_datei, "w", encoding="utf-8") as f:
    f.write(end_resultat)

print(f"\nFertig! Dein komplettes Audio wurde transkribiert und in '{ausgabe_datei}' gespeichert.")