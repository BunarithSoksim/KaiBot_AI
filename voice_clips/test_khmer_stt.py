"""
Quick, free Khmer STT accuracy test — no Google Cloud account or billing
needed. Uses the free Google Web Speech API via the `SpeechRecognition`
library. Good enough for a first impression before committing to the paid
Cloud Speech-to-Text API.

Setup (run once):
    pip install SpeechRecognition pydub
    # pydub also needs ffmpeg installed on your system:
    #   sudo apt install ffmpeg

Usage:
    1. Record a few short Khmer voice clips (any format: mp3, m4a, ogg, wav)
    2. Put them in a folder, e.g. ./voice_clips/
    3. Run: python test_khmer_stt.py ./voice_clips/
    4. Read results.txt for what got transcribed vs. what you actually said
"""
import sys
from pathlib import Path

import speech_recognition as sr
from pydub import AudioSegment


def transcribe_folder(folder_path: str):
    folder = Path(folder_path)
    if not folder.exists():
        print(f"Folder not found: {folder_path}")
        return

    recognizer = sr.Recognizer()
    results = []

    audio_files = sorted(
        f for f in folder.iterdir()
        if f.suffix.lower() in (".mp3", ".m4a", ".ogg", ".wav", ".flac")
    )

    if not audio_files:
        print(f"No audio files found in {folder_path}")
        return

    for audio_file in audio_files:
        print(f"Processing: {audio_file.name}")
        wav_path = audio_file.with_suffix(".converted.wav")

        try:
            # Convert to wav (Google's API needs wav/flac)
            audio = AudioSegment.from_file(audio_file)
            audio.export(wav_path, format="wav")

            with sr.AudioFile(str(wav_path)) as source:
                audio_data = recognizer.record(source)

            transcribed_text = recognizer.recognize_google(audio_data, language="km-KH")
            results.append((audio_file.name, transcribed_text, None))
            print(f"  -> {transcribed_text}")

        except sr.UnknownValueError:
            results.append((audio_file.name, None, "Could not understand audio"))
            print("  -> [Could not understand audio]")
        except sr.RequestError as e:
            results.append((audio_file.name, None, f"API error: {e}"))
            print(f"  -> [API error: {e}]")
        finally:
            if wav_path.exists():
                wav_path.unlink()  # clean up temp file

    # Write results to a file for easy comparison against what you actually said
    with open("results.txt", "w", encoding="utf-8") as f:
        f.write("Khmer STT Test Results\n")
        f.write("=" * 50 + "\n\n")
        for filename, text, error in results:
            f.write(f"File: {filename}\n")
            if text:
                f.write(f"Transcribed: {text}\n")
            else:
                f.write(f"Error: {error}\n")
            f.write(f"What I actually said: [fill this in manually]\n")
            f.write("-" * 50 + "\n\n")

    print(f"\nDone. Results saved to results.txt — fill in what you actually said "
          f"next to each transcription to judge accuracy.")


if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "./voice_clips"
    transcribe_folder(folder)
