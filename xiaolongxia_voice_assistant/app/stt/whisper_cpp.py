import subprocess
import tempfile
import soundfile as sf

class WhisperCppSTT:
    def __init__(self, bin_path, model_path, language="zh"):
        self.bin = bin_path
        self.model = model_path
        self.language = language

    def transcribe(self, audio, sample_rate=16000):
        with tempfile.NamedTemporaryFile(suffix=".wav") as f:
            sf.write(f.name, audio, sample_rate)

            cmd = [
                self.bin,
                "-m", self.model,
                "-f", f.name,
                "-l", self.language,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
