import os

from app.audio.recorder_v2 import RecorderV2
from app.llm.openclaw_client import OpenClawClient
from app.runtime.assistant import Assistant
from app.runtime.wake_word import WakeWordMatcher
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.macos_say import MacOSSayTTS

recorder = RecorderV2()
stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)
tts = MacOSSayTTS()
assistant = Assistant()
llm = OpenClawClient()
wake = WakeWordMatcher()

print("🦞 OpenClaw语音助手V2（增强唤醒）启动...")

while True:
    audio = recorder.record_once()
    text = stt.transcribe(audio)

    if not text:
        continue

    print("🎤 识别:", text)

    if not wake.contains_wake_word(text):
        continue

    cleaned = wake.strip_wake_word(text)

    if "QQ" in cleaned or "qq" in cleaned:
        result = assistant.handle_text(cleaned)
        reply = result.get("reply") or result.get("content")
    else:
        reply = llm.chat(cleaned)

    if reply:
        print("🧠 回复:", reply)
        tts.speak(reply)
