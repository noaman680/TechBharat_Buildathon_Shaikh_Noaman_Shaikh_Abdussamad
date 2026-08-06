"""Agent 12: Audit — record the full trace, results, and receipts for a meeting run."""
from datetime import datetime, timezone

from app.agents.state import MeetingState, ProcessingStatus
from app.db import db
from app.memory.memory_service import update_organizational_memory


async def audit_agent(state: MeetingState) -> MeetingState:
    """
    Persist the complete audit trail, mark the meeting complete, and (if any
    items were approved) trigger the cross-meeting memory update so future
    meetings can reference this one.
    """
    await db.audit_logs.bulk_insert(state["meeting_id"], state["audit_trail"])

    if state.get("approved_items"):
        await update_organizational_memory(state["meeting_id"], state)

    await db.meetings.mark_complete(state["meeting_id"], processed_at=datetime.now(timezone.utc))

    return {**state, "status": ProcessingStatus.COMPLETE}


async def error_handler_node(state: MeetingState) -> MeetingState:
    """Terminal node for unrecoverable errors — logs and marks the meeting failed."""
    await db.meetings.mark_failed(state["meeting_id"], errors=state.get("errors", []))
    return {**state, "status": ProcessingStatus.FAILED}
