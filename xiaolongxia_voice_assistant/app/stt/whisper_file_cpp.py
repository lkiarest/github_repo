import os
import subprocess
from pathlib import Path


class WhisperFileCppSTT:
    def __init__(self):
        self.bin_path = os.getenv("WHISPER_CPP_BIN", "whisper-cli")
        self.model_path = os.getenv("WHISPER_CPP_MODEL", "model.bin")
        self.language = os.getenv("WHISPER_CPP_LANGUAGE", "zh")
        self.threads = int(os.getenv("WHISPER_CPP_THREADS", "4"))

    def transcribe_file(self, audio_path: str) -> str:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(audio_path)

        cmd = [
            self.bin_path,
            "-m", self.model_path,
            "-f", str(path),
            "-l", self.language,
            "-t", str(self.threads),
            "--no-timestamps",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "whisper cpp failed")

        lines = []
        for line in result.stdout.splitlines():
            text = line.strip()
            if not text:
                continue
            if text.startswith("[") or text.startswith("main:") or text.startswith("whisper_"):
                continue
            lines.append(text)

        return " ".join(lines).strip()
