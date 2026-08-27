"""
Voice layer abstraction for STT/TTS. Now accepts a `language` flag
("km" | "en") so the same code path handles both Khmer and English audio.
"""
from dataclasses import dataclass

from config import settings


@dataclass
class TranscriptionResult:
    text: str
    confidence: float


class BaseSTT:
    def transcribe(self, audio_bytes: bytes, language: str = "km") -> TranscriptionResult:
        raise NotImplementedError


class BaseTTS:
    def synthesize(self, text: str, language: str = "km") -> bytes:
        raise NotImplementedError


class MockSTT(BaseSTT):
    def transcribe(self, audio_bytes: bytes, language: str = "km") -> TranscriptionResult:
        return TranscriptionResult(
            text=f"[mock transcription ({language}) - replace with real STT]",
            confidence=0.0,
        )


class MockTTS(BaseTTS):
    def synthesize(self, text: str, language: str = "km") -> bytes:
        return b""


class GoogleSTT(BaseSTT):
    """Google Cloud Speech-to-Text. Expects WebM/Opus audio from the
    browser's MediaRecorder. `language` selects km-KH vs en-US."""

    def transcribe(self, audio_bytes: bytes, language: str = "km") -> TranscriptionResult:
        from google.cloud import speech

        client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=audio_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code=settings.language_code(language),
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
    """Google Cloud Text-to-Speech. Returns MP3 audio bytes. `language`
    selects km-KH vs en-US voice."""

    def synthesize(self, text: str, language: str = "km") -> bytes:
        from google.cloud import texttospeech

        client = texttospeech.TextToSpeechClient()
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=settings.language_code(language),
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL,
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        try:
            response = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        except Exception as e:  # noqa: BLE001 -- external API call, surface a clear error
            raise RuntimeError(f"Google Text-to-Speech request failed: {e}") from e

        return response.audio_content


def get_stt() -> BaseSTT:
    return {"mock": MockSTT(), "google": GoogleSTT()}[settings.stt_provider]


def get_tts() -> BaseTTS:
    return {"mock": MockTTS(), "google": GoogleTTS()}[settings.tts_provider]