import math
import base64
import io
from pydub import AudioSegment

WACKEL_INTERVAL_MS = 100
WACKEL_DAUER_MS    = 2000

# ---------------------------------------------------------
# 1. MOTOR LOGIK
# ---------------------------------------------------------

def get_body_state(future_volume, threshold) -> int:
    return 1 if future_volume > threshold else 0

def get_head_state(volume, threshold) -> int:
    return 1 if volume > threshold else 0

def apply_body_tail_failsafe(body, tail) -> tuple[int, int]:
    if body == 1 and tail == 1:
        return (1, 0)
    return (body, tail)

# ---------------------------------------------------------
# 2. AUDIO-BLÖCKE (nur echtes Audio, keine Token-Logik)
# ---------------------------------------------------------
def build_audio_blocks(audio, fps_ms, threshold, block_length_ms):
    remainder = len(audio) % block_length_ms
    if remainder > 0:
        audio += AudioSegment.silent(duration=block_length_ms - remainder)

    # Einmal komplett vorausberechnen: wann wird gesprochen?
    is_speech = []
    for k in range(0, len(audio), fps_ms):
        chunk = audio[k:k + fps_ms]
        vol   = -100 if math.isinf(chunk.dBFS) else chunk.dBFS
        is_speech.append(vol > threshold)

    blocks = []
    for i in range(0, len(audio), block_length_ms):
        audio_block = audio[i:i + block_length_ms]

        buffer = io.BytesIO()
        audio_block.export(buffer, format="mp3")
        encoded_audio = base64.b64encode(buffer.getvalue()).decode("utf-8")

        motor_frames = []
        for j in range(0, len(audio_block), fps_ms):
            current_ms  = i + j
            frame_idx   = current_ms // fps_ms

            chunk = audio_block[j:j + fps_ms]
            vol   = -100 if math.isinf(chunk.dBFS) else chunk.dBFS

            # Körper: schau 1 sec voraus ob irgendwann in den nächsten 20 Frames gesprochen wird
            lookahead_frames = 1000 // fps_ms  # = 20 bei 50ms
            body = 0
            for offset in range(lookahead_frames + 1):
                if frame_idx + offset < len(is_speech) and is_speech[frame_idx + offset]:
                    body = 1
                    break

            head = 1 if vol > threshold else 0
            tail = 0

            body, tail = apply_body_tail_failsafe(body, tail)
            motor_frames.append([head, body, tail])

        blocks.append({
            "audio_base64": encoded_audio,
            "fps_ms":       fps_ms,
            "motor_frames": motor_frames
        })

    return blocks

# ---------------------------------------------------------
# 3. TOKEN-BLOCK (nur Stille + Wackel-Animation)
# ---------------------------------------------------------
def build_token_block(token, fps_ms, block_length_ms):
    """Eigener Block: 1 sec Stille + Wackel-Animation für [FREUEN] oder [NEIN]."""
    silence = AudioSegment.silent(duration=block_length_ms)

    buffer = io.BytesIO()
    silence.export(buffer, format="mp3")
    encoded_audio = base64.b64encode(buffer.getvalue()).decode("utf-8")

    motor_frames = []
    timer_ms     = WACKEL_DAUER_MS

    for j in range(0, block_length_ms, fps_ms):
        if timer_ms > 0:
            blink = 1 if (timer_ms // WACKEL_INTERVAL_MS) % 2 == 0 else 0
            timer_ms -= fps_ms
        else:
            blink = 0

        if token == "[FREUEN]":
            head, body, tail = 0, 0, blink
        elif token == "[NEIN]":
            head, body, tail = blink, 0, 0
        else:
            head, body, tail = 0, 0, 0

        motor_frames.append([head, body, tail])

    return {
        "audio_base64": encoded_audio,
        "fps_ms":       fps_ms,
        "motor_frames": motor_frames
    }

# ---------------------------------------------------------
# 4. HAUPTFUNKTION
# ---------------------------------------------------------
def process_audio_to_blocks(file_path, text="", block_sec=3, fps_ms=50, threshold=-35.0):
    audio           = AudioSegment.from_file(file_path)
    block_length_ms = block_sec * 1000
    text_upper      = text.upper()

    # Audio-Blöcke bauen
    output_objects = build_audio_blocks(audio, fps_ms, threshold, block_length_ms)

    # Token-Blöcke anhängen
    for token in ["[FREUEN]", "[NEIN]"]:
        if token in text_upper:
            output_objects.append(build_token_block(token, fps_ms, block_length_ms))

    return output_objects