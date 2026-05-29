from openai import OpenAI
import json
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
DATA_DIR    = CURRENT_DIR.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

config_pfad = CURRENT_DIR / "config.json"
prompt_pfad = DATA_DIR    / "prompt.json"

OPENROUTER_API_KEY = ""
SYSTEM_PROMPT      = "Antworte kurz und präzise."

if config_pfad.exists():
    with open(config_pfad, "r", encoding="utf-8") as f:
        OPENROUTER_API_KEY = json.load(f).get("api", "")
else:
    print(f"Warnung: config.json nicht gefunden: {config_pfad}")

if prompt_pfad.exists():
    with open(prompt_pfad, "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = json.load(f).get("prompt", SYSTEM_PROMPT)
else:
    print(f"Warnung: prompt.json nicht gefunden: {prompt_pfad}")

MODEL_NAME = "deepseek/deepseek-v4-flash"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

MAX_HISTORY = 10  # Maximale Anzahl an User+Assistent Nachrichten die mitgeschickt werden

# Gesprächshistorie – wird pro Session im RAM gehalten
_history: list[dict] = []

def get_omini_response(user_input: str) -> str:
    """Sendet einen String an OpenRouter mit Gesprächshistorie und gibt die Antwort zurück."""
    global _history

    _history.append({"role": "user", "content": user_input})

    # History auf MAX_HISTORY kürzen (älteste raus, immer paarweise: user+assistant)
    if len(_history) > MAX_HISTORY:
        _history = _history[-MAX_HISTORY:]

    try:
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *_history
            ]
        )
        response = completion.choices[0].message.content
        _history.append({"role": "assistant", "content": response})
        return response

    except Exception as e:
        # Bei Fehler die letzte User-Nachricht wieder raus damit History konsistent bleibt
        _history.pop()
        return f"Fehler: {str(e)}"

def clear_history():
    """Setzt die Gesprächshistorie zurück – z.B. bei neuem Gespräch."""
    global _history
    _history = []