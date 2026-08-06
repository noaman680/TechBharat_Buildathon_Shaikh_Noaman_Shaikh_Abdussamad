"""Agent 9: Memory — cross-meeting context, deduplication, enrichment."""
import time
import structlog

from app.agents.state import MeetingAgentState, AuditEntry

logger = structlog.get_logger()


async def memory_node(state: MeetingAgentState) -> dict:
    """Enrich with cross-meeting context and deduplicate action items."""
    start = time.perf_counter()
    items = state["verified_items"]
    org_id = state["org_id"]
    warnings = []
    new_items = []

    try:
        from app.memory.memory_service import MemoryService
        memory = MemoryService()

        # Deduplicate against vector store
        for item in items:
            is_dup, similar_title = await memory.is_duplicate(
                item.title + " " + item.description, org_id
            )
            if is_dup:
                warnings.append(
                    f"Skipping duplicate: \'{item.title}\' (similar to existing: \'{similar_title}\')"
                )
            else:
                new_items.append(item)

        # Get overdue follow-ups from past meetings
        owners = list({i.owner_resolved.email for i in new_items if i.owner_resolved and i.owner_resolved.email})
        overdue = await memory.get_overdue_tasks(org_id, owners)

        # Find related meetings
        summary = state.get("structured_report")
        related = []
        if summary:
            related = await memory.find_related_meetings(summary.executive_summary, org_id)

        # Build recurring owner cache
        recurring = await memory.get_recurring_owners(org_id)

    except Exception as e:
        logger.warning("Memory service unavailable", error=str(e))
        new_items = items
        overdue = []
        related = []
        recurring = {}
        warnings.append(f"Memory service unavailable: {e}")

    # Enrich report with overdue tasks
    report = state.get("structured_report")
    if report and overdue:
        for task in overdue[:5]:
            report.follow_ups.append(
                f"⚠️ Overdue from {task.get('meeting_date', 'past meeting')}: "
                f"\'{task.get('title')}\'  (Owner: {task.get('owner')})"
            )

    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="MemoryAgent",
        action="enrich_and_deduplicate",
        output_summary=f"kept={len(new_items)}, dupes_removed={len(items)-len(new_items)}, overdue={len(overdue)}",
        duration_ms=duration_ms,
    )

    return {
        "verified_items": new_items,
        "structured_report": report,
        "related_meetings": related,
        "overdue_followups": overdue,
        "recurring_owners": recurring,
        "warnings": warnings,
        "current_phase": "memory_enriched",
        "audit_log": [audit],
    }
