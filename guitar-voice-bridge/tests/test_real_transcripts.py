"""Regression set: transcripts Vosk really produced for the owner's voice, with hand-labelled intent."""
import json
from pathlib import Path

import pytest

from helpers import outcome_of

CASES = json.loads((Path(__file__).parent / "fixtures" / "real_transcripts.json").read_text())["cases"]


@pytest.mark.parametrize("case", CASES, ids=[c["say"][:50] for c in CASES])
def test_real_transcript(case, switches):
    assert outcome_of(case["say"], switches) == case["expect"]
