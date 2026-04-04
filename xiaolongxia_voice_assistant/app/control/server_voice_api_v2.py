import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, JSONResponse

from app.tts.piper_file_tts import PiperFileTTS
from app.stt.whisper_file_cpp import WhisperFileCppSTT
from app.llm.openclaw_stream_client_v2 import OpenClawStreamClientV2

app = FastAPI(title="XiaoLongXia Voice API v2 (Unified Real Pipeline)")

PIPER_MODEL = os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx")

stt_engine = WhisperFileCppSTT()
tts_engine = PiperFileTTS(PIPER_MODEL)
llm = OpenClawStreamClientV2()


@app.get("/healthz")
def health():
    return {"status": "ok", "pipeline": "stt->llm->tts"}


@app.post("/voice/turn")
def voice_turn(file: UploadFile = File(...)):
    # 1️⃣ 保存音频
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(file.file.read())
    tmp.close()

    # 2️⃣ STT
    try:
        text = stt_engine.transcribe_file(tmp.name)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    if not text:
        return {"text": "", "reply": "", "audio": None}

    # 3️⃣ LLM（非流式，先稳定）
    reply = ""
    try:
        for chunk in llm.stream_chat([{"role": "user", "content": text}]):
            reply += chunk
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    # 4️⃣ TTS
    try:
        audio_path = tts_engine.synthesize_to_file(reply)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return FileResponse(audio_path, media_type="audio/wav", filename="reply.wav", headers={
        "X-User-Text": text,
        "X-Assistant-Text": reply
    })


@app.post("/voice/chat")
def chat(text: str):
    reply = ""
    for chunk in llm.stream_chat([{"role": "user", "content": text}]):
        reply += chunk
    return {"reply": reply}


@app.post("/voice/tts")
def tts(text: str):
    path = tts_engine.synthesize_to_file(text)
    return FileResponse(path, media_type="audio/wav", filename="tts.wav")
