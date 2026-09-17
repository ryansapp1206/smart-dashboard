import pyaudio
import numpy as np
import requests
import json
import time
import re
from openwakeword.model import Model
from vosk import Model as VoskModel, KaldiRecognizer

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

def extract_score(text):
    text = text.replace(" and ", " ")
    
    replacements = {
        "six tee": "sixty", "sick stee": "sixty", "six d": "sixty", "six tea": "sixty",
        "fifth tee": "fifty", "fif d": "fifty", 
        "four d": "forty", "four tee": "forty", "for d": "forty",
        "third e": "thirty", "thir d": "thirty", "dirty": "thirty",
        "seven d": "seventy", "eight d": "eighty", "ate e": "eighty", "nine d": "ninety",
        "twen e": "twenty", "a hundred": "one hundred"
    }
    for word, num in replacements.items():
        text = text.replace(word, num)
        
    word_to_num = {
        "zero": 0, "one": 1, "won": 1, "two": 2, "three": 3, "tree": 3, 
        "four": 4, "for": 4, "five": 5, "six": 6, "sex": 6, "seven": 7, 
        "eight": 8, "ate": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
        "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
        "eighteen": 18, "nineteen": 19,
        "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
        "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100
    }
    
    words = text.split()
    nums = []
    current_num = None
    
    for w in words:
        val = None
        if w.isdigit():
            val = int(w)
        elif w in word_to_num:
            val = word_to_num[w]
            
        if val is not None:
            if current_num is None:
                current_num = val
            else:
                if val == 100:
                    current_num = current_num * 100
                elif current_num >= 100 and val < 100:
                    current_num += val
                elif 20 <= current_num <= 90 and current_num % 10 == 0 and val < 10:
                    current_num += val
                elif 1 <= current_num <= 9 and 10 <= val <= 99:
                    current_num = (current_num * 100) + val
                else:
                    nums.append(current_num)
                    current_num = val
        else:
            if current_num is not None:
                nums.append(current_num)
                current_num = None
                
    if current_num is not None:
        nums.append(current_num)
        
    if nums:
        return nums[-1]
        
    return None

chord_map = {
    " a minor ": "Am", " ay minor ": "Am", " aim in her ": "Am", " a miner ": "Am",
    " eight minor ": "Am", " ate minor ": "Am", " a minner ": "Am", " a myner ": "Am",
    " amen or ": "Am", " a might ": "Am", " aiming her ": "Am", " a liner ": "Am",
    " a my nor ": "Am", " a diner ": "Am", " a finer ": "Am", " pay minor ": "Am",
    " day minor ": "Am", " a meaner ": "Am", " hey minor ": "Am",

    " d minor ": "Dm", " dee minor ": "Dm", " the minor ": "Dm", " the miner ": "Dm",
    " demon or ": "Dm", " de minor ": "Dm", " team in her ": "Dm", " the higher ": "Dm",
    " d higher ": "Dm", " dee higher ": "Dm", " deep minor ": "Dm", " dean minor ": "Dm",
    " jimmy dean minor ": "Dm", " tea minor ": "Dm", " t minor ": "Dm", " diminish ": "Dm",
    " dominor ": "Dm", " the myner ": "Dm",

    " e minor ": "Em", " ee minor ": "Em", " he minor ": "Em", " he miner ": "Em",
    " e miner ": "Em", " meaner ": "Em", " eat minor ": "Em", " e higher ": "Em",
    " he higher ": "Em", " ee higher ": "Em", " you minor ": "Em", " yi minor ": "Em",
    " even or ": "Em", " see minor ": "Em", " sea minor ": "Em", " c minor ": "Em",
    " me minor ": "Em", " be minor ": "Em", " vee minor ": "Em", " v minor ": "Em",
    " z minor ": "Em", " b minor ": "Em",

    " a chord ": "A", " a cord ": "A", " a board ": "A", " a court ": "A", " a core ": "A",
    " hey chord ": "A", " eight chord ": "A", " ay chord ": "A", " a cool ": "A",
    " hey cool ": "A", " a for ": "A", " hey for ": "A", " a card ": "A", " ate chord ": "A",
    " ape chord ": "A",

    " c chord ": "C", " see chord ": "C", " sea chord ": "C", " c cord ": "C",
    " see cord ": "C", " sea cord ": "C", " record ": "C", " secord ": "C",
    " z chord ": "C", " see board ": "C", " see core ": "C", " c cool ": "C",
    " see cool ": "C", " c card ": "C", " see card ": "C", " seat chord ": "C",
    " seed chord ": "C", " seek chord ": "C", " secret ": "C", " zee chord ": "C",
    " si chord ": "C", " she chord ": "C",

    " d chord ": "D", " dee chord ": "D", " d cord ": "D", " dee cord ": "D",
    " decor ": "D", " decord ": "D", " beat chord ": "D", " d cool ": "D",
    " dee cool ": "D", " d for ": "D", " d card ": "D", " the chord ": "D",
    " the cord ": "D", " the board ": "D", " the core ": "D", " the cool ": "D",
    " the for ": "D", " the card ": "D", " tea chord ": "D", " t chord ": "D",
    " deep chord ": "D", " dean chord ": "D", " these chord ": "D", " jimmy dean ": "D",
    " de chord ": "D",

    " e chord ": "E", " ee chord ": "E", " he chord ": "E", " he cord ": "E",
    " e cord ": "E", " eat chord ": "E", " ee cord ": "E", " e cool ": "E",
    " ee cool ": "E", " he cool ": "E", " e for ": "E", " he for ": "E",
    " e card ": "E", " key chord ": "E", " be chord ": "E", " me chord ": "E",
    " each chord ": "E",

    " g chord ": "G", " gee chord ": "G", " g cord ": "G", " gee cord ": "G",
    " g cool ": "G", " gee cool ": "G", " g core ": "G", " g court ": "G",
    " jig cord ": "G", " cheese chord ": "G", " g for ": "G", " gee for ": "G",
    " g card ": "G", " gee card ": "G", " jeep chord ": "G", " chief chord ": "G",
    " cheap chord ": "G", " g board ": "G", " jean chord ": "G", " jee chord ": "G",
    " chi chord ": "G", " cheap board ": "G",

    " a ": "A", " ay ": "A", " hey ": "A", " aye ": "A", " eight ": "A", " ate ": "A", " ape ": "A",
    " c ": "C", " see ": "C", " sea ": "C", " z ": "C", " si ": "C", " zee ": "C", " seat ": "C", " seed ": "C",
    " d ": "D", " dee ": "D", " de ": "D", " tee ": "D", " tea ": "D", " dean ": "D",
    " e ": "E", " ee ": "E", " he ": "E", " yi ": "E", " eat ": "E", " each ": "E",
    " g ": "G", " gee ": "G", " jee ": "G", " chi ": "G", " cheese ": "G", " jig ": "G", " jean ": "G"
}

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
        payload = None

        if any(w in padded_text for w in [" timer ", " time her ", " metronome ", " metro gnome ", " metro ", " bpm ", " beat ", " be ", " mentor know ", " measuring ", " metro know "]):
            if any(w in padded_text for w in [" stop ", " cancel ", " off ", " kill "]):
                print("Action: Stopping Metronome/Timer")
                payload = {"metronome_bpm": 0, "timer_active": False}
            elif any(w in padded_text for w in [" timer ", " time her "]):
                print("Action: Starting 1-Minute Timer")
                payload = {"timer_active": True, "metronome_bpm": 0, "current_view": "hub"}
            else:
                target_bpm = extract_score(padded_text)
                if target_bpm is not None and target_bpm > 0:
                    print(f"Action: Starting Metronome at {target_bpm} BPM")
                    payload = {"metronome_bpm": target_bpm, "timer_active": False, "current_view": "hub"}
                else:
                    print("Action: Invalid BPM parsed.")

        elif any(w in padded_text for w in [" hub ", " pub ", " cub ", " sub ", " chart ", " tart ", " shart ", " scores ", " changes ", " tracking ", " list ", " grid ", " overview ", " over view "]):
            print("Action: Loading Hub")
            payload = {"current_view": "hub"}

        elif any(w in padded_text for w in [" all chords ", " show all ", " every chord ", " chord library ", " chord list ", " all of my chords ", " show me all chords "]):
            print("Action: Loading Chord Library")
            payload = {"current_view": "all_chords"}

        elif any(w in padded_text for w in [" help ", " yelp ", " kelp ", " commands ", " menu ", " what can you do "]):
            print("Action: Loading Help Screen")
            payload = {"current_view": "help"}

        elif any(w in padded_text for w in [" update ", " up date ", " edit ", " head it ", " swap ", " swab ", " slop ", " modify ", " set "]):
            score = extract_score(padded_text)
            temp_text = padded_text
            extracted = []
            
            for var, actual in sorted(chord_map.items(), key=lambda x: len(x[0]), reverse=True):
                start = 0
                while True:
                    idx = temp_text.find(var, start)
                    if idx == -1: break
                    extracted.append((idx, actual))
                    temp_text = temp_text[:idx] + (" " * len(var)) + temp_text[idx+len(var):]
                    start = idx + len(var)
            
            extracted.sort(key=lambda x: x[0])
            found_chords = []
            for _, ch in extracted:
                if ch not in found_chords:
                    found_chords.append(ch)
            
            if len(found_chords) >= 2 and score is not None:
                c1 = found_chords[0]
                c2 = found_chords[1]
                
                current_state = requests.get(GET_URL).json()
                switches = current_state.get('switches', [])
                
                is_valid_pair = False
                for sw in switches:
                    if (sw['from'] == c1 and sw['to'] == c2) or (sw['from'] == c2 and sw['to'] == c1):
                        is_valid_pair = True
                        break
                
                if is_valid_pair:
                    print(f"Action: Initiating update for {c1} <-> {c2} to {score} bpm")
                    
                    update_backend({
                        "current_view": "hub", 
                        "pending_update": {"chord1": c1, "chord2": c2, "score": score},
                        "is_listening": True
                    })
                    
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
                            if (sw['from'] == c1 and sw['to'] == c2) or (sw['from'] == c2 and sw['to'] == c1):
                                sw['score'] = score
                                break
                        update_backend({"switches": switches, "pending_update": None})
                        print("Update confirmed.")
                    else:
                        update_backend({"pending_update": None})
                        print("Update cancelled.")
                else:
                    print("Action: Invalid chord combination parsed. Aborting.")
            else:
                print(f"Action: Update parsing failed. Chords: {found_chords}, Score: {score}. Aborting.")
                
            flush_microphone()
            continue 

        elif any(w in padded_text for w in [" calendar ", " colander ", " home ", " dome ", " comb ", " close ", " clothes ", " exit ", " eggs it ", " dashboard ", " dash board ", " main ", " return ", " back ", " stop ", " cancel ", " dash for ", " gosh border ", " dash or "]):
            print("Action: Returning to Dashboard")
            payload = {"current_view": "calendar", "timer_active": False, "metronome_bpm": 0}

        elif any(w in padded_text for w in [" template ", " templet ", " ten plate ", " blank ", " plank ", " clear ", " empty ", " m t "]):
            print("Action: Loading Blank Template")
            payload = {"current_view": "template"}   
            
        else:
            identified_chord = None
            for variation, actual_chord in sorted(chord_map.items(), key=lambda x: len(x[0]), reverse=True):
                if variation in padded_text:
                    identified_chord = actual_chord
                    break
            
            if identified_chord:
                print(f"Action: Loading {identified_chord} Chord")
                payload = {"current_view": identified_chord}
            else:
                print("Action: No match found. Ignoring.")

        if payload is not None:
            update_backend(payload)
            if "current_view" in payload:
                print(f"State updated: {payload['current_view']}")
        
        flush_microphone()