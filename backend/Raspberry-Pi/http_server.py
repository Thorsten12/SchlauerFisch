from flask import Flask, request, jsonify
import base64

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute_fish():
    data = request.json
    
    # 1. Audio-Daten extrahieren
    audio_base64 = data.get("audio_base64")
    # 2. Motor-Befehle extrahieren
    fps_ms = data.get("fps_ms")
    motor_frames = data.get("motor_frames")
    
    # HIER kommt dein Code ins Spiel:
    # - Audio decodieren und abspielen
    # - Durch die motor_frames loopen und GPIO-Pins ansteuern
    
    print(f"Empfangen: {len(motor_frames)} Bewegungsframes mit {fps_ms}ms Takt.")
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)