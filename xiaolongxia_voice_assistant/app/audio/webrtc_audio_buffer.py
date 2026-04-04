import audioop
import io
import wave
from typing import Optional

import numpy as np


class WebRTCAudioBuffer:
    def __init__(self, target_sample_rate: int = 16000):
        self.target_sample_rate = target_sample_rate
        self._buffer = bytearray()
        self._rate_state = None

    def append_frame(self, frame):
        ndarray = frame.to_ndarray()

        if ndarray.ndim == 2:
            # aiortc/av 常见布局: [channels, samples]
            if ndarray.shape[0] <= 8:
                mono = ndarray.mean(axis=0)
            else:
                mono = ndarray.mean(axis=1)
        else:
            mono = ndarray

        if mono.dtype != np.int16:
            mono = mono.astype(np.int16)

        pcm = mono.tobytes()
        input_rate = int(getattr(frame, "sample_rate", self.target_sample_rate) or self.target_sample_rate)

        if input_rate != self.target_sample_rate:
            pcm, self._rate_state = audioop.ratecv(
                pcm,
                2,
                1,
                input_rate,
                self.target_sample_rate,
                self._rate_state,
            )

        self._buffer.extend(pcm)

    def clear(self):
        self._buffer.clear()
        self._rate_state = None

    def has_audio(self) -> bool:
        return len(self._buffer) > 0

    def export_wav_bytes(self) -> bytes:
        bio = io.BytesIO()
        with wave.open(bio, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.target_sample_rate)
            wf.writeframes(bytes(self._buffer))
        return bio.getvalue()
