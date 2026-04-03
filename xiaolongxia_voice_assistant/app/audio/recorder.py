import sounddevice as sd
import numpy as np
import time
import webrtcvad

class Recorder:
    def __init__(self, sample_rate=16000, frame_ms=30, silence_ms=900):
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_size = int(sample_rate * frame_ms / 1000)
        self.vad = webrtcvad.Vad(2)
        self.silence_frames = silence_ms // frame_ms

    def record_once(self, max_seconds=15):
        frames = []
        silence_count = 0
        start = time.time()

        def callback(indata, frames_count, time_info, status):
            nonlocal silence_count
            audio = indata[:, 0]
            pcm = (audio * 32768).astype(np.int16).tobytes()

            is_speech = self.vad.is_speech(pcm, self.sample_rate)
            if is_speech:
                silence_count = 0
            else:
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
                if silence_count > self.silence_frames:
                    break
                if time.time() - start > max_seconds:
                    break

        return np.concatenate(frames)
