"""Agent 12: Audit Finalization — persist audit trail and update meeting status."""
import time
import json
import structlog

from app.agents.state import MeetingAgentState, AuditEntry

logger = structlog.get_logger()


async def audit_node(state: MeetingAgentState) -> dict:
    """Persist final audit trail and update meeting status in database."""
    start = time.perf_counter()

    summary = {
        "meeting_id": state["meeting_id"],
        "phase": state.get("current_phase", "unknown"),
        "action_items_extracted": len(state.get("action_items", [])),
        "action_items_verified": len(state.get("verified_items", [])),
        "action_items_approved": len(state.get("approved_items", [])),
        "action_items_executed": sum(
            1 for r in state.get("execution_results", []) if r.status == "success"
        ),
        "warnings": len(state.get("warnings", [])),
        "errors": len(state.get("errors", [])),
        "audit_entries": len(state.get("audit_log", [])),
    }

    logger.info("Meeting processing complete", **summary)

    # Persist to database if available
    try:
        from app.db.repositories.meetings import MeetingRepository
        repo = MeetingRepository()
        await repo.update_status(state["meeting_id"], "complete", summary)
        await repo.save_audit_log(state["meeting_id"], state.get("audit_log", []))
    except Exception as e:
        logger.warning("Failed to persist audit log", error=str(e))

    # Store in vector memory
    try:
        from app.memory.memory_service import MemoryService
        memory = MemoryService()
        await memory.store_meeting_embedding(
            meeting_id=state["meeting_id"],
            org_id=state["org_id"],
            summary=state.get("structured_report", {}).executive_summary if state.get("structured_report") else "",
            items=state.get("approved_items", []),
        )
    except Exception as e:
        logger.warning("Failed to store memory embedding", error=str(e))

    duration_ms = int((time.perf_counter() - start) * 1000)
    final_audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="AuditAgent",
        action="finalize",
        output_summary=json.dumps(summary),
        duration_ms=duration_ms,
    )

    return {
        "current_phase": "complete",
        "audit_log": [final_audit],
    }
