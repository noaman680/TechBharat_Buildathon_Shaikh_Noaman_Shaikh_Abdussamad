"""Agent 2: Transcription — convert audio/video into timestamped text."""
from app.agents.state import MeetingState
from app.services.transcription import whisper_client
from app.services.audio import extract_audio
from app.services.language import handle_code_switched_transcript
from app.utils.audit import build_audit_entry
from app.utils.transcript import build_raw_transcript


async def transcription_agent(state: MeetingState) -> MeetingState:
    """
    Uses Whisper v3-large for:
    - Multi-language transcription (including code-switched Hindi+English)
    - Word-level timestamps
    - Confidence scores per segment
    - Noise handling
    """
    audio_path = await extract_audio(state["raw_input_path"])

    result = await whisper_client.transcribe(
        audio_path,
        model="whisper-1",
        response_format="verbose_json",
        timestamp_granularities=["word", "segment"],
        language=None,  # Auto-detect
    )

    # Handle code-switched languages (Hindi-English mixing) — see Appendix B
    if result.language in ["hi", "mr", "ta", "te", "kn"]:
        result = await handle_code_switched_transcript(result)

    raw_transcript = build_raw_transcript(result)
    audit_entry = build_audit_entry("transcription_agent", result)

    return {
        **state,
        "transcript_raw": raw_transcript,
        "audit_trail": state["audit_trail"] + [audit_entry],
    }
