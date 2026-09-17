# listener.py

import pyaudio
import numpy as np
import requests
import json
from openwakeword.model import Model
from vosk import Model as VoskModel, KaldiRecognizer

# IMPORT THE NEW LOGIC ENGINE
from command_parser import parse_intent

# Initialize Models
owwModel = Model()
try:
    vosk_model = VoskModel("model")
    recognizer = KaldiRecognizer(vosk_model, 16000)
except Exception as e:
    print("VOSK ERROR: Could not find the 'model' folder.")
    exit(1)

# Audio Hardware Configuration
CHUNK = 1280
RATE = 16000
audio = pyaudio.PyAudio()
mic_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

API_URL = "http://localhost:3001/api/guitar/update"
GET_URL = "http://localhost:3001/api/guitar"

def update_backend(new_data):
    try:
        current_state = requests.get(GET_URL, timeout=2).json()
        current_state.update(new_data)
        requests.post(API_URL, json=current_state, timeout=2)
    except Exception as e:
        print(f"Backend Sync Failure: {e}")

update_backend({"is_listening": False, "pending_update": None})

def flush_microphone():
    """Flushes the audio buffer and resets the wake word model to prevent artifact triggers."""
    update_backend({"is_listening": False, "pending_update": None})
    print("Warming up model and flushing buffer...")
    
    if mic_stream.get_read_available() > 0:
        mic_stream.read(mic_stream.get_read_available(), exception_on_overflow=False)
        
    owwModel.reset()
    
    for _ in range(15):
        audio_data = np.frombuffer(mic_stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        owwModel.predict(audio_data)
        
    print("Listening for wake word...")

print("Listener active. Waiting for wake word...")

while True:
    try:
        audio_data = np.frombuffer(mic_stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
    except Exception:
        continue
        
    prediction = owwModel.predict(audio_data)
    
    if prediction.get('hey_jarvis', 0.0) > 0.75:
        print("Wake word detected.")
        
        if mic_stream.get_read_available() > 0:
            mic_stream.read(mic_stream.get_read_available(), exception_on_overflow=False)
            
        update_backend({"is_listening": True})
        print("Listening for command...")
        
        command_audio = b''
        for _ in range(80): 
            chunk = mic_stream.read(CHUNK, exception_on_overflow=False)
            command_audio += chunk
            if recognizer.AcceptWaveform(chunk):
                break 
            
        spoken_text = json.loads(recognizer.FinalResult()).get("text", "").lower()
        spoken_text = spoken_text.replace("hey jarvis", "").replace("jarvis", "").strip()
        print(f"Parsed input: '{spoken_text}'")
        
        if not spoken_text:
            flush_microphone()
            continue
            
        padded_text = f" {spoken_text} "

        # FETCH CURRENT STATE BEFORE PARSING
        try:
            current_state = requests.get(GET_URL, timeout=2).json()
            switches = current_state.get('switches', [])
        except Exception as e:
            print("Backend unreachable, aborting command.")
            flush_microphone()
            continue

        # SEND TO THE NEW PARSER
        action_type, result = parse_intent(padded_text, switches)

        # HANDLE THE PARSER'S INSTRUCTIONS
        if action_type == "standard":
            update_backend(result)
            if "current_view" in result:
                print(f"State updated: {result['current_view']}")
                
        elif action_type == "requires_confirmation":
            print(f"Action: Initiating update for {result['c1']} <-> {result['c2']} to {result['score']} bpm")
            update_backend(result['payload'])
            
            print("Awaiting confirmation...")
            conf_audio = b''
            for _ in range(60): 
                chunk = mic_stream.read(CHUNK, exception_on_overflow=False)
                conf_audio += chunk
                if recognizer.AcceptWaveform(chunk):
                    break
            
            conf_text = json.loads(recognizer.FinalResult()).get('text', '').lower()
            conf_text = f" {conf_text.replace('hey jarvis', '').replace('jarvis', '').strip()} "
            print(f"Confirmation input: '{conf_text.strip()}'")
            
            if any(w in conf_text for w in [" yes ", " yeah ", " yep ", " sure ", " confirm ", " do it ", " absolutely ", " right ", " correct ", " yup "]):
                for sw in switches:
                    if (sw['from'] == result['c1'] and sw['to'] == result['c2']) or (sw['from'] == result['c2'] and sw['to'] == result['c1']):
                        sw['score'] = result['score']
                        break
                update_backend({"switches": switches, "pending_update": None})
                print("Update confirmed.")
            else:
                update_backend({"pending_update": None})
                print("Update cancelled.")
                
        elif action_type == "error":
            print(result)
        elif action_type == "ignore":
            print("Action: No match found. Ignoring.")
            
        flush_microphone()