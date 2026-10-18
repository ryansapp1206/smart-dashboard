"""Replay real transcripts from the PM2 voice-bridge log through the current parser.

Usage (from guitar-voice-bridge/):  venv/bin/python tools/replay_log.py [path-to-log]
Read-only: nothing is sent to the backend and no state file is touched.
"""
import contextlib
import io
import json
import os
import re
import sys
from collections import OrderedDict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from command_parser import parse_intent  # noqa: E402

LOG = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.pm2/logs/voice-bridge-out.log")
DATA = os.path.join(os.path.dirname(__file__), "..", "..", "smart-dashboard", "backend", "guitar_data.json")
switches = json.load(open(DATA))["switches"]

transcripts = OrderedDict()
for line in open(LOG):
    m = re.search(r"Parsed input: '(.*)'", line)
    if m and m.group(1):
        transcripts[m.group(1)] = transcripts.get(m.group(1), 0) + 1

for text, count in sorted(transcripts.items(), key=lambda kv: (-kv[1], kv[0])):
    with contextlib.redirect_stdout(io.StringIO()):
        kind, result = parse_intent(f" {text} ", switches)
    if kind == "requires_confirmation":
        summary = f"confirm {result['c1']}<->{result['c2']} = {result['score']}"
    elif kind == "standard":
        summary = json.dumps(result)
    else:
        summary = f"{kind}: {result}" if result else kind
    print(f"{count:3} {text[:55]!r:58} -> {summary[:90]}")
