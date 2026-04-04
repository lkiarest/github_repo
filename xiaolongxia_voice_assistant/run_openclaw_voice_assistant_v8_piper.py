# Piper版本（不覆盖原V8，方便回滚）
import os

from app.audio.porcupine_listener import PorcupineWakeListener
from app.audio.recorder_v2 import RecorderV2
from app.audio.barge_in_detector import BargeInDetector
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.interruptible_piper_tts import InterruptiblePiperTTS
from app.runtime.assistant import Assistant
from app.runtime.conversation_mode import ContinuousConversationMode
from app.runtime.interrupt_intent import InterruptIntentMatcher
from app.runtime.session_memory import SessionMemory
from app.llm.openclaw_stream_client_v2 import OpenClawStreamClientV2

listener = PorcupineWakeListener()
recorder = RecorderV2()
barge = BargeInDetector()
interrupt_intent = InterruptIntentMatcher()
memory = SessionMemory()

piper_model = os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx")
tts = InterruptiblePiperTTS(model_path=piper_model)

stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)

assistant = Assistant()
llm = OpenClawStreamClientV2()
conversation = ContinuousConversationMode(timeout_seconds=12)

print("V8 Voice Assistant (Piper)")


def speak_stream(messages):
    buffer = ""
    full_reply = ""

    for chunk in llm.stream_chat(messages):
        buffer += chunk
        full_reply += chunk

        if any(p in buffer for p in ["。", "！", "？"]):
            tts.speak_async(buffer)
            buffer = ""

            while tts.is_speaking():
                if barge.listen_once(timeout_frames=6):
                    audio2 = recorder.record_once(max_seconds=2)
                    text2 = stt.transcribe(audio2)

                    if interrupt_intent.is_interrupt(text2):
                        tts.stop()
                        return None
                    else:
                        tts.stop()
                        return text2

    if buffer:
        tts.speak_async(buffer)

    return full_reply


while True:
    if not conversation.is_active():
        listener.wait_for_wake()
        conversation.activate()
        memory.clear()

    audio = recorder.record_once()
    text = stt.transcribe(audio)

    if not text:
        continue

    print("user:", text)

    if interrupt_intent.is_interrupt(text):
        tts.stop()
        continue

    if any(x in text for x in ["退出", "关闭"]):
        tts.stop()
        conversation.deactivate()
        memory.clear()
        continue

    conversation.touch()

    if "QQ" in text or "qq" in text:
        result = assistant.handle_text(text)
        reply = result.get("reply") or result.get("content")
        if reply:
            tts.speak_async(reply)
        continue

    memory.add_user(text)

    next_input = speak_stream(memory.get_messages())

    if isinstance(next_input, str) and next_input.strip():
        print("semantic switch ->", next_input)
        memory.add_user(next_input)
        continue

    if next_input:
        memory.add_assistant(next_input)
