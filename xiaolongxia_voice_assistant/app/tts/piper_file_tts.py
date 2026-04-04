import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class PiperFileTTS:
    def __init__(self, model_path: str, config_path: Optional[str] = None):
        self.model_path = model_path
        self.config_path = config_path

    def synthesize_to_file(self, text: str, suffix: str = ".wav") -> str:
        fd, output_path = tempfile.mkstemp(prefix="xlx_tts_", suffix=suffix)
        os.close(fd)

        cmd = [
            "piper",
            "--model",
            self.model_path,
            "--output_file",
            output_path,
        ]
        if self.config_path:
            cmd.extend(["--config", self.config_path])

        result = subprocess.run(
            cmd,
            input=text.encode("utf-8"),
            capture_output=True,
        )
        if result.returncode != 0:
            try:
                Path(output_path).unlink(missing_ok=True)
            except Exception:
                pass
            raise RuntimeError(result.stderr.decode("utf-8", errors="ignore") or "piper synthesis failed")

        return output_path
