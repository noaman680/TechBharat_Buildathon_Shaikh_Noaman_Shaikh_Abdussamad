"""Agent 3: Diarization — identify and label speakers throughout the transcript."""
from app.agents.state import MeetingState
from app.services.diarization import pyannote_pipeline, align_diarization_with_transcript
from app.services.subtitles import parse_subtitle_speakers
from app.services.txt_transcript import parse_plain_text_turns


async def diarization_agent(state: MeetingState) -> MeetingState:
    """
    Strategy:
    1. If VTT/SRT has speaker labels, use them directly.
    2. If a plain-text transcript uses "Name (HH:MM:SS): text" lines, parse those.
    3. Otherwise (raw audio/video), run Pyannote diarization and match to
       Whisper timestamps, cross-referencing meeting.participants for names.
    4. Output: List[SpeakerTurn] with speaker_id and best-guess name.
    """
    if state["input_format"] in ["vtt", "srt"]:
        turns = parse_subtitle_speakers(state["transcript_raw"])
    elif state["input_format"] == "txt":
        turns = parse_plain_text_turns(state["transcript_raw"])
    else:
        diarization = await pyannote_pipeline(state["raw_input_path"])
        turns = align_diarization_with_transcript(
            diarization,
            state["transcript_raw"],
            state["meeting_metadata"].get("participants", []),
        )

    return {**state, "transcript_turns": turns}