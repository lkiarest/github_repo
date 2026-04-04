import time
from difflib import SequenceMatcher
from typing import Optional


class EchoGuard:
    def __init__(self, suppress_seconds: float = 2.5, similarity_threshold: float = 0.72):
        self.suppress_seconds = suppress_seconds
        self.similarity_threshold = similarity_threshold
        self._last_assistant_text: str = ""
        self._last_assistant_at: float = 0.0

    def remember_assistant_text(self, text: str):
        if text and text.strip():
            self._last_assistant_text = self._normalize(text)
            self._last_assistant_at = time.time()

    def looks_like_echo(self, candidate: Optional[str]) -> bool:
        if not candidate or not candidate.strip():
            return False
        if not self._last_assistant_text:
            return False
        if time.time() - self._last_assistant_at > self.suppress_seconds:
            return False

        normalized = self._normalize(candidate)
        if not normalized:
            return False

        if normalized in self._last_assistant_text:
            return True
        if self._last_assistant_text in normalized:
            return True

        ratio = SequenceMatcher(None, normalized, self._last_assistant_text).ratio()
        return ratio >= self.similarity_threshold

    def _normalize(self, text: str) -> str:
        return (
            text.strip()
            .replace("，", "")
            .replace("。", "")
            .replace("？", "")
            .replace("！", "")
            .replace(",", "")
            .replace(".", "")
            .replace("?", "")
            .replace("!", "")
            .replace(" ", "")
            .lower()
        )
