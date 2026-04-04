import asyncio
import json
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from aiortc import RTCPeerConnection, RTCSessionDescription

app = FastAPI(title="XiaoLongXia AIORTC Voice Server (Experimental)")
pcs = set()


@app.post("/rtc/offer")
async def offer(request: Request):
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            # 简单回显，可扩展为 STT+LLM+TTS
            if isinstance(message, str):
                channel.send(json.dumps({"type": "echo", "text": message}))

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return JSONResponse({
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })


@app.on_event("shutdown")
async def on_shutdown():
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
