"""
engine.py
=========
Core logic for RuleBot. Separated from any interface (terminal or browser)
so both can share the exact same "brain."

Key upgrades over a basic rule-based chatbot:
    1. Knowledge lives in a JSON file, not hardcoded in Python.
    2. Fuzzy matching - understands "helo" or "wats ur name" even with typos,
       instead of requiring an exact string match.
    3. Conversation memory - keeps a history of the chat.
    4. "Teach" feature - users can add their own custom Q&A pairs at runtime,
       and they get saved permanently back into the knowledge base.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

DEFAULT_KB_PATH = Path(__file__).resolve().parents[1] / "data" / "knowledge_base.json"
FALLBACK_REPLIES = [
    "I don't understand that yet. Type 'help' to see what I know, or teach me with: teach: <question> => <answer>",
    "Hmm, I'm not sure how to respond to that. Try 'help' for ideas.",
]
MATCH_THRESHOLD = 0.72  # similarity score (0-1) required to accept a fuzzy match


@dataclass
class ChatTurn:
    """A single exchange in the conversation."""
    user_message: str
    bot_reply: str
    matched_tag: str | None = None


@dataclass
class ChatEngine:
    """
    The chatbot's brain. Loads a knowledge base, matches user input against
    it (exact or fuzzy), and can learn new responses on the fly.
    """

    kb_path: Path = DEFAULT_KB_PATH
    intents: list[dict] = field(default_factory=list)
    history: list[ChatTurn] = field(default_factory=list)

    def __post_init__(self):
        self.kb_path = Path(self.kb_path)
        self._load_kb()

    # ------------------------------------------------------------------
    def _load_kb(self) -> None:
        if not self.kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found at '{self.kb_path}'")
        with open(self.kb_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.intents = data.get("intents", [])

    def _save_kb(self) -> None:
        with open(self.kb_path, "w", encoding="utf-8") as f:
            json.dump({"intents": self.intents}, f, indent=2)

    # ------------------------------------------------------------------
    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """Returns a 0-1 score of how alike two strings are (typo-tolerant)."""
        return SequenceMatcher(None, a, b).ratio()

    def _best_match(self, user_input: str) -> tuple[dict | None, float]:
        """Finds the intent whose patterns best match the user's input."""
        best_intent = None
        best_score = 0.0

        for intent in self.intents:
            for pattern in intent["patterns"]:
                # Exact substring match counts as a very strong match
                if pattern in user_input or user_input in pattern:
                    score = 0.95
                else:
                    score = self._similarity(user_input, pattern)

                if score > best_score:
                    best_score = score
                    best_intent = intent

        return best_intent, best_score

    # ------------------------------------------------------------------
    def get_response(self, raw_input: str) -> ChatTurn:
        """
        Main entry point: takes raw user text, returns a ChatTurn containing
        the bot's reply. Also records the exchange in self.history.
        """
        user_input = raw_input.lower().strip()

        # Special command: teach the bot a new response
        if user_input.startswith("teach:"):
            reply = self._handle_teach(raw_input[len("teach:"):])
            turn = ChatTurn(raw_input, reply, matched_tag="teach")
            self.history.append(turn)
            return turn

        intent, score = self._best_match(user_input)

        if intent and score >= MATCH_THRESHOLD:
            reply = random.choice(intent["responses"])
            tag = intent["tag"]
        else:
            reply = random.choice(FALLBACK_REPLIES)
            tag = None

        turn = ChatTurn(raw_input, reply, matched_tag=tag)
        self.history.append(turn)
        return turn

    # ------------------------------------------------------------------
    def _handle_teach(self, payload: str) -> str:
        """
        Parses input like: " what is python => Python is a programming language"
        and saves it as a new custom intent, persisted to the JSON file.
        """
        if "=>" not in payload:
            return "To teach me, use this format: teach: <question> => <answer>"

        pattern, response = payload.split("=>", 1)
        pattern = pattern.strip().lower()
        response = response.strip()

        if not pattern or not response:
            return "Both the question and answer must be non-empty."

        self.intents.append(
            {
                "tag": f"custom_{len(self.intents)}",
                "patterns": [pattern],
                "responses": [response],
            }
        )
        self._save_kb()
        return f"Got it! I'll now respond to '{pattern}' with that answer."

    # ------------------------------------------------------------------
    def reset_history(self) -> None:
        self.history = []
