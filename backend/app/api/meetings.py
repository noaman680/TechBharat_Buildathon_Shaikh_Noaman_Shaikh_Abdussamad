"""Meeting API routes — MeetMind."""
import json
import uuid
import hashlib
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

# In-memory store for demo (replaces DB for now)
_meetings: dict = {}


class MeetingResponse(BaseModel):
    meeting_id: str
    status: str
    message: str


async def run_pipeline(meeting_id: str, file_path: str, meeting_date: str,
                       timezone: str, participants: list, org_id: str, user_id: str):
    """Run the LangGraph agent pipeline in background."""
    _meetings[meeting_id]["status"] = "processing"
    _meetings[meeting_id]["phase"] = "planning"

    try:
        from app.agents.graph import build_graph

        graph = build_graph()

        initial_state = {
            "meeting_id": meeting_id,
            "org_id": org_id,
            "user_id": user_id,
            "idempotency_key": "",
            "raw_input_path": file_path,
            "input_type": _detect_type(file_path),
            "meeting_date": meeting_date,
            "timezone": timezone,
            "participants_hint": participants,
            "transcript_raw": None,
            "transcript_segments": [],
            "speakers": [],
            "language_detected": "en",
            "planning_steps": [],
            "structured_report": None,
            "action_items": [],
            "verified_items": [],
            "pending_approval": [],
            "approved_items": [],
            "rejected_items": [],
            "approval_session_id": None,
            "execution_results": [],
            "current_phase": "starting",
            "errors": [],
            "warnings": [],
            "audit_log": [],
            "related_meetings": [],
            "recurring_owners": {},
            "overdue_followups": [],
        }

        config = {"configurable": {"thread_id": meeting_id}}
        result = await graph.ainvoke(initial_state, config=config)

        _meetings[meeting_id]["status"] = "awaiting_approval"
        _meetings[meeting_id]["phase"] = "awaiting_approval"
        _meetings[meeting_id]["result"] = result

    except Exception as e:
        import structlog
        log = structlog.get_logger()
        log.error("Pipeline failed", meeting_id=meeting_id, error=str(e))
        _meetings[meeting_id]["status"] = "error"
        _meetings[meeting_id]["phase"] = "error"
        _meetings[meeting_id]["error"] = str(e)


def _detect_type(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext in (".mp3", ".wav", ".m4a", ".flac", ".ogg", ".opus", ".webm"):
        return "audio"
    if ext in (".mp4", ".mov", ".mkv", ".avi"):
        return "video"
    return ext.lstrip(".") or "txt"


@router.post("/upload", response_model=MeetingResponse)
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    meeting_date: str = Form(default=datetime.utcnow().strftime("%Y-%m-%d")),
    timezone: str = Form(default="Asia/Kolkata"),
    participants: str = Form(default="[]"),
    org_id: str = Form(default="demo-org"),
    user_id: str = Form(default="demo-user"),
):
    import os

    meeting_id = str(uuid.uuid4())

    # ── ABSOLUTE path — fixes WinError 2 on Windows ──────────────
    # Goes up from meetings.py → api → app → backend → uploads
    backend_dir = Path(__file__).resolve().parent.parent.parent
    upload_dir  = backend_dir / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix    = Path(file.filename or "meeting.txt").suffix or ".txt"
    file_path = str(upload_dir / f"{meeting_id}{suffix}")
    # ─────────────────────────────────────────────────────────────

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Verify file actually saved before queueing
    if not Path(file_path).exists():
        return MeetingResponse(
            meeting_id=meeting_id,
            status="error",
            message=f"File save failed. Path: {file_path}",
        )

    try:
        participant_list = json.loads(participants)
    except Exception:
        participant_list = []

    _meetings[meeting_id] = {
        "meeting_id":   meeting_id,
        "status":       "queued",
        "phase":        "starting",
        "file_path":    file_path,
        "meeting_date": meeting_date,
        "timezone":     timezone,
        "participants": participant_list,
        "org_id":       org_id,
        "created_at":   datetime.utcnow().isoformat(),
    }

    background_tasks.add_task(
        run_pipeline,
        meeting_id=meeting_id,
        file_path=file_path,
        meeting_date=meeting_date,
        timezone=timezone,
        participants=participant_list,
        org_id=org_id,
        user_id=user_id,
    )

    return MeetingResponse(
        meeting_id=meeting_id,
        status="processing",
        message=f"Uploaded: {file.filename} → {file_path}",
    )

@router.get("/{meeting_id}/status")
async def get_status(meeting_id: str):
    """Get processing status — also streams SSE events."""
    meeting = _meetings.get(meeting_id)
    if not meeting:
        return {"meeting_id": meeting_id, "status": "not_found", "phase": "error"}

    result = meeting.get("result", {})
    action_items = []
    if result and hasattr(result.get("verified_items"), "__iter__"):
        action_items = [i.model_dump() if hasattr(i, "model_dump") else i
                        for i in result.get("verified_items", [])]

    return {
        "meeting_id": meeting_id,
        "status": meeting.get("status", "processing"),
        "phase": meeting.get("phase", "starting"),
        "message": _phase_message(meeting.get("phase", "starting")),
        "progress": _phase_progress(meeting.get("phase", "starting")),
        "action_items_count": len(action_items),
        "error": meeting.get("error"),
    }


@router.get("/{meeting_id}/report")
async def get_report(meeting_id: str):
    """Get the structured meeting report."""
    meeting = _meetings.get(meeting_id, {})
    result = meeting.get("result", {})

    report = result.get("structured_report")
    if report and hasattr(report, "model_dump"):
        report_data = report.model_dump()
    elif isinstance(report, dict):
        report_data = report
    else:
        report_data = {
            "executive_summary": "Processing not complete yet.",
            "decisions": [],
            "action_items": [],
            "open_questions": [],
            "risks": [],
            "key_insights": [],
            "follow_ups": [],
        }

    return {
        "meeting_id": meeting_id,
        "status": meeting.get("status", "processing"),
        "report": report_data,
        "warnings": result.get("warnings", []),
    }


@router.get("/{meeting_id}/audit")
async def get_audit(meeting_id: str):
    """Get the full audit trail."""
    meeting = _meetings.get(meeting_id, {})
    result = meeting.get("result", {})
    audit = result.get("audit_log", [])
    entries = [e.model_dump() if hasattr(e, "model_dump") else e for e in audit]
    return {"meeting_id": meeting_id, "audit_entries": entries}


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """Delete a meeting."""
    _meetings.pop(meeting_id, None)
    return {"meeting_id": meeting_id, "deleted": True}


@router.get("")
async def list_meetings(org_id: str = "demo-org"):
    """List all meetings."""
    return {
        "meetings": [
            {"meeting_id": k, "status": v.get("status"), "created_at": v.get("created_at")}
            for k, v in _meetings.items()
            if v.get("org_id") == org_id
        ]
    }


def _phase_message(phase: str) -> str:
    return {
        "starting":           "Initialising pipeline...",
        "ingested":           "File validated ✓",
        "transcribing":       "Transcribing audio with Whisper...",
        "diarizing":          "Identifying speakers...",
        "planning":           "Analysing meeting type...",
        "extracting":         "Extracting action items with GPT-4o...",
        "verifying":          "Verifying extracted items...",
        "resolving_identity": "Resolving owner identities...",
        "resolving_dates":    "Converting dates to calendar...",
        "memory_enriching":   "Loading cross-meeting context...",
        "awaiting_approval":  "Ready for your review ✅",
        "executing":          "Creating tasks in external systems...",
        "complete":           "Done!",
        "error":              "Processing failed",
    }.get(phase, "Processing...")


def _phase_progress(phase: str) -> int:
    order = [
        "starting", "ingested", "transcribing", "diarizing",
        "planning", "extracting", "verifying",
        "resolving_identity", "resolving_dates",
        "memory_enriching", "awaiting_approval",
        "executing", "complete",
    ]
    try:
        return round((order.index(phase) / (len(order) - 1)) * 100)
    except ValueError:
        return 0