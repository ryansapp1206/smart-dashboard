# command_parser.py

from vocabulary import replacements, word_to_num, chord_map

def extract_score(text):
    text = text.replace(" and ", " ")
    
    for word, num in replacements.items():
        text = text.replace(word, num)
        
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

def parse_intent(padded_text, current_switches):
    """
    Parses spoken text and returns a tuple: (action_type, data)
    action_type can be "standard", "requires_confirmation", "error", or "ignore".
    """
    if any(w in padded_text for w in [" timer ", " time her ", " metronome ", " metro gnome ", " metro ", " bpm ", " beat ", " be ", " mentor know ", " measuring ", " metro know "]):
        if any(w in padded_text for w in [" stop ", " cancel ", " off ", " kill "]):
            print("Action: Stopping Metronome/Timer")
            return "standard", {"metronome_bpm": 0, "timer_active": False}
        elif any(w in padded_text for w in [" timer ", " time her "]):
            print("Action: Starting 1-Minute Timer")
            return "standard", {"timer_active": True, "metronome_bpm": 0, "current_view": "hub"}
        else:
            target_bpm = extract_score(padded_text)
            if target_bpm is not None and target_bpm > 0:
                print(f"Action: Starting Metronome at {target_bpm} BPM")
                return "standard", {"metronome_bpm": target_bpm, "timer_active": False, "current_view": "hub"}
            else:
                return "error", "Invalid BPM parsed."

    elif any(w in padded_text for w in [" hub ", " pub ", " cub ", " sub ", " chart ", " tart ", " shart ", " scores ", " changes ", " tracking ", " list ", " grid ", " overview ", " over view "]):
        print("Action: Loading Hub")
        return "standard", {"current_view": "hub"}

    elif any(w in padded_text for w in [" all chords ", " show all ", " every chord ", " chord library ", " chord list ", " all of my chords ", " show me all chords "]):
        print("Action: Loading Chord Library")
        return "standard", {"current_view": "all_chords"}

    elif any(w in padded_text for w in [" help ", " yelp ", " kelp ", " commands ", " menu ", " what can you do "]):
        print("Action: Loading Help Screen")
        return "standard", {"current_view": "help"}

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
            
            is_valid_pair = False
            for sw in current_switches:
                if (sw['from'] == c1 and sw['to'] == c2) or (sw['from'] == c2 and sw['to'] == c1):
                    is_valid_pair = True
                    break
            
            if is_valid_pair:
                payload = {
                    "current_view": "hub", 
                    "pending_update": {"chord1": c1, "chord2": c2, "score": score},
                    "is_listening": True
                }
                return "requires_confirmation", {"c1": c1, "c2": c2, "score": score, "payload": payload}
            else:
                return "error", "Invalid chord combination parsed. Aborting."
        else:
            return "error", f"Update parsing failed. Chords: {found_chords}, Score: {score}. Aborting."

    elif any(w in padded_text for w in [" calendar ", " colander ", " home ", " dome ", " comb ", " close ", " clothes ", " exit ", " eggs it ", " dashboard ", " dash board ", " main ", " return ", " back ", " stop ", " cancel ", " dash for ", " gosh border ", " dash or "]):
        print("Action: Returning to Dashboard")
        return "standard", {"current_view": "calendar", "timer_active": False, "metronome_bpm": 0}

    elif any(w in padded_text for w in [" template ", " templet ", " ten plate ", " blank ", " plank ", " clear ", " empty ", " m t "]):
        print("Action: Loading Blank Template")
        return "standard", {"current_view": "template"}   
        
    else:
        identified_chord = None
        for variation, actual_chord in sorted(chord_map.items(), key=lambda x: len(x[0]), reverse=True):
            if variation in padded_text:
                identified_chord = actual_chord
                break
        
        if identified_chord:
            print(f"Action: Loading {identified_chord} Chord")
            return "standard", {"current_view": identified_chord}
        else:
            return "ignore", None