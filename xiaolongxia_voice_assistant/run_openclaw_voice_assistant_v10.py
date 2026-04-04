# V10: 半实时语音（whisper-stream + 流式LLM + Piper）
import os

from app.audio.porcupine_listener import PorcupineWakeListener
from app.audio.barge_in_detector import BargeInDetector
from app.stt.whisper_stream_cpp import WhisperStreamCppSTT
from app.tts.interruptible_piper_tts import InterruptiblePiperTTS
from app.tts.streaming_sentence_player import StreamingSentencePlayer
from app.runtime.interrupt_intent import InterruptIntentMatcher
from app.runtime.session_memory import SessionMemory
from app.runtime.conversation_mode import ContinuousConversationMode
from app.llm.openclaw_stream_client_v2 import OpenClawStreamClientV2

listener = PorcupineWakeListener()
barge = BargeInDetector()
interrupt_intent = InterruptIntentMatcher()
memory = SessionMemory()

stt = WhisperStreamCppSTT()

piper_model = os.getenv("PIPER_MODEL_PATH", "models/piper/zh.onnx")
tts = InterruptiblePiperTTS(model_path=piper_model)
player = StreamingSentencePlayer(tts)

llm = OpenClawStreamClientV2()
conversation = ContinuousConversationMode(timeout_seconds=12)

print("V10 Voice Assistant (pseudo realtime duplex)")


def stream_and_play(messages):
    buffer = ""
    full = ""

    player.start()

    for chunk in llm.stream_chat(messages):
        buffer += chunk
        full += chunk

        if any(p in buffer for p in ["。", "！", "？"]):
            player.enqueue(buffer)
            buffer = ""

        if barge.listen_once(timeout_frames=2):
            text2 = stt.transcribe_live_once(max_seconds=3)
            if interrupt_intent.is_interrupt(text2):
                player.stop()
                return None
            elif text2:
                player.stop()
                return text2

    if buffer:
        player.enqueue(buffer)

    player.finish()
    return full


while True:
    if not conversation.is_active():
        listener.wait_for_wake()
        conversation.activate()
        memory.clear()

    text = stt.transcribe_live_once(max_seconds=8)

    if not text:
        continue

    print("user:", text)

    if interrupt_intent.is_interrupt(text):
        player.stop()
        continue

    if any(x in text for x in ["退出", "关闭"]):
        player.stop()
        conversation.deactivate()
        memory.clear()
        continue

    conversation.touch()

    memory.add_user(text)

    result = stream_and_play(memory.get_messages())

    if isinstance(result, str) and result.strip():
        memory.add_assistant(result)
    elif isinstance(result, str):
        memory.add_user(result)
