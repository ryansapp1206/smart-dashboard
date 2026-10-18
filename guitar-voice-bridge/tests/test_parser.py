"""Transcript tests: what the parser does with text Vosk might produce. No server, no audio."""
import pytest

import command_parser
from command_parser import (clean_transcript, is_confirmed, extract_score, valid_bpm,
                            build_command_grammar, build_confirmation_grammar)
from vocabulary import chord_map
from helpers import run, outcome, outcome_of


# ---------------------------------------------------------------- navigation
@pytest.mark.parametrize("text,view", [
    ("dashboard", "calendar"), ("home", "calendar"), ("colander", "calendar"), ("stop", "calendar"),
    ("help", "help"), ("yelp", "help"), ("what can you do", "help"), ("commands", "help"),
    ("show all chords", "all_chords"), ("show me all chords", "all_chords"),
    ("chord library", "all_chords"), ("every chord", "all_chords"),
    ("template", "template"), ("blank", "template"), ("clear", "template"),
])
def test_navigation_non_hub_views(text, view, switches):
    kind, result = run(text, switches)
    assert (kind, result["current_view"]) == ("standard", view)


@pytest.mark.parametrize("text", ["hub", "chord changes", "show chord changes", "pub", "chart",
                                  "org chart", "cord chart", "scores", "tracking", "overview"])
def test_navigation_hub(text, switches):
    assert run(text, switches) == ("standard", {"current_view": "hub"})


# -------------------------------------------- leaving the hub stops the metronome
@pytest.mark.parametrize("text", ["show all chords", "chord list", "help", "template", "a minor",
                                  "c chord", "see", "dashboard", "home", "stop"])
def test_leaving_hub_clears_metronome(text, switches):
    kind, result = run(text, switches)
    assert kind == "standard"
    assert result["metronome_bpm"] == 0


@pytest.mark.parametrize("text", ["hub", "chord changes"])
def test_hub_leaves_metronome_alone(text, switches):
    _, result = run(text, switches)
    assert "metronome_bpm" not in result


# --------------------------------------------------------------------- numbers
@pytest.mark.parametrize("text,expected", [
    ("sixty nine", 69), ("eighty five", 85), ("ninety", 90), ("twenty", 20), ("twenty five", 25),
    ("85", 85), ("one twenty", 120), ("one hundred twenty five", 125), ("a hundred and ten", 110),
    ("one fifteen", 115), ("sixteen", 16), ("dirty five", 35),
    ("set metronome to sixty", 60),
])
def test_extract_score(text, expected):
    assert extract_score(f" {text} ") == expected


@pytest.mark.parametrize("text", ["hub", "set metronome", ""])
def test_extract_score_no_number(text):
    assert extract_score(f" {text} ") is None


@pytest.mark.parametrize("text,expected", [
    ("metronome two eighty", 80),   # only "one" merges into hundreds; a stray "two" must not make 280
    ("metronome four eighty", 80),  # last number wins
    ("to two eighty", 80),
])
def test_stray_digit_does_not_merge_into_hundreds(text, expected):
    assert extract_score(f" {text} ") == expected


def test_replacements_match_whole_words_only(switches):
    # "for d" is a replacement phrase; it must not fire inside "for dee"
    assert extract_score(" update a to d for dee to sixty ") == 60


def test_bpm_limits():
    assert not valid_bpm(None) and not valid_bpm(29) and not valid_bpm(301)
    assert valid_bpm(30) and valid_bpm(300)


# ------------------------------------------------------------ metronome / timer
@pytest.mark.parametrize("text,expected", [
    ("set metronome to ninety", "bpm:90"), ("metronome one twenty", "bpm:120"),
    ("said metronome to eighty five", "bpm:85"), ("the set metronome to sixty", "bpm:60"),
    ("metro sixty", "bpm:60"), ("bpm one hundred", "bpm:100"),
])
def test_metronome_start(text, expected, switches):
    assert outcome_of(text, switches) == expected


def test_metronome_start_switches_to_hub_and_stops_timer(switches):
    _, result = run("set metronome to ninety", switches)
    assert result == {"metronome_bpm": 90, "timer_active": False, "current_view": "hub"}


@pytest.mark.parametrize("text", [
    "set metronome to sixteen",       # below 30
    "set metronome to four hundred",  # above 300
    "metronome",                      # no number
    "beat",
])
def test_metronome_rejects_bad_bpm(text, switches):
    assert outcome_of(text, switches) == "error"


@pytest.mark.parametrize("text", ["stop metronome", "stop metro", "stop metro know", "metronome off",
                                  "cancel timer", "kill the metronome"])
def test_stop(text, switches):
    assert run(text, switches) == ("standard", {"metronome_bpm": 0, "timer_active": False})


@pytest.mark.parametrize("text", ["timer", "start timer", "time her"])
def test_timer_start(text, switches):
    assert run(text, switches) == ("standard", {"timer_active": True, "metronome_bpm": 0, "current_view": "hub"})


@pytest.mark.parametrize("text", ["set metrodome too eighty five", "set metrodome to eighty five",
                                  "set bedroom to eighty five", "set match around to eighty five"])
def test_set_garbled_word_to_number_is_a_metronome(text, switches):
    # Real log: Vosk mangled "metronome"; with no chords present, "set ... to <n>" means metronome
    assert outcome_of(text, switches) == "bpm:85"


# ---------------------------------------------------------------------- updates
def test_update_asks_for_confirmation(switches):
    kind, result = run("update a to a minor to seventy", switches)
    assert kind == "requires_confirmation"
    assert (result["c1"], result["c2"], result["score"]) == ("A", "Am", 70)
    assert result["payload"] == {"current_view": "hub", "is_listening": True,
                                 "pending_update": {"chord1": "A", "chord2": "Am", "score": 70}}


@pytest.mark.parametrize("text,expected", [
    ("update a to a minor to seventy", "confirm:A,Am,70"),
    ("update a to eat to sixty nine", "confirm:A,E,69"),
    ("set a to e to sixty nine", "confirm:A,E,69"),
    ("modify a minor to a to eighty", "confirm:Am,A,80"),   # spoken order is kept
])
def test_update_valid_pairs(text, expected, switches):
    assert outcome_of(text, switches) == expected


def test_update_unknown_pair_is_rejected(switches):
    assert not any({s["from"], s["to"]} == {"Bm", "Cm"} for s in switches)
    kind, message = run("update b minor to c minor to sixty", switches)
    assert kind == "error" and "Invalid chord combination" in message


@pytest.mark.parametrize("text", [
    "update a to a minor",                  # no score
    "update a to seventy",                  # one chord
    "update a to a minor to four hundred",  # score above 300
    "update a to a minor to zero",          # score below 1
    "update",
])
def test_update_bad_input_is_an_error(text, switches):
    assert outcome_of(text, switches) == "error"


# ---------------------------------------------------------------- single chords
@pytest.mark.parametrize("text,chord", [
    ("a minor", "Am"), ("c chord", "C"), ("see", "C"), ("a", "A"), ("show a", "A"),
    ("the cord", "D"), ("show me that a chord", "A"), ("beat chord", "D"), ("e minor", "Em"),
])
def test_short_chord_requests(text, chord, switches):
    assert outcome_of(text, switches) == f"view:{chord}"


@pytest.mark.parametrize("text", [
    # Invented sentences full of single-letter chord words ("a", "he", "see", "each", "tea"): in
    # the real log, chatter like this used to pop open chord screens.
    "we went to see a movie and he said it was great",
    "i think a lot of people eat a late dinner on each weekend",
    "she ordered a tea and he asked what a good time would be to leave",
    "could you see that a few of them have already gone out early",
    "he thought the plan was fine but each of us needed a break",
])
def test_background_speech_does_not_open_chord_screens(text, switches):
    assert outcome_of(text, switches) == "ignore"


@pytest.mark.parametrize("text", ["", "oh", "yeah", "hello", "that", "the", "really"])
def test_noise_is_ignored(text, switches):
    assert outcome_of(text, switches) == "ignore"


# ------------------------------------------- collisions found by audit / live use
@pytest.mark.parametrize("text,expected", [
    ("chord list", "view:all_chords"),    # hub's " list " must not claim it
    ("cord list", "view:all_chords"),     # what Vosk actually heard
    ("beat chord", "view:D"),             # " beat " must not start the metronome
    ("chord changes", "view:hub"),
    ("set metronome to sixty", "bpm:60"), # " set " must not hijack the metronome
])
def test_known_collisions(text, expected, switches):
    assert outcome_of(text, switches) == expected


# ------------------------------------------------------------ routing audit
@pytest.mark.parametrize("phrase", command_parser.LIBRARY_WORDS)
def test_every_library_phrase_opens_library(phrase, switches):
    assert outcome_of(phrase.strip(), switches) == "view:all_chords"


@pytest.mark.parametrize("phrase", command_parser.HUB_WORDS)
def test_every_hub_phrase_opens_hub(phrase, switches):
    assert outcome_of(phrase.strip(), switches) == "view:hub"


@pytest.mark.parametrize("phrase", command_parser.HELP_WORDS)
def test_every_help_phrase_opens_help(phrase, switches):
    assert outcome_of(phrase.strip(), switches) == "view:help"


@pytest.mark.parametrize("phrase", command_parser.HOME_WORDS)
def test_every_home_phrase_opens_calendar(phrase, switches):
    assert outcome_of(phrase.strip(), switches) == "view:calendar"


@pytest.mark.parametrize("phrase", command_parser.TEMPLATE_WORDS)
def test_every_template_phrase_opens_template(phrase, switches):
    assert outcome_of(phrase.strip(), switches) == "view:template"


@pytest.mark.parametrize("variant,chord", [(k.strip(), v) for k, v in chord_map.items()])
def test_every_chord_variant_loads_its_chord(variant, chord, switches):
    assert outcome_of(variant, switches) == f"view:{chord}"


def test_no_phrase_is_a_substring_of_another_in_the_same_list():
    # A phrase fully contained in another phrase of the same group is redundant or a collision risk
    groups = {"library": command_parser.LIBRARY_WORDS, "hub": command_parser.HUB_WORDS,
              "help": command_parser.HELP_WORDS, "home": command_parser.HOME_WORDS,
              "template": command_parser.TEMPLATE_WORDS}
    for name, words in groups.items():
        assert len(words) == len(set(words)), f"duplicate phrase in {name}"


# ------------------------------------------------------------------ confirmation
@pytest.mark.parametrize("text", ["yes", "yeah", "yep", "yup", "sure", "confirm", "do it", "absolutely",
                                  "hey jarvis yes", "yeah i'll do it", "Yes"])
def test_confirmed(text):
    assert is_confirmed(text)


@pytest.mark.parametrize("text", ["no", "nope", "not", "that's not right", "not right", "don't", "cancel",
                                  "wrong", "stop", "yes no", "yes that's wrong",
                                  "love", "now", "right", "correct", "maybe", "", "oh"])
def test_not_confirmed(text):
    assert not is_confirmed(text)


# --------------------------------------------------------------- transcript cleanup
@pytest.mark.parametrize("raw,clean", [
    ("hey jarvis hub", "hub"), ("Hey Jarvis Hub", "hub"), ("jarvis", ""), ("HELLO", "hello"),
    ("  help  ", "help"), ("", ""),
])
def test_clean_transcript(raw, clean):
    assert clean_transcript(raw) == clean


# ------------------------------------------------------------------- grammars
def test_confirmation_grammar_covers_all_answer_words():
    grammar = build_confirmation_grammar()
    assert grammar[-1] == "[unk]"
    for phrase in command_parser.YES_WORDS + command_parser.NO_WORDS:
        for word in phrase.split():
            assert word in grammar


def test_command_grammar_is_clean_and_complete():
    grammar = build_command_grammar()
    assert grammar[-1] == "[unk]"
    assert len(grammar) == len(set(grammar)) and "" not in grammar
    for word in ("hub", "metronome", "update", "to", "sixty", "minor", "chord", "dashboard"):
        assert word in grammar
