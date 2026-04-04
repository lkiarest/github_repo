from typing import List, Dict


class SessionMemory:
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self.messages: List[Dict[str, str]] = []

    def add_user(self, text: str):
        self.messages.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, text: str):
        self.messages.append({"role": "assistant", "content": text})
        self._trim()

    def get_messages(self) -> List[Dict[str, str]]:
        return list(self.messages)

    def clear(self):
        self.messages = []

    def _trim(self):
        max_messages = self.max_turns * 2
        if len(self.messages) > max_messages:
            self.messages = self.messages[-max_messages:]
