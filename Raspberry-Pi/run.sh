#!/bin/bash
# Verwendung:
#   Vom eigenen Rechner aus:
#   scp output.json pi@raspberrypi:~/player/ && ssh pi@raspberrypi 'bash ~/player/run.sh'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JSON="$SCRIPT_DIR/output.json"

if [ ! -f "$JSON" ]; then
    echo "[FEHLER] output.json nicht gefunden in $SCRIPT_DIR"
    exit 1
fi

echo "[INFO] Starte player.py mit $JSON ..."
python3 "$SCRIPT_DIR/player.py"