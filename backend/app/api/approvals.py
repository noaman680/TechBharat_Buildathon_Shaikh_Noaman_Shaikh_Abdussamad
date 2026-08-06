"""Approval API routes — HITL review and execution."""
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ApprovalDecision(BaseModel):
    approved_items: list[dict]
    rejected_ids: list[str]
    rejection_reasons: dict = {}


@router.get("/{meeting_id}")
async def get_approval_session(meeting_id: str):
    """Get items pending approval for a meeting."""
    return {
        "meeting_id": meeting_id,
        "status": "awaiting_approval",
        "action_items": [],
        "warnings": [],
        "overdue_followups": [],
    }


@router.post("/{meeting_id}/submit")
async def submit_approval(meeting_id: str, decision: ApprovalDecision):
    """Submit human approval — resumes the LangGraph pipeline."""
    try:
        from app.agents.graph import build_graph
        from langgraph.types import Command

        graph = build_graph()
        config = {"configurable": {"thread_id": meeting_id}}
        result = await graph.ainvoke(
            Command(resume=decision.model_dump()),
            config=config,
        )
        return {
            "meeting_id": meeting_id,
            "status": "executing",
            "approved_count": len(decision.approved_items),
            "rejected_count": len(decision.rejected_ids),
        }
    except Exception as e:
        return {"meeting_id": meeting_id, "status": "error", "error": str(e)}


@router.get("/{meeting_id}/results")
async def get_execution_results(meeting_id: str):
    """Get integration execution results after approval."""
    return {"meeting_id": meeting_id, "execution_results": []}
