import assemblyai as aai
import os

aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY", "")


def transcribe_audio(audio_path: str) -> str:
    config = aai.TranscriptionConfig(
        speech_models=["universal-3-pro", "universal-2"]  # ✅ required as list of strings
    )
    transcriber = aai.Transcriber(config=config)
    transcript = transcriber.transcribe(audio_path)

    if transcript.status == aai.TranscriptStatus.error:
        return f"[STT ERROR] {transcript.error}"

    return transcript.text