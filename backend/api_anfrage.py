from openai import OpenAI
import json
from pathlib import Path

# 1. Haupt-Ordner definieren
CURRENT_DIR = Path(__file__).resolve().parent  # Das ist der Ordner "backend"
DATA_DIR = CURRENT_DIR.parent / "data"         # Das ist der Ordner "data"

# Den data-Ordner zur Sicherheit erstellen, falls er fehlt
DATA_DIR.mkdir(exist_ok=True)

# 2. Die Pfade richtig zuweisen:
config_pfad = CURRENT_DIR / "config.json"  # <-- Bleibt im "backend"-Ordner!
prompt_pfad = DATA_DIR / "prompt.json"     # <-- Geht in den "data"-Ordner!

# 3. Variablen vorher leer definieren
OPENROUTER_API_KEY = ""
SYSTEM_PROMPT = "Antworte kurz und präzise." # Fallback

# 4. Config laden (aus backend/config.json)
if config_pfad.exists():
    with open(config_pfad, "r", encoding="utf-8") as file:
        config_data = json.load(file)
        OPENROUTER_API_KEY = config_data.get("api", "") 
else:
    print(f"Warnung: config.json wurde nicht gefunden unter: {config_pfad}")

# 5. Prompt laden (aus data/prompt.json)
if prompt_pfad.exists():
    with open(prompt_pfad, "r", encoding="utf-8") as file:
        prompt_data = json.load(file)
        SYSTEM_PROMPT = prompt_data.get("prompt", SYSTEM_PROMPT)
else:
    print(f"Warnung: prompt.json wurde nicht gefunden unter: {prompt_pfad}")

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