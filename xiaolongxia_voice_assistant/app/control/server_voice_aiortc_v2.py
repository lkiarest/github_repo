import asyncio
import json
import os
import tempfile

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from aiortc import RTCPeerConnection, RTCSessionDescription

from app.audio.webrtc_audio_buffer import WebRTCAudioBuffer
from app.stt.whisper_file_cpp import WhisperFileCppSTT
from app.tts.piper_file_tts import PiperFileTTS
from app.llm.openclaw_stream_client_v2 import OpenClawStreamClientV2

app = FastAPI(title="XiaoLongXia AIORTC Voice Server v2 (Real Audio)")
pcs = set()

stt = WhisperFileCppSTT()
tts = PiperFileTTS(os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx"))
llm = OpenClawStreamClientV2()


@app.post("/rtc/offer")
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    audio_buffer = WebRTCAudioBuffer()

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            asyncio.create_task(handle_audio(track, audio_buffer))

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        async def on_message(message):
            msg = json.loads(message)

            if msg.get("type") == "commit":
                if not audio_buffer.has_audio():
                    channel.send(json.dumps({"type": "empty"}))
                    return

                wav_bytes = audio_buffer.export_wav_bytes()
                audio_buffer.clear()

                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
                tmp.write(wav_bytes)
                tmp.close()

                text = await asyncio.to_thread(stt.transcribe_file, tmp.name)
                channel.send(json.dumps({"type": "transcript", "text": text}))

                reply = ""
                for chunk in llm.stream_chat([{"role": "user", "content": text}]):
                    reply += chunk
                    channel.send(json.dumps({"type": "delta", "text": chunk}))

                audio_path = await asyncio.to_thread(tts.synthesize_to_file, reply)
                with open(audio_path, "rb") as f:
                    import base64
                    b64 = base64.b64encode(f.read()).decode()

                channel.send(json.dumps({"type": "audio", "data": b64}))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return JSONResponse({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})


async def handle_audio(track, buffer: WebRTCAudioBuffer):
    while True:
        frame = await track.recv()
        buffer.append_frame(frame)


@app.on_event("shutdown")
async def shutdown():
    await asyncio.gather(*[pc.close() for pc in pcs])
    pcs.clear()
