import os
import signal
import subprocess
import tempfile
from typing import Optional


class InterruptiblePiperTTS:
    def __init__(self, model_path: str, config_path: Optional[str] = None):
        self.model_path = model_path
        self.config_path = config_path
        self._play_process: Optional[subprocess.Popen] = None
        self._last_output_path: Optional[str] = None

    def speak_async(self, text: str):
        self.stop()

        fd, output_path = tempfile.mkstemp(suffix=".wav", prefix="piper_tts_")
        os.close(fd)
        self._last_output_path = output_path

        cmd = [
            "piper",
            "--model",
            self.model_path,
            "--output_file",
            output_path,
        ]
        if self.config_path:
            cmd.extend(["--config", self.config_path])

        synth = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            capture_output=True,
        )
        if synth.returncode != 0:
            raise RuntimeError(synth.stderr.decode("utf-8", errors="ignore") or "piper synthesis failed")

        self._play_process = subprocess.Popen(["afplay", output_path])

    def is_speaking(self) -> bool:
        return self._play_process is not None and self._play_process.poll() is None

    def stop(self):
        if self._play_process is not None and self._play_process.poll() is None:
            self._play_process.terminate()
            try:
                self._play_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._play_process.kill()
        self._play_process = None

        if self._last_output_path and os.path.exists(self._last_output_path):
            try:
                os.remove(self._last_output_path)
            except OSError:
                pass
        self._last_output_path = None
