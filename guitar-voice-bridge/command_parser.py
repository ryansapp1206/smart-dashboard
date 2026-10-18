import re

from vocabulary import replacements, word_to_num, chord_map

# TRIGGER PHRASES (padded with spaces so they only match whole words)
METRONOME_TRIGGERS = [" timer ", " time her ", " metronome ", " metro gnome ", " metro ", " bpm ", " beat ", " mentor know ", " metro know "]
STOP_WORDS = [" stop ", " cancel ", " off ", " kill "]
TIMER_WORDS = [" timer ", " time her "]
LIBRARY_WORDS = [" all chords ", " show all ", " every chord ", " chord library ", " chord list ", " cord list ", " all of my chords ", " show me all chords "]
HUB_WORDS = [" hub ", " pub ", " cub ", " sub ", " chart ", " tart ", " shart ", " scores ", " changes ", " tracking ", " list ", " grid ", " overview ", " over view "]
HELP_WORDS = [" help ", " yelp ", " kelp ", " commands ", " menu ", " what can you do "]
UPDATE_WORDS = [" update ", " up date ", " edit ", " head it ", " swap ", " swab ", " slop ", " modify ", " set "]
HOME_WORDS = [" calendar ", " colander ", " home ", " dome ", " comb ", " close ", " clothes ", " exit ", " eggs it ", " dashboard ", " dash board ", " main ", " return ", " back ", " stop ", " cancel ", " dash for ", " gosh border ", " dash or "]
TEMPLATE_WORDS = [" template ", " templet ", " ten plate ", " blank ", " plank ", " clear ", " empty ", " m t "]

# YES / NO CONFIRMATION WORDS
YES_WORDS = [" yes ", " yeah ", " yep ", " sure ", " confirm ", " do it ", " absolutely ", " yup "]
NO_WORDS = [" no ", " not ", " nope ", " don't ", " dont ", " cancel ", " stop ", " wrong "]

# SANITY LIMITS: a number outside these is far more likely a mishearing than a real request
MIN_BPM, MAX_BPM = 30, 300
MIN_SCORE, MAX_SCORE = 1, 300

# The single-chord fallback only fires on short utterances, so background conversation
# containing "a", "he", "see" etc. can't pop open a chord screen.
SINGLE_LETTER_MAX_WORDS = 2
CHORD_PHRASE_MAX_WORDS = 5


def clean_transcript(text):
    """Lowercases a Vosk transcript and strips the wake word. Returns '' if nothing is left."""
    return text.lower().replace("hey jarvis", "").replace("jarvis", "").strip()


def is_confirmed(text):
    """Returns True only for a clear 'yes'. Any negation ("that's not right") vetoes it."""
    padded = f" {clean_transcript(text)} "
    if any(w in padded for w in NO_WORDS):
        return False
    return any(w in padded for w in YES_WORDS)


def build_command_grammar():
    """Word list for an optional restricted Vosk recognizer (see listener.py, VOSK_COMMAND_GRAMMAR)."""
    words = {"to", "too", "and", "jarvis"}
    for source in (chord_map, replacements, word_to_num):
        for key in source:
            words.update(key.split())
    for group in (METRONOME_TRIGGERS, STOP_WORDS, TIMER_WORDS, LIBRARY_WORDS, HUB_WORDS,
                  HELP_WORDS, UPDATE_WORDS, HOME_WORDS, TEMPLATE_WORDS):
        for phrase in group:
            words.update(phrase.split())
    return sorted(words) + ["[unk]"]


def build_confirmation_grammar():
    """Word list for an optional restricted yes/no recognizer (see listener.py, VOSK_CONFIRM_GRAMMAR)."""
    words = set()
    for phrase in YES_WORDS + NO_WORDS:
        words.update(phrase.split())
    return sorted(words) + ["[unk]"]


def valid_bpm(value):
    return value is not None and MIN_BPM <= value <= MAX_BPM


def extract_score(text):
    """
    NLP Helper: Scans a transcribed audio string and converts spoken numbers into integer values.
    Handles combinations like "one hundred twenty" -> 120.
    Returns the last identified integer in the string, which represents the target BPM/Score.
    """
    text = text.replace(" and ", " ")
    
    # Normalize edge-case spoken words to standard number words (whole words only, so
    # "for d" can't be matched inside "for dee")
    for word, num in replacements.items():
        text = re.sub(rf"(?<!\w){re.escape(word)}(?!\w)", num, text)
        
    words = text.split()
    nums = []
    current_num = None
    
    # Parse sequential number words into actual integers
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
                # Handle hundreds without the word "hundred" (e.g., "one" + "twenty" -> 120).
                # Only "one" merges: a stray "two" (a mishearing of "to") must not turn
                # "to eighty" into 280.
                elif current_num == 1 and 10 <= val <= 99:
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
    Includes phonetic variation to account for offline STT inaccuracies.
    
    Returns a tuple: (action_type, data)
    - action_type: "standard", "requires_confirmation", "error", or "ignore".
    - data: The dictionary payload for the backend API, or an error string.
    """
    
    # TIMER & METRONOME CONTROLS
    # " beat chord " is a D-chord mishearing, so it must not trip the " beat " metronome trigger
    metro_text = padded_text.replace(" beat chord ", " ")
    if any(w in metro_text for w in METRONOME_TRIGGERS):
        
        # Stop command
        if any(w in padded_text for w in STOP_WORDS):
            print("Action: Stopping Metronome/Timer")
            return "standard", {"metronome_bpm": 0, "timer_active": False}
            
        # 1 Minute Practice Timer
        elif any(w in padded_text for w in TIMER_WORDS):
            print("Action: Starting 1-Minute Timer")
            return "standard", {"timer_active": True, "metronome_bpm": 0, "current_view": "hub"}
            
        # Set Metronome BPM
        else:
            target_bpm = extract_score(padded_text)
            if valid_bpm(target_bpm):
                print(f"Action: Starting Metronome at {target_bpm} BPM")
                return "standard", {"metronome_bpm": target_bpm, "timer_active": False, "current_view": "hub"}
            else:
                return "error", f"Invalid BPM parsed ({target_bpm}); expected {MIN_BPM}-{MAX_BPM}."

    # VIEW NAVIGATION
    # Leaving the hub stops the metronome (every non-hub view below sends metronome_bpm: 0);
    # the hub itself leaves it running.
    # The library is checked before the hub: " chord list " must not be claimed by the hub's " list "
    elif any(w in padded_text for w in LIBRARY_WORDS):
        print("Action: Loading Chord Library")
        return "standard", {"current_view": "all_chords", "metronome_bpm": 0}

    elif any(w in padded_text for w in HUB_WORDS):
        print("Action: Loading Hub")
        return "standard", {"current_view": "hub"}

    elif any(w in padded_text for w in HELP_WORDS):
        print("Action: Loading Help Screen")
        return "standard", {"current_view": "help", "metronome_bpm": 0}

    # DATABASE UPDATES
    # Target Syntax: "Update [Chord 1] to [Chord 2] to [Score]"
    elif any(w in padded_text for w in UPDATE_WORDS):
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
        
        # "Set <garbled word> to <number>" with no chords is a mangled "set metronome to <number>"
        if not found_chords and " set " in padded_text and valid_bpm(score):
            print(f"Action: Starting Metronome at {score} BPM (set with no chords)")
            return "standard", {"metronome_bpm": score, "timer_active": False, "current_view": "hub"}

        # Ensure we found exactly 2 chords and 1 valid score
        if len(found_chords) >= 2 and score is not None and MIN_SCORE <= score <= MAX_SCORE:
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

    # HOME & DASHBOARD RETURN
    elif any(w in padded_text for w in HOME_WORDS):
        print("Action: Returning to Dashboard")
        # Returning home explicitly clears any active practice tools
        return "standard", {"current_view": "calendar", "timer_active": False, "metronome_bpm": 0}

    elif any(w in padded_text for w in TEMPLATE_WORDS):
        print("Action: Loading Blank Template")
        return "standard", {"current_view": "template", "metronome_bpm": 0}
        
    # SINGLE CHORD FALLBACK
    # If no structural commands matched, check if the user just yelled a chord name.
    # Only short utterances count, so background chatter can't trigger a chord screen.
    else:
        word_count = len(padded_text.split())
        identified_chord = None
        for variation, actual_chord in sorted(chord_map.items(), key=lambda x: len(x[0]), reverse=True):
            max_words = SINGLE_LETTER_MAX_WORDS if len(variation.split()) == 1 else CHORD_PHRASE_MAX_WORDS
            if word_count > max_words:
                continue
            if variation in padded_text:
                identified_chord = actual_chord
                break
        
        if identified_chord:
            print(f"Action: Loading {identified_chord} Chord")
            return "standard", {"current_view": identified_chord, "metronome_bpm": 0}
        else:
            return "ignore", None
