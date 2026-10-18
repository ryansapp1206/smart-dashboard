"""Shared fixtures. The backend fixture starts a throwaway server and can never touch production."""
import json
import os
import shutil
import socket
import subprocess
import time
from pathlib import Path

import pytest
import requests

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = REPO_ROOT / "smart-dashboard" / "backend"
STARTER_DATA = BACKEND_DIR / "guitar_data.example.json"
LIVE_DATA = (BACKEND_DIR / "guitar_data.json").resolve()
PRODUCTION_PORT = 3001


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Backend:
    """A running throwaway backend plus helpers to inspect its state."""

    def __init__(self, port, data_path):
        self.port = port
        self.data_path = data_path
        self.url = f"http://localhost:{port}"

    def state(self):
        return requests.get(f"{self.url}/api/guitar", timeout=2).json()

    def post(self, payload):
        return requests.post(f"{self.url}/api/guitar/update", json=payload, timeout=2)

    def score(self, a, b):
        for sw in self.state()["switches"]:
            if {sw["from"], sw["to"]} == {a, b}:
                return sw["score"]
        raise KeyError((a, b))


@pytest.fixture
def backend(tmp_path):
    """Fresh backend per test: random port, temp copy of the STARTER data (never the live file)."""
    port = _free_port()
    data_path = (tmp_path / "state.json").resolve()
    shutil.copy(STARTER_DATA, data_path)

    # Safety guard: refuse to run anywhere near production
    assert port != PRODUCTION_PORT, "refusing to use the production port"
    assert data_path != LIVE_DATA, "refusing to use the live state file"

    env = dict(os.environ, PORT=str(port), DATA_PATH=str(data_path), GOOGLE_CREDENTIALS="")
    proc = subprocess.Popen(["node", "server.js"], cwd=BACKEND_DIR, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    backend = Backend(port, data_path)
    try:
        for _ in range(50):
            try:
                requests.get(f"{backend.url}/api/guitar", timeout=0.5)
                break
            except requests.RequestException:
                time.sleep(0.1)
        else:
            pytest.fail("test backend did not start")
        yield backend
    finally:
        proc.terminate()
        proc.wait(timeout=5)


@pytest.fixture
def listener(backend, monkeypatch):
    """The listener module, pointed at the throwaway backend."""
    import listener as listener_module
    monkeypatch.setattr(listener_module, "GET_URL", f"{backend.url}/api/guitar")
    monkeypatch.setattr(listener_module, "API_URL", f"{backend.url}/api/guitar/update")
    return listener_module


@pytest.fixture(scope="session")
def switches():
    """Chord-switch list from the starter data, for parser tests that don't need a server."""
    return json.loads(STARTER_DATA.read_text())["switches"]
