import os
import tempfile
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

from app.tts.piper_file_tts import PiperFileTTS

app = FastAPI(title="XiaoLongXia Voice API (Cross Platform)")

PIPER_MODEL = os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx")
tts_engine = PiperFileTTS(PIPER_MODEL)


@app.get("/healthz")
def health():
    return {"status": "ok", "voice": "enabled"}


@app.post("/voice/tts")
def tts(text: str):
    path = tts_engine.synthesize_to_file(text)
    return FileResponse(path, media_type="audio/wav", filename="tts.wav")


@app.post("/voice/stt")
def stt(file: UploadFile = File(...)):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    tmp.write(file.file.read())
    tmp.close()

    # TODO: replace with whisper_cpp or faster-whisper
    return {"text": "[stub] 识别结果"}


@app.post("/voice/chat")
def chat(text: str):
    # TODO: 接入 openclaw
    return {"reply": f"[stub reply] {text}"}
