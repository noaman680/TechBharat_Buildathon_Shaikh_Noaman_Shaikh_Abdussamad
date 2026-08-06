"""Agent 10: Human-in-the-Loop approval checkpoint."""
import time
import structlog
from langgraph.types import interrupt

from app.agents.state import MeetingAgentState, ActionItem, AuditEntry

logger = structlog.get_logger()


async def approval_node(state: MeetingAgentState) -> dict:
    """
    HITL checkpoint — execution pauses here.
    LangGraph persists state and returns to caller.
    Graph resumes when human submits approval via API.
    """
    start = time.perf_counter()
    items = state["verified_items"]

    # Build approval payload shown to human
    approval_payload = {
        "meeting_id": state["meeting_id"],
        "action_items": [item.model_dump() for item in items],
        "structured_report": state.get("structured_report", {}).model_dump() if state.get("structured_report") else {},
        "warnings": state.get("warnings", []),
        "overdue_followups": state.get("overdue_followups", []),
        "related_meetings": state.get("related_meetings", []),
        "total_items": len(items),
        "high_confidence_count": sum(1 for i in items if i.confidence >= 0.8),
    }

    logger.info("Awaiting human approval", meeting_id=state["meeting_id"], items=len(items))

    # This raises GraphInterrupt — graph pauses, state is checkpointed
    human_decision = interrupt(approval_payload)

    # ── Resumed after human submits decision ──────────────────────────────────
    approved_raw = human_decision.get("approved_items", [])
    rejected_ids = set(human_decision.get("rejected_ids", []))

    # Apply human edits to action items
    approved_items = []
    for item_data in approved_raw:
        item = ActionItem(**item_data)
        item.status = "approved"
        approved_items.append(item)

    rejected_items = [i for i in items if i.id in rejected_ids]
    for item in rejected_items:
        item.status = "rejected"
        item.rejection_reason = human_decision.get("rejection_reasons", {}).get(item.id, "Rejected by user")

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="ApprovalAgent",
        action="human_review",
        input_summary=f"presented={len(items)} items",
        output_summary=f"approved={len(approved_items)}, rejected={len(rejected_items)}",
        reasoning="Human reviewed and approved/rejected action items",
        duration_ms=duration_ms,
    )

    return {
        "approved_items": approved_items,
        "rejected_items": rejected_items,
        "current_phase": "approved",
        "audit_log": [audit],
    }
