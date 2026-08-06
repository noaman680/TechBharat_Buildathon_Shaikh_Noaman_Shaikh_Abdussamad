"""Pyannote-based speaker diarization for audio/video input."""


async def pyannote_pipeline(input_path: str):
    raise NotImplementedError("TODO: run Pyannote Audio 3.1 diarization pipeline")


def align_diarization_with_transcript(diarization, transcript_raw: str, participants: list):
    raise NotImplementedError(
        "TODO: merge Pyannote speaker segments with Whisper timestamps, "
        "then match speaker_id to a participant name where possible"
    )
