#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/github_repo/xiaolongxia_voice_assistant}"

echo "==> project dir: $PROJECT_DIR"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: project dir not found: $PROJECT_DIR"
  echo "You can run with:"
  echo "  PROJECT_DIR=/your/path/to/xiaolongxia_voice_assistant bash install_v3.sh"
  exit 1
fi

cd "$PROJECT_DIR"

echo "==> checking Homebrew"
if ! command -v brew >/dev/null 2>&1; then
  echo "ERROR: Homebrew not found."
  echo "Install Homebrew first, then rerun."
  exit 1
fi

echo "==> installing system deps"
brew list portaudio >/dev/null 2>&1 || brew install portaudio

echo "==> preparing python venv"
if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

source .venv/bin/activate

echo "==> upgrading pip"
python -m pip install --upgrade pip setuptools wheel

echo "==> installing python deps"
pip install -r requirements.txt
pip install sounddevice numpy webrtcvad-wheels soundfile pvporcupine pytest

echo "==> creating directories"
mkdir -p app/audio

echo "==> writing app/audio/porcupine_listener.py"
cat > app/audio/porcupine_listener.py <<'PY'
import os
import pvporcupine
import sounddevice as sd

class PorcupineWakeListener:
    def __init__(self):
        access_key = os.getenv("PORCUPINE_ACCESS_KEY")
        keyword_path = os.getenv("PORCUPINE_KEYWORD_PATH")

        if not access_key or not keyword_path:
            raise ValueError("需要配置 PORCUPINE_ACCESS_KEY 和 PORCUPINE_KEYWORD_PATH")

        self.engine = pvporcupine.create(
            access_key=access_key,
            keyword_paths=[keyword_path],
        )

    def wait_for_wake(self):
        with sd.RawInputStream(
            samplerate=self.engine.sample_rate,
            blocksize=self.engine.frame_length,
            dtype="int16",
            channels=1,
        ) as stream:
            while True:
                pcm, _ = stream.read(self.engine.frame_length)
                if self.engine.process(pcm) >= 0:
                    return
PY

echo "==> writing run_openclaw_voice_assistant_v3.py"
cat > run_openclaw_voice_assistant_v3.py <<'PY'
import os

from app.audio.porcupine_listener import PorcupineWakeListener
from app.audio.recorder_v2 import RecorderV2
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.macos_say import MacOSSayTTS
from app.runtime.assistant import Assistant
from app.llm.openclaw_client import OpenClawClient

listener = PorcupineWakeListener()
recorder = RecorderV2()

stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)

tts = MacOSSayTTS()
assistant = Assistant()
llm = OpenClawClient()

print("V3 Voice Assistant (Porcupine)")

while True:
    print("waiting wake word...")
    listener.wait_for_wake()

    print("wake detected")

    audio = recorder.record_once()
    text = stt.transcribe(audio)

    if not text:
        continue

    print("text:", text)

    if "QQ" in text or "qq" in text:
        result = assistant.handle_text(text)
        reply = result.get("reply") or result.get("content")
    else:
        reply = llm.chat(text)

    if reply:
        print("reply:", reply)
        tts.speak(reply)
PY

echo "==> writing .env.porcupine.example"
cat > .env.porcupine.example <<'ENV'
PORCUPINE_ACCESS_KEY=replace_me
PORCUPINE_KEYWORD_PATH=/absolute/path/to/xiaolongxia.ppn

WHISPER_CPP_BIN=/absolute/path/to/whisper-cli
WHISPER_CPP_MODEL=/absolute/path/to/ggml-base.bin

OPENCLAW_BASE_URL=http://127.0.0.1:18789/v1
OPENCLAW_API_KEY=openclaw-local
OPENCLAW_MODEL=replace_me
ENV

echo "==> done"
