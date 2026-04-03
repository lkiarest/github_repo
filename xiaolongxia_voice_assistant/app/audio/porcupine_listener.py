import os
from typing import Optional

import pvporcupine
import sounddevice as sd


class PorcupineWakeListener:
    def __init__(
        self,
        access_key: Optional[str] = None,
        keyword_path: Optional[str] = None,
        model_path: Optional[str] = None,
        audio_device_index: Optional[int] = None,
    ):
        self.access_key = access_key or os.getenv("PORCUPINE_ACCESS_KEY", "")
        self.keyword_path = keyword_path or os.getenv("PORCUPINE_KEYWORD_PATH", "")
        self.model_path = model_path or os.getenv("PORCUPINE_MODEL_PATH", "")
        self.audio_device_index = audio_device_index

        if not self.access_key:
            raise ValueError("PORCUPINE_ACCESS_KEY is required")
        if not self.keyword_path:
            raise ValueError("PORCUPINE_KEYWORD_PATH is required")

        kwargs = {
            "access_key": self.access_key,
            "keyword_paths": [self.keyword_path],
        }
        if self.model_path:
            kwargs["model_path"] = self.model_path

        self.engine = pvporcupine.create(**kwargs)

    @property
    def sample_rate(self) -> int:
        return self.engine.sample_rate

    @property
    def frame_length(self) -> int:
        return self.engine.frame_length

    def wait_for_wake(self):
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_length,
            dtype="int16",
            channels=1,
            device=self.audio_device_index,
        ) as stream:
            while True:
                pcm, _ = stream.read(self.frame_length)
                keyword_index = self.engine.process(pcm)
                if keyword_index >= 0:
                    return keyword_index

    def close(self):
        if self.engine is not None:
            self.engine.delete()
