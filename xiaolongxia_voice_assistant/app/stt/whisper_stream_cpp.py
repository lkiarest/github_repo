import os
import subprocess
import threading
import time
from queue import Queue, Empty
from typing import Optional


class WhisperStreamCppSTT:
    def __init__(self):
        self.bin_path = os.getenv("WHISPER_STREAM_BIN", "whisper-stream")
        self.model_path = os.getenv("WHISPER_CPP_MODEL", "model.bin")
        self.language = os.getenv("WHISPER_CPP_LANGUAGE", "zh")
        self.step_ms = int(os.getenv("WHISPER_STREAM_STEP_MS", "500"))
        self.length_ms = int(os.getenv("WHISPER_STREAM_LENGTH_MS", "5000"))
        self.keep_ms = int(os.getenv("WHISPER_STREAM_KEEP_MS", "200"))
        self.capture_id = os.getenv("WHISPER_STREAM_CAPTURE_ID", "")
        self.threads = int(os.getenv("WHISPER_STREAM_THREADS", "4"))

    def transcribe_live_once(self, max_seconds: int = 8, idle_seconds: float = 1.2) -> str:
        cmd = [
            self.bin_path,
            "-m", self.model_path,
            "-l", self.language,
            "-t", str(self.threads),
            "--step", str(self.step_ms),
            "--length", str(self.length_ms),
            "--keep", str(self.keep_ms),
        ]
        if self.capture_id:
            cmd.extend(["-c", str(self.capture_id)])

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        q: Queue[str] = Queue()

        def reader():
            assert process.stdout is not None
            for line in process.stdout:
                q.put(line.rstrip())

        thread = threading.Thread(target=reader, daemon=True)
        thread.start()

        start = time.time()
        last_text_time = 0.0
        last_text = ""

        try:
            while time.time() - start < max_seconds:
                try:
                    line = q.get(timeout=0.2)
                except Empty:
                    if last_text and (time.time() - last_text_time) >= idle_seconds:
                        break
                    continue

                cleaned = self._extract_text(line)
                if cleaned:
                    last_text = cleaned
                    last_text_time = time.time()
        finally:
            process.terminate()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()

        return last_text.strip()

    def _extract_text(self, line: str) -> str:
        text = line.strip()
        if not text:
            return ""
        prefixes = ["[", "whisper_", "main:", "init:"]
        if any(text.startswith(prefix) for prefix in prefixes):
            return ""
        return text
