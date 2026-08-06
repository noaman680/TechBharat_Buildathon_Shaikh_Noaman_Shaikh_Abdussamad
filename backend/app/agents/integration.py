"""Agent 11: Integration Execution — create tasks in external systems."""
import time
import structlog

from app.agents.state import MeetingAgentState, ExecutionResult, AuditEntry
from app.integrations.registry import IntegrationRegistry

logger = structlog.get_logger()


async def integration_node(state: MeetingAgentState) -> dict:
    """Execute approved action items in configured integrations."""
    start = time.perf_counter()
    approved = state["approved_items"]
    registry = IntegrationRegistry()
    results = []
    warnings = []

    for item in approved:
        integration_name = item.target_integration
        integration = registry.get(integration_name)

        if not integration:
            warnings.append(f"Integration '{integration_name}' not configured — skipping '{item.title}'")
            results.append(ExecutionResult(
                action_item_id=item.id,
                integration=integration_name,
                status="skipped",
                error="Integration not configured",
            ))
            continue

        try:
            logger.info("Creating task", integration=integration_name, title=item.title)
            result = await integration.create_task(item, {})
            item.external_ref = {integration_name: result.external_id}
            item.status = "executed"
            results.append(result)
        except Exception as e:
            logger.error("Integration failed", integration=integration_name, error=str(e))
            results.append(ExecutionResult(
                action_item_id=item.id,
                integration=integration_name,
                status="failed",
                error=str(e),
            ))

    success = sum(1 for r in results if r.status == "success")
    duration_ms = int((time.perf_counter() - start) * 1000)
    audit = AuditEntry(
        timestamp=__import__("datetime").datetime.utcnow().isoformat(),
        agent="IntegrationAgent",
        action="execute_integrations",
        output_summary=f"success={success}, failed={len(results)-success}",
        duration_ms=duration_ms,
    )

    return {
        "execution_results": results,
        "approved_items": approved,
        "warnings": warnings,
        "current_phase": "executed",
        "audit_log": [audit],
    }
