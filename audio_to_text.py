import torch
import librosa
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

#Model Laden
print("Lade Modell...")
processor = AutoProcessor.from_pretrained("Hanhpt23/whisper-medium-GermanMed-v1")
model = AutoModelForSpeechSeq2Seq.from_pretrained("Hanhpt23/whisper-medium-GermanMed-v1")

#Audiodatei laden
audio_pfad = "Die Prinzessin auf der Erbse.mp3" 
print(f"Lade Audiodatei: {audio_pfad}")

audio_array, sampling_rate = librosa.load(audio_pfad, sr=16000)

inputs = processor(audio_array, sampling_rate=sampling_rate, return_tensors="pt")


print("Transkribiere...")
with torch.no_grad():
    predicted_ids = model.generate(inputs.input_features)

transkription = processor.batch_decode(predicted_ids, skip_special_tokens=True)[0]

#in .txt-Datei speichern
ausgabe_datei = "fertige_transkript.txt"
with open(ausgabe_datei, "w", encoding="utf-8") as f:
    f.write(transkription)

print(f"Fertig! Dein Text wurde in '{ausgabe_datei}' gespeichert.")