"""Whisper client wrapper for the transcription agent."""


class _WhisperClient:
    async def transcribe(self, audio_path: str, **kwargs):
        raise NotImplementedError("TODO: call OpenAI Whisper v3-large and return verbose_json")


whisper_client = _WhisperClient()
