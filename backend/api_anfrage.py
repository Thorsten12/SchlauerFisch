from openai import OpenAI
import json
import os

# Prüfen, ob die Datei existiert, um Abstürze zu vermeiden
if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as file:
        config_data = json.load(file)
        # Den Wert vom Schlüssel "api" auslesen
        OPENROUTER_API_KEY = config_data.get("api", "") 
else:
    print("Warnung: config.json wurde nicht gefunden!")

# 1. Konfiguration
MODEL_NAME = "deepseek/deepseek-v4-flash"

# 2. Client Setup
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
)

def get_omini_response(user_input: str) -> str:
    """Sendet einen String an OpenRouter und gibt die Antwort als String zurück."""
    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Antworte kurz und präzise."},
                {"role": "user", "content": user_input}
            ]
        )
        # Extrahiert den reinen Text-String
        return completion.choices[0].message.content
    except Exception as e:
        return f"Fehler: {str(e)}"

# --- Beispiel für die Nutzung ---
"""if _name_ == "_main_":
    frage = "Wer bist du?"
    antwort = get_omini_response(frage)
    
    # Gibt nur den nackten String aus
    print(antwort)"""