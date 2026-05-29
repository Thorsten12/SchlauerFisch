from openai import OpenAI
import json
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Baue die absoluten Pfade zu den JSON-Dateien
config_pfad = os.path.join(CURRENT_DIR, "config.json")
prompt_pfad = os.path.join(CURRENT_DIR, "prompt.json")

# Prüfen, ob die Datei existiert, um Abstürze zu vermeiden
if os.path.exists(config_pfad):
    with open(config_pfad, "r", encoding="utf-8") as file:
        config_data = json.load(file)
        # Den Wert vom Schlüssel "api" auslesen
        OPENROUTER_API_KEY = config_data.get("api", "") 
else:
    print("Warnung: config.json wurde nicht gefunden!")

if os.path.exists(prompt_pfad):
    with open(prompt_pfad, "r", encoding="utf-8") as file:
        prompt_data = json.load(file)
        # Den Wert vom Schlüssel "prompt" auslesen
        SYSTEM_PROMPT = prompt_data.get("prompt", "")
else:
    print("Warnung: prompt.json wurde nicht gefunden!")

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
                {"role": "system", "content": SYSTEM_PROMPT},
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