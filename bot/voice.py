"""Speech to text for voice messages with faster-whisper, free and offline.

The package is optional (requirements-voice.txt): without it the bot asks
the user to type instead.
"""

import asyncio
import io
import logging

log = logging.getLogger(__name__)


class Transcriber:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.lock = asyncio.Lock()
        try:
            import faster_whisper  # noqa: F401

            self.available = True
        except ImportError:
            log.warning("faster-whisper is not installed, voice messages are off")
            self.available = False

    def _load(self):
        if self.model is None:
            from faster_whisper import WhisperModel

            log.info("Loading Whisper model %s", self.model_name)
            self.model = WhisperModel(self.model_name, device="cpu", compute_type="int8")
        return self.model

    def _transcribe(self, audio: bytes, language: str | None) -> str:
        segments, _ = self._load().transcribe(io.BytesIO(audio), language=language, beam_size=1, vad_filter=True)
        return " ".join(s.text.strip() for s in segments).strip()

    async def transcribe(self, audio: bytes, language: str | None = None) -> str:
        # One at a time: the model is heavy for a small server.
        async with self.lock:
            return await asyncio.to_thread(self._transcribe, audio, language)
