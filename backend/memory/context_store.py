import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class ContextStore:
    """Manages conversation context and state for ANAY."""
    
    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.history: List[Dict[str, str]] = []

    def add_message(self, role: str, content: str):
        """Add a message to the history."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self) -> List[Dict[str, str]]:
        """Retrieve the conversation history."""
        return self.history

    def clear(self):
        """Clear the history."""
        self.history = []
        logger.info("Context history cleared.")
