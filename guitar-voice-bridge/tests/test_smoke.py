"""Proves the test tooling works. Real tests live in test_parser.py and test_flow.py."""
from command_parser import parse_intent


def test_parser_imports_and_runs(switches):
    kind, result = parse_intent(" hub ", switches)
    assert kind == "standard" and result == {"current_view": "hub"}


def test_backend_fixture_is_isolated(backend):
    assert backend.port != 3001
    assert backend.data_path.name == "state.json"
    assert backend.state()["current_view"] == "calendar"


def test_listener_fixture_targets_throwaway_backend(listener, backend):
    assert str(backend.port) in listener.GET_URL
    assert listener.handle_command("hub", lambda: "") == "standard"
    assert backend.state()["current_view"] == "hub"
