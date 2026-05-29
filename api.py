import os
import sys
import shutil
from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
CONVERTER_DIR = os.path.join(BACKEND_DIR, "converter")

sys.path.append(BACKEND_DIR)
sys.path.append(CONVERTER_DIR)

# Importiere die ausgelagerte Logik
from backend.processing import process_text_pipeline, process_audio_pipeline

app = FastAPI(title="Billy Bass API")

class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    """Verarbeitet getippte Nachrichten vom Frontend."""
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Nachricht darf nicht leer sein.")

    try:
        response_data = await process_text_pipeline(request.message)
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verarbeitungsfehler: {str(e)}")

@app.post("/api/upload-audio")
async def upload_audio_endpoint(audio: UploadFile = File(...)):
    """Verarbeitet eingesprochene Nachrichten vom Frontend."""
    temp_file_path = os.path.join(BACKEND_DIR, "temp_recording.webm")
    
    try:
        # Audio temporär speichern
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)
        
        # Audio-Pipeline aufrufen
        response_data = await process_audio_pipeline(temp_file_path)
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio-Verarbeitungsfehler: {str(e)}")
    
    finally:
        audio.file.close()
        # Optional: Speicherplatz freigeben, wenn STT abgeschlossen ist
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Frontend einbinden
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend") 
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)