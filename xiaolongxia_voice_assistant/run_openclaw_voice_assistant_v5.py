import os

from app.audio.porcupine_listener import PorcupineWakeListener
from app.audio.recorder_v2 import RecorderV2
from app.audio.barge_in_detector import BargeInDetector
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.interruptible_macos_say import InterruptibleMacOSSayTTS
from app.runtime.assistant import Assistant
from app.llm.openclaw_client import OpenClawClient
from app.runtime.conversation_mode import ContinuousConversationMode

listener = PorcupineWakeListener()
recorder = RecorderV2()
barge = BargeInDetector()

tts = InterruptibleMacOSSayTTS()

stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)

assistant = Assistant()
llm = OpenClawClient()
conversation = ContinuousConversationMode(timeout_seconds=12)

print("V5 Voice Assistant (interruptible)")

while True:
    if not conversation.is_active():
        print("waiting wake word...")
        listener.wait_for_wake()
        print("wake detected")
        conversation.activate()

    audio = recorder.record_once()
    text = stt.transcribe(audio)

    if not text:
        continue

    print("text:", text)

    if any(x in text for x in ["退出", "关闭", "停一下"]):
        tts.stop()
        conversation.deactivate()
        continue

    conversation.touch()

    if "QQ" in text or "qq" in text:
        result = assistant.handle_text(text)
        reply = result.get("reply") or result.get("content")
    else:
        reply = llm.chat(text)

    if not reply:
        continue

    print("reply:", reply)

    tts.speak_async(reply)

    # while speaking, listen for interruption
    while tts.is_speaking():
        interrupted = barge.listen_once(timeout_frames=10)
        if interrupted:
            print("interrupted by user")
            tts.stop()
            break
