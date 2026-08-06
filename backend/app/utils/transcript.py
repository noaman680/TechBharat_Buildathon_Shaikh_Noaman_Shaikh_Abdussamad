"""Transcript formatting helpers shared across agents."""


def build_raw_transcript(whisper_result) -> str:
    raise NotImplementedError("TODO: flatten Whisper verbose_json segments into plain text")


def format_transcript_for_extraction(turns: list) -> str:
    """Render speaker turns as `[HH:MM:SS] Speaker: text` lines for the extraction prompt."""
    raise NotImplementedError("TODO: format List[SpeakerTurn] into the extraction prompt's shape")
