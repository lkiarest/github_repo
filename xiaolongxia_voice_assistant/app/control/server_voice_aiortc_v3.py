import asyncio
import base64
import json
import os
import tempfile
import audioop

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription

from app.audio.vad_segmenter import VadAutoSegmenter
from app.stt.whisper_file_cpp import WhisperFileCppSTT
from app.tts.piper_file_tts import PiperFileTTS
from app.llm.openclaw_stream_client_v2 import OpenClawStreamClientV2

app = FastAPI(title="XiaoLongXia AIORTC Voice Server v3 (Auto VAD Duplex)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

pcs = set()
stt = WhisperFileCppSTT()
tts = PiperFileTTS(os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx"))
llm = OpenClawStreamClientV2()


class Session:
    def __init__(self, pc: RTCPeerConnection):
        self.pc = pc
        self.channel = None
        self.segmenter = VadAutoSegmenter()
        self.current_task = None
        self.rate_state = None
        self.closed = False

    async def send(self, payload: dict):
        if self.channel and self.channel.readyState == "open":
            self.channel.send(json.dumps(payload, ensure_ascii=False))

    def append_frame(self, frame):
        ndarray = frame.to_ndarray()
        if ndarray.ndim == 2:
            if ndarray.shape[0] <= 8:
                mono = ndarray.mean(axis=0)
            else:
                mono = ndarray.mean(axis=1)
        else:
            mono = ndarray
        if str(mono.dtype) != "int16":
            mono = mono.astype("int16")
        pcm = mono.tobytes()
        input_rate = int(getattr(frame, "sample_rate", 16000) or 16000)
        if input_rate != 16000:
            pcm, self.rate_state = audioop.ratecv(pcm, 2, 1, input_rate, 16000, self.rate_state)
        self.segmenter.add_pcm(pcm)

    async def process_completed_segments(self):
        while True:
            wav_bytes = self.segmenter.pop_completed_segment()
            if wav_bytes is None:
                break
            if self.current_task and not self.current_task.done():
                self.current_task.cancel()
                await self.send({"type": "response.interrupted"})
            self.current_task = asyncio.create_task(self._run_turn(wav_bytes))

    async def _run_turn(self, wav_bytes: bytes):
        tmp_path = None
        try:
            fd, tmp_path = tempfile.mkstemp(prefix="xlx_rtc_vad_", suffix=".wav")
            os.close(fd)
            with open(tmp_path, "wb") as f:
                f.write(wav_bytes)

            await self.send({"type": "turn.started"})
            text = await asyncio.to_thread(stt.transcribe_file, tmp_path)
            await self.send({"type": "transcript.final", "text": text})
            if not text.strip():
                await self.send({"type": "turn.completed", "text": "", "reply": ""})
                return

            reply = ""
            sentence = ""
            for chunk in llm.stream_chat([{"role": "user", "content": text}]):
                reply += chunk
                sentence += chunk
                await self.send({"type": "response.text.delta", "delta": chunk})
                if any(p in sentence for p in ["。", "！", "？", ".", "!", "?"]):
                    audio_path = await asyncio.to_thread(tts.synthesize_to_file, sentence)
                    with open(audio_path, "rb") as af:
                        audio_b64 = base64.b64encode(af.read()).decode("utf-8")
                    await self.send({"type": "response.audio.chunk", "audio_base64": audio_b64, "format": "wav", "text": sentence})
                    try:
                        os.remove(audio_path)
                    except OSError:
                        pass
                    sentence = ""

            if sentence.strip():
                audio_path = await asyncio.to_thread(tts.synthesize_to_file, sentence)
                with open(audio_path, "rb") as af:
                    audio_b64 = base64.b64encode(af.read()).decode("utf-8")
                await self.send({"type": "response.audio.chunk", "audio_base64": audio_b64, "format": "wav", "text": sentence})
                try:
                    os.remove(audio_path)
                except OSError:
                    pass

            await self.send({"type": "response.completed", "text": text, "reply": reply})
        except asyncio.CancelledError:
            await self.send({"type": "response.cancelled"})
            raise
        except Exception as e:
            await self.send({"type": "error", "message": str(e)})
        finally:
            if tmp_path:
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass


@app.get("/healthz")
def healthz():
    return {"status": "ok", "transport": "aiortc-audio-track", "vad": "auto-segmentation"}


@app.post("/rtc/offer")
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)
    session = Session(pc)

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            asyncio.create_task(handle_audio(track, session))

    @pc.on("datachannel")
    def on_datachannel(channel):
        session.channel = channel

        @channel.on("message")
        def on_message(message):
            try:
                payload = json.loads(message)
            except Exception:
                payload = {"type": "text", "text": str(message)}

            if payload.get("type") == "response.cancel" and session.current_task and not session.current_task.done():
                session.current_task.cancel()

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    return JSONResponse({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})


async def handle_audio(track, session: Session):
    while True:
        frame = await track.recv()
        session.append_frame(frame)
        await session.process_completed_segments()


@app.on_event("shutdown")
async def shutdown():
    await asyncio.gather(*[pc.close() for pc in pcs])
    pcs.clear()
