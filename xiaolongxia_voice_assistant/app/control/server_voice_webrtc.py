import asyncio
import base64
import json
import os
import tempfile
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.stt.whisper_file_cpp import WhisperFileCppSTT
from app.tts.piper_file_tts import PiperFileTTS
from app.llm.openclaw_stream_client_v2 import OpenClawStreamClientV2

app = FastAPI(title="XiaoLongXia WebRTC Signaling API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

stt_engine = WhisperFileCppSTT()
tts_engine = PiperFileTTS(os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx"))
llm = OpenClawStreamClientV2()


@app.get("/healthz")
def healthz():
    return {"status": "ok", "transport": "webrtc-signaling"}


@app.get("/webrtc/config")
def webrtc_config():
    return {
        "iceServers": [
            {"urls": ["stun:stun.l.google.com:19302"]}
        ],
        "audio": {
            "sampleRate": 16000,
            "channelCount": 1,
            "echoCancellation": True,
            "noiseSuppression": True,
            "autoGainControl": True,
        }
    }


class RealtimeWebRTCSession:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
        self.pending_audio = bytearray()
        self.current_task: Optional[asyncio.Task] = None

    async def send_json(self, payload: dict):
        await self.websocket.send_text(json.dumps(payload, ensure_ascii=False))

    async def on_offer(self, sdp: str):
        # 这里先做 signaling scaffold，真实媒体协商可后续切到 aiortc
        await self.send_json({
            "type": "answer",
            "sdp": "stub-answer",
            "note": "当前版本先通过 data channel / websocket 承载音频块，下一步可切 aiortc"
        })

    async def on_audio_chunk(self, audio_base64: str):
        self.pending_audio.extend(base64.b64decode(audio_base64))
        await self.send_json({"type": "input_audio_buffer.updated", "bytes": len(self.pending_audio)})

    async def on_commit(self):
        if not self.pending_audio:
            await self.send_json({"type": "warning", "message": "no audio buffered"})
            return

        if self.current_task and not self.current_task.done():
            self.current_task.cancel()

        audio_bytes = bytes(self.pending_audio)
        self.pending_audio.clear()
        self.current_task = asyncio.create_task(self._run_turn(audio_bytes))

    async def on_interrupt(self):
        if self.current_task and not self.current_task.done():
            self.current_task.cancel()
        await self.send_json({"type": "response.interrupted"})

    async def _run_turn(self, audio_bytes: bytes):
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(prefix="xlx_rtc_", suffix=".wav")
            os.close(fd)
            with open(tmp_path, "wb") as f:
                f.write(audio_bytes)

            text = await asyncio.to_thread(stt_engine.transcribe_file, tmp_path)
            await self.send_json({"type": "transcript.final", "text": text})

            if not text.strip():
                await self.send_json({"type": "response.completed", "text": "", "reply": ""})
                return

            reply = ""
            sentence = ""
            for chunk in llm.stream_chat([{"role": "user", "content": text}]):
                reply += chunk
                sentence += chunk
                await self.send_json({"type": "response.text.delta", "delta": chunk})
                if any(p in sentence for p in ["。", "！", "？", ".", "!", "?"]):
                    audio_path = await asyncio.to_thread(tts_engine.synthesize_to_file, sentence)
                    with open(audio_path, "rb") as af:
                        audio_b64 = base64.b64encode(af.read()).decode("utf-8")
                    await self.send_json({
                        "type": "response.audio.chunk",
                        "audio_base64": audio_b64,
                        "format": "wav",
                        "text": sentence,
                    })
                    try:
                        os.remove(audio_path)
                    except OSError:
                        pass
                    sentence = ""

            if sentence.strip():
                audio_path = await asyncio.to_thread(tts_engine.synthesize_to_file, sentence)
                with open(audio_path, "rb") as af:
                    audio_b64 = base64.b64encode(af.read()).decode("utf-8")
                await self.send_json({
                    "type": "response.audio.chunk",
                    "audio_base64": audio_b64,
                    "format": "wav",
                    "text": sentence,
                })
                try:
                    os.remove(audio_path)
                except OSError:
                    pass

            await self.send_json({"type": "response.completed", "text": text, "reply": reply})
        except asyncio.CancelledError:
            await self.send_json({"type": "response.cancelled"})
            raise
        except Exception as e:
            await self.send_json({"type": "error", "message": str(e)})
        finally:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass


@app.websocket("/ws/webrtc")
async def ws_webrtc(websocket: WebSocket):
    await websocket.accept()
    session = RealtimeWebRTCSession(websocket)
    await session.send_json({"type": "session.created", "mode": "webrtc-signaling"})

    try:
        while True:
            raw = await websocket.receive_text()
            message = json.loads(raw)
            msg_type = message.get("type")

            if msg_type == "offer":
                await session.on_offer(message.get("sdp", ""))
            elif msg_type == "input_audio_buffer.append":
                await session.on_audio_chunk(message.get("audio_base64", ""))
            elif msg_type == "input_audio_buffer.commit":
                await session.on_commit()
            elif msg_type == "response.cancel":
                await session.on_interrupt()
            elif msg_type == "ping":
                await session.send_json({"type": "pong"})
            else:
                await session.send_json({"type": "warning", "message": f"unknown message type: {msg_type}"})
    except WebSocketDisconnect:
        if session.current_task and not session.current_task.done():
            session.current_task.cancel()


@app.post("/webrtc/turn")
def fallback_turn():
    return JSONResponse({"ok": True, "message": "Use /ws/webrtc for realtime sessions"})
