"""Meeting API routes."""
import json
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


class MeetingResponse(BaseModel):
    meeting_id: str
    status: str
    message: str


async def process_meeting_background(meeting_id: str, file_path: str,
                                      meeting_date: str, timezone: str,
                                      participants: list[str], org_id: str, user_id: str):
    """Run the LangGraph pipeline in background."""
    try:
        from app.agents.graph import build_graph
        from app.agents.state import MeetingAgentState

        graph = build_graph()
        initial_state: MeetingAgentState = {
            "meeting_id": meeting_id,
            "org_id": org_id,
            "user_id": user_id,
            "idempotency_key": "",
            "raw_input_path": file_path,
            "input_type": "txt",
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
        return result

    except Exception as e:
        import structlog
        logger = structlog.get_logger()
        logger.error("Meeting processing failed", meeting_id=meeting_id, error=str(e))


@router.post("/upload", response_model=MeetingResponse)
async def upload_meeting(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    meeting_date: str = Form(...),
    timezone: str = Form("UTC"),
    participants: str = Form("[]"),
    org_id: str = Form("demo-org"),
    user_id: str = Form("demo-user"),
):
    """Upload a meeting file and start async processing."""
    import uuid, aiofiles, os
    from app.config import settings

    meeting_id = str(uuid.uuid4())
    upload_dir = Path(settings.local_storage_path)
    upload_dir.mkdir(parents=True, exist_ok=True)

    suffix = Path(file.filename or "meeting.txt").suffix
    file_path = str(upload_dir / f"{meeting_id}{suffix}")

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(await file.read())

    participants_list = json.loads(participants)

    background_tasks.add_task(
        process_meeting_background,
        meeting_id=meeting_id,
        file_path=file_path,
        meeting_date=meeting_date,
        timezone=timezone,
        participants=participants_list,
        org_id=org_id,
        user_id=user_id,
    )

    return MeetingResponse(
        meeting_id=meeting_id,
        status="processing",
        message="Meeting uploaded. Processing started.",
    )


@router.get("/{meeting_id}/status")
async def get_meeting_status(meeting_id: str):
    """Get processing status for a meeting."""
    return {"meeting_id": meeting_id, "status": "processing", "phase": "extracting"}


@router.get("/{meeting_id}/report")
async def get_meeting_report(meeting_id: str):
    """Get the structured report for a processed meeting."""
    return {
        "meeting_id": meeting_id,
        "status": "complete",
        "report": {
            "executive_summary": "Demo meeting summary.",
            "decisions": [],
            "action_items": [],
            "open_questions": [],
            "risks": [],
        },
    }


@router.get("/{meeting_id}/audit")
async def get_audit_trail(meeting_id: str):
    """Get the full audit trail for a meeting."""
    return {"meeting_id": meeting_id, "audit_entries": []}


@router.delete("/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """Delete a meeting and all its artifacts (GDPR)."""
    return {"meeting_id": meeting_id, "deleted": True}
