"""Analytics routes."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/org/{org_id}/summary")
async def org_summary(org_id: str):
    """Organization-level meeting analytics."""
    return {
        "org_id": org_id,
        "total_meetings": 0,
        "total_action_items": 0,
        "completion_rate": 0.0,
        "avg_items_per_meeting": 0.0,
        "top_owners": [],
        "overdue_count": 0,
    }


@router.get("/org/{org_id}/health")
async def meeting_health(org_id: str):
    """Meeting health analytics — talk time, participation, decision density."""
    return {
        "org_id": org_id,
        "avg_decision_density": 0.0,
        "avg_participation": 0.0,
        "commitment_completion_rate": 0.0,
    }
