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
        return b""


class GoogleSTT(BaseSTT):
    """Google Cloud Speech-to-Text, Khmer (km-KH). Expects WebM/Opus audio
    from the browser's MediaRecorder (see chat.html mic button)."""

    def transcribe(self, audio_bytes: bytes) -> TranscriptionResult:
        from google.cloud import speech

        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=settings.khmer_language_code,
        )
        try:
            response = client.recognize(config=config, audio=audio)
        except Exception as e:  # noqa: BLE001 -- external API call, surface a clear error
            raise RuntimeError(f"Google Speech-to-Text request failed: {e}") from e

        if not response.results:
            return TranscriptionResult(text="", confidence=0.0)

        best = response.results[0].alternatives[0]
        return TranscriptionResult(text=best.transcript, confidence=best.confidence)

class GoogleTTS(BaseTTS):
    """Google Cloud Text-to-Speech, Khmer (km-KH). Returns MP3 audio bytes."""

    def synthesize(self, text: str) -> bytes:
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=settings.khmer_language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        try:
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
        except Exception as e:
            raise RuntimeError(f"Google Text-to-Speech request failed: {e}") from e

        return response.audio_content

def get_stt() -> BaseSTT:
    return {"mock": MockSTT(), "google": GoogleSTT()}[settings.stt_provider]


def get_tts() -> BaseTTS:
    return {"mock": MockTTS(), "google": GoogleTTS()}[settings.tts_provider]