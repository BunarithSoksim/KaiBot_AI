"""
Voice layer abstraction for Khmer STT/TTS. Kept provider-agnostic since
Week 1 (Jul 6-10) explicitly includes benchmarking Google STT/TTS vs.
Whisper vs. any Khmer-specific model against real accents/background
noise before committing.
"""
from dataclasses import dataclass

from config import settings


@dataclass
class TranscriptionResult:
    text: str
    confidence: float


class BaseSTT:
    def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        raise NotImplementedError


class BaseTTS:
    def synthesize(self, text: str) -> bytes:
        raise NotImplementedError


class MockSTT(BaseSTT):
    """Offline stand-in: real audio handling isn't wired up yet."""

    def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        return TranscriptionResult(
            text="[mock transcription - replace with real STT before demo]",
            confidence=0.0,
        )


class MockTTS(BaseTTS):
    def synthesize(self, text: str) -> bytes:
        return b""  # placeholder; wire up real audio synthesis before demo


class GoogleSTT(BaseSTT):
    """Stub: wire up google-cloud-speech with language_code=km-KH."""

    def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        raise NotImplementedError(
            f"Wire up google.cloud.speech here with "
            f"language_code='{settings.khmer_language_code}'."
        )


class GoogleTTS(BaseTTS):
    """Stub: wire up google-cloud-texttospeech with language_code=km-KH."""

    def synthesize(self, text: str) -> bytes:
        raise NotImplementedError(
            f"Wire up google.cloud.texttospeech here with "
            f"language_code='{settings.khmer_language_code}'."
        )


def get_stt() -> BaseSTT:
    return {"mock": MockSTT(), "google": GoogleSTT()}[settings.stt_provider]


def get_tts() -> BaseTTS:
    return {"mock": MockTTS(), "google": GoogleTTS()}[settings.tts_provider]
