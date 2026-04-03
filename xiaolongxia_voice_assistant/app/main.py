from fastapi import FastAPI
from pydantic import BaseModel
from app.runtime.assistant import Assistant

app = FastAPI()
assistant = Assistant()

class ChatRequest(BaseModel):
    text: str

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/chat")
def chat(req: ChatRequest):
    return assistant.handle_text(req.text)

@app.post("/actions/send-qq-message")
def send_qq(req: ChatRequest):
    return assistant.send_qq(req.text)
