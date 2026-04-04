import queue
import threading
import time
from typing import Optional


class DuplexCoordinator:
    def __init__(self):
        self._user_queue: queue.Queue[str] = queue.Queue()
        self._stop_event = threading.Event()
        self._listening_enabled = threading.Event()
        self._listening_enabled.set()
        self._speaking_until = 0.0
        self._lock = threading.Lock()

    def submit_user_text(self, text: str):
        if text and text.strip():
            self._user_queue.put(text.strip())

    def get_user_text(self, timeout: float = 0.2) -> Optional[str]:
        try:
            return self._user_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self):
        self._stop_event.set()
        self._listening_enabled.set()

    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def allow_listening(self):
        self._listening_enabled.set()

    def pause_listening(self):
        self._listening_enabled.clear()

    def listening_allowed(self) -> bool:
        return self._listening_enabled.is_set()

    def mark_speaking(self, seconds: float = 1.0):
        with self._lock:
            self._speaking_until = time.time() + seconds

    def is_recently_speaking(self) -> bool:
        with self._lock:
            return time.time() < self._speaking_until
