import subprocess
import time
from typing import Optional


class InterruptibleMacOSSayTTS:
    def __init__(self, voice: str = "Tingting"):
        self.voice = voice
        self._process: Optional[subprocess.Popen] = None

    def speak_async(self, text: str):
        self.stop()
        self._process = subprocess.Popen(["say", "-v", self.voice, text])

    def is_speaking(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def wait(self, poll_interval: float = 0.05):
        while self.is_speaking():
            time.sleep(poll_interval)

    def stop(self):
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._process.kill()
        self._process = None
