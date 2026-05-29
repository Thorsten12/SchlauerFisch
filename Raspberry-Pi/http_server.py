from flask import Flask, request, jsonify
import os
import base64
import motor_control

app = Flask(__name__)

AUDIO_FILE_PATH = "received_speech.wav"

@app.route('/execute', methods=['POST'])
def execute_fish():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "Keine Daten empfangen"}), 400
    
    # 1. Audio-Daten extrahieren
    audio_base64 = data.get("audio_base64")
    # 2. Motor-Befehle extrahieren
    fps_ms = data.get("fps_ms", 50)
    motor_frames = data.get("motor_frames", [])

    # 3. AUDIO VERARBEITEN (Falls Audiodaten mitgeschickt wurden)
    if audio_base64:
        try:
            # Base64-Text wieder in echte Audio-Bytes umwandeln
            audio_bytes = base64.b64decode(audio_base64)
            
            # Als lokale WAV/MP3-Datei auf dem Pi speichern
            with open(AUDIO_FILE_PATH, "wb") as f:
                f.write(audio_bytes)
                
            print("[Server] Audio erfolgreich empfangen und gespeichert.")
            
            # --- AUDIO ABSPIELEN ---
            # 'aplay' ist auf dem Pi für WAV-Dateien standardmäßig installiert.
            # Das '&' am Ende sorgt dafür, dass der Befehl den Code nicht blockiert!
            os.system(f"aplay {AUDIO_FILE_PATH} &")
            
        except Exception as e:
            print(f"[Server] Fehler bei der Audio-Verarbeitung: {e}")
            
    # 4. MOTOREN STARTEN (Parallel zum Sound)
    if motor_frames:
        motor_control.execute_timeline(motor_frames, fps_ms)
    else:
        print("[Server] Keine Motor-Frames im Paket enthalten.")
    
    return jsonify({"status": "success", "message": "Choreographie ausgeführt :)"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)