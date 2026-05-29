import os
import sys
import json
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.concurrency import run_in_threadpool # Wichtig für synchrone Funktionen
from flask import json
from pydantic import BaseModel
import uvicorn
import traceback

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Pfade zu den Unterordnern bauen
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
CONVERTER_DIR = os.path.join(BASE_DIR, "backend", "converter")

#Python-Suchpfad hinzufügen
sys.path.append(BACKEND_DIR)
sys.path.append(CONVERTER_DIR)


# Importiere die Hauptlogik aus deiner separaten Datei
from fetch import process_chat_message
#from sst import transcribe_audio                #importiert die funktion zum transkipieren
from api_anfrage import get_omini_response

from text_to_audio import convert_txt_to_mp3
from audio_to_object import process_audio_to_blocks

#from openclaw_starter import start_openclaw_gateway

app = FastAPI(title="Billy Bass API")

# Definiere die Struktur der eingehenden Anfrage
class ChatRequest(BaseModel):
    message: str

# 1. API-Routen ZUERST definieren
@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Nimmt die Nachricht vom Frontend entgegen, leitet sie an die 
    Logik weiter und gibt das finale JSON (Text, Audio, Motor-Frames) zurück.
    """
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Nachricht darf nicht leer sein.")

    try:
        ai_text = await run_in_threadpool(get_omini_response, request.message)

        if ai_text.startswith("Fehler:"):
            raise HTTPException(status_code=502, detail=ai_text)

        response_data = await process_chat_message(ai_text)

        print(f"AI-Text: {ai_text}")

        path = convert_txt_to_mp3(ai_text)

        print(f"Audio generiert unter: {path}")

        data = process_audio_to_blocks(path, text=ai_text)

        print(f"Generierte Blöcke gesamt: {len(data)}")

        json.dump(data, open("output.json", "w"), indent=4) # Speichert die Daten in output.json
        # TODO send to piCo

        return response_data
    
    except Exception as e:
        # Das hier zwingt Python, den EXAKTEN Fehler rot ins Terminal zu drucken!
        print("\n--- HIER IST DER WAHRE FEHLER ---")
        traceback.print_exc() 
        print("---------------------------------\n")
        
        raise HTTPException(status_code=500, detail=f"Verarbeitungsfehler: {str(e)}")


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(CURRENT_DIR, "frontend") 

app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    # Startet den Uvicorn-Server direkt aus Python heraus
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
