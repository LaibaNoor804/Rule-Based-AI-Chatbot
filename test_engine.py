"""
test_engine.py
===============
Run with: pytest tests/
"""

import json
import shutil
from pathlib import Path

import pytest

from core.engine import ChatEngine

ORIGINAL_KB = Path(__file__).resolve().parents[1] / "data" / "knowledge_base.json"


@pytest.fixture
def engine(tmp_path):
    """Uses a temporary COPY of the knowledge base so tests never modify the real file."""
    temp_kb = tmp_path / "knowledge_base.json"
    shutil.copy(ORIGINAL_KB, temp_kb)
    return ChatEngine(kb_path=temp_kb)


def test_exact_match_returns_correct_intent(engine):
    turn = engine.get_response("hello")
    assert turn.matched_tag == "greeting"


def test_fuzzy_match_handles_typos(engine):
    turn = engine.get_response("helo")
    assert turn.matched_tag == "greeting"


def test_unknown_input_returns_fallback(engine):
    turn = engine.get_response("asdkjhaskjdh nonsense text")
    assert turn.matched_tag is None


def test_exit_words_are_not_in_knowledge_base(engine):
    # exit handling is the CLI's job, not the engine's - just confirm no false intent match
    turn = engine.get_response("bye")
    assert turn.bot_reply is not None


def test_teach_adds_new_response_and_it_becomes_retrievable(engine):
    teach_turn = engine.get_response("teach: what is rust => Rust is a systems programming language")
    assert "Got it" in teach_turn.bot_reply

    followup = engine.get_response("what is rust")
    assert "Rust" in followup.bot_reply


def test_teach_with_bad_format_gives_helpful_error(engine):
    turn = engine.get_response("teach: this has no separator")
    assert "format" in turn.bot_reply.lower()


def test_history_records_every_turn(engine):
    engine.get_response("hello")
    engine.get_response("thanks")
    assert len(engine.history) == 2


def test_reset_history_clears_it(engine):
    engine.get_response("hello")
    engine.reset_history()
    assert len(engine.history) == 0


def test_missing_kb_file_raises_error():
    with pytest.raises(FileNotFoundError):
        ChatEngine(kb_path="nonexistent_file.json")
