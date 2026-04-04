import queue
import threading
from typing import Optional


class StreamingSentencePlayer:
    def __init__(self, tts):
        self.tts = tts
        self._queue: queue.Queue[Optional[str]] = queue.Queue()
        self._worker: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            self.stop()
            self._stop_event.clear()
            self._worker = threading.Thread(target=self._run, daemon=True)
            self._worker.start()

    def enqueue(self, text: str):
        if text and text.strip():
            self._queue.put(text.strip())

    def finish(self):
        self._queue.put(None)
        worker = self._worker
        if worker is not None:
            worker.join(timeout=30)

    def stop(self):
        self._stop_event.set()
        self.tts.stop()
        try:
            while True:
                self._queue.get_nowait()
        except queue.Empty:
            pass
        worker = self._worker
        if worker is not None and worker.is_alive():
            worker.join(timeout=1)
        self._worker = None

    def is_speaking(self) -> bool:
        return self.tts.is_speaking()

    def _run(self):
        while not self._stop_event.is_set():
            item = self._queue.get()
            if item is None:
                break
            if self._stop_event.is_set():
                break
            self.tts.speak_async(item)
            while self.tts.is_speaking() and not self._stop_event.is_set():
                pass
