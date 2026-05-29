import os
import json
from fastapi.concurrency import run_in_threadpool

# Importiere die Module für deine Datenverarbeitung
from fetch import process_chat_message
from api_anfrage import get_omini_response
from converter.text_to_audio import convert_txt_to_mp3
from converter.audio_to_object import process_audio_to_blocks

# STT-Modul aus dem converter-Ordner importieren
from converter.sst import transcribe_audio

async def process_text_pipeline(user_text: str) -> dict:
    """
    Kernlogik: Nimmt den erkannten/eingegebenen Text, fragt die KI, 
    generiert Audio und die Motor-Frames für den Fisch.
    """
    # 1. KI verarbeitet den Text
    ai_text = await run_in_threadpool(get_omini_response, user_text)

    if ai_text.startswith("Fehler:"):
        raise Exception(ai_text) 

    response_data = await process_chat_message(ai_text)
    print(f"AI-Text: {ai_text}")

    # 2. KI-Antwort in Audio umwandeln
    path = convert_txt_to_mp3(ai_text)
    print(f"Audio generiert unter: {path}")

    # 3. Motor-Frames für den Fisch berechnen
    data = process_audio_to_blocks(path, text=ai_text)
    print(f"Generierte Blöcke gesamt: {len(data)}")

    # 4. JSON-Daten abspeichern
    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    # TODO send to piCo

    # Fallback, falls 'text' im Frontend gebraucht wird
    if "text" not in response_data:
        response_data["text"] = ai_text

    return response_data

async def process_audio_pipeline(file_path: str) -> dict:
    """
    Logik für Sprachnachrichten: Wandelt Audio in Text um und übergibt 
    das Ergebnis an die Standard-Text-Pipeline.
    """
    print(f"Übergebe an STT-Modell: {file_path}")
    
    # 1. Speech-to-Text (Whisper) im Threadpool ausführen, um den Server nicht zu blockieren
    user_text = await run_in_threadpool(transcribe_audio, file_path)

    print(f"Erkannter Text aus Audio: {user_text}")

    if not user_text.strip():
        raise Exception("Audio war leer oder unverständlich.")

    # 2. An die normale Pipeline übergeben
    return await process_text_pipeline(user_text)