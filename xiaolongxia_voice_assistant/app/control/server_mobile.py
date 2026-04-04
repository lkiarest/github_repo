import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.control import server_v3

app = FastAPI(title="XiaoLongXia Unified API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT = Path(__file__).resolve().parents[2]


class ConversationRequest(BaseModel):
    text: str
    session_id: Optional[str] = "default"


class ConversationResponse(BaseModel):
    reply: str
    model: str
    session_id: str


@app.get("/healthz")
def healthz():
    return {"status": "ok", "platform": "unified"}


@app.get("/config")
def get_config():
    return server_v3.get_config()


@app.post("/config")
def update_config(req: server_v3.ConfigUpdateRequest):
    return server_v3.update_config(req)


@app.get("/status")
def status():
    return server_v3.status()


@app.post("/start")
def start(req: server_v3.StartRequest):
    return server_v3.start_voice(req)


@app.post("/stop")
def stop():
    return server_v3.stop_voice()


@app.post("/conversation", response_model=ConversationResponse)
def conversation(req: ConversationRequest):
    model = server_v3._runtime_config.get("openclaw_model", "")
    # 移动端 / 跨平台前端可优先使用这个统一入口
    # 这里暂时复用现有模型配置，具体调用仍由桌面语音主循环承担
    return ConversationResponse(
        reply=f"[stub] 已收到：{req.text}",
        model=model,
        session_id=req.session_id or "default",
    )


@app.get("/platforms")
def platforms():
    return {
        "desktop": ["macos", "windows", "linux"],
        "mobile": ["android"],
        "ui_mode": "shared_web_ui",
        "backend_mode": "shared_http_api",
        "root": str(ROOT),
    }
