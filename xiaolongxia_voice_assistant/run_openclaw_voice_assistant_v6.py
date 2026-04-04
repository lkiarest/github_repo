import os

from app.audio.porcupine_listener import PorcupineWakeListener
from app.audio.recorder_v2 import RecorderV2
from app.audio.barge_in_detector import BargeInDetector
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.interruptible_macos_say import InterruptibleMacOSSayTTS
from app.runtime.assistant import Assistant
from app.llm.openclaw_client import OpenClawClient
from app.runtime.conversation_mode import ContinuousConversationMode
from app.runtime.interrupt_intent import InterruptIntentMatcher

listener = PorcupineWakeListener()
recorder = RecorderV2()
barge = BargeInDetector()
interrupt_intent = InterruptIntentMatcher()

tts = InterruptibleMacOSSayTTS()

stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)

assistant = Assistant()
llm = OpenClawClient()
conversation = ContinuousConversationMode(timeout_seconds=12)

print("V6 Voice Assistant (semantic interrupt)")

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

    if interrupt_intent.is_interrupt(text):
        print("semantic interrupt detected")
        tts.stop()
        continue

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

    while tts.is_speaking():
        if barge.listen_once(timeout_frames=10):
            print("voice detected, checking intent...")
            audio2 = recorder.record_once(max_seconds=3)
            text2 = stt.transcribe(audio2)
            print("interrupt text:", text2)

            if interrupt_intent.is_interrupt(text2):
                print("confirmed interrupt")
                tts.stop()
                break
