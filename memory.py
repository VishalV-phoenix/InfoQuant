# memory.py
# This module defines the SessionMemory system for InfoQuant.
# It stores conversation history (topics, questions, and responses)
# for the current active session in memory to provide tracking and serializability.

import json
from typing import List, Dict

class SessionMemory:
    """A lightweight in-memory and JSON-serializable session memory store.
    
    This class tracks conversation history for the current session. It stores:
      - Previous topics discussed
      - User questions
      - Tutor responses
    """
    def __init__(self):
        self.history: List[Dict[str, str]] = []

    def add_turn(self, topic: str, question: str, response: str) -> None:
        """Adds a turn to the session history."""
        self.history.append({
            "topic": topic,
            "question": question,
            "response": response
        })

    def get_topics(self) -> List[str]:
        """Returns a list of all unique topics discussed in the session."""
        return list(dict.fromkeys(turn["topic"] for turn in self.history if turn.get("topic")))

    def to_json(self) -> str:
        """Serializes the session history to a JSON string."""
        return json.dumps(self.history, indent=2)

    def clear(self) -> None:
        """Clears the session history."""
        self.history.clear()

# Global instance for the current active session
session_memory = SessionMemory()
