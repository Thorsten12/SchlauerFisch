import math
import base64
import io
from pydub import AudioSegment

# ---------------------------------------------------------
# 1. MOTOR LOGIK
# ---------------------------------------------------------
def get_mouth_state(volume, threshold):
    return (220, 0) if volume > threshold else (0, 180)

def get_body_state(volume, threshold):
    return (150, 0) if volume > threshold else (0, 0)

# NEU: Kopf und Schwanz teilen sich EINEN Motor
def get_head_tail_state(future_volume, threshold, has_nein, timer_ms, fps_ms):
    motor_state = (0, 0)
    
    # --- BEDINGUNG 1: KOPF (Hat Vorrang) ---
    # Kopf klappt nach vorne (Motor Forward), wenn in 1 Sekunde gesprochen wird
    # ODER wenn das [NEIN] Flag gesetzt ist.
    needs_head_out = (future_volume > threshold) or has_nein
    
    # --- BEDINGUNG 2: SCHWANZ/FLOSSE ---
    # Timer runterzählen
    if timer_ms > 0:
        timer_ms -= fps_ms 
        
    # --- KONFLIKTLÖSUNG & MOTOR-STEUERUNG ---
    if needs_head_out:
        # Kopf MUSS draußen sein. Motor dreht vorwärts.
        # Flosse wackelt in diesem Moment nicht (mechanisch nicht möglich).
        motor_state = (200, 0)
    
    elif timer_ms > 0:
        # Kopf muss nicht draußen sein UND der Flossen-Timer läuft.
        # Wackeln: Motor zuckt zwischen Rückwärts (Flosse) und Nullstellung.
        # Wir können nicht zwischen Forward/Backward wechseln, da Forward den Kopf bewegen würde!
        if (timer_ms // 100) % 2 == 0:
            motor_state = (0, 255) # Schlag mit der Flosse (Rückwärtsgang)
        else:
            motor_state = (0, 0)   # Entspannen
            
    else:
        # Standard-Ruheposition: Kopf ist eingefahren (Motor dreht sanft zurück)
        motor_state = (0, 180)
        
    return motor_state, timer_ms

# ---------------------------------------------------------
# 2. HAUPTFUNKTION (Mit Padding & 6-Werte-Array)
# ---------------------------------------------------------
def process_audio_to_blocks(file_path, text="", block_sec=3, fps_ms=50, threshold=-15.0):
    audio = AudioSegment.from_file(file_path)
    original_len = len(audio)
    
    text_upper = text.upper()
    has_nein = "[NEIN]" in text_upper
    has_freuen = "[FREUEN]" in text_upper
    has_tail_trigger = has_nein or has_freuen 
    
    trigger_at_end = text_upper.strip().endswith("]")
    
    if has_tail_trigger and trigger_at_end:
        audio += AudioSegment.silent(duration=3000)
        
    block_length_ms = block_sec * 1000
    remainder = len(audio) % block_length_ms
    if remainder > 0:
        padding_ms = block_length_ms - remainder
        audio += AudioSegment.silent(duration=padding_ms)
        
    post_speech_block_start = math.ceil(original_len / block_length_ms) * block_length_ms
    
    output_objects = []
    tail_timer_ms = 0 
    tail_has_triggered = False

    for i in range(0, len(audio), block_length_ms):
        audio_block = audio[i:i + block_length_ms]
        
        buffer = io.BytesIO()
        audio_block.export(buffer, format="mp3")
        encoded_audio = base64.b64encode(buffer.getvalue()).decode("utf-8")
        
        motor_frames = []
        
        for j in range(0, len(audio_block), fps_ms):
            current_ms = i + j
            
            chunk = audio_block[j:j + fps_ms]
            vol = -100 if math.isinf(chunk.dBFS) else chunk.dBFS
            
            future_ms = current_ms + 1000
            if future_ms < len(audio):
                future_chunk = audio[future_ms : future_ms + fps_ms]
                future_vol = -100 if math.isinf(future_chunk.dBFS) else future_chunk.dBFS
            else:
                future_vol = -100 
            
            if has_tail_trigger and not tail_has_triggered:
                if trigger_at_end:
                    if current_ms >= post_speech_block_start:
                        tail_timer_ms = 3000
                        tail_has_triggered = True
                else:
                    if vol > threshold:
                        tail_timer_ms = 3000
                        tail_has_triggered = True
            
            mouth = get_mouth_state(vol, threshold)
            body  = get_body_state(vol, threshold)
            
            # --- NEUER KOMBINIERTER MOTOR AUFRUF ---
            head_tail, tail_timer_ms = get_head_tail_state(future_vol, threshold, has_nein, tail_timer_ms, fps_ms)
            
            # Array besteht jetzt aus 6 Werten (3 Motoren)
            frame_array = [
                mouth[0], mouth[1], 
                body[0],  body[1], 
                head_tail[0], head_tail[1] 
            ]
            motor_frames.append(frame_array)
                
        output_objects.append({
            "audio_base64": encoded_audio,
            "fps_ms": fps_ms,
            "motor_frames": motor_frames
        })
        
    return output_objects