import os

from app.audio.porcupine_listener import PorcupineWakeListener
from app.audio.recorder_v2 import RecorderV2
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.macos_say import MacOSSayTTS
from app.runtime.assistant import Assistant
from app.llm.openclaw_client import OpenClawClient
from app.runtime.conversation_mode import ContinuousConversationMode

listener = PorcupineWakeListener()
recorder = RecorderV2()

stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)

tts = MacOSSayTTS()
assistant = Assistant()
llm = OpenClawClient()
conversation = ContinuousConversationMode(timeout_seconds=12)

print("V4 Voice Assistant (continuous mode)")

while True:
    if not conversation.is_active():
        print("waiting wake word...")
        listener.wait_for_wake()
        print("wake detected")
        conversation.activate()
    else:
        print(f"continuous mode active ({conversation.remaining_seconds()}s left)")

    audio = recorder.record_once()
    text = stt.transcribe(audio)

    if not text:
        continue

    print("text:", text)

    # exit phrase
    if any(x in text for x in ["退出", "关闭", "停一下"]):
        print("exit continuous mode")
        tts.speak("好的，我先退下，有需要再叫我")
        conversation.deactivate()
        continue

    conversation.touch()

    if "QQ" in text or "qq" in text:
        result = assistant.handle_text(text)
        reply = result.get("reply") or result.get("content")
    else:
        reply = llm.chat(text)

    if reply:
        print("reply:", reply)
        tts.speak(reply)
