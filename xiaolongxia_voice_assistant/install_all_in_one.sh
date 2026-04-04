#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
BREW_BIN="${BREW_BIN:-brew}"
WHISPER_CPP_DIR="${WHISPER_CPP_DIR:-$PROJECT_DIR/third_party/whisper.cpp}"
PIPER_MODEL_DIR="${PIPER_MODEL_DIR:-$PROJECT_DIR/models/piper}"
PIPER_MODEL_NAME="${PIPER_MODEL_NAME:-zh_CN-huayan-medium}"
PIPER_MODEL_PATH="$PIPER_MODEL_DIR/${PIPER_MODEL_NAME}.onnx"
PIPER_CONFIG_PATH="$PIPER_MODEL_DIR/${PIPER_MODEL_NAME}.onnx.json"
OPENCLAW_BASE_URL="${OPENCLAW_BASE_URL:-http://127.0.0.1:18789/v1}"
VOICE_CONTROL_PORT="${VOICE_CONTROL_PORT:-8000}"

say_step() {
  echo
  echo "==> $1"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: missing command: $1"
    exit 1
  fi
}

say_step "Project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"

say_step "Checking Homebrew"
require_cmd "$BREW_BIN"

say_step "Installing system dependencies"
$BREW_BIN list portaudio >/dev/null 2>&1 || $BREW_BIN install portaudio
$BREW_BIN list ffmpeg >/dev/null 2>&1 || $BREW_BIN install ffmpeg
$BREW_BIN list piper >/dev/null 2>&1 || $BREW_BIN install piper

say_step "Preparing Python virtual environment"
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r requirements-webrtc.txt || true
pip install sounddevice numpy webrtcvad-wheels soundfile pvporcupine pytest

say_step "Installing whisper.cpp"
mkdir -p "$(dirname "$WHISPER_CPP_DIR")"
if [ ! -d "$WHISPER_CPP_DIR/.git" ]; then
  git clone https://github.com/ggml-org/whisper.cpp "$WHISPER_CPP_DIR"
fi
cd "$WHISPER_CPP_DIR"
make
./models/download-ggml-model.sh base
WHISPER_CPP_BIN="$WHISPER_CPP_DIR/build/bin/whisper-cli"
WHISPER_STREAM_BIN="$WHISPER_CPP_DIR/build/bin/whisper-stream"
WHISPER_CPP_MODEL="$WHISPER_CPP_DIR/models/ggml-base.bin"
cd "$PROJECT_DIR"

say_step "Downloading Piper model"
mkdir -p "$PIPER_MODEL_DIR"
if [ ! -f "$PIPER_MODEL_PATH" ]; then
  curl -L -o "$PIPER_MODEL_PATH" "https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/${PIPER_MODEL_NAME}.onnx"
fi
if [ ! -f "$PIPER_CONFIG_PATH" ]; then
  curl -L -o "$PIPER_CONFIG_PATH" "https://huggingface.co/rhasspy/piper-voices/resolve/main/zh/zh_CN/huayan/medium/${PIPER_MODEL_NAME}.onnx.json"
fi

say_step "Writing local environment file"
cat > .env.local <<EOF
OPENCLAW_BASE_URL=$OPENCLAW_BASE_URL
OPENCLAW_MODEL=
OPENCLAW_API_KEY=openclaw-local
WHISPER_CPP_BIN=$WHISPER_CPP_BIN
WHISPER_STREAM_BIN=$WHISPER_STREAM_BIN
WHISPER_CPP_MODEL=$WHISPER_CPP_MODEL
WHISPER_CPP_LANGUAGE=zh
PIPER_MODEL_PATH=$PIPER_MODEL_PATH
VOICE_CONTROL_PORT=$VOICE_CONTROL_PORT
EOF

say_step "Making launch scripts executable"
chmod +x launch_control_api.sh || true
chmod +x launch_control_api_v2.sh || true
chmod +x install_v3.sh || true

say_step "Printing next steps"
cat <<EOF

安装完成。

1. 先编辑 .env.local，填入：
   - OPENCLAW_MODEL
   - PORCUPINE_ACCESS_KEY
   - PORCUPINE_KEYWORD_PATH

2. 启动控制后端：
   source .venv/bin/activate
   export $(grep -v '^#' .env.local | xargs)
   ./launch_control_api_v2.sh

3. 打开最新 UI：
   mac_app/frontend_v4/index.html

4. 打包桌面 App：
   cd mac_app/tauri_v2
   tauri dev
   tauri build

5. WebRTC 实时语音：
   uvicorn app.control.server_voice_aiortc_v3:app --reload --port 8000

EOF
