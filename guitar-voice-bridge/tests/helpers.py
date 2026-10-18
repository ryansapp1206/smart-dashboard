"""Shared helpers for parser tests."""
from command_parser import parse_intent


def run(text, switches):
    """Runs one transcript through the parser the way listener.py does (padded with spaces)."""
    return parse_intent(f" {text} ", switches)


def outcome(kind, result):
    """Compact description of a parser result, so tests read like a table.

    view:<name>   navigate (non-hub views also clear the metronome)
    bpm:<n>       start metronome
    stop          stop metronome and timer
    timer         start the practice timer
    confirm:<c1>,<c2>,<score>   update awaiting yes/no
    error / ignore
    """
    if kind == "requires_confirmation":
        return f"confirm:{result['c1']},{result['c2']},{result['score']}"
    if kind != "standard":
        return kind
    if result.get("timer_active") is True:
        return "timer"
    if result.get("metronome_bpm", 0) > 0:
        return f"bpm:{result['metronome_bpm']}"
    if "current_view" not in result:
        return "stop"
    return f"view:{result['current_view']}"


def outcome_of(text, switches):
    return outcome(*run(text, switches))
