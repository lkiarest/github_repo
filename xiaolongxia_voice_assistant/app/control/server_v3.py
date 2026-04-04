import os
import subprocess
import threading
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="XiaoLongXia Desktop Control API v3")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VOICE_RUNNER = os.getenv("VOICE_RUNNER", str(ROOT / "run_openclaw_voice_assistant_v12.py"))
DEFAULT_PYTHON_BIN = os.getenv("VOICE_PYTHON_BIN", "python")

_process_lock = threading.Lock()
_voice_process: Optional[subprocess.Popen] = None
_last_logs: list[str] = []
_recent_events: list[dict] = []
_MAX_LOGS = 400
_runtime_config = {
    "voice_runner": DEFAULT_VOICE_RUNNER,
    "python_bin": DEFAULT_PYTHON_BIN,
    "openclaw_base_url": os.getenv("OPENCLAW_BASE_URL", "http://127.0.0.1:18789/v1"),
    "openclaw_model": os.getenv("OPENCLAW_MODEL", ""),
    "whisper_model": os.getenv("WHISPER_CPP_MODEL", ""),
    "piper_model": os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx"),
}


class StartRequest(BaseModel):
    runner: Optional[str] = None


class ConfigResponse(BaseModel):
    voice_runner: str
    python_bin: str
    openclaw_base_url: str
    openclaw_model: str
    whisper_model: str
    piper_model: str


class ConfigUpdateRequest(BaseModel):
    voice_runner: Optional[str] = None
    python_bin: Optional[str] = None
    openclaw_base_url: Optional[str] = None
    openclaw_model: Optional[str] = None
    whisper_model: Optional[str] = None
    piper_model: Optional[str] = None


class StatusResponse(BaseModel):
    running: bool
    runner: str
    pid: Optional[int]
    uptime_seconds: Optional[int]
    logs: list[str]
    events: list[dict]
    config: ConfigResponse


def _append_log(line: str):
    line = line.rstrip()
    if not line:
        return
    _last_logs.append(line)
    if len(_last_logs) > _MAX_LOGS:
        del _last_logs[: len(_last_logs) - _MAX_LOGS]

    lowered = line.lower()
    if line.startswith("user:"):
        _recent_events.append({"ts": time.time(), "kind": "user", "text": line[5:].strip()})
    elif line.startswith("reply:") or "assistant" in lowered:
        _recent_events.append({"ts": time.time(), "kind": "assistant", "text": line.split(":", 1)[-1].strip()})
    elif "wake" in lowered or line.startswith("status:"):
        _recent_events.append({"ts": time.time(), "kind": "status", "text": line})

    if len(_recent_events) > 100:
        del _recent_events[: len(_recent_events) - 100]


def _tail_stdout(process: subprocess.Popen):
    assert process.stdout is not None
    for line in process.stdout:
        _append_log(line)


def _current_config() -> ConfigResponse:
    return ConfigResponse(**_runtime_config)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/config", response_model=ConfigResponse)
def get_config():
    return _current_config()


@app.post("/config", response_model=ConfigResponse)
def update_config(req: ConfigUpdateRequest):
    updates = req.model_dump(exclude_none=True)
    for key, value in updates.items():
        if isinstance(value, str) and value.strip():
            _runtime_config[key] = value.strip()
    _append_log(f"status: updated config model={_runtime_config['openclaw_model']}")
    return _current_config()


@app.get("/status", response_model=StatusResponse)
def status():
    running = _voice_process is not None and _voice_process.poll() is None
    started_at = getattr(_voice_process, "_xlx_started_at", None) if running else None
    uptime = int(time.time() - started_at) if started_at else None
    return StatusResponse(
        running=running,
        runner=_runtime_config["voice_runner"],
        pid=_voice_process.pid if running else None,
        uptime_seconds=uptime,
        logs=_last_logs[-80:],
        events=_recent_events[-30:],
        config=_current_config(),
    )


@app.post("/start")
def start_voice(req: StartRequest):
    global _voice_process
    with _process_lock:
        if _voice_process is not None and _voice_process.poll() is None:
            return {"started": False, "reason": "already_running", "pid": _voice_process.pid}

        runner = req.runner or _runtime_config["voice_runner"]
        _last_logs.clear()
        _recent_events.clear()

        child_env = os.environ.copy()
        child_env["OPENCLAW_BASE_URL"] = _runtime_config["openclaw_base_url"]
        child_env["OPENCLAW_MODEL"] = _runtime_config["openclaw_model"]
        child_env["WHISPER_CPP_MODEL"] = _runtime_config["whisper_model"]
        child_env["PIPER_MODEL_PATH"] = _runtime_config["piper_model"]

        _voice_process = subprocess.Popen(
            [_runtime_config["python_bin"], runner],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=child_env,
        )
        _voice_process._xlx_started_at = time.time()
        threading.Thread(target=_tail_stdout, args=(_voice_process,), daemon=True).start()
        _append_log(f"status: started runner {runner} model={_runtime_config['openclaw_model']}")
        return {"started": True, "pid": _voice_process.pid, "runner": runner, "model": _runtime_config["openclaw_model"]}


@app.post("/stop")
def stop_voice():
    global _voice_process
    with _process_lock:
        if _voice_process is None or _voice_process.poll() is not None:
            return {"stopped": False, "reason": "not_running"}

        _voice_process.terminate()
        try:
            _voice_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _voice_process.kill()
        pid = _voice_process.pid
        _voice_process = None
        _append_log("status: stopped runner")
        return {"stopped": True, "pid": pid}
