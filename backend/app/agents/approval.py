"""Agent 10: Approval — human-in-the-loop gate before any external action is taken."""
from app.agents.state import MeetingState, ProcessingStatus
from app.db import db
from app.services.notification import notify_approver


async def approval_agent(state: MeetingState) -> MeetingState:
    """
    This node is interrupted before execution (LangGraph interrupt_before).

    Flow:
    1. Create an approval request in the DB.
    2. Send notification (email + Slack).
    3. Return — LangGraph suspends the graph.
    4. Human reviews the dashboard and approves/edits/rejects items.
    5. Human clicks "Execute" -> resumes the graph via the API.
    6. Graph reads updated state from the checkpoint.
    """
    if state.get("approval_request_id"):
        approval = await db.approvals.get(state["approval_request_id"])

        if approval.status == "approved":
            return {
                **state,
                "approved_items": approval.approved_items,
                "rejected_items": approval.rejected_items,
                "edited_items": approval.edited_items,
            }
        elif approval.status == "pending":
            return {**state, "status": "awaiting_approval"}

    approval_id = await db.approvals.create({
        "meeting_id": state["meeting_id"],
        "items": state["resolved_items"],
        "report": state["meeting_report"],
        "historical_context": state["historical_context"],
        "created_by": state["submitted_by"],
        "status": "pending",
    })

    await notify_approver(
        meeting_id=state["meeting_id"],
        approval_id=approval_id,
        submitted_by=state["submitted_by"],
        item_count=len(state["resolved_items"]),
    )

    return {
        **state,
        "approval_request_id": approval_id,
        "status": ProcessingStatus.AWAITING_APPROVAL,
    }
