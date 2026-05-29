import asyncio
import base64
import httpx  # Für die HTTP-Anfrage an den Raspberry Pi

# Trage hier die lokale IP-Adresse deines Raspberry Pi ein
RASPBERRY_PI_URL = "http://192.168.178.X:5000/execute" 

async def generate_llm_reply(user_input: str) -> str:
    """Schritt 1: Text to Text (LLM)"""
    await asyncio.sleep(1) # Platzhalter
    return f"Fischige Antwort auf: {user_input}"

async def generate_audio_and_frames(text: str) -> dict:
    """Schritt 2: Text to Speech und Motor-Timeline berechnen"""
    await asyncio.sleep(1) # Platzhalter
    
    dummy_audio_bytes = b"fisch_geraeusche_platzhalter"
    encoded_audio = base64.b64encode(dummy_audio_bytes).decode("utf-8")
    
    return {
        "audio_base64": encoded_audio,
        "fps_ms": 50,
        "motor_frames": [
            [220, 0, 150, 0], # [MundUpSpeed, MundDownSpeed, KörperUpSpeed, KörperDownSpeed]
            [0, 180, 0, 255], 
            [0, 0, 0, 0]
        ]
    }

async def send_to_raspberry(media_data: dict):
    """
    Sendet das fertige Paket asynchron an den Raspberry Pi.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Sendet das JSON an den Pi (Timeout von 5 Sekunden)
            response = await client.post(RASPBERRY_PI_URL, json=media_data, timeout=5.0)
            response.raise_for_status()
            print("Erfolg: Paket an Raspberry Pi gesendet!")
    except Exception as e:
        print(f"Fehler bei der Kommunikation mit dem Raspberry Pi: {e}")

async def process_chat_message(user_message: str) -> dict:
    """
    Orchestriert den Ablauf und antwortet dem Frontend.
    """
    # 1. Antwort vom Text-Modell holen
    reply_text = await generate_llm_reply(user_message)
    
    # 2. Audio und Bewegung generieren
    media_data = await generate_audio_and_frames(reply_text)
    
    # 3. Fire-and-Forget: Paket an den Raspberry Pi senden, 
    # OHNE dass das Frontend darauf warten muss.
    #asyncio.create_task(send_to_raspberry(media_data))
    
    # 4. NUR den reinen Text an das Frontend (script.js) zurückgeben
    return {
        "reply": reply_text
    }