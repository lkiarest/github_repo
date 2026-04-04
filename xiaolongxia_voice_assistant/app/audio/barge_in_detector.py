import sounddevice as sd
import webrtcvad
import numpy as np


class BargeInDetector:
    def __init__(self, sample_rate=16000, frame_ms=30, vad_level=2, trigger_frames=3):
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_size = int(sample_rate * frame_ms / 1000)
        self.vad = webrtcvad.Vad(vad_level)
        self.trigger_frames = trigger_frames

    def listen_once(self, timeout_frames=50):
        speech_count = 0

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.frame_size,
        ) as stream:
            for _ in range(timeout_frames):
                data, _ = stream.read(self.frame_size)
                audio = data[:, 0]
                pcm = (audio * 32768).astype(np.int16).tobytes()

                if self.vad.is_speech(pcm, self.sample_rate):
                    speech_count += 1
                    if speech_count >= self.trigger_frames:
                        return True
                else:
                    speech_count = 0

        return False
