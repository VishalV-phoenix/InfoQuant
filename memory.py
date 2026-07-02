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
      - Active session states (current_topic, last_research_notes, last_tutor_response, last_quiz)
    """
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.current_topic: str | None = None
        self.last_research_notes: str | None = None
        self.last_tutor_response: str | None = None
        self.last_quiz: str | None = None

    def add_turn(self, topic: str, question: str, response: str) -> None:
        """Adds a turn to the session history and updates active memory variables."""
        self.history.append({
            "topic": topic,
            "question": question,
            "response": response
        })
        self.current_topic = topic
        self.last_tutor_response = response
        self.last_quiz = None  # Reset quiz since a new topic has been learned

    def get_topics(self) -> List[str]:
        """Returns a list of all unique topics discussed in the session."""
        return list(dict.fromkeys(turn["topic"] for turn in self.history if turn.get("topic")))

    def to_json(self) -> str:
        """Serializes the session history to a JSON string."""
        return json.dumps(self.history, indent=2)

    def clear(self) -> None:
        """Clears the session history and active learning variables."""
        self.history.clear()
        self.current_topic = None
        self.last_research_notes = None
        self.last_tutor_response = None
        self.last_quiz = None

# Global instance for the current active session
session_memory = SessionMemory()
