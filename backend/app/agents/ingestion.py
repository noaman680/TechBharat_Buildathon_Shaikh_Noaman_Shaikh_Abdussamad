"""Agent 1: Ingestion — normalize input, hash it, and check for duplicates."""
import hashlib
import logging

from app.agents.state import MeetingState, ProcessingStatus
from app.db import db
from app.services.storage import storage
from app.services.format_detection import detect_format, extract_metadata

logger = logging.getLogger(__name__)


async def ingestion_agent(state: MeetingState) -> MeetingState:
    """
    1. Detect input format (txt/vtt/srt/mp3/mp4/wav/webm)
    2. Compute SHA-256 hash of raw content
    3. Check PostgreSQL for an existing meeting with the same hash
    4. Extract metadata (file size, duration, detected language hint)
    5. Route to transcription or text normalization
    """
    content = await storage.read(state["raw_input_path"])
    input_hash = hashlib.sha256(content).hexdigest()

    # Idempotency check — Layer 1 (see docs/BLUEPRINT.md §13)
    existing = await db.meetings.find_by_hash(input_hash, state["organization_id"])
    if existing:
        logger.info("Duplicate detected: %s", existing.meeting_id)
        return {**state, "status": "duplicate", "meeting_id": existing.meeting_id}

    format_info = detect_format(content, state["raw_input_path"])
    metadata = extract_metadata(content, format_info)

    return {
        **state,
        "input_hash": input_hash,
        "input_format": format_info.type,
        "meeting_metadata": metadata,
        "status": ProcessingStatus.TRANSCRIBING
        if format_info.needs_transcription
        else ProcessingStatus.ANALYZING,
    }
