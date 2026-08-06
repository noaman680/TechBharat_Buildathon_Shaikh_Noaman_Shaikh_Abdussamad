"""Agent 2: Audio/Video Transcription using OpenAI Whisper."""
import time
from pathlib import Path
from typing import Optional
import structlog

from app.agents.state import MeetingAgentState, TranscriptSegment, AuditEntry

logger = structlog.get_logger()


def format_timestamp(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def segments_to_raw(segments: list[dict]) -> str:
    lines = []
    for seg in segments:
        ts = format_timestamp(seg["start"])
        lines.append(f"[{ts}] {seg['text'].strip()}")
    return "\n".join(lines)


async def transcription_node(state: MeetingAgentState) -> dict:
    """Transcribe audio/video file to text using Whisper large-v3."""
    start = time.perf_counter()
    path = state["raw_input_path"]

    try:
        import whisper
        import torch

        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info("Loading Whisper model", device=device)

        model = whisper.load_model("large-v3", device=device)
        result = model.transcribe(
            path,
            language=None,
            word_timestamps=True,
            task="transcribe",
            verbose=False,
        )

        segments = [
            TranscriptSegment(
                speaker_id="UNKNOWN",
                text=seg["text"].strip(),
                start_time=seg["start"],
                end_time=seg["end"],
                timestamp_label=format_timestamp(seg["start"]),
            )
            for seg in result["segments"]
        ]

        transcript_raw = segments_to_raw(result["segments"])
        language = result.get("language", "en")

    except ImportError:
        logger.warning("Whisper not installed — using mock transcription")
        transcript_raw = "[00:00:00] Mock transcript — install openai-whisper for real transcription."
        segments = [
            TranscriptSegment(
                speaker_id="SPEAKER_00",
                text="Mock transcript",
                start_time=0.0,
                end_time=5.0,
                timestamp_label="00:00:00",
            )
        ]
        language = "en"

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="TranscriptionAgent",
        action="whisper_transcribe",
        input_summary=f"file={path}",
        output_summary=f"segments={len(segments)}, lang={language}",
        duration_ms=duration_ms,
    )

    return {
        "transcript_raw": transcript_raw,
        "transcript_segments": segments,
        "language_detected": language,
        "current_phase": "transcribed",
        "audit_log": [audit],
    }
