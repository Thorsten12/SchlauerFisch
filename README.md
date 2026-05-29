# Big Mouth Billy Bass - AI Lip-Sync System

![Rotating Fish](https://i.gifer.com/WiC8.gif)

## Beschreibung
Dieses Projekt ist ein KI-gesteuertes Animatronik-System, das einem klassischen "Big Mouth Billy Bass" das Sprechen beibringt. Das System generiert Textantworten über ein LLM (angebunden über OpenClaw), erstellt daraus Audio-Dateien und berechnet die Amplituden, um lippensynchrone Motorsteuerungs-Frames zu generieren. 

Um Latenzen zu minimieren und die Hardware zu entlasten, ist das Projekt in ein ressourcenintensives Backend (Laptop/Server) und einen reinen Ausführungs-Client (Raspberry Pi) unterteilt.

## Systemarchitektur

### 1. Frontend (Web-Interface)
Eine HTML/JS-basierte Benutzeroberfläche zur Eingabe von Prompts. Kommuniziert asynchron mit dem Backend. Das Frontend zeigt den aktuellen Verarbeitungsstatus an und erhält nach Abschluss der Berechnung den reinen Antworttext.

### 2. Backend (Laptop/Lokaler Server)
Ein FastAPI-Server in Python, der die gesamte Logik bündelt.
* Empfängt die Textanfrage aus dem Frontend.
* Holt die inhaltliche Antwort via OpenClaw/LLM.
* Generiert die entsprechende Audiodatei (Text-to-Speech).
* Zerschneidet das Audio in 50-Millisekunden-Blöcke (Frames) und analysiert die Lautstärke (dBFS), um die exakten PWM-Werte für die Motorsteuerung zu berechnen.
* Sendet ein fertiges JSON-Paket (Audio + motor_frames) per HTTP-Request an den Raspberry Pi.
* Gibt den Text an das Frontend zurück.

### 3. Ausführungs-Client (Raspberry Pi)
Ein minimalistisches Empfänger-Skript, das als Webserver agiert.
* Wartet auf das JSON-Paket vom Backend.
* Dekodiert die Base64-Audiodatei.
* Spielt die Audiodatei ab und steuert simultan die GPIO-Pins für die H-Brücke an, um die DC-Motoren des Fisches (Mund und Körper) strikt synchron zur Audiospur zu bewegen.

## Hardware-Voraussetzungen
* 1x Big Mouth Billy Bass (originale DC-Motoren)
* 1x Raspberry Pi (Zero W, 3, oder 4)
* 1x H-Brücken-Motortreiber (z. B. MX1508 oder L298N)
* 1x Lautsprecher (verbunden mit dem Raspberry Pi)
* 1x Leistungsstarker Host-Rechner (Laptop/Server) für das Backend

## Software-Voraussetzungen und Setup

### Backend (Laptop)
Es wird Python 3.9 oder höher empfohlen. Zudem muss `ffmpeg` auf dem System installiert und im PATH hinterlegt sein, um MP3-Dateien verarbeiten zu können.

Benötigte Python-Pakete installieren:
```bash
pip install fastapi uvicorn pydantic httpx pydub