"""Agent 1: Meeting Ingestion & Validation."""
import hashlib
import mimetypes
import time
from pathlib import Path

import structlog

from app.agents.state import MeetingAgentState, AuditEntry

logger = structlog.get_logger()

SUPPORTED_TEXT  = {".txt", ".vtt", ".srt"}
SUPPORTED_AUDIO = {".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".webm"}
SUPPORTED_VIDEO = {".mp4", ".mov", ".mkv", ".avi"}
MAX_FILE_SIZE   = 500 * 1024 * 1024  # 500 MB


async def ingestion_node(state: MeetingAgentState) -> dict:
    """Validate, classify, and hash the uploaded meeting file."""
    start = time.perf_counter()
    path  = Path(state["raw_input_path"])

    # ── Debug log so you can see exact path in terminal ──────────
    logger.info("Ingestion checking path", path=str(path), exists=path.exists())

    if not path.exists():
        parent_contents = (
            [str(p) for p in path.parent.iterdir()]
            if path.parent.exists()
            else ["parent directory does not exist"]
        )
        return {
            "errors": [
                f"File not found: {path}\n"
                f"Upload folder contents: {parent_contents}"
            ],
            "current_phase": "error",
            "audit_log": [],
            "warnings": [],
        }

    # ── Size check ────────────────────────────────────────────────
    file_size = path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        return {
            "errors": [f"File too large: {file_size / 1024 / 1024:.1f} MB (max 500 MB)"],
            "current_phase": "error",
            "audit_log": [],
            "warnings": [],
        }

    # ── Type detection ────────────────────────────────────────────
    ext = path.suffix.lower()
    if ext in SUPPORTED_TEXT:
        input_type = ext.lstrip(".")
    elif ext in SUPPORTED_AUDIO:
        input_type = "audio"
    elif ext in SUPPORTED_VIDEO:
        input_type = "video"
    else:
        return {
            "errors": [f"Unsupported file type: '{ext}'. Allowed: txt, vtt, srt, mp3, wav, m4a, mp4, mov"],
            "current_phase": "error",
            "audit_log": [],
            "warnings": [],
        }

    # ── Content hash (idempotency) ────────────────────────────────
    content          = path.read_bytes()
    content_hash     = hashlib.sha256(content).hexdigest()
    idempotency_key  = f"{state['org_id']}:{content_hash}"

    # ── For text files, load transcript immediately ───────────────
    transcript_raw = None
    if input_type in ("txt", "vtt", "srt"):
        transcript_raw = path.read_text(encoding="utf-8", errors="replace")
        logger.info("Text transcript loaded", chars=len(transcript_raw))

    duration_ms = int((time.perf_counter() - start) * 1000)

    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="IngestionAgent",
        action="validate_and_classify",
        input_summary=f"{path.name} ({file_size / 1024:.1f} KB)",
        output_summary=f"type={input_type}, hash={content_hash[:12]}",
        duration_ms=duration_ms,
    )

    logger.info(
        "Ingestion complete",
        file=path.name,
        type=input_type,
        size_kb=round(file_size / 1024, 1),
        duration_ms=duration_ms,
    )

    return {
        "input_type":       input_type,
        "idempotency_key":  idempotency_key,
        "transcript_raw":   transcript_raw,
        "current_phase":    "ingested",
        "audit_log":        [audit],
        "warnings":         [],
    }