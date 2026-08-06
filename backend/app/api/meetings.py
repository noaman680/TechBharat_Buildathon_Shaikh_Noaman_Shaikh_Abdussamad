"""
Meeting processing endpoints.

POST   /api/meetings/upload              -> Upload file, start processing
GET    /api/meetings/{id}/status         -> Polling / SSE stream
GET    /api/meetings/{id}                -> Full meeting data
GET    /api/meetings/{id}/report         -> Structured report
GET    /api/meetings/{id}/items          -> Action items
GET    /api/meetings/{id}/transcript     -> Full transcript with speakers
GET    /api/meetings/{id}/audit          -> Full audit trail
GET    /api/meetings/{id}/explain/{item_id} -> Explainability for one item
POST   /api/webhooks/zoom | teams | meet -> Live-meeting webhooks
"""
from fastapi import APIRouter, UploadFile, HTTPException

router = APIRouter()


@router.post("/upload")
async def upload_meeting(file: UploadFile):
    """Accept a transcript or media file and kick off the LangGraph pipeline."""
    raise NotImplementedError("TODO: persist file, create meeting row, start graph run")


@router.get("/{meeting_id}/status")
async def get_status(meeting_id: str):
    raise NotImplementedError("TODO: return current ProcessingStatus, or stream via SSE")


@router.get("/{meeting_id}")
async def get_meeting(meeting_id: str):
    raise NotImplementedError("TODO: fetch full meeting record")


@router.get("/{meeting_id}/report")
async def get_report(meeting_id: str):
    raise NotImplementedError("TODO: fetch meeting_reports row")


@router.get("/{meeting_id}/items")
async def get_action_items(meeting_id: str):
    raise NotImplementedError("TODO: fetch action_items for this meeting")


@router.get("/{meeting_id}/transcript")
async def get_transcript(meeting_id: str):
    raise NotImplementedError("TODO: fetch transcript + speaker turns")


@router.get("/{meeting_id}/audit")
async def get_audit(meeting_id: str):
    raise NotImplementedError("TODO: fetch full audit_logs trail")


@router.get("/{meeting_id}/explain/{item_id}")
async def explain_item(meeting_id: str, item_id: str):
    """Return extraction reasoning, confidence breakdown, evidence, and resolution trace."""
    raise NotImplementedError("TODO: build explainability payload (see blueprint §14)")
