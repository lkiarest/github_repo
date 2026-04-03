import collections
import time
from typing import Deque

import numpy as np
import sounddevice as sd
import webrtcvad


class RecorderV2:
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_ms: int = 30,
        silence_ms: int = 900,
        vad_level: int = 2,
        pre_roll_ms: int = 500,
    ):
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_size = int(sample_rate * frame_ms / 1000)
        self.vad = webrtcvad.Vad(vad_level)
        self.silence_frames = silence_ms // frame_ms

        self.pre_roll_frames = max(1, pre_roll_ms // frame_ms)

    def record_once(self, max_seconds: int = 15):
        frames = []
        silence_count = 0
        start = time.time()

        pre_buffer: Deque[np.ndarray] = collections.deque(maxlen=self.pre_roll_frames)
        speech_started = False

        def callback(indata, frames_count, time_info, status):
            nonlocal silence_count, speech_started

            audio = indata[:, 0]
            pcm = (audio * 32768).astype(np.int16).tobytes()

            is_speech = self.vad.is_speech(pcm, self.sample_rate)

            pre_buffer.append(audio.copy())

            if is_speech:
                if not speech_started:
                    # prepend pre-roll audio
                    frames.extend(list(pre_buffer))
                    speech_started = True
                silence_count = 0
                frames.append(audio.copy())
            else:
                if speech_started:
                    silence_count += 1
                    frames.append(audio.copy())

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.frame_size,
            callback=callback,
        ):
            while True:
                time.sleep(self.frame_ms / 1000)
                if speech_started and silence_count > self.silence_frames:
                    break
                if time.time() - start > max_seconds:
                    break

        if not frames:
            return np.zeros(0, dtype=np.float32)

        return np.concatenate(frames)
