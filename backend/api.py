import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# Importiere die Hauptlogik aus deiner separaten Datei
from fetch import process_chat_message
from sst import transcribe_audio                #importiert die funktion zum transkipieren
from openclaw_starter import start_openclaw_gateway

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
        response_data = await process_chat_message(request.message)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verarbeitungsfehler: {str(e)}")


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR) # Geht eine Ebene nach oben
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

"""if __name__ == "__main__":
    # Startet den Uvicorn-Server direkt aus Python heraus
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)"""

if __name__ == "__main__":
    gateway_process = None
    try:
        # 1. Zuerst das OpenClaw-Gateway hochfahren
        gateway_process = start_openclaw_gateway()
        
        # 2. Danach API-Server starten
        print("-> Starte Uvicorn Server...")
        uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
        
    except KeyboardInterrupt:
        
        print("\n-> Server-Abbruch durch Benutzer (Strg+C).")
        
    finally:
        # 3. Wird garantiert ausgeführt, wenn Uvicorn beendet wird
        if gateway_process:
            print("-> Beende OpenClaw Gateway...")
            gateway_process.terminate()
            gateway_process.wait()
            print("-> OpenClaw erfolgreich beendet.")