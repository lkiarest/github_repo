# V11: 实验性“全双工”架构（后台监听 + 前台生成）
import os
import threading

from app.audio.porcupine_listener import PorcupineWakeListener
from app.stt.whisper_stream_cpp import WhisperStreamCppSTT
from app.tts.interruptible_piper_tts import InterruptiblePiperTTS
from app.tts.streaming_sentence_player import StreamingSentencePlayer
from app.runtime.duplex_coordinator import DuplexCoordinator
from app.runtime.interrupt_intent import InterruptIntentMatcher
from app.runtime.session_memory import SessionMemory
from app.runtime.conversation_mode import ContinuousConversationMode
from app.llm.openclaw_stream_client_v2 import OpenClawStreamClientV2

listener = PorcupineWakeListener()
stt = WhisperStreamCppSTT()
interrupt_intent = InterruptIntentMatcher()
memory = SessionMemory()
coordinator = DuplexCoordinator()

piper_model = os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx")
tts = InterruptiblePiperTTS(model_path=piper_model)
player = StreamingSentencePlayer(tts)

llm = OpenClawStreamClientV2()
conversation = ContinuousConversationMode(timeout_seconds=15)

print("V11 Voice Assistant (experimental duplex)")


def background_listener():
    while not coordinator.stopped():
        if not coordinator.listening_allowed():
            continue

        text = stt.transcribe_live_once(max_seconds=4)
        if not text:
            continue

        if coordinator.is_recently_speaking():
            # 简单“回声抑制”：刚说完就忽略
            continue

        print("[bg user]", text)
        coordinator.submit_user_text(text)


def stream_and_speak(messages):
    buffer = ""
    full = ""

    player.start()

    for chunk in llm.stream_chat(messages):
        buffer += chunk
        full += chunk

        if any(p in buffer for p in ["。", "！", "？"]):
            player.enqueue(buffer)
            coordinator.mark_speaking(1.0)
            buffer = ""

    if buffer:
        player.enqueue(buffer)

    player.finish()
    return full


# 启动后台监听线程
threading.Thread(target=background_listener, daemon=True).start()

while True:
    if not conversation.is_active():
        listener.wait_for_wake()
        conversation.activate()
        memory.clear()

    user_text = coordinator.get_user_text(timeout=0.5)
    if not user_text:
        continue

    print("user:", user_text)

    if interrupt_intent.is_interrupt(user_text):
        player.stop()
        continue

    if any(x in user_text for x in ["退出", "关闭"]):
        player.stop()
        conversation.deactivate()
        memory.clear()
        continue

    conversation.touch()

    memory.add_user(user_text)

    reply = stream_and_speak(memory.get_messages())

    if reply:
        memory.add_assistant(reply)
