#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")" && pwd)}"
PYTHON_BIN="${VOICE_PYTHON_BIN:-python}"
HOST="${VOICE_CONTROL_HOST:-127.0.0.1}"
PORT="${VOICE_CONTROL_PORT:-8000}"

cd "$PROJECT_DIR"

exec "$PYTHON_BIN" -m uvicorn app.control.server_v3:app --host "$HOST" --port "$PORT"
