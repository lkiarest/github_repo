# V9: 真·边生成边播（句子队列 + 并行TTS）
import os

from app.audio.porcupine_listener import PorcupineWakeListener
from app.audio.recorder_v2 import RecorderV2
from app.audio.barge_in_detector import BargeInDetector
from app.stt.whisper_cpp import WhisperCppSTT
from app.tts.interruptible_piper_tts import InterruptiblePiperTTS
from app.tts.streaming_sentence_player import StreamingSentencePlayer
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
player = StreamingSentencePlayer(tts)

stt = WhisperCppSTT(
    bin_path=os.getenv("WHISPER_CPP_BIN", "whisper-cli"),
    model_path=os.getenv("WHISPER_CPP_MODEL", "model.bin"),
)

assistant = Assistant()
llm = OpenClawStreamClientV2()
conversation = ContinuousConversationMode(timeout_seconds=12)

print("V9 Voice Assistant (true streaming)")


def stream_and_play(messages):
    buffer = ""
    full = ""

    player.start()

    for chunk in llm.stream_chat(messages):
        buffer += chunk
        full += chunk

        # 一旦形成句子就立即播放（不中断生成）
        if any(p in buffer for p in ["。", "！", "？"]):
            player.enqueue(buffer)
            buffer = ""

        # 同时监听打断（不阻塞生成）
        if barge.listen_once(timeout_frames=2):
            audio2 = recorder.record_once(max_seconds=2)
            text2 = stt.transcribe(audio2)

            if interrupt_intent.is_interrupt(text2):
                player.stop()
                return None
            else:
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

    audio = recorder.record_once()
    text = stt.transcribe(audio)

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

    if "QQ" in text or "qq" in text:
        result = assistant.handle_text(text)
        reply = result.get("reply") or result.get("content")
        if reply:
            tts.speak_async(reply)
        continue

    memory.add_user(text)

    result = stream_and_play(memory.get_messages())

    if isinstance(result, str) and result.strip():
        memory.add_assistant(result)
    elif isinstance(result, str):
        memory.add_user(result)
