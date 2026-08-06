"""Agent 3: Speaker Diarization using pyannote.audio."""
import time
import structlog

from app.agents.state import MeetingAgentState, Speaker, TranscriptSegment, AuditEntry
from app.config import settings

logger = structlog.get_logger()


def find_dominant_speaker(start: float, end: float, diarization) -> str:
    """Find the speaker with maximum overlap in a time segment."""
    speaker_time = {}
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        overlap_start = max(start, turn.start)
        overlap_end = min(end, turn.end)
        if overlap_end > overlap_start:
            speaker_time[speaker] = speaker_time.get(speaker, 0) + (overlap_end - overlap_start)
    if not speaker_time:
        return "UNKNOWN"
    return max(speaker_time, key=speaker_time.get)


async def diarization_node(state: MeetingAgentState) -> dict:
    """Assign speakers to transcript segments using pyannote diarization."""
    start = time.perf_counter()
    segments = state["transcript_segments"]
    path = state["raw_input_path"]

    try:
        from pyannote.audio import Pipeline

        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=settings.hf_token,
        )
        diarization = pipeline(path)

        speaker_labels = set()
        updated_segments = []
        for seg in segments:
            speaker_id = find_dominant_speaker(seg.start_time, seg.end_time, diarization)
            speaker_labels.add(speaker_id)
            updated_segments.append(seg.model_copy(update={"speaker_id": speaker_id}))

        speakers = [
            Speaker(id=label, label=label)
            for label in sorted(speaker_labels)
        ]

    except (ImportError, Exception) as e:
        logger.warning("Diarization unavailable", error=str(e))
        # Fallback: mark all segments as single speaker
        updated_segments = [
            seg.model_copy(update={"speaker_id": "SPEAKER_00"})
            for seg in segments
        ]
        speakers = [Speaker(id="SPEAKER_00", label="SPEAKER_00")]

    # Attempt speaker resolution from participants hint
    participant_emails = state.get("participants_hint", [])
    if participant_emails and len(speakers) == len(participant_emails):
        for i, speaker in enumerate(speakers):
            parts = participant_emails[i].split("@")[0].split(".")
            name = " ".join(p.capitalize() for p in parts)
            speaker.resolved_name = name
            speaker.email = participant_emails[i]
            speaker.confidence = 0.6

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="DiarizationAgent",
        action="speaker_diarization",
        output_summary=f"speakers={len(speakers)}",
        duration_ms=duration_ms,
    )

    return {
        "transcript_segments": updated_segments,
        "speakers": speakers,
        "current_phase": "diarized",
        "audit_log": [audit],
    }
