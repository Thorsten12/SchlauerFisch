import math
import base64
import io
from pydub import AudioSegment

# ---------------------------------------------------------
# 1. MOTOR LOGIK (Unverändert, Schwanz aus Parameter gesteuert)
# ---------------------------------------------------------
def get_mouth_state(volume, threshold):
    return (220, 0) if volume > threshold else (0, 180)

def get_body_state(volume, threshold):
    return (150, 0) if volume > threshold else (0, 0)

def get_head_state(future_volume, threshold, has_nein):
    if future_volume > threshold or has_nein:
        return (200, 0)
    else:
        return (0, 180)

def get_tail_state(timer_ms, fps_ms):
    if timer_ms > 0:
        timer_ms -= fps_ms 
        if (timer_ms // 100) % 2 == 0:
            motor_state = (255, 0)
        else:
            motor_state = (0, 255)
        return motor_state, timer_ms
    return (0, 0), 0

# ---------------------------------------------------------
# 2. HAUPTFUNKTION (Mit Padding & Block-Alignment)
# ---------------------------------------------------------
def process_audio_to_blocks(file_path, text="", block_sec=3, fps_ms=50, threshold=-15.0):
    audio = AudioSegment.from_file(file_path)
    original_len = len(audio)
    
    text_upper = text.upper()
    has_nein = "[NEIN]" in text_upper
    has_freuen = "[FREUEN]" in text_upper
    has_tail_trigger = has_nein or has_freuen 
    
    # Prüfen, ob der Trigger ganz am Ende des Textes steht
    trigger_at_end = text_upper.strip().endswith("]")
    
    # --- NEU: PADDING (AUFFÜLLEN) LOGIK ---
    
    # 1. Wenn der Trigger am Ende ist, fügen wir 3 Sekunden hinzu, 
    # damit die Animation einen eigenen, ungestörten Block bekommt.
    if has_tail_trigger and trigger_at_end:
        audio += AudioSegment.silent(duration=3000)
        
    # 2. Wir füllen die gesamte Länge so auf, dass sie ein perfektes Vielfaches von block_sec ist.
    # (Aus 5s werden z.B. 6s. + die 3s von oben = 9s gesamt = genau drei 3s-Blöcke)
    block_length_ms = block_sec * 1000
    remainder = len(audio) % block_length_ms
    if remainder > 0:
        padding_ms = block_length_ms - remainder
        audio += AudioSegment.silent(duration=padding_ms)
        
    print(f"Audio auf {len(audio)/1000}s aufgefüllt (Vielfaches von {block_sec}s).")
    
    # Berechnen, wann exakt der 3s-Block NACH dem Sprechen beginnt
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
            
            # --- WANN STARTEN WIR DEN SCHWANZ-TIMER? ---
            if has_tail_trigger and not tail_has_triggered:
                if trigger_at_end:
                    # Trigger zündet exakt am Anfang des aufgefüllten Blocks NACH dem Sprechen
                    if current_ms >= post_speech_block_start:
                        tail_timer_ms = 3000
                        tail_has_triggered = True
                else:
                    # Steht der Trigger mitten im Satz, wackelt er beim Sprechen
                    if vol > threshold:
                        tail_timer_ms = 3000
                        tail_has_triggered = True
            
            mouth = get_mouth_state(vol, threshold)
            body  = get_body_state(vol, threshold)
            head  = get_head_state(future_vol, threshold, has_nein)
            tail, tail_timer_ms = get_tail_state(tail_timer_ms, fps_ms)
            
            frame_array = [
                mouth[0], mouth[1], 
                body[0],  body[1], 
                head[0],  head[1], 
                tail[0],  tail[1]
            ]
            motor_frames.append(frame_array)
                
        output_objects.append({
            "audio_base64": encoded_audio,
            "fps_ms": fps_ms,
            "motor_frames": motor_frames
        })
        
    return output_objects

# --- Ausführung ---
if __name__ == "__main__":
    MEINE_MP3 = "ausgabe.mp3" 
    GENERIERTER_TEXT = "Das ist ein fünf Sekunden Test. [FREUEN]"
    
    data_blocks = process_audio_to_blocks(MEINE_MP3, text=GENERIERTER_TEXT)
    
    print(f"\nGenerierte Blöcke gesamt: {len(data_blocks)}")