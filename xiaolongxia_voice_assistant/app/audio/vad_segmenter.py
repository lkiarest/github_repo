import collections
import io
import wave
from typing import Deque, List, Optional

import webrtcvad


class VadAutoSegmenter:
    def __init__(
        self,
        sample_rate: int = 16000,
        frame_ms: int = 30,
        vad_level: int = 2,
        pre_roll_ms: int = 300,
        silence_ms: int = 700,
        min_speech_ms: int = 350,
    ):
        self.sample_rate = sample_rate
        self.frame_ms = frame_ms
        self.frame_bytes = int(sample_rate * frame_ms / 1000) * 2
        self.vad = webrtcvad.Vad(vad_level)

        self.pre_roll_frames = max(1, pre_roll_ms // frame_ms)
        self.max_silence_frames = max(1, silence_ms // frame_ms)
        self.min_speech_frames = max(1, min_speech_ms // frame_ms)

        self._pre_roll: Deque[bytes] = collections.deque(maxlen=self.pre_roll_frames)
        self._active_frames: List[bytes] = []
        self._speech_started = False
        self._speech_frames = 0
        self._silence_frames = 0
        self._completed_segments: Deque[bytes] = collections.deque()

    def add_pcm(self, pcm_bytes: bytes):
        if not pcm_bytes:
            return

        offset = 0
        while offset + self.frame_bytes <= len(pcm_bytes):
            frame = pcm_bytes[offset: offset + self.frame_bytes]
            offset += self.frame_bytes
            self._consume_frame(frame)

    def pop_completed_segment(self) -> Optional[bytes]:
        if self._completed_segments:
            return self._completed_segments.popleft()
        return None

    def reset(self):
        self._pre_roll.clear()
        self._active_frames.clear()
        self._speech_started = False
        self._speech_frames = 0
        self._silence_frames = 0
        self._completed_segments.clear()

    def _consume_frame(self, frame: bytes):
        is_speech = self.vad.is_speech(frame, self.sample_rate)
        self._pre_roll.append(frame)

        if is_speech:
            if not self._speech_started:
                self._speech_started = True
                self._active_frames.extend(list(self._pre_roll))
            self._active_frames.append(frame)
            self._speech_frames += 1
            self._silence_frames = 0
            return

        if self._speech_started:
            self._active_frames.append(frame)
            self._silence_frames += 1
            if self._silence_frames >= self.max_silence_frames:
                self._finalize_segment()

    def _finalize_segment(self):
        if self._speech_frames >= self.min_speech_frames and self._active_frames:
            self._completed_segments.append(self._frames_to_wav_bytes(self._active_frames))
        self._active_frames = []
        self._speech_started = False
        self._speech_frames = 0
        self._silence_frames = 0
        self._pre_roll.clear()

    def _frames_to_wav_bytes(self, frames: List[bytes]) -> bytes:
        bio = io.BytesIO()
        with wave.open(bio, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(self.sample_rate)
            wf.writeframes(b"".join(frames))
        return bio.getvalue()
