"""
Human-in-the-loop approval endpoints.

GET    /api/approvals/{id}                 -> Approval dashboard data
PATCH  /api/approvals/{id}/items/{item_id} -> Edit action item
DELETE /api/approvals/{id}/items/{item_id} -> Reject item
POST   /api/approvals/{id}/execute         -> Resume graph after approval
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/{approval_id}")
async def get_approval(approval_id: str):
    raise NotImplementedError("TODO: fetch approval_requests row + items + historical context")


@router.patch("/{approval_id}/items/{item_id}")
async def edit_item(approval_id: str, item_id: str, edits: dict):
    raise NotImplementedError("TODO: apply edits, record diff in edit_history")


@router.delete("/{approval_id}/items/{item_id}")
async def reject_item(approval_id: str, item_id: str):
    raise NotImplementedError("TODO: move item into rejected_items")


@router.post("/{approval_id}/execute")
async def execute_approval(approval_id: str):
    """Mark the approval decided and resume the LangGraph run past interrupt_before."""
    raise NotImplementedError("TODO: set approval.status='approved', resume graph checkpoint")
