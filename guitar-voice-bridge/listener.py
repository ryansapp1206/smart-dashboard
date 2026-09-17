import pyaudio
import numpy as np
import requests
import json
from openwakeword.model import Model
from vosk import Model as VoskModel, KaldiRecognizer

# IMPORT THE NEW LOGIC ENGINE (Decoupled text parsing)
from command_parser import parse_intent

# ---------------------------------------------------------
# MODEL INITIALIZATION (100% Offline processing)
# ---------------------------------------------------------
owwModel = Model() # OpenWakeWord model for detecting "Hey Jarvis"
try:
    vosk_model = VoskModel("model") # Vosk model for full speech-to-text
    recognizer = KaldiRecognizer(vosk_model, 16000)
except Exception as e:
    print("VOSK ERROR: Could not find the 'model' folder.")
    exit(1)

# ---------------------------------------------------------
# AUDIO HARDWARE CONFIGURATION
# ---------------------------------------------------------
CHUNK = 1280
RATE = 16000
audio = pyaudio.PyAudio()
# Open a continuous mono audio stream from the default microphone
mic_stream = audio.open(format=pyaudio.paInt16, channels=1, rate=RATE, input=True, frames_per_buffer=CHUNK)

API_URL = "http://localhost:3001/api/guitar/update"
GET_URL = "http://localhost:3001/api/guitar"

# ---------------------------------------------------------
# NETWORK HELPERS
# ---------------------------------------------------------
def update_backend(new_data):
    """Fetches the current state, merges new data, and pushes it to the Node backend."""
    try:
        current_state = requests.get(GET_URL, timeout=2).json()
        current_state.update(new_data)
        requests.post(API_URL, json=current_state, timeout=2)
    except Exception as e:
        print(f"Backend Sync Failure: {e}")

# Ensure UI starts in a resting state
update_backend({"is_listening": False, "pending_update": None})

def flush_microphone():
    """Clears the audio buffer and resets the wake word model to prevent false triggers from background noise or echoes."""
    update_backend({"is_listening": False, "pending_update": None})
    print("Warming up model and flushing buffer...")
    
    if mic_stream.get_read_available() > 0:
        mic_stream.read(mic_stream.get_read_available(), exception_on_overflow=False)
        
    owwModel.reset()
    
    # Process a few empty chunks to let the model settle
    for _ in range(15):
        audio_data = np.frombuffer(mic_stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
        owwModel.predict(audio_data)
        
    print("Listening for wake word...")

# ---------------------------------------------------------
# MAIN LISTENING LOOP
# ---------------------------------------------------------
print("Listener active. Waiting for wake word...")

while True:
    # 1. Continually read audio chunks
    try:
        audio_data = np.frombuffer(mic_stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
    except Exception:
        continue
        
    # 2. Check for the wake word
    prediction = owwModel.predict(audio_data)
    
    # If confidence threshold is met, activate command listener
    if prediction.get('hey_jarvis', 0.0) > 0.75:
        print("Wake word detected.")
        
        # Clear any leftover audio to ensure a clean command recording
        if mic_stream.get_read_available() > 0:
            mic_stream.read(mic_stream.get_read_available(), exception_on_overflow=False)
            
        # Trigger the glowing listening indicator on the React UI
        update_backend({"is_listening": True})
        print("Listening for command...")
        
        # 3. Record the spoken command (max ~6 seconds / 80 chunks)
        command_audio = b''
        for _ in range(80): 
            chunk = mic_stream.read(CHUNK, exception_on_overflow=False)
            command_audio += chunk
            # Break early if Vosk detects the end of a sentence
            if recognizer.AcceptWaveform(chunk):
                break 
            
        # 4. Clean the transcript
        spoken_text = json.loads(recognizer.FinalResult()).get("text", "").lower()
        spoken_text = spoken_text.replace("hey jarvis", "").replace("jarvis", "").strip()
        print(f"Parsed input: '{spoken_text}'")
        
        if not spoken_text:
            flush_microphone()
            continue
            
        padded_text = f" {spoken_text} "

        # 5. FETCH CURRENT STATE BEFORE PARSING (Protected against backend crashes)
        try:
            current_state = requests.get(GET_URL, timeout=2).json()
            switches = current_state.get('switches', [])
        except Exception as e:
            print("Backend unreachable, aborting command.")
            flush_microphone()
            continue

        # 6. SEND TO THE LOGIC ENGINE (Returns what action to take)
        action_type, result = parse_intent(padded_text, switches)

        # 7. EXECUTE THE ACTION
        if action_type == "standard":
            # Simple state updates (e.g., changing views, starting timers)
            update_backend(result)
            if "current_view" in result:
                print(f"State updated: {result['current_view']}")
                
        elif action_type == "requires_confirmation":
            # Two-step action (e.g., modifying database records)
            print(f"Action: Initiating update for {result['c1']} <-> {result['c2']} to {result['score']} bpm")
            update_backend(result['payload']) # Triggers confirmation modal on UI
            
            # Briefly take over the microphone to listen for "Yes" or "No"
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
            
            # Process confirmation
            if any(w in conf_text for w in [" yes ", " yeah ", " yep ", " sure ", " confirm ", " do it ", " absolutely ", " right ", " correct ", " yup "]):
                # Find the specific chord switch block and update its score
                for sw in switches:
                    if (sw['from'] == result['c1'] and sw['to'] == result['c2']) or (sw['from'] == result['c2'] and sw['to'] == result['c1']):
                        sw['score'] = result['score']
                        break
                update_backend({"switches": switches, "pending_update": None})
                print("Update confirmed.")
            else:
                # Cancel the action and close the modal
                update_backend({"pending_update": None})
                print("Update cancelled.")
                
        elif action_type == "error":
            print(result)
        elif action_type == "ignore":
            print("Action: No match found. Ignoring.")
            
        # Reset the audio environment for the next command
        flush_microphone()