#toter call funktioniert nur wenn auf dem server openclaw instaliert ist

import subprocess
import time
import socket
import sys

OPENCLAW_PORT = 18789
OPENCLAW_URL = f"http://127.0.0.1:{OPENCLAW_PORT}/api/chat"

def is_port_open(port):
    """Prüft, ob der OpenClaw-Port auf dem Server bereits lauscht."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex(('127.0.0.1', port))
        return result == 0

def start_openclaw_gateway():
    """Startet OpenClaw im Hintergrund."""
    if is_port_open(OPENCLAW_PORT):
        print(f"-> OpenClaw läuft bereits auf Port {OPENCLAW_PORT}.")
        return None

    print("-> Starte OpenClaw Gateway im Hintergrund...")
    
    cmd = ["uv", "run", "openclaw"] 
    
    # stdout und stderr umleiten
    process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Timeout-Check
    timeout = 30
    start_time = time.time()
    while not is_port_open(OPENCLAW_PORT):
        if time.time() - start_time > timeout:
            print("Fehler: OpenClaw ist nach 30 Sekunden nicht hochgefahren!")
            process.terminate()
            sys.exit(1)
        time.sleep(1)
        
    print(f"-> OpenClaw Gateway ist online auf Port {OPENCLAW_PORT}!")
    return process