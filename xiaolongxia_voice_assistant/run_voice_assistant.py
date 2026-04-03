import os
from app.audio.recorder import Recorder
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.macos_say import MacOSSayTTS
from app.runtime.assistant import Assistant

recorder = Recorder()
stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)
tts = MacOSSayTTS()
assistant = Assistant()

print("🎤 小龙虾语音助手启动，开始监听...")

while True:
    audio = recorder.record_once()
    text = stt.transcribe(audio)

    if not text:
        continue

    print("你说:", text)

    if "小龙虾" not in text:
        continue

    cleaned = text.replace("小龙虾", "").strip()
    result = assistant.handle_text(cleaned)

    reply = result.get("reply") or result.get("content")
    if reply:
        print("助手:", reply)
        tts.speak(reply)
