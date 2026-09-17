from vocabulary import replacements, word_to_num, chord_map

def extract_score(text):
    """
    NLP Helper: Scans a transcribed audio string and converts spoken numbers into integer values.
    Handles combinations like "one hundred twenty" -> 120.
    Returns the last identified integer in the string, which represents the target BPM/Score.
    """
    text = text.replace(" and ", " ")
    
    # 1. Normalize edge-case spoken words to standard number words
    for word, num in replacements.items():
        text = text.replace(word, num)
        
    words = text.split()
    nums = []
    current_num = None
    
    # 2. Parse sequential number words into actual integers
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
                # Handle multipliers (e.g., "one" "hundred" -> 100)
                if val == 100:
                    current_num = current_num * 100
                # Handle additions (e.g., "one hundred" + "twenty" -> 120)
                elif current_num >= 100 and val < 100:
                    current_num += val
                # Handle hyphenated splits (e.g., "twenty" + "five" -> 25)
                elif 20 <= current_num <= 90 and current_num % 10 == 0 and val < 10:
                    current_num += val
                # Handle hundreds without the word "hundred" (e.g., "one" + "twenty" -> 120)
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
    Core Logic Engine: Translates clean Vosk transcriptions into actionable state updates.
    Includes phonetic variations (e.g., "colander" for "calendar") to account for offline STT inaccuracies.
    
    Returns a tuple: (action_type, data)
    - action_type: "standard", "requires_confirmation", "error", or "ignore".
    - data: The dictionary payload for the backend API, or an error string.
    """
    
    # ---------------------------------------------------------
    # 1. TIMER & METRONOME CONTROLS
    # ---------------------------------------------------------
    if any(w in padded_text for w in [" timer ", " time her ", " metronome ", " metro gnome ", " metro ", " bpm ", " beat ", " mentor know ", " metro know "]):
        
        # Stop command
        if any(w in padded_text for w in [" stop ", " cancel ", " off ", " kill "]):
            print("Action: Stopping Metronome/Timer")
            return "standard", {"metronome_bpm": 0, "timer_active": False}
            
        # 1-Minute Practice Timer
        elif any(w in padded_text for w in [" timer ", " time her "]):
            print("Action: Starting 1-Minute Timer")
            return "standard", {"timer_active": True, "metronome_bpm": 0, "current_view": "hub"}
            
        # Set Metronome BPM
        else:
            target_bpm = extract_score(padded_text)
            if target_bpm is not None and target_bpm > 0:
                print(f"Action: Starting Metronome at {target_bpm} BPM")
                return "standard", {"metronome_bpm": target_bpm, "timer_active": False, "current_view": "hub"}
            else:
                return "error", "Invalid BPM parsed."

    # ---------------------------------------------------------
    # 2. VIEW NAVIGATION
    # ---------------------------------------------------------
    elif any(w in padded_text for w in [" hub ", " pub ", " cub ", " sub ", " chart ", " tart ", " shart ", " scores ", " changes ", " tracking ", " list ", " grid ", " overview ", " over view "]):
        print("Action: Loading Hub")
        return "standard", {"current_view": "hub"}

    elif any(w in padded_text for w in [" all chords ", " show all ", " every chord ", " chord library ", " chord list ", " all of my chords ", " show me all chords "]):
        print("Action: Loading Chord Library")
        return "standard", {"current_view": "all_chords"}

    elif any(w in padded_text for w in [" help ", " yelp ", " kelp ", " commands ", " menu ", " what can you do "]):
        print("Action: Loading Help Screen")
        return "standard", {"current_view": "help"}

    # ---------------------------------------------------------
    # 3. DATABASE UPDATES (Two-Step Action)
    # Target Syntax: "Update [Chord 1] to [Chord 2] to [Score]"
    # ---------------------------------------------------------
    elif any(w in padded_text for w in [" update ", " up date ", " edit ", " head it ", " swap ", " swab ", " slop ", " modify ", " set "]):
        score = extract_score(padded_text)
        temp_text = padded_text
        extracted = []
        
        # Sort chord_map by length descending to prevent partial matches 
        # (e.g., matching "A" before checking for "A minor")
        for var, actual in sorted(chord_map.items(), key=lambda x: len(x[0]), reverse=True):
            start = 0
            while True:
                idx = temp_text.find(var, start)
                if idx == -1: break
                
                # Store the exact character index so we retain the spoken order of the chords
                extracted.append((idx, actual))
                
                # Blank out the matched text to prevent overlap parsing
                temp_text = temp_text[:idx] + (" " * len(var)) + temp_text[idx+len(var):]
                start = idx + len(var)
        
        extracted.sort(key=lambda x: x[0])
        
        # Deduplicate while preserving order
        found_chords = []
        for _, ch in extracted:
            if ch not in found_chords:
                found_chords.append(ch)
        
        # Ensure we found exactly 2 chords and 1 valid score
        if len(found_chords) >= 2 and score is not None:
            c1 = found_chords[0]
            c2 = found_chords[1]
            
            # Validate the chord pairing against the current local database state
            is_valid_pair = False
            for sw in current_switches:
                if (sw['from'] == c1 and sw['to'] == c2) or (sw['from'] == c2 and sw['to'] == c1):
                    is_valid_pair = True
                    break
            
            if is_valid_pair:
                payload = {
                    "current_view": "hub", 
                    "pending_update": {"chord1": c1, "chord2": c2, "score": score},
                    "is_listening": True # Keep the UI glow active while waiting for Yes/No
                }
                return "requires_confirmation", {"c1": c1, "c2": c2, "score": score, "payload": payload}
            else:
                return "error", "Invalid chord combination parsed. Aborting."
        else:
            return "error", f"Update parsing failed. Chords: {found_chords}, Score: {score}. Aborting."

    # ---------------------------------------------------------
    # 4. HOME & DASHBOARD RETURN
    # ---------------------------------------------------------
    elif any(w in padded_text for w in [" calendar ", " colander ", " home ", " dome ", " comb ", " close ", " clothes ", " exit ", " eggs it ", " dashboard ", " dash board ", " main ", " return ", " back ", " stop ", " cancel ", " dash for ", " gosh border ", " dash or "]):
        print("Action: Returning to Dashboard")
        # Returning home explicitly clears any active practice tools
        return "standard", {"current_view": "calendar", "timer_active": False, "metronome_bpm": 0}

    elif any(w in padded_text for w in [" template ", " templet ", " ten plate ", " blank ", " plank ", " clear ", " empty ", " m t "]):
        print("Action: Loading Blank Template")
        return "standard", {"current_view": "template"}   
        
    # ---------------------------------------------------------
    # 5. SINGLE CHORD FALLBACK
    # If no structural commands matched, check if the user just yelled a chord name
    # ---------------------------------------------------------
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