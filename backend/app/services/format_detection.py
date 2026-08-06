"""Detect input file format and extract basic metadata (§5 Agent 1)."""
from dataclasses import dataclass


@dataclass
class FormatInfo:
    type: str                # txt/vtt/srt/mp3/mp4/wav/webm
    needs_transcription: bool


def detect_format(content: bytes, path: str) -> FormatInfo:
    raise NotImplementedError("TODO: sniff file type from extension/magic bytes")


def extract_metadata(content: bytes, format_info: FormatInfo) -> dict:
    raise NotImplementedError(
        "TODO: extract date, timezone, participants, title, duration, "
        "language hint from the file/headers"
    )
