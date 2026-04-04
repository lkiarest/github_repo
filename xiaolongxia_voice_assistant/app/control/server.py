import os
import subprocess
import threading
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="XiaoLongXia Control API")

ROOT = Path(__file__).resolve().parents[2]
VOICE_RUNNER = os.getenv("VOICE_RUNNER", str(ROOT / "run_openclaw_voice_assistant_v11.py"))
PYTHON_BIN = os.getenv("VOICE_PYTHON_BIN", "python")

_process_lock = threading.Lock()
_voice_process: Optional[subprocess.Popen] = None
_last_logs: list[str] = []
_MAX_LOGS = 200


class StartRequest(BaseModel):
    runner: Optional[str] = None


def _append_log(line: str):
    line = line.rstrip()
    if not line:
        return
    _last_logs.append(line)
    if len(_last_logs) > _MAX_LOGS:
        del _last_logs[: len(_last_logs) - _MAX_LOGS]


def _tail_stdout(process: subprocess.Popen):
    assert process.stdout is not None
    for line in process.stdout:
        _append_log(line)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/status")
def status():
    running = _voice_process is not None and _voice_process.poll() is None
    return {
        "running": running,
        "runner": VOICE_RUNNER,
        "pid": _voice_process.pid if running else None,
        "logs": _last_logs[-50:],
    }


@app.post("/start")
def start_voice(req: StartRequest):
    global _voice_process
    with _process_lock:
        if _voice_process is not None and _voice_process.poll() is None:
            return {"started": False, "reason": "already_running", "pid": _voice_process.pid}

        runner = req.runner or VOICE_RUNNER
        _last_logs.clear()
        _voice_process = subprocess.Popen(
            [PYTHON_BIN, runner],
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        threading.Thread(target=_tail_stdout, args=(_voice_process,), daemon=True).start()
        return {"started": True, "pid": _voice_process.pid, "runner": runner}


@app.post("/stop")
def stop_voice():
    global _voice_process
    with _process_lock:
        if _voice_process is None or _voice_process.poll() is not None:
            return {"stopped": False, "reason": "not_running"}

        _voice_process.terminate()
        try:
            _voice_process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            _voice_process.kill()
        pid = _voice_process.pid
        _voice_process = None
        return {"stopped": True, "pid": pid}
